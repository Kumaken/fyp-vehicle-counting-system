# import custom modules:
from sliders import Sliders
import numpy as np
import cv2
import csv
from PyQt5.QtWidgets import (QLabel, QFileDialog, QPushButton, QDialog)
from PyQt5.QtCore import Qt, QDir

# custom imports:
from utils import Utils
from const import BUTTON_OPEN_IMG, BUTTON_SAVE_IMG, BUTTON_SAVE_CONFIG, BUTTON_CAPTURE_IMG, BUTTON_LOAD_CONFIG, SOURCE_IMG_PATH, OUTPUT_IMG_CV2, MASK_IMG_CV2, SLIDER_LABELS, CSV_CONFIG_KEYS
from video_player import VideoPlayer

class GUIUtils:
    # static variable
    @staticmethod
    def setupImageLayout(image_layout, label_dict):
        image_layout.addWidget(label_dict.image_label, 0, 0, 3, 1)
        image_layout.addWidget(label_dict.text_label, 3, 0)
        image_layout.addWidget(label_dict.mask_label, 4, 0)
        image_layout.addWidget(label_dict.mask_enhanced_label, 4, 1)
        image_layout.addWidget(label_dict.output_image_label, 5, 0, 3, 1)
        # image_layout.addWidget(label_dict.output_image_label, 3, 0, 1, 2, Qt.AlignCenter)


    @staticmethod
    def createHSVSliders(grid, sliders, images_dict, label_dict, parent):
        for i in range(6):
            slider = Sliders(SLIDER_LABELS[i], 1 if i<3 else 255, parent) # IMPORTANT: PASS SELF AS PARENT!
            slider.sl.valueChanged[int].connect(lambda: GUIUtils.updateHSVMasking(images_dict, label_dict, sliders))
            sliders.append(slider)
            grid.addWidget(slider.getComponent(), i % 3, 0 if i < 3 else 1)

    @staticmethod
    def setupSourceImage(images_dict, label_dict):
        try:
            images_dict.source_img_cv2 = cv2.imread(images_dict.SOURCE_IMG_PATH)
            qt_hsv_mask = Utils.convert_cv_qt(images_dict.source_img_cv2)
            label_dict.image_label.setPixmap(qt_hsv_mask)
        except Exception as e:
            print('Read image fails:', e)

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

            cv_hsv_mask = cv2.inRange(images_dict.source_img_cv2, lower, upper)
            qt_hsv_mask = Utils.convert_cv_qt(cv_hsv_mask)

            # update image
            label_dict.mask_label.setPixmap(qt_hsv_mask)

            enhanced_mask = Utils.enhanceMask(cv_hsv_mask)
            images_dict[MASK_IMG_CV2] = enhanced_mask
            qt_enhanced_mask = Utils.convert_cv_qt(enhanced_mask)
            label_dict.mask_enhanced_label.setPixmap(qt_enhanced_mask)

            masked_img = Utils.maskImage(images_dict.source_img_cv2, enhanced_mask)
            images_dict[OUTPUT_IMG_CV2] = masked_img

            qt_masked_img = Utils.convert_cv_qt(masked_img)
            label_dict.output_image_label.setPixmap(qt_masked_img)
        except Exception as e:
            print('Update HSV masking fails:', e)


    @staticmethod
    def setupButtons(parent, buttons_dict, images_dict, label_dict, sliders, target_layout):
        button = QPushButton('Upload Image', parent)
        button.setToolTip('Select image path to process.')
        button.clicked.connect(lambda: GUIUtils.openImageDialog(parent, images_dict, label_dict))
        buttons_dict[BUTTON_OPEN_IMG] = button
        target_layout.addWidget(button, 0, 1)

        button_load_config = QPushButton('Upload Config', parent)
        button_load_config.setToolTip('Select config path to process.')
        button_load_config.clicked.connect(lambda: GUIUtils.read_HSV_config_csv(parent, sliders, images_dict, label_dict))
        buttons_dict[BUTTON_LOAD_CONFIG] = button_load_config
        target_layout.addWidget(button_load_config, 1, 1)

        button_video = QPushButton('Capture from Video', parent)
        button_video.setToolTip('Select an image frame from a video.')
        button_video.clicked.connect(lambda: GUIUtils.openVideoPlayer(parent, images_dict, label_dict))
        buttons_dict[BUTTON_CAPTURE_IMG] = button_video
        target_layout.addWidget(button_video, 2, 1)

        button_save = QPushButton('Save Image', parent)
        button_save.setToolTip('Select file path to save into.')
        button_save.clicked.connect(lambda: GUIUtils.saveImageDialog(parent, images_dict[MASK_IMG_CV2]))
        buttons_dict[BUTTON_SAVE_IMG] = button_save
        target_layout.addWidget(button_save, 5, 1)

        button_save_config = QPushButton('Save Mask Config', parent)
        button_save_config.setToolTip('Select file path to save the sliders config into.')
        button_save_config.clicked.connect(lambda: GUIUtils.save_HSV_config_csv(sliders, images_dict))
        buttons_dict[BUTTON_SAVE_CONFIG] = button_save_config
        target_layout.addWidget(button_save_config, 6, 1)


    @staticmethod
    def refreshImage(images_dict, label_dict):
        GUIUtils.setupSourceImage(images_dict, label_dict)
        GUIUtils.updateHSVMasking(images_dict, label_dict)

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
    def save_HSV_config_csv(sliders, images_dict):
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
        else:
            print('Cancelled')

    @staticmethod
    def read_HSV_config_csv(parent, sliders, images_dict, label_dict):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(parent,"QFileDialog.getOpenFileName()", "","csv(*.csv)", options=options)
        print(fileName)
        with open(fileName, 'r', newline='') as f:
            reader = csv.DictReader(f)
            config_dict = {}
            for row in reader:
                config_dict[row[CSV_CONFIG_KEYS[0]]] = row[CSV_CONFIG_KEYS[1]]

            images_dict[SOURCE_IMG_PATH] = config_dict[SOURCE_IMG_PATH]
            for i,label in enumerate(SLIDER_LABELS):
                sliders[i].setSliderValue(int(config_dict[label]))
            GUIUtils.refreshImage(images_dict, label_dict)

    @staticmethod
    def openVideoPlayer(parent, images_dict, label_dict):
         # Setup Video Player"
         # have to add video_player as main window's class attributes, else garbage collection will automatically remove it (close immediately)
        parent.video_player = VideoPlayer(main_window=parent)
        parent.video_player.setWindowTitle("Player")
        parent.video_player.resize(600, 400)
        parent.video_player.show()