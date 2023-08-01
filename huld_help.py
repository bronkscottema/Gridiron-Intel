import io
import math
import time
from tkinter import *
import sys
import os
import cv2
import numpy as np
import pyautogui
import requests
from PIL import Image, ImageDraw, ImageFont
from dotenv import load_dotenv
from requests_toolbelt.multipart.encoder import MultipartEncoder
from roboflow import Roboflow

load_dotenv()

global DL
global OL
global DB
global LB
global QB
global SKILL

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


# The points in tuple latitude/longitude degrees space
def losangle(Cpos, QBpos, Skillpos):
    A = (Cpos[0], Cpos[1])
    B = (QBpos[0], QBpos[1])
    C = (Skillpos[0], Skillpos[1])

    # Convert the points to numpy latitude/longitude radians space
    a = np.radians(np.array(A))
    b = np.radians(np.array(B))
    c = np.radians(np.array(C))

    myradians = math.atan2(C[1] - A[1], C[0] - A[0])
    mydegrees = math.degrees(myradians)

    tackle_box_radians = math.atan2(A[1]-B[1], A[0]-B[0])
    tackle_box_angle = math.degrees(tackle_box_radians)

    # Print the results
    #print('\nThe angle ABC in 2D space in degrees:', mydegrees)

    x1_length = (Cpos[0] - 1440) / math.cos(mydegrees)
    y1_length = (Cpos[1] - 1440) / math.sin(mydegrees)
    length = max(abs(x1_length), abs(y1_length))
    endx1 = Cpos[0] + length * math.cos(math.radians(mydegrees))
    endy1 = Cpos[1] + length * math.sin(math.radians(mydegrees))

    x2_length = (Cpos[0] - 1440) / math.cos(mydegrees + 180)
    y2_length = (Cpos[1] - 1440) / math.sin(mydegrees + 180)
    length = max(abs(x2_length), abs(y2_length))
    endx2 = Cpos[0] + length * math.cos(math.radians(mydegrees + 180))
    endy2 = Cpos[1] + length * math.sin(math.radians(mydegrees + 180))

    #pic = cv2.imread('boxes.jpg')
    #cv2.line(pic, (int(endx1), int(endy1)), (int(endx2), int(endy2)), (0, 0, 255), 2)
    #cv2.imshow("FRAME", pic)
    #cv2.waitKey()
    return endx1, endy1, endx2, endy2, tackle_box_angle, mydegrees


def is_left(x,y,a,b,c,d):
    return (c - a)*(y - b) - (d - b)*(x - a) < 0


def player_count(players):
    DB = 0
    LB = 0
    OL = 0
    SKILL = 0
    QB = 0
    DL = 0
    for i in players:
        if i['class'] == 'DB' or i['class'] == 'S':
            DB += 1
        elif i['class'] == 'LB':
            LB += 1
        elif i['class'] == 'SKILL' or i['class'] == 'RB' or i['class'] == 'TE' or i['class'] == 'WR' or i['class'] == 'FB' or i['class'] == 'WING':
            SKILL += 1
        elif i['class'] == 'QB':
            QB += 1
        elif i['class'] == 'DE' or i['class'] == 'DT':
            DL += 1
        elif i['class'] == 'OT' or i['class'] == 'OG':
            OL += 1

