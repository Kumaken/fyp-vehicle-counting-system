
# import module
import traceback
import numpy as np
import cv2
import csv
import pickle # serializing tuples/objects/lists easily
from PyQt5.QtWidgets import (QLabel, QFileDialog, QPushButton, QDialog)
from PyQt5.QtCore import Qt, QDir

# import custom modules:
from GUI.sliders import Sliders
from GUI.utils import Utils
from GUI.const import BUTTON_OPEN_IMG, BUTTON_SAVE_IMG, BUTTON_SAVE_CONFIG, BUTTON_CAPTURE_IMG, BUTTON_LOAD_CONFIG, BUTTON_START_DETECTION, SOURCE_IMG_PATH, OUTPUT_IMG_CV2, OUTPUT_IMG_QT, MASK_IMG_CV2, SLIDER_LABELS, CSV_CONFIG_KEYS, SOURCE_IMG_CV2
from GUI.video_player import VideoPlayer

class GUIUtils:
    # static variable
    drawing_line_mode = False
    line = []

    @staticmethod
    def getClickPositionOnImage(event, label_dict, images_dict, parent):
        print(event.pos().x(), event.pos().y())
        # return event.pos().x(), event.pos().y()
        GUIUtils.saveCoords(event.pos().x(), event.pos().y(), images_dict)
        if GUIUtils.drawing_line_mode:
            print("APPLYING LINES")
            GUIUtils.saveLine(parent)
            GUIUtils.refreshLines(parent, label_dict, images_dict)
            GUIUtils.drawing_line_mode = False
        else:
            GUIUtils.drawing_line_mode = True



    @staticmethod
    def saveCoords(x, y, images_dict):
        GUIUtils.line.append(GUIUtils.applyRatio((x,y), images_dict))

    @staticmethod
    def saveLine(parent, label = 'Nameless Line'):
        count = len(parent.lines)
        line_dict = {
            'label': label if count == 0 else label + str(count),
            'line': GUIUtils.line
        }
        parent.lines.append(line_dict)
        GUIUtils.line = []

    @staticmethod
    def applyRatio(og_size, images_dict):
        return (int(og_size[0] * images_dict["image_ratio"]["width"]), int(og_size[1] * images_dict["image_ratio"]["height"]))

    @staticmethod
    def drawLines(parent, images_dict):
        from GUI.config import Config
        import copy
        image = copy.deepcopy(images_dict[SOURCE_IMG_CV2])
        for line_entry in parent.lines:
            point1, point2 = line_entry['line']
            print("Drawing line between: ", point1, point2)
            cv2.line(image, point1, point2, [0, 0, 255], 10)
        return image

    @staticmethod
    def applyLines(label_dict, image_cv):
        image_qt = Utils.convert_cv_qt(image_cv)
        label_dict.output_image_label.setPixmap(image_qt)

    @staticmethod
    def refreshLines(parent, label_dict, images_dict):
        parent.line_list_widget.setupList()
        result_cv2_img = GUIUtils.drawLines(parent, images_dict)
        GUIUtils.applyLines(label_dict, result_cv2_img)

    @staticmethod
    def setupImageLayout(parent, image_layout, label_dict, image_dict):
        image_layout.addWidget(QLabel("Source Image"), 0, 0)
        image_layout.addWidget(label_dict.image_label, 1, 0, 3, 1)
        # image_layout.addWidget(label_dict.text_label, 3, 0)
        image_layout.addWidget(QLabel("Mask"), 4, 0)
        image_layout.addWidget(label_dict.mask_label, 5, 0)
        image_layout.addWidget(QLabel("Mask Enhanced"), 4, 1)
        image_layout.addWidget(label_dict.mask_enhanced_label, 5, 1)

        # prepare output label:
        label_dict.output_image_label.mousePressEvent = lambda event: GUIUtils.getClickPositionOnImage(event, label_dict, image_dict, parent)
        image_layout.addWidget(QLabel("Output Image"), 6, 0)
        image_layout.addWidget(label_dict.output_image_label, 7, 0, 4, 2)
        # image_layout.addWidget(label_dict.output_image_label, 3, 0, 1, 2, Qt.AlignCenter)



    @staticmethod
    def createHSVSliders(grid, sliders, images_dict, label_dict, parent):
        for i in range(6):
            slider = Sliders(SLIDER_LABELS[i], 1 if i<3 else 255, parent) # IMPORTANT: PASS SELF AS PARENT!
            slider.sl.valueChanged[int].connect(lambda: GUIUtils.updateHSVMasking(images_dict, label_dict, sliders))
            sliders.append(slider)
            grid.addWidget(slider.getComponent(), i % 3, 0 if i < 3 else 2, 1, 2)

    @staticmethod
    def setupSourceImage(images_dict, label_dict):
        try:
            images_dict[SOURCE_IMG_CV2] = cv2.imread(images_dict.SOURCE_IMG_PATH)
            qt_hsv_mask = Utils.convert_cv_qt(images_dict[SOURCE_IMG_CV2],)
            # set qt image size
            images_dict["qt_image_size"] = {"width": qt_hsv_mask.width(), "height": qt_hsv_mask.height()}
            print("IMAGES_DICT QT_IMAGE_SIZE", images_dict["qt_image_size"])
            # set qt image ratio for conversion back to cv2 size
            og_width, og_height  = images_dict[SOURCE_IMG_CV2].shape[1::-1]
            ratio_h, ratio_w = og_height/images_dict["qt_image_size"]["height"], og_width/images_dict["qt_image_size"]["width"]
            print("OG:", og_width, og_height)
            print("Scaled: ", images_dict["qt_image_size"])
            images_dict["image_ratio"] = {"width" : ratio_w, "height": ratio_h}

            print("IMAGES DICT:", images_dict["image_ratio"])

            label_dict.image_label.setPixmap(qt_hsv_mask)
        except Exception as e:
            print('Read image fails:', e)
            traceback.print_exc()



    @staticmethod
    def updateHSVMasking(images_dict, label_dict, sliders = None):
        try:
            if not sliders:
                print("Default slider initialization")
                lower = np.array([0,0,0], dtype="uint8")
                upper = np.array([255,255,255], dtype="uint8")
            else:
                lower = np.array([sliders[0].getSliderValue(), sliders[1].getSliderValue(), sliders[2].getSliderValue()], dtype="uint8")
                upper = np.array([sliders[3].getSliderValue(), sliders[4].getSliderValue(), sliders[5].getSliderValue()], dtype="uint8")

            cv_hsv_mask = cv2.inRange(images_dict[SOURCE_IMG_CV2], lower, upper)
            qt_hsv_mask = Utils.convert_cv_qt(cv_hsv_mask)

            # update image
            label_dict.mask_label.setPixmap(qt_hsv_mask)

            enhanced_mask = Utils.enhanceMask(cv_hsv_mask)
            images_dict[MASK_IMG_CV2] = enhanced_mask
            qt_enhanced_mask = Utils.convert_cv_qt(enhanced_mask)
            label_dict.mask_enhanced_label.setPixmap(qt_enhanced_mask)

            masked_img = Utils.maskImage(images_dict[SOURCE_IMG_CV2], enhanced_mask)
            images_dict[OUTPUT_IMG_CV2] = masked_img

            qt_masked_img = Utils.convert_cv_qt(masked_img, multiplier=3)
            images_dict[OUTPUT_IMG_QT] = qt_masked_img
            label_dict.output_image_label.setPixmap(qt_masked_img)
        except Exception as e:
            print('Update HSV masking fails:', e)


    @staticmethod
    def setupButtons(parent, buttons_dict, images_dict, label_dict, sliders, target_layout):
        button = QPushButton('Upload Image', parent)
        button.setToolTip('Select image path to process.')
        button.clicked.connect(lambda: GUIUtils.openImageDialog(parent, images_dict, label_dict))
        buttons_dict[BUTTON_OPEN_IMG] = button
        target_layout.addWidget(button, 1, 1)

        button_load_config = QPushButton('Upload Config', parent)
        button_load_config.setToolTip('Select config path to process.')
        button_load_config.clicked.connect(lambda: GUIUtils.read_HSV_config_csv(parent, sliders, images_dict, label_dict))
        buttons_dict[BUTTON_LOAD_CONFIG] = button_load_config
        target_layout.addWidget(button_load_config, 2, 1)

        button_video = QPushButton('Capture from Video', parent)
        button_video.setToolTip('Select an image frame from a video.')
        button_video.clicked.connect(lambda: GUIUtils.openVideoPlayer(parent, images_dict, label_dict))
        buttons_dict[BUTTON_CAPTURE_IMG] = button_video
        target_layout.addWidget(button_video, 3, 1)

        button_save = QPushButton('Save Image', parent)
        button_save.setToolTip('Select file path to save into.')
        button_save.clicked.connect(lambda: GUIUtils.saveImageDialog(parent, images_dict[MASK_IMG_CV2]))
        buttons_dict[BUTTON_SAVE_IMG] = button_save
        target_layout.addWidget(button_save, 7, 2)

        button_save_config = QPushButton('Save Mask Config', parent)
        button_save_config.setToolTip('Select file path to save the sliders config into.')
        button_save_config.clicked.connect(lambda: GUIUtils.save_HSV_config_csv(sliders, images_dict, parent.lines))
        buttons_dict[BUTTON_SAVE_CONFIG] = button_save_config
        target_layout.addWidget(button_save_config, 8, 2)

        from main import run
        button_start_detection = QPushButton('Start Detection', parent)
        button_start_detection.setToolTip('Proceed to Vehicle Counting module.')
        button_start_detection.clicked.connect(lambda: run(images_dict, parent.lines))
        buttons_dict[BUTTON_START_DETECTION] = button_start_detection
        target_layout.addWidget(button_start_detection, 9, 2)

    @staticmethod
    def setupLineList(parent, lines, target_layout):
        from GUI.line_list import LineListWidget
        list_widget = LineListWidget(parent, lines)
        parent.line_list_widget = list_widget
        target_layout.addWidget(list_widget, 0, 6, 9, 2)

    @staticmethod
    def refreshImage(images_dict, label_dict, sliders=None):
        GUIUtils.setupSourceImage(images_dict, label_dict)
        GUIUtils.updateHSVMasking(images_dict, label_dict, sliders=sliders)

    @staticmethod
    def openImageDialog(parent, images_dict, label_dict):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(parent,"QFileDialog.getOpenFileName()", "","All Files (*);;Python Files (*.py)", options=options)
        print(fileName)
        images_dict[SOURCE_IMG_PATH] = fileName
        GUIUtils.refreshImage(images_dict, label_dict)

    @staticmethod
    def saveImageDialog(parent, image, cv=True):
        dialog = QFileDialog()
        dialog.setFilter(dialog.filter() | QDir.Hidden)
        dialog.setDefaultSuffix("jpg")
        dialog.setAcceptMode(QFileDialog.AcceptSave)
        dialog.setNameFilters(['JPEG (*.jpg *.jpeg)'])
        if dialog.exec_() == QDialog.Accepted:
            print(dialog.selectedFiles())
            fileName = dialog.selectedFiles()[0]
            if cv:
                cv2.imwrite(fileName, image)
            else:
                image.save(fileName)
            parent.images_dict[SOURCE_IMG_PATH] = fileName
        else:
            print('Cancelled')
        # fileName, _ = QFileDialog.getSaveFileName(parent, "Save Image", "", filter, options=options)
        # print(fileName)

    @staticmethod
    def save_HSV_config_csv(sliders, images_dict, lines):
        dialog = QFileDialog()
        dialog.setFilter(dialog.filter() | QDir.Hidden)
        dialog.setDefaultSuffix("csv")
        dialog.setAcceptMode(QFileDialog.AcceptSave)
        dialog.setNameFilters(["csv(*.csv)"])
        if dialog.exec_() == QDialog.Accepted:
            print(dialog.selectedFiles())
            fileName = dialog.selectedFiles()[0]
            with open(fileName, 'w', newline='') as f:
                writer = csv.writer(f, delimiter=',')
                writer.writerow(CSV_CONFIG_KEYS)
                writer.writerow([SOURCE_IMG_PATH, images_dict[SOURCE_IMG_PATH]])
                for i in range(len(sliders)):
                    writer.writerow([SLIDER_LABELS[i], sliders[i].getSliderValue()])
            with open(fileName+'.pickle', 'wb') as handle:
                pickle.dump(lines, handle, protocol=pickle.HIGHEST_PROTOCOL)
        else:
            print('Cancelled')

    @staticmethod
    def read_HSV_config_csv(parent, sliders, images_dict, label_dict):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(parent,"Load Config", "","csv(*.csv)", options=options)
        print(fileName)
        try:
            with open(fileName, 'r', newline='') as f:
                reader = csv.DictReader(f)
                config_dict = {}
                for row in reader:
                    config_dict[row[CSV_CONFIG_KEYS[0]]] = row[CSV_CONFIG_KEYS[1]]

                images_dict[SOURCE_IMG_PATH] = config_dict[SOURCE_IMG_PATH]
                for i,label in enumerate(SLIDER_LABELS):
                    sliders[i].setSliderValue(int(config_dict[label]))
                GUIUtils.refreshImage(images_dict, label_dict, sliders=sliders)
            print(fileName)
            with open(fileName+'.pickle', 'rb') as handle:
                parent.lines = pickle.load(handle)
                GUIUtils.refreshLines(parent, label_dict, images_dict)
        except:
            print("Read config failed!")
            traceback.print_exc()

    @staticmethod
    def openVideoPlayer(parent, images_dict, label_dict):
         # Setup Video Player"
         # have to add video_player as main window's class attributes, else garbage collection will automatically remove it (close immediately)
        parent.video_player = VideoPlayer(main_window=parent)
        parent.video_player.resize(600, 400)
        parent.video_player.show()