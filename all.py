import os
from tkinter import *
from tkinter import simpledialog
import cv2
import numpy as np
from psycopg2 import connect, sql
import requests
import base64
import io
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

def opencv(file, radioOption, gameidNumber, offenseLorR, yardline):

    global totalPlayers
    trackerName = 'csrt'

    OPENCV_OBJECT_TRACKERS = {
        "csrt": cv2.TrackerCSRT_create,
        "MOSSE": cv2.TrackerCSRT_create
    }

    # initialize OpenCV's special multi-object tracker
    trackers = cv2.MultiTracker_create()
    dstpointTracker = cv2.MultiTracker_create()
    cap = cv2.VideoCapture(file)


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
    #test
    conn = connect(dbname=os.getenv('DATABASE_NAME'), host=os.getenv('DATABASE_HOST'), user=os.getenv('DATABASE_USER'), password=os.getenv('DATABASE_PASSWORD'))
    #prod
    # conn = connect(dbname="footballiq", host="52.91.161.249", user="postgres", password="F00tball")
    conn.autocommit = True
    cur = conn.cursor()
    file.strip()
    tableName = file.replace(' ', '_').split('/')[-1].split('.')[0]
    tableName = str.lower(tableName)
    cur.execute(sql.SQL("select count(*) from temp_table where playid = '" + str(paths[11].strip()) + "';"))
    exists = cur.fetchone()[0]
    if exists > 0:
        cur.execute("select max(playerid) from temp_table where playid ='" + str(paths[11].strip()) + "';")
        totalPlayers = cur.fetchone()
        totalPlayers = totalPlayers[0] + 1
    else:
        exists = False

    home = (0,0,0)
    away = (0,0,0)

    pt3 = []
    if paths[4].strip() == "NFL":
        if radioOption == "Hashmark" and paths[12].strip() == "Offense Left":
            srcPts = [(310, 800), (310, 400), (390, 400), (390, 800)]
        elif radioOption == "Hashmark" and paths[12].strip() == "Offense Right":
            srcPts = [(161, ), (310, 400), (390, 400), (390, 800)]
        elif radioOption == "Numbers":
            srcPts = [(160, 800), (158, 400), (540, 400), (540, 600)]
        elif "inside":
            srcPts = [(276, 700), (276, 680), (447, 680), (447, 700)]
    else:
        if radioOption == "Hashmark":
            srcPts = [(269, 600), (270, 204), (435, 203), (434, 601)]
        elif radioOption == "Numbers":
            srcPts = [(94, 791), (94, 392), (623, 392), (623, 592)]
        elif radioOption == "hashmarkRt":
            #right hash
            srcPts = [(355,300),(350, 200),(445, 200), (445, 300)]
        elif radioOption == "hashmarkLt":
            #left hash
            srcPts = [(275,300),(275, 200),(370, 200), (370,300)]

    dstPts = []
    speed_pts2 = []
    if paths[4].strip() == "NFL":
        if yardline >= 70:
            field = cv2.imread('images/nfl_g_40.png')
        elif 70 > yardline > 50:
            field = cv2.imread('images/nfl_20_30.png')
        elif 50 > yardline > 30:
            field = cv2.imread('images/nfl_40_10.png')
        else:
            field = cv2.imread('images/nfl_40_g.png')

        cur.execute("select rgb1 from nfl_team_colors where team_name = '"+paths[5].strip()+"'")
        home = cur.fetchone()
        home = eval(home[0])[::-1]
        cur.execute("select rgb1 from nfl_team_colors where team_name = '"+paths[9].strip()+"'")
        away = cur.fetchone()
        away = eval(away[0])[::-1]
    else:
        if 0 < yardline < 30:
            field = cv2.imread('images/ncaa_g_40.png')
        elif 30 < yardline < 50:
            field = cv2.imread('images/ncaa_20_30.png')
        elif 50 < yardline < 70:
            field = cv2.imread('images/ncaa_40_10.png')
        else:
            field = cv2.imread('images/ncaa_40_g.png')

        cur.execute("select rgb1 from college_team_colors where team_name = '"+paths[5].strip()+"'")
        home = cur.fetchone()
        home = eval(home[0])[::-1]
        cur.execute("select rgb1 from college_team_colors where team_name = '"+paths[9].strip()+"'")
        away = cur.fetchone()
        away = eval(away[0])[::-1]

    screenShot = 0
    nullVariable = None
    result = []
    jsonPrediction = []

    def mouse_func(event,x1,y1,flags,param):
        if event == cv2.EVENT_RBUTTONDBLCLK:
            ix, iy = x1, y1
            print(ix, iy)
        elif event == cv2.EVENT_RBUTTONDOWN:
            ix, iy = x1, y1
            print(ix, iy)
        elif event == cv2.EVENT_LBUTTONDBLCLK:
            ix, iy = x1, y1
            print(ix, iy)
        elif event == cv2.EVENT_LBUTTONDOWN:
            ix, iy = x1, y1
            print(ix, iy)


    while cap.isOpened():
        key = cv2.waitKey(50) & 0xFF

        ret, frameCap = cap.read()
        if frameCap is None:
            break
        cv2.destroyWindow("mywindow")

        if offenseLorR == "Offense Right":
            frameCap = cv2.flip(frameCap, 1)
        frameCap = cv2.resize(frameCap, (1280,720))

        (success, boxes) = trackers.update(frameCap)
        (dstwins, dst_pts) = dstpointTracker.update(frameCap)

        if len(boxes) == 0:
            cv2.imwrite("file.jpg", frameCap)
            # select the bounding box of the object we want to track (make
            # sure you press ENTER or SPACE after selecting the ROI)
            box = cv2.selectROIs("Frame", frameCap, fromCenter=False,
                                 showCrosshair=True)

            parts = []
            url_base = 'https://detect.roboflow.com/'
            endpoint = env('ROBOFLOW_URL')
            access_token = env('ROBOFLOW_API_KEY')
            format = '&format=json'
            confidence = '&confidence=70'
            stroke = '&stroke=4'
            overlap = '&overlap=0'
            parts.append(url_base)
            parts.append(endpoint)
            parts.append(access_token)
            parts.append(format)
            parts.append(confidence)
            parts.append(overlap)
            parts.append(stroke)
            url = ''.join(parts)

            f = 'file.jpg'
            image = Image.open(f)
            buffered = io.BytesIO()
            image = image.convert("RGB")
            image.save(buffered, quality=100, format="JPEG")
            img_str = base64.b64encode(buffered.getvalue())
            img_str = img_str.decode("ascii")

            headers = {'accept': 'application/json'}
            # start = time.time()
            r = requests.post(url, data=img_str, headers=headers)
            # print('post took ' + str(time.time() - start))

            # POST to the API
            # re = requests.post("https://app.roboflow.com/bronkscottema/football-players-zm06l/upload?api_key=UkLzsuZSvsQOnmhR2JaS", data=img_str, headers={
            #     'accept': 'application/json'})
            # print(re.json())
            # print(r.json())
            preds = r.json()
            detections = preds['predictions']

            draw = ImageDraw.Draw(image)
            font = ImageFont.load_default()
            for box in detections:
                color = "#4892EA"
                w = box['width']
                h = box['height']
                playerClass = box['class']
                x1 = box['x'] - box['width'] / 2
                x2 = box['x'] + box['width'] / 2
                y1 = box['y'] - box['height'] / 2
                y2 = box['y'] + box['height'] / 2
                jsonPrediction.append(playerClass)
                tracker = OPENCV_OBJECT_TRACKERS[trackerName]()
                trackers.add(tracker, frameCap, (x1, y1, w, h))
            #     draw.rectangle([
            #         x1, y1, x2, y2
            #     ], outline=color, width=5)
            #
            #     if True:
            #         text = box['class']
            #         text_size = font.getsize(text)
            #
            #         # set button size + 10px margins
            #         button_size = (text_size[0] + 20, text_size[1] + 20)
            #         button_img = Image.new('RGBA', button_size, color)
            #         # put text on button with 10px margins
            #         button_draw = ImageDraw.Draw(button_img)
            #         button_draw.text((10, 10), text, font=font, fill=(255, 255, 255, 255))
            #
            #         # put button on source image in position (0, 0)
            #         image.paste(button_img, (int(x1), int(y1)))
            # image.show()
            screenShot = cap.get(cv2.CAP_PROP_POS_FRAMES)

        # loop over the bounding boxes and draw them on the frame
        for dstbox in enumerate(dst_pts):
            (d, e) = [f for f in dstbox]
            cv2.circle(frameCap, (int(e[0]), int(e[1])), 5, (255, 255, 0), -1)
            dstPts.append((int(e[0]), int(e[1])))

        if exists == True:
            for face_no, box in enumerate(boxes):
                (x, y, w, h) = [int(v) for v in box]
                pt3.append(((x,y), face_no))
                cv2.rectangle(frameCap, (x, y), (x + w, y + h), (0, 255, 0), 3)
                cv2.putText(frameCap, str(face_no + totalPlayers), (x, y - 30), cv2.FONT_HERSHEY_TRIPLEX,
                            .7, (0, 0, 0), 1, cv2.LINE_AA)

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
                                cur.execute(
                                    sql.SQL("INSERT INTO temp_table VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"),
                                    (str(paths[11].strip()), int(box_id), (int(abs(x1))), (int(abs(y1))),
                                     cap.get(cv2.CAP_PROP_POS_FRAMES), nullVariable,
                                     nullVariable, gameidNumber))
                                screenShot += 1
                                break
                            speed_pts2.clear()
                            speed_pts2 = pt3.copy()
                        pt3.clear()
            dstPts.clear()
        else:
            for face_no, box in enumerate(boxes):
                (x, y, w, h) = [int(v) for v in box]
                pt3.append(((x+int(w/2),y+h), face_no))
                cv2.rectangle(frameCap, (x, y), (x + w, y + h), (0, 255, 0), 3)
                cv2.putText(frameCap, str(face_no), (x, y - 30), cv2.FONT_HERSHEY_TRIPLEX,
                            .7, (0, 0, 0), 1, cv2.LINE_AA)

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


                                if face_no < len(jsonPrediction):
                                    if jsonPrediction[0] == "DB" or jsonPrediction[0] == "LB":
                                        cv2.rectangle(field, ((int(abs(x1))), int(abs(y1))),
                                                  (int(abs(x1)) + 1, int(abs(y1)) + 1), away, 2)
                                    else:
                                        cv2.rectangle(field, ((int(abs(x1))), int(abs(y1))),
                                                      (int(abs(x1)) + 1, int(abs(y1)) + 1), home, 2)
                                    cur.execute(sql.SQL("INSERT INTO temp_table VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"),
                                            (str(paths[11].strip()), int(box_id), (int(abs(x1))), (int(abs(y1))),
                                    cap.get(cv2.CAP_PROP_POS_FRAMES), nullVariable,
                                    str(jsonPrediction[face_no]), gameidNumber))
                                else:
                                    cur.execute(
                                        sql.SQL("INSERT INTO temp_table VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"),
                                        (str(paths[11].strip()), int(box_id), (int(abs(x1))), (int(abs(y1))),
                                         cap.get(cv2.CAP_PROP_POS_FRAMES), nullVariable,
                                         nullVariable, gameidNumber))
                                screenShot += 1
                                break
                            speed_pts2.clear()
                            speed_pts2 = pt3.copy()
                        pt3.clear()
            dstPts.clear()

        cv2.imshow("Frame", frameCap)
        if screenShot > 0 or exists == True:
            cv2.imshow("field", field)
            cv2.destroyWindow("points")


        # if the 'space' key is selected, we are going to "select" a bounding
        # box to track
        if key == ord(" "):
            if exists == True:
                cur.execute("select min(frame) from temp_table where playid=" + str(paths[11].strip()) + ";")
                frameStart = cur.fetchone()[0]
                cap.set(cv2.CAP_PROP_POS_FRAMES, frameStart)
                box = cv2.selectROIs("Frame", frameCap, fromCenter=False, showCrosshair=True)
                box = tuple(map(tuple, box))
                for bb in box:
                    tracker = OPENCV_OBJECT_TRACKERS[trackerName]()
                    trackers.add(tracker, frameCap, bb)
            else:
                if screenShot == 0:
                    cap.set(cv2.CAP_PROP_POS_FRAMES, start)
                    box = cv2.selectROIs("Frame", frameCap, fromCenter=False, showCrosshair=True)
                    box = tuple(map(tuple, box))
                    for bb in box:
                        tracker = OPENCV_OBJECT_TRACKERS[trackerName]()
                        trackers.add(tracker, frameCap, bb)
                else:
                    cap.set(cv2.CAP_PROP_POS_FRAMES, screenShot)
                    box = cv2.selectROIs("Frame", frameCap, fromCenter=False, showCrosshair=True)
                    box = tuple(map(tuple, box))
                    for bb in box:
                        tracker = OPENCV_OBJECT_TRACKERS[trackerName]()
                        trackers.add(tracker, frameCap, bb)

        elif key == ord("p"):
            i = 1
            for points in srcPts:
                cv2.circle(field, points, 5, (20, 131, 60), -1)
                cv2.putText(field, str(i), (points[0] + 5, points[1] + 5), cv2.FONT_HERSHEY_TRIPLEX,
                            .7, (20, 131, 60), 1, cv2.LINE_AA)
                cv2.imshow("points", field)
                i += 1
            dstpointTracker = cv2.MultiTracker_create()

            dstbox = cv2.selectROIs("Frame", frameCap, fromCenter=False, showCrosshair=True)
            dstbox = tuple(map(tuple, dstbox))
            for dstbb in dstbox:
                tracker = OPENCV_OBJECT_TRACKERS[trackerName]()
                dstpointTracker.add(tracker, frameCap, dstbb)

        if cap.get(cv2.CAP_PROP_POS_FRAMES) >= end:
            #write sql query to drop rows with result numbers
            USER_INP = simpledialog.askstring(title="Delete",
                                              prompt="Any ID's you'd like to delete? (Comma Seperated Values Only Please e.g. 1,2,3")
            result.append(USER_INP)

            for value in result[0].split(","):
                try:
                    cur.execute(sql.SQL("DELETE FROM temp_table WHERE playerid = %s and playid = '" + str(paths[11].strip()) + "';"),
                            (value,))
                except:
                    continue
            if not exists:
                cur.execute(sql.SQL("INSERT INTO recently_viewed (game_id, playid, offense, defense, play_text, date_added, file_path, league, year, regular_post, week)"
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"), (paths[10].strip(), paths[11].strip(), paths[5].strip(), paths[9].strip(),
                tableName, datetime.now(timezone.utc), file, paths[4].strip(), paths[7].strip(), paths[6].strip(), paths[8].strip()))

            cur.execute("select frame,player_position, color, y_pos, playerid from temp_table where playid = '" + paths[11].strip() +"' order by frame asc")
            off_vs_def = cur.fetchall()
            for x in off_vs_def:
                if x[1] == 'C':
                    y_pos = x[3]
                    for y in off_vs_def:
                        playerid = y[4]
                        if y[3] < y_pos:
                            cur.execute(sql.SQL("update temp_table set color = 'defense' where playid = '" + paths[
                                11].strip() + "' and playerid = %s"),(playerid,))
                        else:
                            cur.execute(sql.SQL("update temp_table set color = 'offense' where playid = '" + paths[
                                11].strip() + "' and playerid = %s"),(playerid,))
                    break
                else:
                    continue
            else:
                #There was no center
                USER_INP = simpledialog.askstring(title="Center Identification",
                                                  prompt="Which Id number on the screen is the center?")
                for x in off_vs_def:
                    if x[4] == USER_INP:
                        cur.execute(sql.SQL("update temp_table set player_position = 'C' where playid = '" + paths[
                            11].strip() + "' and playerid = %s"), (USER_INP,))
                        y_pos = x[3]
                        for y in off_vs_def:
                            playerid = y[4]
                            if y[3] < y_pos:
                                cur.execute(sql.SQL("update temp_table set color = 'defense' where playid = '" + paths[
                                    11].strip() + "' and playerid = %s"),(playerid,))
                            else:
                                cur.execute(sql.SQL("update temp_table set color = 'offense' where playid = '" + paths[
                                    11].strip() + "' and playerid = %s"),(playerid,))

            cur.close()
            conn.close()
            cap.release()
            cv2.destroyAllWindows()

    cap.release()
    cv2.destroyAllWindows()