def in_the_box(player_x, player_y, player_height, high_tackle, low_tackle, tack_angle, los, direction):
    #first draw the line
    length = 1000
    angle = tack_angle
    highy = 0
    highx = 0
    lowy = 0
    lowx = 0

    if direction == "left":
        highy = high_tackle[1] + length * math.sin(math.radians(angle))
        highx = high_tackle[0] + length * math.cos(math.radians(angle))

        lowy = low_tackle[1] + length * math.sin(math.radians(angle))
        lowx = low_tackle[0] + length * math.cos(math.radians(angle))
    else:
        highy = high_tackle[1] - length * math.sin(math.radians(angle))
        highx = high_tackle[0] - length * math.cos(math.radians(angle))

        lowy = low_tackle[1] - length * math.sin(math.radians(angle))
        lowx = low_tackle[0] - length * math.cos(math.radians(angle))

    #pic = cv2.imread('boxes.jpg')
    #cv2.line(pic, (int(low_tackle[0]), int(low_tackle[1])), (int(lowx), int(lowy)), (0, 0, 255), 2)
    #cv2.line(pic, (int(high_tackle[0]), int(high_tackle[1])), (int(highx), int(highy)), (0, 0, 255), 2)
    #cv2.line(pic, (int(los[0]), int(los[1])), (int(los[2]), int(los[3])), (0, 0, 255), 2)
    #cv2.circle(pic, (int(player_x), int(player_y)), 5, (255, 255, 0), -1)
    #cv2.circle(pic, (int(player_x), int(player_y)+int(player_height/2)), 5, (255, 255, 0), -1)
    #cv2.imwrite('boxes.jpg', pic)
    # cv2.waitKey()
    if direction == "left":
        if (player_x < lowx and player_x < highx and player_y < lowy and player_y > highy):
            return True
        elif (player_x < lowx and player_x < highx and (player_y+(player_height/2)) < lowy and (player_y+(player_height/2)) > highy):
            return True
        else:
            return False
    else:
        if (player_x > lowx and player_x < high_tackle[0] and player_y < lowy and player_y > highy):
            return True
        if (player_x > lowx and player_x < high_tackle[0] and (player_y+(player_height/2)) < lowy and (player_y+(player_height/2)) > highy):
            return True
        else:
            return False


def check_formation(players, cx, cy, is_left):
    formation = []
    qbx = 0
    wr_right = 0
    wr_left = 0
    for i in players:
        if i['class'] == 'QB':
            qbx = i['x']
            if is_left == True:
                if i['x'] - cx < -20:
                    formation.append("shotgun")
                else:
                    formation.append("under center")
            else:
                if i['x'] - cx > 20:
                    formation.append("under center")
                else:
                    formation.append("shotgun")
        if i['class'] == 'WR' or i['class'] == 'TE' or i['class'] == 'WING':
            if cy - i['y'] < 0:
                wr_right += 1
            else:
                wr_left += 1
        if i['class'] == 'RB':
            if -10 <= i['y'] - qbx <= 10:
                formation.append("pistol")
            elif i['y'] - qbx < 10:
                formation.append("rb right")
            else:
                formation.append("rb left")

    formation.append(str(wr_left) + "X" + str(wr_right))

    return formation


def check_safeties(players, cx, cy, is_left):
    safeties_count = 0
    for i in players:
        if i['class'] == "S":
            #check how far they from center width and height
            safeties_count += 1
            return "mofc"

def draw_players(detections, file_name):
    image = cv2.imread(file_name)
    for box in detections:
        if box['remove'] != 'yes':

            x = int(box['x'])
            y = int(box['y'])
            w = int(box['width'] / 2)
            h = int(box['height'] / 2)
            player_class = box['class']

            cv2.rectangle(image, (x - w, y-h), (x + w, y + h), (0, 255, 0), 3)
            cv2.putText(image, player_class + str(box['id']), (x, y - 30), cv2.FONT_HERSHEY_TRIPLEX,
                        .7, (0, 0, 0), 1, cv2.LINE_AA)
    cv2.imwrite("boxes.jpg", image)
    picture = cv2.imread("boxes.jpg")
    cv2.imshow("frame", picture)
    cv2.waitKey()


