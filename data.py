import cv2
import os
import time
from psycopg2 import sql, connect
from dotenv import load_dotenv

load_dotenv()
# prod
# conn = connect(dbname="footballiq", host="52.91.161.249", user="postgres", password="F00tball")
# testing
conn = connect(dbname=os.getenv('DATABASE_NAME'), host=os.getenv('DATABASE_HOST'), user=os.getenv('DATABASE_USER'),
               password=os.getenv('DATABASE_PASSWORD'))
conn.autocommit = True
cur = conn.cursor()


while True:
    k = cv2.waitKey(1000) & 0xFF
    # press 'q' to exit
    if k == ord('q'):
        break

    elif k == ord('k'):
        try:
            cur.execute(sql.SQL(
                "select playerid, min(x_pos),max(x_pos),min(y_pos),max(y_pos) from main_table where playid = '401301004101849902' and playerid = %s group by playerid order by playerid asc;"),
                (0,))
            result_position = cur.fetchall()
            image_size = result_position[0]
            x1 = int(image_size[1])
            x2 = int(image_size[2])
            y1 = int(image_size[3])
            y2 = int(image_size[4])

            img = cv2.imread('dottedfield.jpg')
            cv2.imshow("original", img)
            cropped_image = img[x1:x2, y1:y2]
            cv2.imshow("cropped", cropped_image)

        except:
            pass