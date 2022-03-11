from tkinter import *
from tkinter import simpledialog
from tkinter.filedialog import askopenfilename
import cv2
import numpy as np



def playerSpeedTracker():
    USER_INP = simpledialog.askstring(title="Left Or Right",
                                      prompt="Is the offense moving left or right (Options are Left Or Right)")


    global totalPlayers
    trackerName = 'csrt'
    Tk().withdraw()  # we don't want a full GUI, so keep the root window from appearing
    filename = askopenfilename()  # show an "Open" dialog box and return the path to the selected file
    OPENCV_OBJECT_TRACKERS = {
        "csrt": cv2.TrackerCSRT_create
    }

    # initialize OpenCV's special multi-object tracker
    trackers = cv2.MultiTracker_create()
    dstpointTracker = cv2.MultiTracker_create()
    cap = cv2.VideoCapture(filename)


    length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    def onChange(trackbarValue):
        cap.set(cv2.CAP_PROP_POS_FRAMES, trackbarValue)
        err,img = cap.read()
        cv2.imshow("mywindow", img)
        pass


    cv2.namedWindow('mywindow')
    cv2.createTrackbar('start', 'mywindow', 0, length, onChange)
    cv2.createTrackbar('end', 'mywindow', 200, length, onChange)

    onChange(0)
    cv2.waitKey()

    start = cv2.getTrackbarPos('start', 'mywindow')
    end = cv2.getTrackbarPos('end', 'mywindow')
    if start >= end:
        raise Exception("start must be less than end")

    cap.set(cv2.CAP_PROP_POS_FRAMES, start)

    srcMat = cv2.imread('Figure_1.png')
    speed1 = []
    speed2 = []
    pt3 = []
    srcPts = [(94, 791), (94, 392), (623, 392), (623, 592)]
    dstPts = []
    speed_pts2 = []
    field = cv2.imread('Figure_1.png')
    screenShot = 0

    while cap.isOpened():

        ret, frameCap = cap.read()
        if frameCap is None:
            break
        cv2.destroyWindow("mywindow")

        if USER_INP.uppercase() == "Right" or USER_INP.lowercase() == "right":
            frameCap = cv2.flip(frameCap, 1)
        frameCap = cv2.resize(frameCap, (1280,720))

        (success, boxes) = trackers.update(frameCap)
        (dstwins, dst_pts) = dstpointTracker.update(frameCap)

        # loop over the bounding boxes and draw them on the frame
        for dstbox in enumerate(dst_pts):
            (d, e) = [f for f in dstbox]
            cv2.circle(frameCap, (int(e[0]), int(e[1])), 5, (255, 255, 0), -1)
            dstPts.append((int(e[0]), int(e[1])))


        for face_no, box in enumerate(boxes):
            (x, y, w, h) = [int(v) for v in box]
            pt3.append(((x,y), face_no))
            if len(speed_pts2) > 0:
                if len(pt3) > 0:
                    x0, y0 = pt3[0][0]
                    x1, y1 = speed_pts2[0][0]
                    if -1 > x1 - x0 < 1  or -1 > y1-y0 < 1:
                        currentSpeed = (np.math.sqrt((((x1 - x0 * 100)) ** 2) + (((y1 - y0 * 100)) ** 2)))
                        inchesPerSecond = (currentSpeed * (1/30))
                        mph = inchesPerSecond/176
                        mph = "%.1f" % mph
                        cv2.rectangle(frameCap, (x, y), (x + w, y + h), (0, 255, 0), 3)
                        cv2.putText(frameCap, str(mph), (x, y - 30), cv2.FONT_HERSHEY_TRIPLEX,
                                    .7, (0, 0, 0), 1, cv2.LINE_AA)
                        speed1.append(mph)


            if len(srcPts) > 0:
                if len(dstPts) > 0:
                    box_id = pt3[0][1]
                    if box_id == face_no:
                        src_pts = np.float32(srcPts).reshape(-1, 1, 2)
                        dst_pts = np.float32([dstPts]).reshape(-1, 1, 2)
                        z, mask = cv2.findHomography(dst_pts, src_pts, cv2.RANSAC)
                        a = np.float32(pt3[0][0]).reshape(-1, 1, 2)
                        pointsOut = cv2.perspectiveTransform(a, z)
                        np.split(pointsOut, 1)
                        for x in pointsOut:
                            x1, y1 = x[0]
                            #img, center, radius, color, thickness=None
                            cv2.circle(field, (int(abs(x1)+50), int(abs(y1))),
                                          (5), (0, 0, 0), 2)
                            screenShot += 1
                            break
                        speed_pts2.clear()
                        speed_pts2 = pt3.copy()
                    pt3.clear()
        dstPts.clear()
        try:
            if srcMat is not NONE:
                cv2.destroyWindow("srcFrame")
        except:
            pass
        cv2.imshow("Frame", frameCap)
        if screenShot > 0:
            cv2.imshow("field", field)
            cv2.destroyWindow("points")

        key = cv2.waitKey(100) & 0xFF

        if key == ord("s"):
            box = cv2.selectROIs("Frame", frameCap, fromCenter=False, showCrosshair=True)
            box = tuple(map(tuple, box))
            for bb in box:
                tracker = OPENCV_OBJECT_TRACKERS[trackerName]()
                trackers.add(tracker, frameCap, bb)

        elif key == ord("p"):
            i = 1
            for points in srcPts:
                cv2.circle(srcMat, points, 5, (0,0,0), -1)
                cv2.putText(srcMat, str(i), (points[0] + 5, points[1] + 5), cv2.FONT_HERSHEY_TRIPLEX,
                            .7, (0, 0, 0), 1, cv2.LINE_AA)
                cv2.imshow("points", srcMat)
                i += 1
            dstpointTracker = cv2.MultiTracker_create()

            dstbox = cv2.selectROIs("Frame", frameCap, fromCenter=False, showCrosshair=True)
            dstbox = tuple(map(tuple, dstbox))
            for dstbb in dstbox:
                tracker = OPENCV_OBJECT_TRACKERS[trackerName]()
                dstpointTracker.add(tracker, frameCap, dstbb)

        if cap.get(cv2.CAP_PROP_POS_FRAMES) >= end:
            #write sql query to drop rows with result numbers
            print(speed1)
            simpledialog.askstring(title="Top Speed", prompt="Your top speed is ")
            cap.release()
            cv2.destroyAllWindows()
            Tk.destroy()

    cap.release()
    cv2.destroyAllWindows()