def opencv():
    DB: int = 0
    LB = 0
    SKILL = 0
    QB = 0
    DL = 0
    OL = 0
    CENTER = 0
    CenterX, CenterY = 0,0
    CenterW, CenterH = 0,0

    parts = []
    url_base = 'https://detect.roboflow.com/'
    endpoint = os.getenv('ROBOFLOW_URL')
    access_token = os.getenv('ROBOFLOW_API_KEY')
    format = '&format=json'
    confidence = '&confidence=30'
    stroke = '&stroke=3'
    overlap = '&overlap=50'
    parts.append(url_base)
    parts.append(endpoint)
    parts.append(access_token)
    parts.append(format)
    parts.append(confidence)
    parts.append(overlap)
    parts.append(stroke)
    url = ''.join(parts)
    name = "picture" + str(time.time()) + ".png"
    my_screenshot = pyautogui.screenshot()
    my_screenshot.save(name)
    f = name
    # Creating the kernel(2d convolution matrix)
    kernel = np.array([
        [0, -1, 0],
        [-1, 5, -1],
        [0, -1, 0]
    ])
    image = cv2.imread(f)
    # Applying the filter2D() function
    img = cv2.filter2D(src=image, ddepth=-1, kernel=kernel)
    clean = cv2.imwrite(name, img)
    image = Image.open(name).convert("RGB")
    # Convert to JPEG Buffer
    buffered = io.BytesIO()
    image.save(buffered, quality=90, format="JPEG")
    # Construct the URL
    m = MultipartEncoder(fields={'file': (f, buffered.getvalue(), resource_path("image/jpeg"))})
    r = requests.post(url, data=m, headers={'Content-Type': m.content_type})
    preds = r.json()
    detections = preds['predictions']

    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    detect = detections

    for i,j in enumerate(detections):
        if j['class'] == 'DB' or j['class'] == 'S':
            DB += 1
            j['id'] = i
        elif j['class'] == 'LB':
            LB += 1
            j['id'] = i
        elif j['class'] == 'SKILL' or j['class'] == 'RB' or j['class'] == 'TE' or j['class'] == 'WR' or j['class'] == 'FB' or j['class'] == 'WING':
            SKILL += 1
            j['id'] = i
        elif j['class'] == 'QB':
            QB += 1
            j['id'] = i
        elif j['class'] == 'DE' or j['class'] == 'DT':
            DL += 1
            j['id'] = i
        elif j['class'] == 'OT' or j['class'] == 'OG':
            OL += 1
            j['id'] = i
        elif j['class'] == 'CENTER':
            CENTER += 1
            j['id'] = i
            CenterX, CenterY = j['x'], j['y']
            CenterW, CenterH = j['width'], j['height']

    for xydata in detect:
        for second in detections:
            if xydata['class'] != second['class'] or xydata['class'] == second['class']:
                if xydata['x'] - 5 <= second['x'] <= xydata['x'] + 5 or xydata['x'] == second['x']:
                    if xydata['y'] - 5 <= second['y'] <= xydata['y'] + 5 or xydata['y'] == second['y']:
                        if xydata['id'] != second['id']:
                            try:
                                if second['remove'] == 'no' or xydata['remove'] == 'no':
                                    second['remove'] = 'yes'
                            except KeyError:
                                continue
                        else:
                            second['remove'] = 'no'

    for box in detections:
        if box['remove'] != 'yes':

            color = "#4892EA"
            w = box['width']
            h = box['height']
            player_class = box['class']
            x1 = box['x'] - box['width'] / 2
            x2 = box['x'] + box['width'] / 2
            y1 = box['y'] - box['height'] / 2
            y2 = box['y'] + box['height'] / 2
            draw.rectangle([
                x1, y1, x2, y2
            ], outline=color, width=5)

            if True:
                text = box['class']
                text_size = font.getsize(text)

                # set button size + 10px margins
                button_size = (text_size[0] + 20, text_size[1] + 20)
                button_img = Image.new('RGBA', button_size, color)
                # put text on button with 10px margins
                button_draw = ImageDraw.Draw(button_img)
                button_draw.text((10, 10), text + str(box['id']), font=font, fill=(255, 255, 255, 255))

                # put button on source image in position (0, 0)
                image.paste(button_img, (int(x1), int(y1)))
            opencvImage = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            cv2.imwrite("boxes.jpg", opencvImage)


    left = False
    right = False
    lowest_skill_y = []
    qb_x_y = 0,0
    #Logic for Formation
    if CENTER >= 1:
        for i in detections:
            if i['class'] == 'QB':
                if i['x'] < CenterX:
                    left = True
                    right = False
                    qb_y = i['y'] + (i['height'] / 2)
                    qb_x_y = i['x'], qb_y
                else:
                    right = True
                    left = False
                    qb_y = i['y'] + (i['height'] / 2)
                    qb_x_y = i['x'], qb_y

            if i['class'] == 'SKILL' or i['class'] == "WR":
                lowest_skill_y.append((i['x'], i['y'], i['width'], i['height'], i['id']))
        lowest_skill_y.sort(key=lambda x: x[1], reverse=True)
        if len(lowest_skill_y) > 0:
            yes = losangle((int(CenterX + (CenterW / 2)), int(CenterY + (CenterH /2))), (qb_x_y),  (int(lowest_skill_y[0][0]+int(lowest_skill_y[0][2] / 2)), int(lowest_skill_y[0][1] + int(lowest_skill_y[0][3] / 2))))
        else:
            print("no skill player was found, we have added this image to the model please check again another day.")
            upload(detections, name)
    else:
        print("no center was found, we have added this image to the model please check again another day.")
        upload(detections, name)

    p1x,p1y,p2x,p2y,tackle_box_angle,los_angle = yes
    los_line = (p1x,p1y,p2x,p2y)

    # do I try to do corrections?
    for det in detections:
        if is_left(det['x'], det['y'], p1x,p1y,p2x,p2y) is True and left == True and det['class'] != "CENTER":
            #print("here offense", det)
            det['odk'] = "offense"
            if det['class'] == 'LB' or det['class'] == 'DB':
                det['class'] = 'SKILL'
            elif det['class'] == "DT" or det['class'] == 'DL':
                det['class'] = 'OL'
        elif is_left(det['x'], det['y'], p1x,p1y,p2x,p2y) is False and left == False and det['class'] != "CENTER":
            #print("here offense", det)
            det['odk'] = "offense"
            if det['class'] == 'LB' or det['class'] == 'DB':
                det['class'] = 'SKILL'
            elif det['class'] == "DT" or det['class'] == 'DL':
                det['class'] = 'OL'
        elif det['class'] != "CENTER":
            #print("defense", det)
            det['odk'] = "defense"
            if det['class'] == "OT":
                det['class'] = 'DE'
            elif det['class'] == 'OG':
                det['class'] = 'DT'
    draw_players(detections, name)
    player_count(detections)
    #logic for identifying box
    box_linebacker = 0
    if left:
        tackle_box = []
        low_tackle_box = 0
        high_tackle_box = 0
        for player in detections:
            if player['class'] == "OT":
                tackle_box.append((player['x'], player['y'], player['width'], player['height']))
        tackle_box.sort(key=lambda x: x[1])
        if len(tackle_box) >= 2:
            low_tackle_box = (tackle_box[0][0] + (tackle_box[0][2] / 2), tackle_box[0][1] + (tackle_box[0][3] / 2))
            high_tackle_box = (tackle_box[1][0] + (tackle_box[1][2] / 2), tackle_box[1][1] + (tackle_box[1][3] / 2))
            for def_player in detections:
                if def_player['class'] == "LB":
                    if in_the_box(def_player['x'], def_player['y'], def_player['height'], low_tackle_box, high_tackle_box, tackle_box_angle, los_line, "left"):
                        box_linebacker += 1
        else:
            upload(detections, file_name=name)
        print(f'the front is {DL}-{box_linebacker}')
        pic = cv2.imread("boxes.jpg")
        cv2.imshow("frame", pic)
        pyautogui.alert(text=f'the front is {DL}-{box_linebacker}', title='Front', button='OK')

    else:
        tackle_box = []
        low_tackle_box = 0
        high_tackle_box = 0
        for player in detections:
            if player['class'] == "OT":
                tackle_box.append((player['x'], player['y'], player['width'], player['height']))
        tackle_box.sort(key=lambda x: x[1])
        if len(tackle_box) >= 2:
            low_tackle_box = (tackle_box[0][0] - (tackle_box[0][2] / 2), tackle_box[0][1] + (tackle_box[0][3] / 2))
            high_tackle_box = (tackle_box[1][0] - (tackle_box[1][2] / 2), tackle_box[1][1] + (tackle_box[1][3] / 2))
            for def_player in detections:
                if def_player['class'] == "LB":
                    if in_the_box(def_player['x'], def_player['y'], def_player['height'], low_tackle_box, high_tackle_box, tackle_box_angle, los_line, "right"):
                        box_linebacker += 1
        else:
            upload(detections, file_name=name)

        print(f'the front is {DL}-{box_linebacker}')
        pic = cv2.imread("boxes.jpg")
        cv2.imshow("frame", pic)
        pyautogui.alert(text=f'the front is {DL}-{box_linebacker}', title='Front', button='OK')

    mofo_mofc = check_safeties(detections, CenterX, CenterY, left)
    formation = check_formation(detections, CenterX, CenterY, left)
    print(f'the formation is {formation}')
    if mofo_mofc == "MOFO":
        print(f'{mofo_mofc} possible coverages: 0,2,4,6')
    else:
        print(f'{mofo_mofc} possible coverages: 0,1,3')
    upload(detections, name)

