'''
Object Counter class.
'''

# pylint: disable=missing-class-docstring,missing-function-docstring,invalid-name
import copy
from GUI.strings.tracker_options import NO_TRACKER
from consts.object_counter import COUNTING_MODE_ACTUAL, COUNTING_MODE_ACTUAL_LABEL_NAME, COUNTING_MODE_LINES
import multiprocessing
import cv2
from joblib import Parallel, delayed

from tracker import add_new_blobs, remove_duplicates, update_blob_tracker
from detectors.detector import get_bounding_boxes
from util.detection_roi import  draw_roi
from util.logger import get_logger
from counter import attempt_count_actual, attempt_count_lines

from GUI.utils import Utils
logger = get_logger()
NUM_CORES = multiprocessing.cpu_count()
print("[DEBUG][ObjectCounter] NUM_CORES:", NUM_CORES)
# SETUP CLASS NAMES
import settings
with open(settings.YOLO_CLASSES_PATH, 'r') as classes_file:
    CLASSES = dict(enumerate([line.strip() for line in classes_file.readlines()]))

parallel_pool = Parallel(n_jobs=8, prefer="threads")

class ObjectCounter():
    line_colors = [(255, 129, 61), (255, 255, 20), (98, 255, 20), (20, 255, 224), (20, 157, 255), (0, 26, 255), (64, 0, 255), (157, 0, 255), (255, 0, 247), (255, 0, 38), (255, 255, 255), (0, 0, 0)]

    def rescale_counting_lines(self, counting_lines_, target_ratio):
        counting_lines = copy.deepcopy(counting_lines_)
        ratio_w = target_ratio[0] / self.ori_ratio_w
        ratio_h = target_ratio[1] / self.ori_ratio_h

        for line in counting_lines:
            for i, point in enumerate(line['line']):
                line['line'][i] = (int(point[0] * ratio_w), int(point[1] * ratio_h))

        return counting_lines

    def rescale_bounding_boxes(self, x, y, w, h, target_ratio):
        ratio_w = target_ratio[0] / settings.IMG_SIZE
        ratio_h = target_ratio[1] / settings.IMG_SIZE
        return int(x*ratio_w), int(y*ratio_h), int(w*ratio_w), int(h*ratio_h)

    def __init__(self, initial_frame, original_ratio, detector, tracker, droi, show_droi, mcdf, mctf, di, counting_lines, show_counts, hud_color, detector_gui,  counting_mode=COUNTING_MODE_ACTUAL):
        self.frame = initial_frame  # current frame of video
        self.ori_ratio_w, self.ori_ratio_h = original_ratio
        self.detector = detector
        self.tracker = tracker
        self.droi = droi  # detection region of interest
        self.show_droi = show_droi
        self.mcdf = mcdf # maximum consecutive detection failures
        self.mctf = mctf # maximum consecutive tracking failures
        self.detection_interval = di
        self.counting_lines = self.rescale_counting_lines(counting_lines, (settings.IMG_SIZE, settings.IMG_SIZE))
        self.counting_lines_scaled = self.rescale_counting_lines(counting_lines, settings.DEBUG_WINDOW_SIZE) # self.rescale_counting_lines(counting_lines)
        print("[DEBUG] rescaled counting lines",self.counting_lines)
        self.blobs = {}
        self.f_height, self.f_width, _ = self.frame.shape
        self.frame_count = 0 # number of frames since last detection
        # counting modes:
        self.counting_mode = counting_mode
        with open(settings.YOLO_CLASSES_OF_INTEREST_PATH, 'r') as coi_file:
            classes = coi_file.readlines()
            if self.counting_mode == COUNTING_MODE_LINES and len(counting_lines) != 0:
                self.counts = {counting_line['label']: {line.strip(): 0 for line in classes} for counting_line in counting_lines} # counts of objects by type for each counting line
            else: # actual mode
                self.counts = {}
                self.counts[COUNTING_MODE_ACTUAL_LABEL_NAME] = {line.strip(): 0 for line in classes}

        self.show_counts = show_counts
        self.hud_color = hud_color
        self.detector_gui = detector_gui

        # create blobs from initial frame
        # CHANGE:
        # droi_frame = get_roi_frame(self.frame, self.droi)
        # cv2.imshow("test mask in ObjectCounter", self.droi);
        # cv2.imshow("test ori", self.frame);
        cv2.waitKey(0);
        droi_frame = Utils.maskImage(self.frame, self.droi)
        _bounding_boxes, _classes, _confidences = get_bounding_boxes(droi_frame, self.detector)
        self.blobs = add_new_blobs(_bounding_boxes, _classes, _confidences, self.blobs, self.frame, self.tracker, self.mcdf, self.counts, self.counting_mode)

    def get_counts(self):
        return self.counts

    def get_blobs(self):
        return self.blobs

    def count(self, frame):
        self.frame = frame

        blobs_list = list(self.blobs.items())
        # update blob trackers
        if self.tracker != NO_TRACKER:
            # conv to bgr
            # grayscale_frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
            blobs_list = [update_blob_tracker(blob, blob_id, self.frame) for blob_id, blob in blobs_list]
            # blobs_list =parallel_pool(
            #     delayed(update_blob_tracker)(blob, blob_id, self.frame) for blob_id, blob in blobs_list
            # )

            self.blobs = dict(blobs_list)

        for blob_id, blob in blobs_list:
            if self.counting_mode == COUNTING_MODE_LINES:
                # count object if it has crossed a counting line
                # print("[DEBUG] counting lines", self.counting_lines)
                if len(self.counting_lines) == 0:
                    # incremental but without counting lines
                    blob, self.counts = attempt_count_actual(blob, blob_id, self.counts)
                else:
                    blob, self.counts = attempt_count_lines(blob, blob_id, self.counting_lines, self.counts)
            elif self.counting_mode == COUNTING_MODE_ACTUAL:
                blob, self.counts = attempt_count_actual(blob, blob_id, self.counts)

            self.blobs[blob_id] = blob

            # remove blob if it has reached the limit for tracking failures
            if blob.num_consecutive_tracking_failures >= self.mctf:
                if self.counting_mode == COUNTING_MODE_ACTUAL:
                    self.counts[COUNTING_MODE_ACTUAL_LABEL_NAME][blob.type] -= 1
                del self.blobs[blob_id]

        if self.frame_count >= self.detection_interval:
            # rerun detection
            # CHANGE
            # droi_frame = get_roi_frame(self.frame, self.droi)
            droi_frame = Utils.maskImage(self.frame, self.droi)
            _bounding_boxes, _classes, _confidences = get_bounding_boxes(droi_frame, self.detector)

            self.blobs = add_new_blobs(_bounding_boxes, _classes, _confidences, self.blobs, self.frame, self.tracker, self.mcdf, self.counts, self.counting_mode)
            self.blobs = remove_duplicates(self.blobs, self.counts, self.counting_mode)
            self.frame_count = 0

        self.frame_count += 1

    def object_color_picker(self, label):
        colors = [(255, 129, 61), (255, 255, 20), (98, 255, 20), (20, 255, 224)]
        for i in range (len(CLASSES)):
            if label == CLASSES[i]:
                return colors[i]
        return (255,255,255)


    def visualize(self, frame, mask):
        frame = frame
        font = cv2.FONT_HERSHEY_DUPLEX
        font_scale = 0.5
        font_thickness = 1
        line_thickness = 3
        line_font_scale = 1
        line_type = cv2.LINE_AA

        # draw and label blob bounding boxes
        for _id, blob in self.blobs.items():
            color = self.object_color_picker(blob.type)
            (x, y, w, h) = [int(v) for v in blob.bounding_box]
            x, y, w, h = self.rescale_bounding_boxes(x, y, w, h, settings.DEBUG_WINDOW_SIZE)
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, font_thickness)
            object_label = 'I: ' + _id[:8] \
                            if blob.type is None \
                            else '{0} ({1})'.format(blob.type, str(blob.type_confidence)[:4])
            cv2.putText(frame, object_label, (x, y - 5), font, font_scale, color, font_thickness, line_type)

        if self.counting_mode == COUNTING_MODE_LINES:
            # draw counting lines
            for i, counting_line in enumerate(self.counting_lines_scaled):
                color_idx = i % len(self.line_colors)
                cv2.line(frame, counting_line['line'][0], counting_line['line'][1], self.line_colors[color_idx], line_thickness)
                cl_label_origin = (counting_line['line'][0][0], counting_line['line'][0][1] + 35)
                cv2.putText(frame, counting_line['label'], cl_label_origin, font, line_font_scale, self.line_colors[color_idx], font_thickness, line_type)

        # show detection roi
        # CHANGE
        if self.show_droi:
            frame = draw_roi(frame, mask)

        # show counts
        # if self.show_counts:
        #     offset = 1
        #     i = 0
        #     for line, objects in self.counts.items():
        #         color_idx = i % len(self.line_colors)
        #         cv2.putText(frame, line, (10, 40 * offset), font, 1, self.line_colors[color_idx], 2, line_type)
        #         for label, count in objects.items():
        #             offset += 1
        #             cv2.putText(frame, "{}: {}".format(label, count), (10, 40 * offset), font, 1, self.line_colors[color_idx], 2, line_type)
        #         offset += 2
        #         i += 1

        self.detector_gui.refreshDetectionTable(self.counts.items())

        return frame
