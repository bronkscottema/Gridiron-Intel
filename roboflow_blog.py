import io
import time
from tkinter import *
from tkinter import filedialog as fd
import sys
import os
import cv2
import numpy as np
import requests
from PIL import Image
from dotenv import load_dotenv
from requests_toolbelt.multipart.encoder import MultipartEncoder


load_dotenv()

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


def opencv():
    root = Tk()
    root.update()
    filename = fd.askopenfilename()
    root.destroy()
    starting = time.time()
    global source_points
    total_players = 0
    tracker_name = 'csrt'
    cv2.setUseOptimized(True)

    OPENCV_OBJECT_TRACKERS = {
        "csrt": cv2.TrackerCSRT_create
    }

    # initialize OpenCV's special multi-object tracker
    trackers = cv2.MultiTracker_create()
    field_point_tracker = cv2.MultiTracker_create()
    cap = cv2.VideoCapture(filename)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 2)

    length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    def on_open(trackbarValue):
        cap.set(cv2.CAP_PROP_POS_FRAMES, trackbarValue)
        err, img = cap.read()
        cv2.imshow("mywindow", img)
        pass

    cv2.namedWindow('mywindow')
    cv2.createTrackbar('start', 'mywindow', 0, length, on_open)
    cv2.createTrackbar('end', 'mywindow', 200, length, on_open)

    on_open(0)
    cv2.waitKey()

    start = cv2.getTrackbarPos('start', 'mywindow')
    end = cv2.getTrackbarPos('end', 'mywindow')
    if start >= end:
        raise Exception("start must be less than end")

    cap.set(cv2.CAP_PROP_POS_FRAMES, start)

    player_pts3 = []
    source_points = [(160, 800), (158, 600), (540, 600), (540, 800)]
    points_image = cv2.imread(resource_path('images/nfl_30_20.png'))
    field = cv2.imread(resource_path('images/nfl_30_20.png'))

    field_points = []
    player_pts2 = []
    screenshot = 0
    json_prediction = []

    for srcbox in enumerate(source_points):
        (a, b) = [c for c in srcbox]
        cv2.circle(points_image, (int(b[0]), int(b[1])), 5, (255, 255, 0), -1)

    while cap.isOpened():
        key = cv2.waitKey(1) & 0xFF

        ret, frame_cap = cap.read()
        if frame_cap is None:
            break
        cv2.destroyWindow("mywindow")
        # frame_cap = cv2.flip(frame_cap, 1)
        frame_cap = cv2.normalize(
            frame_cap, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8UC1
        )

        (success, boxes) = trackers.update(frame_cap)
        (dstwins, dst_pts) = field_point_tracker.update(frame_cap)

        if len(boxes) == 0:
            cv2.imwrite("file.jpg", frame_cap)

            parts = []
            url_base = 'https://detect.roboflow.com/'
            endpoint = os.getenv('ROBOFLOW_URL')
            access_token = os.getenv('ROBOFLOW_API_KEY')
            format = '&format=json'
            confidence = '&confidence=50'
            stroke = '&stroke=1'
            overlap = '&overlap=60'
            parts.append(url_base)
            parts.append(endpoint)
            parts.append(access_token)
            parts.append(format)
            parts.append(confidence)
            parts.append(overlap)
            parts.append(stroke)
            url = ''.join(parts)

            f = 'file.jpg'
            image = Image.open(f).convert("RGB")
            # Convert to JPEG Buffer
            buffered = io.BytesIO()
            image.save(buffered, quality=90, format="JPEG")
            # Construct the URL
            m = MultipartEncoder(fields={'file': (f, buffered.getvalue(), resource_path("image/jpeg"))})
            r = requests.post(url, data=m, headers={'Content-Type': m.content_type})
            preds = r.json()
            detections = preds['predictions']

            detect = detections

            for xydata in detect:
                for second in detections:
                    if xydata['class'] != second['class'] or xydata['class'] == second['class']:
                        if xydata['x'] - 5 <= second['x'] <= xydata['x'] + 5 or xydata['x'] == second['x']:
                            if xydata['y'] - 5 <= second['y'] <= xydata['y'] + 5 or xydata['y'] == second['y']:
                                second['remove'] = 'yes'
                            second['remove'] = 'no'
                        second['remove'] = 'no'

            for box in detections:
                if box['remove'] != 'yes':
                    color = "#4892EA"
                    w = box['width']
                    h = box['height']
                    player_class = box['class']
                    x1 = box['x'] - box['width'] / 2
                    y1 = box['y'] - box['height'] / 2
                    json_prediction.append(player_class)
                    tracker = cv2.TrackerCSRT_create()
                    trackers.add(tracker, frame_cap, (x1, y1, w, h))

            screenshot = cap.get(cv2.CAP_PROP_POS_FRAMES)

        # loop over the bounding boxes and draw them on the frame
        for dstbox in enumerate(dst_pts):
            (d, e) = [f for f in dstbox]
            cv2.circle(frame_cap, (int(e[0]), int(e[1])), 5, (255, 255, 0), -1)
            field_points.append((int(e[0]), int(e[1])))

        for id_no, box in enumerate(boxes):
            (x, y, w, h) = [int(v) for v in box]
            player_pts3.append(((x + int(w / 2), y + h), id_no))
            cv2.rectangle(frame_cap, (x, y), (x + w, y + h), (0, 255, 0), 3)
            try:
                cv2.putText(frame_cap, str((json_prediction[id_no]) + " " + str(id_no)), (x, y - 30), cv2.FONT_HERSHEY_TRIPLEX,
                        .7, (0, 255, 0), 1, cv2.LINE_AA)
            except (IndexError):
                cv2.putText(frame_cap, str(id_no + total_players), (x, y - 30), cv2.FONT_HERSHEY_TRIPLEX,
                            .7, (0, 0, 0), 1, cv2.LINE_AA)

            if len(source_points) > 0:
                if len(field_points) > 0:
                    box_id = player_pts3[0][1]
                    if box_id == id_no:
                        src_pts = np.float32(source_points).reshape(-1, 1, 2)
                        dst_pts = np.float32([field_points]).reshape(-1, 1, 2)
                        z, mask = cv2.findHomography(dst_pts, src_pts, cv2.RANSAC)
                        a = np.float32(player_pts3[0][0]).reshape(-1, 1, 2)
                        pointsOut = cv2.perspectiveTransform(a, z)
                        np.split(pointsOut, 1)
                        for x in pointsOut:
                            x1, y1 = x[0]

                            if id_no < len(json_prediction):
                                if json_prediction[0] == "DB" or json_prediction[0] == "LB":
                                    cv2.rectangle(field, ((int(abs(x1))), int(abs(y1))),
                                                  (int(abs(x1)) + 1, int(abs(y1)) + 1), (130,255,255), 2)
                                else:
                                    cv2.rectangle(field, ((int(abs(x1))), int(abs(y1))),
                                                  (int(abs(x1)) + 1, int(abs(y1)) + 1), (10,255,255), 2)

                            else:
                                cv2.rectangle(field, ((int(abs(x1))), int(abs(y1))),
                                              (int(abs(x1)) + 1, int(abs(y1)) + 1), (0,0,0), 2)
                                
                            screenshot += 1
                            break
                        player_pts2.clear()
                        player_pts2 = player_pts3.copy()
                    player_pts3.clear()
        field_points.clear()

        cv2.imshow("Frame", frame_cap)
        if screenshot > 0:
            cv2.imshow("field", field)
            cv2.destroyWindow("points")

        # if the 'space' key is selected, we are going to "select" a bounding
        # box to track
        if key == ord(" "):
            if screenshot == 0:
                cap.set(cv2.CAP_PROP_POS_FRAMES, start)
                box = cv2.selectROIs("Frame", frame_cap, fromCenter=False, showCrosshair=True)
                box = tuple(map(tuple, box))
                for bb in box:
                    tracker = OPENCV_OBJECT_TRACKERS[tracker_name]()
                    trackers.add(tracker, frame_cap, bb)
            else:
                cap.set(cv2.CAP_PROP_POS_FRAMES, screenshot)
                box = cv2.selectROIs("Frame", frame_cap, fromCenter=False, showCrosshair=True)
                box = tuple(map(tuple, box))
                for bb in box:
                    tracker = OPENCV_OBJECT_TRACKERS[tracker_name]()
                    trackers.add(tracker, frame_cap, bb)

        elif key == ord("p"):
            i = 1
            cv2.imwrite("boxes.jpg", frame_cap)
            for points in source_points:
                cv2.circle(points_image, points, 5, (20, 131, 60), -1)
                cv2.putText(points_image, str(i), (points[0] + 5, points[1] + 5), cv2.FONT_HERSHEY_TRIPLEX,
                            .7, (20, 131, 60), 1, cv2.LINE_AA)
                cv2.imshow("points", points_image)
                i += 1

            field_point_tracker = cv2.MultiTracker_create()

            dstbox = cv2.selectROIs("Frame", frame_cap, fromCenter=False, showCrosshair=True)
            dstbox = tuple(map(tuple, dstbox))
            for dstbb in dstbox:
                tracker = OPENCV_OBJECT_TRACKERS[tracker_name]()
                field_point_tracker.add(tracker, frame_cap, dstbb)

        if cap.get(cv2.CAP_PROP_POS_FRAMES) >= end:
            cv2.imwrite("dottedfield.jpg", field)
            cv2.imshow("field", field)
            ending = time.time()
            print(ending-starting)
            if key == ord("q"):
                cap.release()
                cv2.destroyAllWindows()

    cap.release()
    cv2.destroyAllWindows()
opencv()