def upload(detections, file_name):
    classes = {'CENTER': 2, 'DB': 4, 'DE': 6, 'DT': 8, 'FB': 9, 'LB': 9, 'OG': 15, 'OT': 16, 'QB': 18, 'SKILL': 22,
               'S': 20, 'RB': 19, 'WR': 27}
    rf = Roboflow(api_key="UkLzsuZSvsQOnmhR2JaS")

    # Retrieve your current workspace and project name
    #print(rf.workspace())
    # Take screenshot

    f = file_name
    image = Image.open(f).convert("RGB")
    # Specify the project for upload
    project = rf.workspace("bronkscottema").project("high-school-football")
    img_height = image.height
    img_width = image.width
    # Upload the image to your project
    # with open('annotate.coco.json', 'w') as pred:
    #     for box in detections:
    #         if box['remove'] != 'yes':
    #
    #             color = "#4892EA"
    #             w = box['width']
    #             h = box['height']
    #             player_class = box['class']
    #             x1 = box['x'] - box['width'] / 2
    #             x2 = box['x'] + box['width'] / 2
    #             y1 = box['y'] - box['height'] / 2
    #             y2 = box['y'] + box['height'] / 2
    #
    #
    #             if x1 > x2:
    #                 x1, x2 = x2, x1
    #             if y1 > y2:
    #                 y1, y2 = y2, y1
    #
    #             width = x2 - x1
    #             height = y2 - y1
    #             x_centre, y_centre = int(width / 2), int(height / 2)
    #
    #             norm_xc = x_centre / img_width
    #             norm_yc = y_centre / img_height
    #             norm_width = width / img_width
    #             norm_height = height / img_height
    #
    #             for name, number in classes.items():  # for name, age in dictionary.iteritems():  (for Python 2.x)
    #                 if name == player_class:
    #                     yolo_annotations = [str(number), ' ' + str(norm_xc),
    #                                         ' ' + str(norm_yc),
    #                                         ' ' + str(norm_width),
    #                                         ' ' + str(norm_height), '\n']
    #
    #             pred.writelines(yolo_annotations)

    project.single_upload(image_path=file_name)
    print("success")
    if os.path.isfile(file_name):
        os.remove(file_name)
    sys.exit(0)

opencv()