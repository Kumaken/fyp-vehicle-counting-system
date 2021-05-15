'''
VCS entry point.
'''

# pylint: disable=wrong-import-position

import sys
import time
import cv2

from dotenv import load_dotenv
load_dotenv()

from PyQt5 import QtWidgets

import settings
from util.logger import init_logger
from util.image import take_screenshot
from util.logger import get_logger
from util.debugger import mouse_callback
from ObjectCounter import ObjectCounter

from GUI.const import MASK_IMG_CV2
from GUI.detector_gui import DetectorGUI
init_logger()
logger = get_logger()

# global variables:
is_paused = False
output_frame = None
stop_detection = False

def play_or_pause():
    global is_paused
    is_paused = False if is_paused else True
    logger.info('Loop paused/played.', extra={'meta': {'label': 'PAUSE_PLAY_LOOP', 'is_paused': is_paused}})

def screenshoot():
    global output_frame
    take_screenshot(output_frame)

def stop():
    global stop_detection
    stop_detection = True
    logger.info('Loop stopped.', extra={'meta': {'label': 'STOP_LOOP'}})

def run(images_dict, detection_lines, video_path, weight_path, cfg_path):
    '''
    Initialize object counter class and run counting loop.
    '''
    global is_paused, output_frame, stop_detection
    # reset global state
    stop_detection = False
    is_paused = False
    output_frame = None

    import settings
    settings.YOLO_WEIGHTS_PATH = weight_path
    settings.YOLO_CONFIG_PATH = cfg_path
    # SET ENV VARIABLES (DETECTION LINES)
    print("[DEBUG][run] Detection lines:", detection_lines)
    settings.COUNTING_LINES = detection_lines

    print("[DEBUG][run] Setup video:", video_path, weight_path, cfg_path)
    video = video_path
    cap = cv2.VideoCapture(video)
    if not cap.isOpened():
        logger.error('Not a valid video source: %s', video, extra={
            'meta': {'label': 'INVALID_VIDEO_SOURCE'},
        })
        sys.exit()
    retval, frame = cap.read()
    f_height, f_width, _ = frame.shape
    detection_interval = settings.DI
    mcdf = settings.MCDF
    mctf = settings.MCTF
    detector = settings.DETECTOR
    tracker = settings.TRACKER
    use_droi = settings.USE_DROI
    # create detection region of interest polygon
    # CHANGE
    # droi = settings.DROI \
    #         if use_droi \
    #         else [(0, 0), (f_width, 0), (f_width, f_height), (0, f_height)]
    droi = images_dict[MASK_IMG_CV2]

    show_droi = settings.SHOW_DROI
    counting_lines = settings.COUNTING_LINES
    show_counts = settings.SHOW_COUNTS
    hud_color = settings.HUD_COLOR

    object_counter = ObjectCounter(frame, detector, tracker, droi, show_droi, mcdf, mctf,
                                   detection_interval, counting_lines, show_counts, hud_color)

    record = settings.RECORD
    if record:
        # initialize video object to record counting
        # CHANGE
        # output_video = cv2.VideoWriter(settings.OUTPUT_VIDEO_PATH, \
        #                                 cv2.VideoWriter_fourcc(*'MJPG'), \
        #                                 30, \
        #                                 (f_width, f_height))
        output_video = cv2.VideoWriter(video_path, \
                                cv2.VideoWriter_fourcc(*'MJPG'), \
                                30, \
                                (f_width, f_height))


    logger.info('[DEBUG] Detector module is starting...', extra={
        'meta': {
            'label': 'DETECTOR_BEGIN',
            'counter_config': {
                'di': detection_interval,
                'mcdf': mcdf,
                'mctf': mctf,
                'detector': detector,
                'tracker': tracker,
                'use_droi': use_droi,
                'droi': droi,
                'counting_lines': counting_lines
            },
        },
    })

    headless = settings.HEADLESS
    window_name = "Detector Module"
    if not headless:
        # capture mouse events in the debug window
        cv2.namedWindow(window_name)
        cv2.setMouseCallback('[DEBUG]', mouse_callback, {'frame_width': f_width, 'frame_height': f_height})

    # is_paused = False

    frames_count = round(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frames_processed = 0

    # initialize control gui:
    detector_gui = DetectorGUI()
    detector_gui.show()

    # to count FPS:
    # used to record the time when we processed last frame
    prev_frame_time = 0

    # used to record the time at which we processed current frame
    new_frame_time = 0
    try:
        # main loop
        # print("IS STOP? ", stop_detection)
        while not stop_detection and retval:
            # 0xFF is a hexadecimal constant which is 11111111 in binary. Bitwise AND with 0xFF extracts 8 bits from cv2.waitKey (which returns 32 bits)
            # waitKey(0) function returns -1 when no input is made. When a button is pressed, it returns a 32 bit integer
            # waitKey(0) means shows indefinitely until keypress. waitKey(1) means it shows only for 1 ms
            k = cv2.waitKey(1) & 0xFF
            if k == ord('p'): # pause/play loop if 'p' key is pressed
                play_or_pause()
                # is_paused = False if is_paused else True
                # logger.info('Loop paused/played.', extra={'meta': {'label': 'PAUSE_PLAY_LOOP', 'is_paused': is_paused}})
            if k == ord('s') and output_frame is not None: # save frame if 's' key is pressed
                take_screenshot(output_frame)
            if k == ord('q'): # end video loop if 'q' key is pressed
                logger.info('Loop stopped.', extra={'meta': {'label': 'STOP_LOOP'}})
                break

            if is_paused:
                time.sleep(0.5)
                continue

            _timer = cv2.getTickCount() # set timer to calculate processing frame rate

            # OBJECT COUNTER STARTS:
            object_counter.count(frame) # bottleneck is here
            output_frame = object_counter.visualize()

            # Calculating the fps
            new_frame_time = time.time()
            # fps will be number of frame processed in given time frame
            # since their will be most of time error of 0.001 second
            # we will be subtracting it to get more accurate result
            fps = 1/(new_frame_time-prev_frame_time)
            prev_frame_time = new_frame_time

            # converting the fps into integer
            fps = str(fps)

            # puting the FPS count on the frame
            cv2.putText(frame, "FPS:"+fps, (settings.DEBUG_WINDOW_SIZE[0], 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 1, cv2.LINE_AA)

            # if record:
            #     output_video.write(output_frame)

            if not headless:
                debug_window_size = settings.DEBUG_WINDOW_SIZE
                # resized_frame = cv2.resize(frame, debug_window_size)
                resized_frame = cv2.resize(output_frame, debug_window_size)
                cv2.imshow(window_name, resized_frame)

            # processing_frame_rate = round(cv2.getTickFrequency() / (cv2.getTickCount() - _timer), 2)
            frames_processed += 1
            # logger.debug('Frame processed.', extra={
            #     'meta': {
            #         'label': 'FRAME_PROCESS',
            #         'frames_processed': frames_processed,
            #         'frame_rate': processing_frame_rate,
            #         'frames_left': frames_count - frames_processed,
            #         'percentage_processed': round((frames_processed / frames_count) * 100, 2),
            #     },
            # })


            retval, frame = cap.read()
    finally:
        # end capture, close window, close log file and video object if any
        cap.release()
        if not headless:
            cv2.destroyAllWindows()
        if record:
            output_video.release()
        logger.info('Processing ended.', extra={
            'meta': {
                'label': 'END_PROCESS',
                'counts': object_counter.get_counts(),
                'completed': frames_count - frames_processed == 0,
            },
        })

from GUI.main_gui import start_GUI
if __name__ == '__main__':
    # images_dict = {}
    # images_dict[MASK_IMG_CV2] = cv2.cvtColor(cv2.imread("data/videos/empty.jpg"), cv2.COLOR_BGR2GRAY)
    # # cv2.imshow("test mask", images_dict[MASK_IMG_CV2]);
    # # cv2.waitKey(0);
    # lines = [{'label': 'A', 'line': [(667, 713), (888, 713)]}, {'label': 'B', 'line': [(1054, 866), (1423, 868)]}]
    # run(images_dict, lines)
    start_GUI()
