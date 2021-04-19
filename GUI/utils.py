import numpy as np
import cv2
import csv
from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from config import Config

class Utils:
    @staticmethod
    def enhanceMask(mask):
        des = mask
        contour,hier = cv2.findContours(des,cv2.RETR_CCOMP,cv2.CHAIN_APPROX_SIMPLE)

        for cnt in contour:
            cv2.drawContours(des,[cnt],-1,(255,255,255),thickness=cv2.FILLED)

        return des

    @staticmethod
    def maskImage(ori, mask):
        return cv2.bitwise_and(ori, ori, mask=mask)

    @staticmethod
    def convert_cv_qt(cv_img):
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(Config.disply_width, Config.display_height, Qt.KeepAspectRatio)
        return QtGui.QPixmap.fromImage(p)
