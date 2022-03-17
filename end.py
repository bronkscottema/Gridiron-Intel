import os
import sys

from PyQt5.QtCore import Qt, QSortFilterProxyModel
from PyQt5.QtGui import QFont, QPixmap, QIcon, QFontDatabase, QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QWidget, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QFormLayout, QTableWidget, \
    QHeaderView, QApplication, QTableWidgetItem, QTabWidget, QLineEdit, QTableView
from psycopg2 import connect
import psycopg2.extras
from typing import Iterator, Dict, Any
from Roster import *
from dotenv import load_dotenv

load_dotenv()
# prod
# conn = connect(dbname="footballiq", host="52.91.161.249", user="postgres", password="F00tball")
# testing
conn = connect(dbname=os.getenv('DATABASE_NAME'), host=os.getenv('DATABASE_HOST'), user=os.getenv('DATABASE_USER'), password=os.getenv('DATABASE_PASSWORD'))
conn.autocommit = True
cur = conn.cursor()

roster_labels = [ "Player Id", "First Name", "Last Name", "Number", "Position"]
roster_keys = [ "last_name", "first_name", "jersey", "position", "height", "weight", "year"]
team_roster = [ "Last Name", "First Name", "Number", "Position", "Height", "Weight", "Year"]


class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.search_field = QLineEdit()
        self.away_search_field = QLineEdit()
        self.tab2 = QWidget()
        self.tab1 = QWidget()
        self.tabs = QTabWidget()
        self.recently_viewed_table = QTableWidget(0, len(roster_labels))
        self.away_roster_table = QTableView()
        self.home_roster_table = QTableView()
        self.setWindowIcon(QIcon('images/favicon.ico'))
        self.setGeometry(0, 0, 1920, 1080)
        self.setWindowTitle("Audible Analytics")
        self.font = QFont("proxima", 18)
        self.table_font = QFont("proxima", 11)
        self.fieldpic = QLabel(self)
        self.play_pic = QLabel(self)
        self.ui()

    def ui(self):
        #layout section
        main_layout = QHBoxLayout()
        field_layout = QVBoxLayout()
        roster_layout = QVBoxLayout()
        image_layout = QVBoxLayout()

        self.fieldpic.setPixmap(QPixmap('dottedfield.jpg'))
        field_layout.addWidget(self.fieldpic)
        main_layout.addLayout(field_layout)

        pixmap = QPixmap('boxes.jpg')
        pixmap = pixmap.scaled(720, 480)
        self.play_pic.setPixmap(pixmap)
        image_layout.addWidget(self.play_pic)

        header = self.recently_viewed_table.horizontalHeader()
        self.recently_viewed_table.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)
        self.recently_viewed_table.horizontalHeader().setFont(self.table_font)
        # self.api_table.clicked.connect(self.set_submit_button)
        image_layout.addWidget(self.recently_viewed_table)

        #api roster data
        cur.execute(
            "select offense,defense from recently_viewed order by date_added desc limit  1;")
        result = cur.fetchall()

        self.tabs.addTab(self.tab1, result[0][0])
        self.tabs.addTab(self.tab2, result[0][1])
        self.tab1.layout = QVBoxLayout()
        self.tab2.layout = QVBoxLayout()

        #tab1/hometeam
        self.home_model = QStandardItemModel(len(team_roster), 1)
        self.filter_proxy_model = QSortFilterProxyModel()
        self.filter_proxy_model.setSourceModel(self.home_model)
        self.filter_proxy_model.setFilterKeyColumn(0)
        self.search_field.setStyleSheet('font-size: 14px; height: 30px;')
        self.search_field.textChanged.connect(self.filter_proxy_model.setFilterRegExp)
        self.home_roster_table.horizontalHeader()
        self.home_roster_table.setModel(self.filter_proxy_model)
        self.home_roster_table.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)
        self.home_roster_table.horizontalHeader().setFont(self.table_font)
        # self.api_table.clicked.connect(self.set_submit_button)
        self.tab1.layout.addWidget(self.search_field)
        self.tab1.layout.addWidget(self.home_roster_table)
        self.tab1.setLayout(self.tab1.layout)

        #tab2/awayteam
        self.away_model = QStandardItemModel(len(team_roster), 1)
        self.away_filter_proxy_model = QSortFilterProxyModel()
        self.away_filter_proxy_model.setSourceModel(self.away_model)
        self.away_filter_proxy_model.setFilterKeyColumn(0)
        self.away_search_field.setStyleSheet('font-size: 14px; height: 30px;')
        self.away_search_field.textChanged.connect(self.away_filter_proxy_model.setFilterRegExp)
        self.away_roster_table.horizontalHeader()
        self.away_roster_table.setModel(self.away_filter_proxy_model)
        self.away_roster_table.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)
        self.away_roster_table.horizontalHeader().setFont(self.table_font)
        # self.api_table.clicked.connect(self.set_submit_button)
        self.tab2.layout.addWidget(self.away_search_field)
        self.tab2.layout.addWidget(self.away_roster_table)
        self.tab2.setLayout(self.tab2.layout)

        roster_layout.addWidget(self.tabs)
        main_layout.addLayout(image_layout)
        main_layout.addLayout(roster_layout)
        self.setLayout(main_layout)

        self.show()

    def update_play_table(self):
        self.recently_viewed_table.setSortingEnabled(False)
        cur.execute("select playid from temp_table where playid = (select playid from recently_viewed order by date_added desc limit 1);")
        result = cur.fetchone()

        cur.execute("select * from roster where playid = '" + result[0] + "';")
        roster_exist = cur.fetchall()

        if len(roster_exist) == 0:
            cur.execute("select gameid, playid, playerid, player_position from temp_table where playid = '" + result[0] + "' "
                        "and frame = (select min(frame) from temp_table where playid = '" + result[0] + "');")
            play_table_result = cur.fetchall()

            def insert_execute_values_iterator(
                    connection,
                    roster: Iterator[Dict[str, Any]],
            ) -> None:
                with connection.cursor() as cursor:
                    psycopg2.extras.execute_values(cursor, """
                        INSERT INTO roster VALUES %s;
                    """, ((
                        str(person[0]),
                        str(person[1]),
                        person[2],
                        " ",
                        " ",
                        0,
                        person[3],
                    ) for person in roster))

            insert_execute_values_iterator(conn, roster=play_table_result)

            try:
                self.recently_viewed_table.setHorizontalHeaderLabels(roster_labels)
                for n, key in enumerate(play_table_result):
                    self.recently_viewed_table.insertRow(n)
                    for column_number, data in enumerate(roster_labels):
                        if data == "First Name" or data == "Last Name":
                            item = QTableWidgetItem(str(" "))
                            item.setTextAlignment(4)
                            item.setFont(self.table_font)
                            self.roster_table.setItem(n, column_number, item)
                        elif data == "Player Id":
                            item = QTableWidgetItem(str(key[0]))
                            item.setTextAlignment(4)
                            item.setFont(self.table_font)
                            self.recently_viewed_table.setItem(n, column_number, item)
                        elif data == "Number":
                            item = QTableWidgetItem(str(0))
                            item.setTextAlignment(4)
                            item.setFont(self.table_font)
                            self.recently_viewed_table.setItem(n, column_number, item)
                        elif data == "Position":
                            item = QTableWidgetItem(str(key[3]))
                            item.setTextAlignment(4)
                            item.setFont(self.table_font)
                            self.recently_viewed_table.setItem(n, column_number, item)
                        else:
                            break
            except:
                pass

        else:
            cur.execute("select playerid, first_name, last_name, position from roster where playid = '" + result[0] + "' order by playerid;")
            play_table_result = cur.fetchall()

            try:
                self.recently_viewed_table.setHorizontalHeaderLabels(roster_labels)
                for n, key in enumerate(play_table_result):
                    self.recently_viewed_table.insertRow(n)
                    for column_number, data in enumerate(roster_labels):
                        if data == "First Name" or data == "Last Name":
                            continue
                        elif data == "Number":
                            item = QTableWidgetItem(str(0))
                            item.setTextAlignment(4)
                            item.setFont(self.table_font)
                            self.recently_viewed_table.setItem(n, column_number, item)
                        elif data == "Position":
                            item = QTableWidgetItem(str(key[3]))
                            item.setTextAlignment(4)
                            item.setFont(self.table_font)
                            self.recently_viewed_table.setItem(n, column_number, item)
                        else:
                            item = QTableWidgetItem(str(key[column_number]))
                            item.setTextAlignment(4)
                            item.setFont(self.table_font)
                            self.recently_viewed_table.setItem(n, column_number, item)
            except:
                pass


    def update_roster_table(self):

        cur.execute(
            "select offense,defense,year,league from recently_viewed order by date_added desc limit  1;")
        result = cur.fetchall()[0]

        if result[3] == "NCAA":
            home_roster = get_whole_ncaa_home_roster(team=result[0], year=result[2])

            try:
                self.home_model.setHorizontalHeaderLabels(team_roster)
                self.home_roster_table.setSortingEnabled(False)
                for n, key in enumerate(home_roster):
                    self.home_model.insertRow(n)
                    for column_number, data in enumerate(roster_keys):
                        item = QStandardItem(str(key.__getattribute__(data)))
                        self.home_model.setItem(n, column_number, item)
            except:
                pass

            away_roster = get_whole_ncaa_away_roster(team=result[1], year=result[2])
            try:
                self.away_model.setHorizontalHeaderLabels(team_roster)
                self.away_roster_table.setSortingEnabled(False)
                for n, key in enumerate(away_roster):
                    self.away_model.insertRow(n)
                    for column_number, data in enumerate(roster_keys):
                        items = QStandardItem(str(key.__getattribute__(data)))
                        self.away_model.setItem(n, column_number, items)
            except:
                pass
        else:
            print("NFL")



def end_page():
    app = QApplication(sys.argv)
    QFontDatabase().addApplicationFont("fonts/proxima.ttf")
    window = Window()
    window.update_play_table()
    window.update_roster_table()
    sys.exit(app.exec_())

if __name__ == '__main__':
    end_page()
