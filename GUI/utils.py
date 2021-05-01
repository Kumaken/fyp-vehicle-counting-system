import numpy as np
import cv2
from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from GUI.config import Config




class Utils:
    @staticmethod
    def enhanceMask(mask):
        des = mask
        contour, _ = cv2.findContours(des,cv2.RETR_CCOMP,cv2.CHAIN_APPROX_SIMPLE)

        for cnt in contour:
            cv2.drawContours(des,[cnt],-1,(255,255,255),thickness=cv2.FILLED)

        return des

    @staticmethod
    def extractLargerSegment(maskROAD):

        contours, hierarchy = cv2.findContours(maskROAD.copy(),cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

        maxA = 0
        maskTemp=np.zeros_like(maskROAD)

        if(len(contours) > 0):
            for h,cnt in enumerate(contours):
                if(cv2.contourArea(cnt) > maxA):
                    cntMax=cnt
                    maxA = cv2.contourArea(cnt)
            mask = np.zeros(maskROAD.shape,np.uint8)
            cv2.drawContours(maskTemp,[cntMax],0,255,-1)
            maskROAD = cv2.bitwise_and(maskROAD,maskTemp)
        return maskROAD

    @staticmethod
    def post_process(img):
        kernel = np.ones((5, 5), np.uint8)
        img_out = cv2.erode(img, kernel,iterations=3)
        kernel = np.ones((20, 20), np.uint8)
        img_out = cv2.dilate(img_out, kernel,iterations=5)

        img_out = Utils.extractLargerSegment(img_out)

        return img_out

    @staticmethod
    def maskImage(ori, mask):
        return cv2.bitwise_and(ori, ori, mask=mask)

    @staticmethod
    def convert_cv_qt(cv_img, multiplier=1):
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(Config.display_width * multiplier, Config.display_height * multiplier, Qt.KeepAspectRatio)
        result = QtGui.QPixmap.fromImage(p)

        return result
