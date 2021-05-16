'''
Perform object detection using models created with the YOLO (You Only Look Once) neural net.
https://pjreddie.com/darknet/yolo/
'''

# pylint: disable=no-member,invalid-name

import cv2
print ("cv2 version", cv2.__version__)
import numpy as np
import settings


# SETUP CLASS NAMES
with open(settings.YOLO_CLASSES_PATH, 'r') as classes_file:
    CLASSES = dict(enumerate([line.strip() for line in classes_file.readlines()]))

# SETUP CLASS NAMES OF INTEREST:
with open(settings.YOLO_CLASSES_OF_INTEREST_PATH, 'r') as coi_file:
    CLASSES_OF_INTEREST = tuple([line.strip() for line in coi_file.readlines()])

# YOLO HYPERPARAMETERS
conf_threshold = settings.YOLO_CONFIDENCE_THRESHOLD

# READ YOLO NET with cv2 deep neural network module
print("[DEBUG][Reading Net with setup:]", settings.YOLO_WEIGHTS_PATH, settings.YOLO_CONFIG_PATH)
net = cv2.dnn.readNet(settings.YOLO_WEIGHTS_PATH, settings.YOLO_CONFIG_PATH)
# USE GPU
net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA);
net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA);

layer_names = net.getLayerNames()
output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]
print("output_layers", output_layers)
# net = cv2.dnn.readNet(settings.YOLO_WEIGHTS_PATH)

def get_bounding_boxes(image):
    '''
    Return a list of bounding boxes of objects detected,
    their classes and the confidences of the detections made.
    '''

    # create image blob
    scalefactor = settings.IMG_VALUE_SCALE
    imgsz = settings.IMG_SIZE # 416 # 640

    # perform preprocessing function:
    '''
    blobFromImage: creates 4-dimensional blob from image. perform:
    1. Scale values (not scale image size) by scalefactor
    2. Resize by imsz
    3. Mean substraction: combat illumination changes!
    4. swapRB (red and blue): boolean. By default this should be true, because openCV is BGR but this function expects RGB
    5. crop image from center: boolean

    blob is just a collection of images with same spatial dimension, same depth (channels), and have been subjected through same preprocessing

    readmore: https://www.pyimagesearch.com/2017/11/06/deep-learning-opencvs-blobfromimage-works/
    '''
    width = image.shape[1]
    height = image.shape[0]
    image_blob = cv2.dnn.blobFromImage(image, scalefactor, (imgsz, imgsz), (0, 0, 0), True, crop=False)

    # detect objects
    net.setInput(image_blob)
    global output_layers
    outputs = net.forward(output_layers)
    # print("outputs")
    # print(outputs)

    classes = []
    confidences = []
    boxes = []

    for output in outputs:
        for detection in output:
            conf_threshold_ = conf_threshold
            scores = detection[5:]
            if(len(scores) == 0):
                continue
            # print(scores)
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if((class_id == 3 or class_id == 0) and confidence != 0):
                print(CLASSES[class_id], confidence)
                conf_threshold_ = 0.2

            # if confidence > conf_threshold and CLASSES[class_id] in CLASSES_OF_INTEREST:
            if confidence > conf_threshold_:
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)
                classes.append(CLASSES[class_id])
                confidences.append(float(confidence))
                boxes.append([x, y, w, h])

    # remove overlapping bounding boxes
    '''
    Non-max suppression: select the most appropriate bounding box for localization.
    NMS takes two things into account:
    1. Objectivess score given by the model (confidence score)
    2. Overlap or IoU of bounding boxes
    So it selects the bounding box with highest confidence score, then remove all boxes that has IoU (overlapping) with the selected box higher than threshold
    '''
    indices = cv2.dnn.NMSBoxes(boxes, confidences, conf_threshold, settings.NMS_THRESHOLD)

    _bounding_boxes = []
    _classes = []
    _confidences = []
    for i in indices:
        i = i[0]
        _bounding_boxes.append(boxes[i])
        _classes.append(classes[i])
        _confidences.append(confidences[i])

    return _bounding_boxes, _classes, _confidences
