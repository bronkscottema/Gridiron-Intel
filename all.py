import io
import math
import time
import tkinter
from datetime import datetime, timezone
from tkinter import *
from tkinter import simpledialog
import sys
import os
import cv2
import numpy as np
import psycopg2.extras
from PIL import Image, ImageDraw, ImageFont
from requests_toolbelt.multipart.encoder import MultipartEncoder
from end import *

load_dotenv()

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


def opencv(file, gameid_number, playid_number, offense_l_or_r, yard_line, offense, defense, league, year, week, regular_post, play_text):
    global source_points
    starting = time.time()
    total_players = 0
    tracker_name = 'csrt'

    OPENCV_OBJECT_TRACKERS = {
        "csrt": cv2.legacy.TrackerCSRT_create
    }

    # initialize OpenCV's special multi-object tracker
    trackers = cv2.legacy.MultiTracker_create()
    cap = cv2.VideoCapture(file)

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
    # test
    conn = connect(dbname=os.getenv('DATABASE_NAME'), host=os.getenv('DATABASE_HOST'), user=os.getenv('DATABASE_USER'),
                   password=os.getenv('DATABASE_PASSWORD'))
    # prod
    # conn = connect(dbname="footballiq", host="52.91.161.249", user="postgres", password="F00tball")
    conn.autocommit = True
    cur = conn.cursor()

    cur.execute(sql.SQL("select count(*) from main_table where playid = '" + str(playid_number) + "';"))
    exists = cur.fetchone()[0]
    if exists > 0:
        cur.execute("select max(playerid) from main_table where playid ='" + str(playid_number) + "';")
        total_players = cur.fetchone()
        total_players = total_players[0] + 1
    else:
        exists = False

    home = (0, 0, 0)
    away = (0, 0, 0)

    pt3 = []
    if league == "NFL":
        if yard_line >= 70:
            source_points = [(160, 800), (158, 400), (540, 400), (540, 600)]
            field = cv2.imread('images/nfl_g_40.png')
        elif 70 > yard_line > 50:
            source_points = [(160, 800), (158, 400), (540, 400), (540, 600)]
            field = cv2.imread(resource_path('images/nfl_20_30.png'))
        elif 50 > yard_line > 30:
            source_points = [(160, 800), (158, 400), (540, 400), (540, 600)]
            field = cv2.imread('images/nfl_40_10.png')
        else:
            source_points = [(160, 800), (158, 400), (540, 400), (540, 600)]
            field = cv2.imread(resource_path('images/nfl_40_g.png'))
        cur.execute("select rgb1 from nfl_team_colors where team_name = '" + offense + "'")
        home = cur.fetchone()
        home = eval(home[0])[::-1]
        cur.execute("select rgb1 from nfl_team_colors where team_name = '" + defense + "'")
        away = cur.fetchone()
        if away is not None:
            away = eval(away[0])[::-1]
    else:
        if 0 < yard_line < 20:
            source_points = [(160, 330), (545, 330), (545, 495),  (160, 495)]
            points_image = cv2.imread('images/ncaa_g_50.png')
            field = cv2.imread('images/ncaa_g_50.png')
        elif 20 < yard_line < 40:
            source_points = [(160, 330), (545, 330), (545, 495),  (160, 495)]
            points_image = cv2.imread('images/ncaa_10_40.png')
            field = cv2.imread('images/ncaa_10_40.png')
        elif 40 < yard_line < 50:
            source_points = [(160, 330), (545, 330), (545, 495),  (160, 495)]
            points_image = cv2.imread('images/ncaa_30_20.png')
            field = cv2.imread('images/ncaa_30_20.png')
        elif 50 < yard_line < 60:
            source_points = [(160, 330), (545, 330), (545, 495),  (160, 495)]
            points_image = cv2.imread('images/ncaa_40_10.png')
            field = cv2.imread('images/ncaa_40_10.png')
        elif 60 < yard_line < 80:
            source_points = [(160, 330), (545, 330), (545, 495),  (160, 495)]
            points_image = cv2.imread('images/ncaa_50_g.png')
            field = cv2.imread('images/ncaa_50_g.png')
        elif 80 < yard_line < 100:
            points_image = cv2.imread('images/ncaa_30_g.png')
            field = cv2.imread('images/ncaa_30_g.png')

        cur.execute("select rgb1 from college_team_colors where team_name = '" + offense + "'")
        home = cur.fetchone()
        home = eval(home[0])[::-1]
        cur.execute("select rgb1 from college_team_colors where team_name = '" + defense + "'")
        away = cur.fetchone()
        if away is not None:
            away = eval(away[0])[::-1]

    field_points = []
    speed_pts2 = []
    screenshot = 0
    null_variable = None
    result = []
    biglist = []
    json_prediction = []
    dst_list = []

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

    def get_dst_pts(image):
        # Load image, convert to grayscale, Otsu's threshold
        image = cv2.imread(image)
        # Set our filtering parameters
        # Initialize parameter setting using cv2.SimpleBlobDetector
        params = cv2.SimpleBlobDetector_Params()

        # Set Area filtering parameters
        params.filterByArea = True
        params.minArea = 300

        # Set Circularity filtering parameters
        params.filterByCircularity = True
        params.minCircularity = 0.6

        # Set Convexity filtering parameters
        params.filterByConvexity = True
        params.minConvexity = 0.2

        # Set inertia filtering parameters
        params.filterByInertia = True
        params.minInertiaRatio = 0.01

        # Create a detector with the parameters
        detector = cv2.SimpleBlobDetector_create(params)

        # Detect blobs
        keypoints = detector.detect(image)

        # Draw blobs on our image as red circles
        blank = np.zeros((1, 1))
        blobs = cv2.drawKeypoints(image, keypoints, blank, (0, 0, 255),
                                  cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

        from itertools import combinations

        p = []
        pts = cv2.KeyPoint_convert(keypoints)

        for i, pt in enumerate(pts):
            p.append(((int(pt[0]), int(pt[1])), i))
            cv2.putText(blobs, str(i), (int(pt[0]), int(pt[1])), cv2.FONT_HERSHEY_TRIPLEX, .7, (0, 0, 0), 1,
                        cv2.LINE_AA)
        height = int(image.shape[0])
        width = int(image.shape[1])

        cv2.line(blobs, (0, int(height / 2)), (width, int(height / 2)), (0, 0, 0), 1)
        cv2.line(blobs, (0, 30), (width, 30), (0, 0, 0), 1)
        cv2.line(blobs, (int(width / 2), 0), (int(width / 2), height), (0, 0, 0), 1)
        for x in p:
            if (x[0][0] > 0 and x[0][0] < width and x[0][1] < 30 and x[0][1] < height):
                p.remove(x)
        possible_combinations = []
        for comb in combinations(p, 4):
            possible_combinations.append(comb)
        print(possible_combinations)
        distnace = []

        for w in possible_combinations:
            pt_0_x, pt_0_y = w[0][0]
            pt_1_x, pt_1_y = w[1][0]
            pt_2_x, pt_2_y = w[2][0]
            pt_3_x, pt_3_y = w[3][0]

            if (pt_2_y - pt_0_y) / (pt_2_x - pt_0_x) == (pt_3_y - pt_1_y) / (pt_3_x - pt_1_x):
                print("parallel")
            else:

                for i, j in enumerate(w):
                    answer = math.dist(j[0], (0, 0))
                    distnace.append((answer, j[0], j[1]))
            distnace.sort()
        res = [i for n, i in enumerate(distnace) if i not in distnace[:n]]
        points_to_send = []
        for j,h in enumerate(res):
            cv2.putText(image, str(j), (int(h[1][0]), int(h[1][1])), cv2.FONT_HERSHEY_TRIPLEX, .7, (0, 0, 0), 1,
                        cv2.LINE_AA)
            points_to_send.append(h[1])

        cv2.imwrite("file.jpg", image)
        print(str(res))
        return points_to_send



    while cap.isOpened():
        key = cv2.waitKey(25) & 0xFF

        ret, frame_cap = cap.read()
        if frame_cap is None:
            break
        #cv2.destroyWindow("mywindow")

        if offense_l_or_r == "Offense Right":
            frame_cap = cv2.flip(frame_cap, 1)
        frame_cap = cv2.resize(frame_cap, (1280, 720))
        (success, boxes) = trackers.update(frame_cap)

        if len(boxes) == 0 and exists == False:
            cv2.imwrite("file.jpg", frame_cap)
            field_points.append(get_dst_pts("file.jpg"))
            # select the bounding box of the object we want to track (make
            # sure you press ENTER or SPACE after selecting the ROI)
            box = cv2.selectROIs("Frame", frame_cap, fromCenter=False,
                                 showCrosshair=True)

            parts = []
            url_base = 'https://detect.roboflow.com/'
            endpoint = os.getenv('ROBOFLOW_URL')
            access_token = os.getenv('ROBOFLOW_API_KEY')
            format = '&format=json'
            confidence = '&confidence=45'
            stroke = '&stroke=3'
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
            image = Image.open(f).convert("RGB")
            # Convert to JPEG Buffer
            buffered = io.BytesIO()
            image.save(buffered, quality=90, format="JPEG")
            # Construct the URL
            m = MultipartEncoder(fields={'file': (f, buffered.getvalue(), resource_path("image/jpeg"))})
            r = requests.post(url, data=m, headers={'Content-Type': m.content_type})
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
                    tracker = cv2.legacy.TrackerCSRT_create()
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
            screenshot = cap.get(cv2.CAP_PROP_POS_FRAMES)

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
                                cv2.rectangle(field, ((int(abs(x1))), int(abs(y1))),
                                              (int(abs(x1)) + 1, int(abs(y1)) + 1), (0, 0, 0), 2)
                                tup = (gameid_number, str(playid_number), int(box_id), (int(abs(x1))), (int(abs(y1))),
                                       cap.get(cv2.CAP_PROP_POS_FRAMES), null_variable,
                                       null_variable, gameid_number)

                                biglist.append(tup)
                                screenshot += 1
                                break
                            speed_pts2.clear()
                            speed_pts2 = pt3.copy()
                        pt3.clear()

        else:
            for face_no, box in enumerate(boxes):
                (x, y, w, h) = [int(v) for v in box]
                pt3.append(((x + int(w / 2), y + h), face_no))
                cv2.rectangle(frame_cap, (x, y), (x + w, y + h), (0, 255, 0), 3)
                try:
                    cv2.putText(frame_cap, str((json_prediction[face_no]) + " " + str(face_no)), (x, y - 30), cv2.FONT_HERSHEY_TRIPLEX,
                            .7, (0, 255, 0), 1, cv2.LINE_AA)
                except (IndexError):
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

                                    tup = (gameid_number, str(playid_number), int(box_id), (int(abs(x1))), (int(abs(y1))),
                                         cap.get(cv2.CAP_PROP_POS_FRAMES), null_variable,
                                         str(json_prediction[face_no]))

                                    biglist.append(tup)
                                else:
                                    cv2.rectangle(field, ((int(abs(x1))), int(abs(y1))),
                                                  (int(abs(x1)) + 1, int(abs(y1)) + 1), (0,0,0), 2)
                                    tup = (gameid_number, str(playid_number), int(box_id), (int(abs(x1))), (int(abs(y1))),
                                           cap.get(cv2.CAP_PROP_POS_FRAMES), null_variable,
                                           null_variable, gameid_number)

                                    biglist.append(tup)
                                screenshot += 1
                                break
                        pt3.clear()

        cv2.imshow("Frame", frame_cap)
        if screenshot > 0 or exists == True:
            cv2.imshow("field", field)
            cv2.imshow("points", points_image)

        # if the 'space' key is selected, we are going to "select" a bounding
        # box to track
        if key == ord(" "):
            if exists == True:
                cur.execute("select min(frame) from main_table where playid=" + str(playid_number) + ";")
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


        for i, points in enumerate(source_points):
            cv2.circle(points_image, points, 5, (255,160,122), -1)
            cv2.putText(points_image, str(i), (points[0] + 5, points[1] + 5), cv2.FONT_HERSHEY_TRIPLEX,
                        .7, (255,160,122), 1, cv2.LINE_AA)

        if cap.get(cv2.CAP_PROP_POS_FRAMES) >= end:
            ending = time.time()
            print(ending - starting)

            def insert_execute_values_iterator(
                    connection,
                    insertList,
            ) -> None:
                with connection.cursor() as cursor:
                    psycopg2.extras.execute_values(cursor, """
                        INSERT INTO main_table VALUES %s;
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
                        "DELETE FROM main_table WHERE playerid = %s and playid = '" + str(playid_number) + "';"),
                                (value,))
                except:
                    continue
            if not exists:
                cur.execute(sql.SQL(
                    "INSERT INTO recently_viewed (game_id, playid, offense, defense, play_text, date_added, league, year, regular_post, week)"
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"),
                            (gameid_number, playid_number, offense, defense,
                             play_text, datetime.now(timezone.utc), league, year, regular_post, week))


            cur.execute(
                "select frame, position, color, y_pos, playerid from main_table where playid = '" + playid_number + "' order by frame asc")
            off_vs_def = cur.fetchall()
            for x in off_vs_def:
                if x[1] == 'C':
                    y_pos = x[3]
                    for y in off_vs_def:
                        playerid = y[4]
                        if y[3] < y_pos:
                            cur.execute(sql.SQL(
                                "update main_table set color = 'defense' where playid = '" + playid_number + "' and playerid = %s"),
                                        (playerid,))
                        else:
                            cur.execute(sql.SQL(
                                "update main_table set color = 'offense' where playid = '" + playid_number + "' and playerid = %s"),
                                        (playerid,))
                    break
                else:
                    continue
            else:
                # There was no center
                CENTER_INP = simpledialog.askstring(title="Center Identification",
                                                  prompt="Which Id number on the screen is the center?")
                for x in off_vs_def:
                    if x[4] == CENTER_INP:
                        cur.execute(sql.SQL(
                            "update main_table set position = 'C' where playid = '" + playid_number + "' and playerid = %s"),
                                    (int(USER_INP),))
                        y_pos = x[3]
                        for y in off_vs_def:
                            playerid = y[4]
                            if y[3] < y_pos:
                                cur.execute(sql.SQL(
                                    "update main_table set color = 'defense' where playid = '" + playid_number + "' and playerid = %s"),
                                            (playerid,))
                            else:
                                cur.execute(sql.SQL(
                                    "update main_table set color = 'offense' where playid = '" + playid_number + "' and playerid = %s"),
                                            (playerid,))

            # get players with no position and update them
            cur.execute("select distinct(playerid), position from main_table where playid = '" + playid_number + "';")
            no_position = cur.fetchall()
            if len(no_position) > 0:
                for p in no_position:
                    if p[1] == None or p[1] == "":
                        USER_INP = simpledialog.askstring(title="Player Identification",
                                                          prompt="What Position is the Player Id?" + str(p[1]))
                        cur.execute(sql.SQL("update {} set position = %s where playerid = %s and playid = %s;").format(
                            sql.Identifier('main_table')),
                            (USER_INP, int(p[0]), str(playid_number)))

                for x in off_vs_def:
                    if x[4] == 'C':
                        cur.execute(sql.SQL(
                            "update main_table set position = 'C' where playid = '" + playid_number + "' and playerid = %s"),
                                    (int(USER_INP),))
                        y_pos = x[3]
                        for y in off_vs_def:
                            playerid = y[4]
                            if y[3] < y_pos:
                                cur.execute(sql.SQL(
                                    "update main_table set color = 'defense' where playid = '" + playid_number + "' and playerid = %s"),
                                            (playerid,))
                            else:
                                cur.execute(sql.SQL(
                                    "update main_table set color = 'offense' where playid = '" + playid_number + "' and playerid = %s"),
                                            (playerid,))

            else:
                print("all positions updated")



            cur.close()
            conn.close()
            cap.release()
            cv2.destroyAllWindows()

    cap.release()
    cv2.destroyAllWindows()
#opencv('C:\\Users\\bronkscottema\\Videos\\Captures\\Jaguars_vs_Lions_wk13_2022.mp4')