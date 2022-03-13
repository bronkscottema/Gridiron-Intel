import os
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap, QIcon, QFontDatabase
from PyQt5.QtWidgets import QWidget, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QFormLayout, QTableWidget, \
    QHeaderView, QApplication, QTableWidgetItem
from dotenv import load_dotenv
from psycopg2 import connect

load_dotenv()
# prod
# conn = connect(dbname="footballiq", host="52.91.161.249", user="postgres", password="F00tball")
# testing
conn = connect(dbname=os.getenv('DATABASE_NAME'), host=os.getenv('DATABASE_HOST'), user=os.getenv('DATABASE_USER'), password=os.getenv('DATABASE_PASSWORD'))
conn.autocommit = True
cur = conn.cursor()

keys = [ "playid", "playerid", "x_pos", "y_pos", "frame", "color", "player_position", "gameid"]


class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon('images/favicon.ico'))
        self.setGeometry(0, 0, 1920, 1080)
        self.setWindowTitle("Audible Analytics")
        self.font = QFont("proxima", 18)
        self.table_font = QFont("proxima", 12)
        self.ui()

    def ui(self):
        #layout section
        main_layout = QVBoxLayout()
        top_layout = QHBoxLayout()
        top_left_layout = QVBoxLayout()
        top_right_layout = QVBoxLayout()
        middle_layout = QHBoxLayout()
        main_layout.addLayout(top_layout)
        top_layout.addLayout(top_left_layout)
        top_layout.addLayout(top_right_layout)
        main_layout.addLayout(middle_layout)

        self.api_table = QTableWidget(0, len(keys))
        header = self.api_table.horizontalHeader()
        self.api_table.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)
        self.api_table.horizontalHeader().setFont(self.table_font)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(8, QHeaderView.ResizeToContents)
        # self.api_table.clicked.connect(self.set_submit_button)
        middle_layout.addWidget(self.api_table)
        self.setLayout(main_layout)

        self.show()

        def update_table(self):
            self.api_table.setSortingEnabled(False)
            cur.execute("select * from temp_table where playid = (select playid from recently_viewed;")
            result = cur.fetchone()
            try:
                self.api_table.setHorizontalHeaderLabels(keys)
                for n, key in enumerate(result):
                    self.api_table.insertRow(n)
                    for column_number, data in enumerate(keys):
                        item = QTableWidgetItem(str(key[data]))
                        item.setTextAlignment(4)
                        item.setFont(self.table_font)
                        self.api_table.setItem(n, column_number, item)
            except:
                pass

        def update_top_left(self):
            pixmap = QPixmap('boxes.jpg')
            pixmap = pixmap.scaled(500, 500)
            self.league_pic.setPixmap(pixmap)

        def update_top_right(self):
            pixmap = QPixmap('dottedfield.jpg')
            pixmap = pixmap.scaled(700, 1000)
            self.league_pic.setPixmap(pixmap)


app = QApplication(sys.argv)
QFontDatabase().addApplicationFont("fonts/proxima.ttf")
window = Window()
window.update_table(0)
sys.exit(app.exec_())