'''
Functions for keeping track of detected objects in a video.
'''

from consts.object_counter import COUNTING_MODE_ACTUAL, COUNTING_MODE_ACTUAL_LABEL_NAME
from GUI.strings.tracker_options import BOOSTING, CSRT, KCF, MEDIANFLOW, MIL, MOSSE, NO_TRACKER, TLD
import sys
import cv2
import settings
from util.blob import Blob
from util.bounding_box import get_overlap, get_box_image
from util.image import get_base64_image
from util.object_info import generate_object_id
from util.logger import get_logger


logger = get_logger()

def _csrt_create(bounding_box, frame):
    '''
    Create an OpenCV CSRT Tracker object.
    '''
    tracker = cv2.TrackerCSRT_create()
    tracker.init(frame, tuple(bounding_box))
    return tracker

def _kcf_create(bounding_box, frame):
    '''
    Create an OpenCV KCF Tracker object.
    '''
    tracker = cv2.TrackerKCF_create()
    bounding_box_tuple = tuple([int(x) for x in bounding_box])
    tracker.init(frame, bounding_box_tuple)
    return tracker

def createTracker(chosen_tracker, bounding_box, frame):
    tracker = None
    if chosen_tracker == CSRT:
        tracker = cv2.TrackerCSRT_create()
    elif chosen_tracker == KCF:
        tracker = cv2.TrackerKCF_create()
    elif chosen_tracker == BOOSTING:
        tracker = cv2.legacy_TrackerBoosting.create()
    elif chosen_tracker == MIL:
        tracker = cv2.TrackerMIL_create()
    elif chosen_tracker == TLD:
        tracker = cv2.legacy_TrackerTLD.create()
    elif chosen_tracker == MEDIANFLOW:
        tracker = cv2.legacy_TrackerMedianFlow.create()
    elif chosen_tracker == MOSSE:
        tracker = cv2.legacy_TrackerMOSSE.create()
    elif chosen_tracker == NO_TRACKER:
        tracker = None
        return tracker

    bounding_box_tuple = tuple([int(x) for x in bounding_box])
    tracker.init(frame, bounding_box_tuple)
    return tracker

def get_tracker(algorithm, bounding_box, frame):
    '''
    Fetch a tracker object based on the algorithm specified.
    '''
    return createTracker(algorithm, bounding_box, frame)
    # if algorithm == 'csrt':
    #     return _csrt_create(bounding_box, frame)
    # if algorithm == 'kcf':
    #     return _kcf_create(bounding_box, frame)

    logger.error('Invalid tracking algorithm specified (options: csrt, kcf)', extra={
        'meta': {'label': 'INVALID_TRACKING_ALGORITHM'},
    })
    sys.exit()

def _remove_stray_blobs(blobs, matched_blob_ids, mcdf, counts, counting_mode):
    '''
    Remove blobs that "hang" after a tracked object has left the frame.
    '''
    for blob_id, blob in list(blobs.items()):
        if blob_id not in matched_blob_ids:
            blob.num_consecutive_detection_failures += 1
        if blob.num_consecutive_detection_failures > mcdf:
            if counting_mode == COUNTING_MODE_ACTUAL:
                counts[COUNTING_MODE_ACTUAL_LABEL_NAME][blob.type] -= 1
            del blobs[blob_id]
    return blobs

def add_new_blobs(boxes, classes, confidences, blobs, frame, tracker, mcdf, counts, counting_mode):
    '''
    Add new blobs or updates existing ones.
    '''
    matched_blob_ids = []
    for i, box in enumerate(boxes):
        _type = classes[i] if classes is not None else None
        _confidence = confidences[i] if confidences is not None else None
        _tracker = get_tracker(tracker, box, frame)

        match_found = False
        for _id, blob in blobs.items():
            if get_overlap(box, blob.bounding_box) >= 0.6:
                match_found = True

                # change detection class result for this blob
                if counting_mode == COUNTING_MODE_ACTUAL:
                    counts[COUNTING_MODE_ACTUAL_LABEL_NAME][blob.type] -= 1
                    counts[COUNTING_MODE_ACTUAL_LABEL_NAME][_type] += 1

                if _id not in matched_blob_ids:
                    blob.num_consecutive_detection_failures = 0
                    matched_blob_ids.append(_id)
                blob.update(box, _type, _confidence, _tracker)

                blob_update_log_meta = {
                    'label': 'BLOB_UPDATE',
                    'object_id': _id,
                    'bounding_box': blob.bounding_box,
                    'type': blob.type,
                    'type_confidence': blob.type_confidence,
                }
                if settings.LOG_IMAGES:
                    blob_update_log_meta['image'] = get_base64_image(get_box_image(frame, blob.bounding_box))
                logger.debug('Blob updated.', extra={'meta': blob_update_log_meta})
                break

        if not match_found:
            _blob = Blob(box, _type, _confidence, _tracker)
            blob_id = generate_object_id()
            blobs[blob_id] = _blob

            # blog_create_log_meta = {
            #     'label': 'BLOB_CREATE',
            #     'object_id': blob_id,
            #     'bounding_box': _blob.bounding_box,
            #     'type': _blob.type,
            #     'type_confidence': _blob.type_confidence,
            # }
            # if settings.LOG_IMAGES:
            #     blog_create_log_meta['image'] = get_base64_image(get_box_image(frame, _blob.bounding_box))
            # logger.debug('Blob created.', extra={'meta': blog_create_log_meta})

    blobs = _remove_stray_blobs(blobs, matched_blob_ids, mcdf, counts, counting_mode)
    return blobs

def remove_duplicates(blobs, counts, counting_mode):
    '''
    Remove duplicate blobs i.e blobs that point to an already detected and tracked object.
    '''
    for blob_id, blob_a in list(blobs.items()):
        for _, blob_b in list(blobs.items()):
            if blob_a == blob_b:
                break

            if get_overlap(blob_a.bounding_box, blob_b.bounding_box) >= 0.6 and blob_id in blobs:
                if counting_mode == COUNTING_MODE_ACTUAL:
                    counts[COUNTING_MODE_ACTUAL_LABEL_NAME][blob_a.type] -= 1
                del blobs[blob_id]

    return blobs

def update_blob_tracker(blob, blob_id, frame):
    '''
    Update a blob's tracker object.
    UPDATE as in positions only! Does not change detection classes!
    '''

    success, box = blob.tracker.update(frame)
    if success:
        blob.num_consecutive_tracking_failures = 0
        blob.update(box)
        # logger.debug('Object tracker updated.', extra={
        #     'meta': {
        #         'label': 'TRACKER_UPDATE',
        #         'object_id': blob_id,
        #         'bounding_box': blob.bounding_box,
        #         'centroid': blob.centroid,
        #     },
        # })
    else:
        blob.num_consecutive_tracking_failures += 1

    return (blob_id, blob)
