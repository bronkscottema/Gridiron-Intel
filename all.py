import os
import tkinter
from tkinter import *
from tkinter import simpledialog
import cv2
import numpy as np
from psycopg2 import connect, sql
import base64
import io
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime, timezone
from start import *
from end import *

import psycopg2.extras
from typing import Iterator, Dict, Any, List, Tuple


from dotenv import load_dotenv

load_dotenv()


def opencv(file, hash_or_num, gameid_number, playid_number, offense_l_or_r, yard_line, offense, defense, league, year, week, regular_post, play_text):
    global source_points
    total_players = 0
    tracker_name = 'csrt'

    OPENCV_OBJECT_TRACKERS = {
        "csrt": cv2.TrackerCSRT_create,
        "MOSSE": cv2.TrackerCSRT_create
    }

    # initialize OpenCV's special multi-object tracker
    trackers = cv2.MultiTracker_create()
    field_point_tracker = cv2.MultiTracker_create()
    cap = cv2.VideoCapture(file)

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
    # test
    conn = connect(dbname=os.getenv('DATABASE_NAME'), host=os.getenv('DATABASE_HOST'), user=os.getenv('DATABASE_USER'),
                   password=os.getenv('DATABASE_PASSWORD'))
    # prod
    # conn = connect(dbname="footballiq", host="52.91.161.249", user="postgres", password="F00tball")
    conn.autocommit = True
    cur = conn.cursor()
    file.strip()

    cur.execute(sql.SQL("select count(*) from temp_table where playid = '" + str(playid_number) + "';"))
    exists = cur.fetchone()[0]
    if exists > 0:
        cur.execute("select max(playerid) from temp_table where playid ='" + str(playid_number) + "';")
        total_players = cur.fetchone()
        total_players = total_players[0] + 1
    else:
        exists = False

    home = (0, 0, 0)
    away = (0, 0, 0)

    pt3 = []
    if league == "NFL":
        if hash_or_num == "Hashmark" and offense_l_or_r == "Offense Left":
            source_points = [(310, 800), (310, 400), (390, 400), (390, 800)]
        elif hash_or_num == "Hashmark" and offense_l_or_r == "Offense Right":
            source_points = [(161,), (310, 400), (390, 400), (390, 800)]
        elif hash_or_num == "Numbers":
            source_points = [(160, 800), (158, 400), (540, 400), (540, 600)]
        elif "inside":
            source_points = [(276, 700), (276, 680), (447, 680), (447, 700)]
    else:
        if hash_or_num == "Hashmark":
            source_points = [(269, 600), (270, 204), (435, 203), (434, 601)]
        elif hash_or_num == "Numbers":
            source_points = [(94, 791), (94, 392), (623, 392), (623, 592)]
        elif hash_or_num == "hashmarkRt":
            # right hash
            source_points = [(355, 300), (350, 200), (445, 200), (445, 300)]
        elif hash_or_num == "hashmarkLt":
            # left hash
            source_points = [(275, 300), (275, 200), (370, 200), (370, 300)]

    field_points = []
    speed_pts2 = []
    if league == "NFL":
        if yard_line >= 70:
            points_image = cv2.imread('images/nfl_g_40.png')
            field = cv2.imread('images/nfl_g_40.png')
        elif 70 > yard_line > 50:
            points_image = cv2.imread('images/nfl_20_30.png')
            field = cv2.imread('images/nfl_20_30.png')
        elif 50 > yard_line > 30:
            points_image = cv2.imread('images/nfl_40_10.png')
            field = cv2.imread('images/nfl_40_10.png')
        else:
            points_image = cv2.imread('images/nfl_40_g.png')
            field = cv2.imread('images/nfl_40_g.png')

        cur.execute("select rgb1 from nfl_team_colors where team_name = '" + offense + "'")
        home = cur.fetchone()
        home = eval(home[0])[::-1]
        cur.execute("select rgb1 from nfl_team_colors where team_name = '" + defense + "'")
        away = cur.fetchone()
        away = eval(away[0])[::-1]
    else:
        if 0 < yard_line < 30:
            points_image = cv2.imread('images/ncaa_g_40.png')
            field = cv2.imread('images/ncaa_g_40.png')
        elif 30 < yard_line < 50:
            points_image = cv2.imread('images/ncaa_20_30.png')
            field = cv2.imread('images/ncaa_20_30.png')
        elif 50 < yard_line < 70:
            points_image = cv2.imread('images/ncaa_40_10.png')
            field = cv2.imread('images/ncaa_40_10.png')
        else:
            points_image = cv2.imread('images/ncaa_40_g.png')
            field = cv2.imread('images/ncaa_40_g.png')

        cur.execute("select rgb1 from college_team_colors where team_name = '" + offense + "'")
        home = cur.fetchone()
        home = eval(home[0])[::-1]
        cur.execute("select rgb1 from college_team_colors where team_name = '" + defense + "'")
        away = cur.fetchone()
        away = eval(away[0])[::-1]

    screenshot = 0
    null_variable = None
    result = []
    biglist = []
    json_prediction = []

    def mouse_func(event, x1, y1, flags, param):
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

        ret, frame_cap = cap.read()
        if frame_cap is None:
            break
        cv2.destroyWindow("mywindow")

        if offense_l_or_r == "Offense Right":
            frame_cap = cv2.flip(frame_cap, 1)
        frame_cap = cv2.resize(frame_cap, (1280, 720))

        (success, boxes) = trackers.update(frame_cap)
        (dstwins, dst_pts) = field_point_tracker.update(frame_cap)

        if len(boxes) == 0:
            cv2.imwrite("file.jpg", frame_cap)
            # select the bounding box of the object we want to track (make
            # sure you press ENTER or SPACE after selecting the ROI)
            box = cv2.selectROIs("Frame", frame_cap, fromCenter=False,
                                 showCrosshair=True)

            parts = []
            url_base = 'https://detect.roboflow.com/'
            endpoint = os.getenv('ROBOFLOW_URL')
            access_token = os.getenv('ROBOFLOW_API_KEY')
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
                player_class = box['class']
                x1 = box['x'] - box['width'] / 2
                x2 = box['x'] + box['width'] / 2
                y1 = box['y'] - box['height'] / 2
                y2 = box['y'] + box['height'] / 2
                json_prediction.append(player_class)
                tracker = OPENCV_OBJECT_TRACKERS[tracker_name]()
                trackers.add(tracker, frame_cap, (x1, y1, w, h))
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
            # opencvImage = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            # cv2.imwrite("boxes.jpg", opencvImage)
            screenshot = cap.get(cv2.CAP_PROP_POS_FRAMES)

        # loop over the bounding boxes and draw them on the frame
        for dstbox in enumerate(dst_pts):
            (d, e) = [f for f in dstbox]
            cv2.circle(frame_cap, (int(e[0]), int(e[1])), 5, (255, 255, 0), -1)
            field_points.append((int(e[0]), int(e[1])))

        if exists:
            for face_no, box in enumerate(boxes):
                (x, y, w, h) = [int(v) for v in box]
                pt3.append(((x, y), face_no))
                cv2.rectangle(frame_cap, (x, y), (x + w, y + h), (0, 255, 0), 3)
                cv2.putText(frame_cap, str(face_no + total_players), (x, y - 30), cv2.FONT_HERSHEY_TRIPLEX,
                            .7, (0, 0, 0), 1, cv2.LINE_AA)

                if len(source_points) > 0:
                    if len(field_points) > 0:

                        box_id = pt3[0][1]
                        if box_id == face_no:
                            src_pts = np.float32(source_points).reshape(-1, 1, 2)
                            dst_pts = np.float32([field_points]).reshape(-1, 1, 2)
                            z, mask = cv2.findHomography(dst_pts, src_pts, cv2.RANSAC)
                            a = np.float32(pt3[0][0]).reshape(-1, 1, 2)
                            points_out = cv2.perspectiveTransform(a, z)
                            np.split(points_out, 1)
                            for x in points_out:
                                x1, y1 = x[0]
                                cv2.circle(field, (int(abs(x1) + 50), int(abs(y1))), 5, (0, 0, 0), 2)
                                cur.execute(
                                    sql.SQL("INSERT INTO temp_table VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"),
                                    (str(playid_number), int(box_id), (int(abs(x1))), (int(abs(y1))),
                                     cap.get(cv2.CAP_PROP_POS_FRAMES), null_variable,
                                     null_variable, gameid_number))
                                screenshot += 1
                                break
                            speed_pts2.clear()
                            speed_pts2 = pt3.copy()
                        pt3.clear()
            field_points.clear()
        else:
            for face_no, box in enumerate(boxes):
                (x, y, w, h) = [int(v) for v in box]
                pt3.append(((x + int(w / 2), y + h), face_no))
                cv2.rectangle(frame_cap, (x, y), (x + w, y + h), (0, 255, 0), 3)
                cv2.putText(frame_cap, str(face_no), (x, y - 30), cv2.FONT_HERSHEY_TRIPLEX,
                            .7, (0, 0, 0), 1, cv2.LINE_AA)

                if len(source_points) > 0:
                    if len(field_points) > 0:
                        box_id = pt3[0][1]
                        if box_id == face_no:
                            src_pts = np.float32(source_points).reshape(-1, 1, 2)
                            dst_pts = np.float32([field_points]).reshape(-1, 1, 2)
                            z, mask = cv2.findHomography(dst_pts, src_pts, cv2.RANSAC)
                            a = np.float32(pt3[0][0]).reshape(-1, 1, 2)
                            pointsOut = cv2.perspectiveTransform(a, z)
                            np.split(pointsOut, 1)
                            for x in pointsOut:
                                x1, y1 = x[0]

                                if face_no < len(json_prediction):
                                    if json_prediction[0] == "DB" or json_prediction[0] == "LB":
                                        cv2.rectangle(field, ((int(abs(x1))), int(abs(y1))),
                                                      (int(abs(x1)) + 1, int(abs(y1)) + 1), away, 2)
                                    else:
                                        cv2.rectangle(field, ((int(abs(x1))), int(abs(y1))),
                                                      (int(abs(x1)) + 1, int(abs(y1)) + 1), home, 2)
                                    # cur.execute(
                                    #     sql.SQL("INSERT INTO temp_table VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"),
                                    #     (str(playid_number), int(box_id), (int(abs(x1))), (int(abs(y1))),
                                    #      cap.get(cv2.CAP_PROP_POS_FRAMES), null_variable,
                                    #      str(json_prediction[face_no]), gameid_number))
                                    tup = (str(playid_number), int(box_id), (int(abs(x1))), (int(abs(y1))),
                                         cap.get(cv2.CAP_PROP_POS_FRAMES), null_variable,
                                         str(json_prediction[face_no]), gameid_number)

                                    biglist.append(tup)
                                else:
                                    # cur.execute(
                                    #     sql.SQL("INSERT INTO temp_table VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"),
                                    #     (str(playid_number), int(box_id), (int(abs(x1))), (int(abs(y1))),
                                    #      cap.get(cv2.CAP_PROP_POS_FRAMES), null_variable,
                                    #      null_variable, gameid_number))
                                    tup = (str(playid_number), int(box_id), (int(abs(x1))), (int(abs(y1))),
                                           cap.get(cv2.CAP_PROP_POS_FRAMES), null_variable,
                                           str(json_prediction[face_no]), gameid_number)

                                    biglist.append(tup)
                                screenshot += 1
                                break
                            speed_pts2.clear()
                            speed_pts2 = pt3.copy()
                        pt3.clear()
            field_points.clear()

        cv2.imshow("Frame", frame_cap)
        if screenshot > 0 or exists == True:
            cv2.imshow("field", field)
            cv2.destroyWindow("points_image")

        # if the 'space' key is selected, we are going to "select" a bounding
        # box to track
        if key == ord(" "):
            if exists == True:
                cur.execute("select min(frame) from temp_table where playid=" + str(playid_number) + ";")
                frameStart = cur.fetchone()[0]
                cap.set(cv2.CAP_PROP_POS_FRAMES, frameStart)
                box = cv2.selectROIs("Frame", frame_cap, fromCenter=False, showCrosshair=True)
                box = tuple(map(tuple, box))
                for bb in box:
                    tracker = OPENCV_OBJECT_TRACKERS[tracker_name]()
                    trackers.add(tracker, frame_cap, bb)
            else:
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
            cv2.imwrite("boxes.jpg", frame_cap)

            def insert_execute_values_iterator(
                    connection,
                    insertList,
            ) -> None:
                with connection.cursor() as cursor:
                    psycopg2.extras.execute_values(cursor, """
                        INSERT INTO temp_table VALUES %s;
                    """, ((
                        datainsert[0],
                        datainsert[1],
                        datainsert[2],
                        datainsert[3],
                        datainsert[4],
                        datainsert[5],
                        datainsert[6],
                        datainsert[7],
                    ) for datainsert in insertList))

            insert_execute_values_iterator(conn, insertList=biglist)
            cv2.imwrite("dottedfield.jpg", field)
            root = tkinter.Tk()
            root.withdraw()

            # write sql query to drop rows with result numbers
            USER_INP = simpledialog.askstring(title="Delete",
                                              prompt="Any ID's you'd like to delete? (Comma Seperated Values Only Please e.g. 1,2,3")
            result.append(USER_INP)

            for value in result[0].split(","):
                try:
                    cur.execute(sql.SQL(
                        "DELETE FROM temp_table WHERE playerid = %s and playid = '" + str(playid_number) + "';"),
                                (value,))
                except:
                    continue
            if not exists:
                cur.execute(sql.SQL(
                    "INSERT INTO recently_viewed (game_id, playid, offense, defense, play_text, date_added, file_path, league, year, regular_post, week)"
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"),
                            (gameid_number, playid_number, offense, defense,
                             play_text, datetime.now(timezone.utc), file, league, year, regular_post, week))

            cur.execute(
                "select frame,player_position, color, y_pos, playerid from temp_table where playid = '" + playid_number + "' order by frame asc")
            off_vs_def = cur.fetchall()
            for x in off_vs_def:
                if x[1] == 'C':
                    y_pos = x[3]
                    for y in off_vs_def:
                        playerid = y[4]
                        if y[3] < y_pos:
                            cur.execute(sql.SQL(
                                "update temp_table set color = 'defense' where playid = '" + playid_number + "' and playerid = %s"),
                                        (playerid,))
                        else:
                            cur.execute(sql.SQL(
                                "update temp_table set color = 'offense' where playid = '" + playid_number + "' and playerid = %s"),
                                        (playerid,))
                    break
                else:
                    continue
            else:
                # There was no center
                USER_INP = simpledialog.askstring(title="Center Identification",
                                                  prompt="Which Id number on the screen is the center?")
                for x in off_vs_def:
                    if x[4] == USER_INP:
                        cur.execute(sql.SQL(
                            "update temp_table set player_position = 'C' where playid = '" + playid_number + "' and playerid = %s"),
                                    (USER_INP,))
                        y_pos = x[3]
                        for y in off_vs_def:
                            playerid = y[4]
                            if y[3] < y_pos:
                                cur.execute(sql.SQL(
                                    "update temp_table set color = 'defense' where playid = '" + playid_number + "' and playerid = %s"),
                                            (playerid,))
                            else:
                                cur.execute(sql.SQL(
                                    "update temp_table set color = 'offense' where playid = '" + playid_number + "' and playerid = %s"),
                                            (playerid,))

            cur.close()
            conn.close()
            cap.release()
            cv2.destroyAllWindows()
            end_page()

    cap.release()
    cv2.destroyAllWindows()
