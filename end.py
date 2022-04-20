import urllib

import cv2
from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtCore import Qt, QSortFilterProxyModel, QDataStream, QIODevice, QVariant, QRectF, \
    pyqtSignal, QPoint, QTimer
from PyQt5.QtGui import QFont, QPixmap, QIcon, QFontDatabase, QStandardItemModel, QStandardItem, QBrush, QColor, QImage
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QApplication, QTableWidgetItem, \
    QTabWidget, QLineEdit, QTableView, QAbstractItemView, QDesktopWidget, QPushButton, QGraphicsView, QFrame, \
    QGraphicsScene, QGraphicsPixmapItem, QGridLayout, QComboBox, QScrollArea, QFormLayout
from psycopg2 import connect
import psycopg2.extras
from typing import Iterator, Dict, Any
from qtwidgets import AnimatedToggle
from Roster import *
from dotenv import load_dotenv

load_dotenv()
# prod
# conn = connect(dbname="footballiq", host="52.91.161.249", user="postgres", password="F00tball")
# testing
conn = connect(dbname=os.getenv('DATABASE_NAME'), host=os.getenv('DATABASE_HOST'), user=os.getenv('DATABASE_USER'),
               password=os.getenv('DATABASE_PASSWORD'))
conn.autocommit = True
cur = conn.cursor()

recent_roster_keys = ["playerid", "last_name", "first_name", "jersey", "position", "height", "weight", "year"]
roster_labels = ["Player Id", "Last Name", "First Name", "Number", "Position", "Height", "Weight", "Year"]
roster_keys = ["last_name", "first_name", "jersey", "position", "height", "weight", "year"]
team_roster = ["Last Name", "First Name", "Number", "Position", "Height", "Weight", "Year"]

cur.execute("select offense,defense,year,league from recently_viewed order by date_added desc limit  1;")
result = cur.fetchone()
tableitems = []


class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.viewer = PhotoViewer()
        self.image_layout = QVBoxLayout()
        self.away_model = QStandardItemModel(len(team_roster), 1)
        self.away_filter_proxy_model = QSortFilterProxyModel(self)
        self.filter_proxy_model = QSortFilterProxyModel(self)
        self.home_model = QStandardItemModel(len(team_roster), 1)
        self.recently_viewed_model = QStandardItemModel(len(roster_labels), 1)
        self.refresh_button = QPushButton('Refresh', self)
        self.submit_button = QPushButton('Submit', self)
        self.submit_button.setObjectName("endPush")
        self.refresh_button.setObjectName("endPush")
        self.search_field = QLineEdit()
        self.away_search_field = QLineEdit()
        self.tab2 = QWidget()
        self.tab1 = QWidget()
        self.tabs = QTabWidget()

        self.breakdown_tab = QWidget()
        self.field_tab = QWidget()
        self.toptabs = QTabWidget()
        self.recently_viewed_table = roster_recent()
        self.away_roster_table = away_table()
        self.home_roster_table = home_table()
        self.setWindowIcon(QIcon('images/favicon.ico'))
        screen = QDesktopWidget().screenGeometry()
        self.setGeometry(0, 0, screen.width(), screen.height())
        self.showMaximized()
        self.setWindowTitle("Audible Analytics")
        self.font = QFont("proxima", 18)
        self.table_font = QFont("proxima", 11)
        self.fieldpic = QLabel(self)
        self.play_pic = QLabel(self)
        self.home_logo = QLabel(self)
        self.away_logo = QLabel(self)
        self.main_layout = QHBoxLayout()
        self.field_layout = QVBoxLayout()
        self.image_layout = QVBoxLayout()
        self.logo_layout = QVBoxLayout()
        self.move_image_layout = QHBoxLayout()
        self.roster_layout = QHBoxLayout()
        self.game_roster_layout = QVBoxLayout()
        self.api_roster_layout = QVBoxLayout()
        self.button_layout = QHBoxLayout()
        self.route_layout = thegrid()
        self.scrollbar = QScrollArea(widgetResizable=True)
        self.toggle_2 = AnimatedToggle(
            checked_color="#4400B0EE",
            pulse_checked_color="#4400B0EE"
        )
        self.ui()

    def ui(self):
        # layout section
        self.fieldpic.setPixmap(QPixmap('dottedfield.jpg'))
        self.field_layout.addWidget(self.fieldpic)

        self.viewer.setPhoto(QPixmap("boxes.jpg"))
        self.move_image_layout.addWidget(self.viewer)
        self.image_layout.setSpacing(0)
        self.image_layout.setContentsMargins(0, 0, 0, 0)
        self.image_layout.addLayout(self.move_image_layout)

        self.scrollbar.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.toptabs.addTab(self.field_tab, "Field")
        self.toptabs.addTab(self.scrollbar, "Breakdown")

        self.main_layout.addWidget(self.toptabs)
        self.scrollbar.setWidget(self.breakdown_tab)
        self.field_tab.layout = QVBoxLayout()
        self.breakdown_tab.layout = QVBoxLayout()
        self.field_tab.layout.addWidget(self.fieldpic)
        self.field_tab.setLayout(self.field_tab.layout)
        self.breakdown_tab.layout.addLayout(self.route_layout)
        self.breakdown_tab.setLayout(self.breakdown_tab.layout)

        self.toggle_2.setStyleSheet("min-width: 75px; max-width: 75px;")
        self.toggle_2.setObjectName("toggle")
        self.toggle_2.clicked.connect(self.set_light_dark_mode)
        self.logo_layout.addWidget(self.toggle_2, alignment=Qt.AlignTop)
        self.move_image_layout.addLayout(self.logo_layout)

        self.image_layout.addWidget(self.play_pic)
        self.image_layout.addLayout(self.roster_layout)
        self.roster_layout.addLayout(self.game_roster_layout)
        self.roster_layout.addLayout(self.api_roster_layout)

        self.recently_viewed_table.setModel(self.recently_viewed_model)
        self.recently_viewed_table.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)
        self.recently_viewed_table.horizontalHeader().setFont(self.table_font)
        self.recently_viewed_table.verticalHeader().setVisible(False)
        self.recently_viewed_table.setAlternatingRowColors(True)
        self.game_roster_layout.addWidget(self.recently_viewed_table)
        self.game_roster_layout.addLayout(self.button_layout)
        self.button_layout.addWidget(self.submit_button)
        self.button_layout.addWidget(self.refresh_button)
        self.submit_button.clicked.connect(self.submit_pushed)
        self.submit_button.setFont(self.font)
        self.refresh_button.setFont(self.font)
        self.refresh_button.clicked.connect(self.refresh_pushed)

        # api roster data

        self.tabs.addTab(self.tab1, "")
        self.tabs.addTab(self.tab2, "")

        self.tab1.layout = QVBoxLayout()
        self.tab2.layout = QVBoxLayout()

        # tab1/hometeam
        self.filter_proxy_model.setSourceModel(self.home_model)
        self.filter_proxy_model.setFilterKeyColumn(0)
        self.search_field.setStyleSheet('font-size: 14px; height: 30px;')
        self.search_field.setPlaceholderText("Search by last name")
        self.search_field.textChanged.connect(self.filter_proxy_model.setFilterRegExp)
        self.home_roster_table.horizontalHeader()
        self.home_roster_table.setModel(self.filter_proxy_model)
        self.home_roster_table.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)
        self.home_roster_table.horizontalHeader().setFont(self.table_font)
        self.home_roster_table.setAlternatingRowColors(True)
        self.home_roster_table.verticalHeader().setVisible(False)

        self.tab1.layout.addWidget(self.home_roster_table)
        self.tab1.layout.addWidget(self.search_field)
        self.tab1.setLayout(self.tab1.layout)

        # tab2/awayteam
        self.away_filter_proxy_model.setSourceModel(self.away_model)
        self.away_filter_proxy_model.setFilterKeyColumn(0)
        self.away_search_field.setStyleSheet('font-size: 14px; height: 30px;')
        self.away_search_field.setPlaceholderText("Search by last name")
        self.away_search_field.textChanged.connect(self.away_filter_proxy_model.setFilterRegExp)
        self.away_roster_table.horizontalHeader()
        self.away_roster_table.setObjectName(result[1].replace(" ", "") + "table")
        self.away_roster_table.setModel(self.away_filter_proxy_model)
        self.away_roster_table.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)
        self.away_roster_table.horizontalHeader().setFont(self.table_font)
        self.away_roster_table.setAlternatingRowColors(True)
        self.away_roster_table.verticalHeader().setVisible(False)
        self.tab2.layout.addWidget(self.away_roster_table)
        self.tab2.layout.addWidget(self.away_search_field)
        self.tab2.setLayout(self.tab2.layout)
        self.api_roster_layout.addWidget(self.tabs)

        self.main_layout.addLayout(self.image_layout)

        self.setLayout(self.main_layout)
        self.show()

    def update_play_table(self):
        self.recently_viewed_table.setSortingEnabled(False)
        cur.execute(
            "select playid from main_table where playid = (select playid from recently_viewed order by date_added desc limit 1);")
        result_main = cur.fetchone()

        cur.execute("select * from roster where playid = '" + result_main[0] + "';")
        roster_exist = cur.fetchall()

        if len(roster_exist) == 0:
            cur.execute(
                "select gameid, playid, playerid, position from main_table where playid = '" + result_main[0] + "' "
                "and frame = (select min(frame) from main_table where playid = '" +
                result_main[0] + "');")
            play_table_result = cur.fetchall()

            defense_count = 0
            for i in play_table_result:
                if i[3] == "LB" or i[3] == "DB":
                    defense_count += 1
            if defense_count == 8:
                gameid = play_table_result[0][0]
                playid = play_table_result[0][1]
                playerid = len(play_table_result) - 1
                play_table_result.append(tuple((gameid, playid, playerid, "DE")))
                play_table_result.append(tuple((gameid, playid, playerid + 1, "DT")))
                play_table_result.append(tuple((gameid, playid, playerid + 2, "DE")))
                play_table_result.append(tuple((gameid, playid, playerid + 3, "RT")))
                play_table_result.append(tuple((gameid, playid, playerid + 4, "RG")))
                play_table_result.append(tuple((gameid, playid, playerid + 5, "LG")))
                play_table_result.append(tuple((gameid, playid, playerid + 6, "LT")))
            else:
                gameid = play_table_result[0][0]
                playid = play_table_result[0][1]
                playerid = len(play_table_result) - 1
                play_table_result.append(tuple((gameid, playid, playerid, "DE")))
                play_table_result.append(tuple((gameid, playid, playerid + 1, "DT")))
                play_table_result.append(tuple((gameid, playid, playerid + 2, "DT")))
                play_table_result.append(tuple((gameid, playid, playerid + 3, "DE")))
                play_table_result.append(tuple((gameid, playid, playerid + 4, "RT")))
                play_table_result.append(tuple((gameid, playid, playerid + 5, "RG")))
                play_table_result.append(tuple((gameid, playid, playerid + 6, "LG")))
                play_table_result.append(tuple((gameid, playid, playerid + 7, "LT")))

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
                        0,
                        0,
                        0,
                    ) for person in roster))

            insert_execute_values_iterator(conn, roster=play_table_result)

            try:
                self.recently_viewed_model.clear()
                self.recently_viewed_model.setHorizontalHeaderLabels(roster_labels)
                for n, key in enumerate(play_table_result):
                    self.recently_viewed_model.insertRow(n)
                    for column_number, data in enumerate(recent_roster_keys):
                        if data == "first_name" or data == "last_name":
                            item = QStandardItem(str(" "))
                            item.setTextAlignment(Qt.AlignCenter)
                            self.recently_viewed_model.setItem(n, column_number, item)
                        elif data == "playerid":
                            item = QStandardItem(str(key[2]))
                            item.setTextAlignment(Qt.AlignCenter)
                            self.recently_viewed_model.setItem(n, column_number, item)
                        elif data == "jersey" or data == "weight" or data == "year" or data == "height":
                            item = QStandardItem(str(0))
                            item.setTextAlignment(Qt.AlignCenter)
                            self.recently_viewed_model.setItem(n, column_number, item)
                        elif data == "position":
                            item = QStandardItem(str(key[3]))
                            item.setTextAlignment(Qt.AlignCenter)
                            self.recently_viewed_model.setItem(n, column_number, item)
                        else:
                            break
            except:
                pass

        else:
            self.recently_viewed_model.clear()
            cur.execute(
                "select playerid, last_name, first_name, position, height, weight, year from roster where playid = '" +
                result_main[0] + "' order by playerid;")
            play_table_result = cur.fetchall()

            try:
                self.recently_viewed_model.setHorizontalHeaderLabels(roster_labels)
                for n, key in enumerate(play_table_result):
                    self.recently_viewed_model.insertRow(n)
                    for column_number, data in enumerate(roster_labels):
                        if data == "First Name" or data == "Last Name":
                            continue
                        elif data == "Number" or data == "Height" or data == "Weight" or data == "Year":
                            item = QStandardItem(str(0))
                            item.setTextAlignment(Qt.AlignCenter)
                            self.recently_viewed_model.setItem(n, column_number, item)
                        elif data == "Position":
                            item = QStandardItem(str(key[3]))
                            item.setTextAlignment(Qt.AlignCenter)
                            self.recently_viewed_model.setItem(n, column_number, item)
                        else:
                            item = QStandardItem(str(key[column_number]))
                            item.setTextAlignment(Qt.AlignCenter)
                            self.recently_viewed_model.setItem(n, column_number, item)
            except:
                pass

    def update_roster_table(self):
        if result[3] == "NCAA":
            self.home_model.clear()

            home_roster = get_whole_ncaa_home_roster(team=result[0], year=result[2])

            try:
                self.home_model.setHorizontalHeaderLabels(team_roster)
                self.home_roster_table.setSortingEnabled(False)
                for n, key in enumerate(home_roster):
                    self.home_model.insertRow(n)
                    for column_number, data in enumerate(roster_keys):
                        item = QStandardItem(str(key.__getattribute__(data)))
                        item.setTextAlignment(Qt.AlignCenter)
                        self.home_model.setItem(n, column_number, item)
            except:
                pass

            away_roster = get_whole_ncaa_away_roster(team=result[1], year=result[2])
            try:
                self.away_model.clear()
                self.away_model.setHorizontalHeaderLabels(team_roster)
                self.away_roster_table.setSortingEnabled(False)
                for n, key in enumerate(away_roster):
                    self.away_model.insertRow(n)
                    for column_number, data in enumerate(roster_keys):
                        items = QStandardItem(str(key.__getattribute__(data)))
                        items.setTextAlignment(Qt.AlignCenter)
                        self.away_model.setItem(n, column_number, items)
            except:
                pass
        else:
            print("NFL")

    def refresh_pushed(self):
        self.update_play_table()

    def submit_pushed(self):
        output = []
        for row in range(self.recently_viewed_table.model().rowCount()):
            row_data = []
            for column in range(self.recently_viewed_model.columnCount()):
                index = self.recently_viewed_model.index(row, column)
                row_data.append(index.data())
            output.append(row_data)
        print(output)

        cur.execute(
            "select playid from main_table where playid = (select playid from recently_viewed order by date_added desc limit 1);")
        result_main = cur.fetchone()

        cur.execute("select min(playerid), max(playerid) from roster where playid = '" + result_main[0] + "';")
        min_max_playerid = cur.fetchall()[0]

        for i in range(min_max_playerid[0], min_max_playerid[1]):
            for j in enumerate(output):
                if i == j[0]:
                    cur.execute("update roster set last_name = %s, first_name = %s, number = %s,"
                                "position = %s, height = %s, weight = %s, year = %s where playerid = %s;"), \
                    (j[1], j[2], j[3], j[4], j[5], j[6], j[8], j[0])

    def set_light_dark_mode(self):
        self.tabs.setCurrentIndex(0)
        if self.toggle_2.checkState() == 2:
            self.style = '''
            QLayout {
                margin: 0;
                spacing: 0;
            }
            QTabWidget::pane{
                border:none; 
            }
            QWidget {
                background-color: black;
            }
            QLabel {
                color: white;
                font-family: Proxima;
                font-size: 16px;
            }
            QComboBox QAbstractItemView {
                background-color: white;
            }
            QTableView {
                background-color: white;
            }
            QComboBox::drop-down {
                border: 0px; /* This seems to replace the whole arrow of the combo box */
                color: white;
            }
            QComboBox {
                background-color: white;
                font-family: Proxima;
                font-size: 16px;
            }
            QLineEdit {
                background-color: white;
                font-family: Proxima;
                font-size: 16px;
            }
            QTabWidget::pane { 
                border: none;
                margin: -9px, -9px, -9px, -9px;
            }
            QLineEdit {
                background-color: white;
            }
            QTabBar::tab {
                background-color: black;
                color: white;
            }
            '''
        else:
            self.style = '''
            QTabWidget::pane { 
                border: none;
                margin: -9px, -9px, -9px, -9px;
            }
            QLabel {
                font-family: Proxima;
                font-size: 16px;
            }
            QComboBox {
                background-color: white;
                font-family: Proxima;
                font-size: 16px;
            }
            QLineEdit {
                background-color: white;
                font-family: Proxima;
                font-size: 16px;
            }
            QWidget {
                background-color: white;
            }
            QLayout {
                margin: 0px;
                spacing: 0px;
            }
            '''
        if result is not None:
            if result[3] == "NFL":
                team_name = result[0]
                team_name = team_name.replace(" ", "").lower()
                # set stylesheet here
                teamFile = "styles/nfl/" + team_name + ".qss"
                try:
                    with open(teamFile, "r") as self.fh:
                        self.setStyleSheet(self.fh.read() + self.style)
                except:
                    pass
            else:
                data = (result[0], result[1])
                cur.mogrify("select logo from college_team_colors where team_name IN %s;", (data,))
                cur.execute("select logo from college_team_colors where team_name IN %s;",
                            (data,))
                url = cur.fetchall()
                data_logo = urllib.request.urlopen(url[1][0]).read()
                image = QtGui.QImage()
                image.loadFromData(data_logo)
                image1 = image.scaled(50, 50, Qt.KeepAspectRatio)

                data_logo_2 = urllib.request.urlopen(url[0][0]).read()
                image_away = QtGui.QImage()
                image_away.loadFromData(data_logo_2)
                image_away1 = image_away.scaled(50, 50, Qt.KeepAspectRatio)

                self.tabs.setIconSize(QtCore.QSize(60, 60))
                self.tabs.setTabIcon(0, QIcon(QPixmap(image1).transformed(QtGui.QTransform().rotate(-90))))
                self.tabs.setTabIcon(1, QIcon(QPixmap(image_away1).transformed(QtGui.QTransform().rotate(-90))))
                self.tabs.setTabPosition(QtWidgets.QTabWidget.East)

                offense_name = result[0]
                offense_name = offense_name.replace(" ", "").lower()
                defense_name = result[1]
                defense_name = defense_name.replace(" ", "").lower()
                # set stylesheet here
                offteamFile = "styles/ncaa/" + offense_name + ".qss"
                defteamFile = "styles/ncaa/" + defense_name + ".qss"
                try:
                    with open(offteamFile, "r") as self.of, open(defteamFile, "r") as self.df:
                        self.setStyleSheet(self.df.read() + self.of.read() + self.style)
                except:
                    pass


class LabelClass(QLabel):
    def __init__(self, title):
        super().__init__(title)
        self.name_label_class = QtWidgets.QLabel(title)
        self.path_class = QLabel()


class EditClass(QLineEdit):
    def __init__(self, *args):
        super().__init__(*args)
        self.formation_class = QLineEdit()
        self.play_class = QLineEdit()


class thegrid(QGridLayout):
    def __init__(self, parent=None):
        QGridLayout.__init__(self, parent)
        self.offense_container = QWidget()
        self.defense_container = QWidget()
        self.timer = QTimer()
        self.timer.front = QTimer()
        self.timer.form = QTimer()
        self.timer.timeout.connect(self.update_players)
        self.timer.form.timeout.connect(self.update_form)
        self.timer.front.timeout.connect(self.update_front)
        self.timer.start(100)
        self.timer.front.start(10)
        self.timer.form.start(10)
        self.timer.path = QTimer()
        self.timer.path.timeout.connect(self.update_path)
        self.timer.path.start(1000)

        cur.execute(
            "select playid from main_table where playid = (select playid from recently_viewed order by date_added desc limit 1);")
        result_main = cur.fetchone()

        cur.execute("select distinct(playerid), position from roster where playid = '" + result_main[
            0] + "' order by playerid;")
        result_distinct = cur.fetchall()
        count = 0
        data = (result[0], result[1])
        cur.execute("select logo from college_team_colors where team_name IN %s;", (data,))
        url = cur.fetchall()
        data_logo = urllib.request.urlopen(url[1][0]).read()
        image = QtGui.QImage()
        image.loadFromData(data_logo)
        image1 = image.scaled(50, 50, Qt.KeepAspectRatio)

        data_logo_2 = urllib.request.urlopen(url[0][0]).read()
        image_away = QtGui.QImage()
        image_away.loadFromData(data_logo_2)
        image_away1 = image_away.scaled(50, 50, Qt.KeepAspectRatio)

        self.labels = []
        self.edits = []

        for x in range(12):
            for y in range(2):
                try:
                    offense = ["SKILL", "QB", "RB", "WR", "RT", "LG", "C", "LT", "RT", "TE", "X", "Y", "Z", "H", "F",
                               "None"]
                    z = result_distinct[0 + count]
                    if z[1] in offense:
                        self.offframe = QFrame()
                        self.offframe.setObjectName(result[0].replace(" ", ""))
                        oline = ["RT", "LG", "C", "LT", "RT", "TE"]
                        image_vert_layout = QVBoxLayout()
                        image_vert_layout.setContentsMargins(0, 15, 0, 15)
                        self.image_hori_layout = QHBoxLayout()
                        self.pictureform = QFormLayout(self.offframe)

                        # left vertical
                        route_pic = QLabel()
                        route_pic.setPixmap(QPixmap(image1))
                        self.path_pic = LabelClass("")
                        self.path_pic.style().unpolish(self.path_pic)
                        self.path_pic.style().polish(self.path_pic)
                        self.path_pic.setPixmap(QPixmap('images/paths/slant.png'))

                        self.name_label = LabelClass("Last, First #" + str(z[0]) + ", " + z[1])
                        self.name_label.setObjectName(result[0].replace(" ", "") + "offname")
                        self.pictureform.addRow(self.name_label)
                        self.name_label.setAlignment(Qt.AlignHCenter)
                        self.playerid_label = QLabel("Player Id:")
                        self.playerid_label.setObjectName(result[0].replace(" ", "") + "offlabel")
                        self.playerid = QLabel(str(z[0]))
                        self.playerid.setObjectName(result[0].replace(" ", "") + "offquestions")
                        self.labels.append(self.name_label)
                        self.pictureform.addRow(self.playerid_label, self.playerid)
                        formation_label = QLabel("Formation:")
                        formation_label.setObjectName(result[0].replace(" ", "") + "offlabel")
                        self.formation = EditClass()
                        self.formation.setObjectName(result[0].replace(" ", "") + "offquestions")
                        self.pictureform.addRow(formation_label, self.formation)
                        play_label = QLabel("Play:")
                        play_label.setObjectName(result[0].replace(" ", "") + "offlabel")
                        self.play = EditClass()
                        self.play.setObjectName(result[0].replace(" ", "") + "offquestions")
                        self.pictureform.addRow(play_label, self.play)
                        player = QComboBox()
                        player.setObjectName(result[0].replace(" ", "") + "offCombo")
                        if z[1] in oline:
                            player.addItems(
                                ["slide left", "slide right", "man", "block", "pull", "block left", "block right"])
                        else:
                            player.addItems(
                                ["slant", "post", "wheel", "dig", "drag", "out", "in", "whip", "jerk", "bubble",
                                 "swing", "comeback", "curl", "hitch", "fade", "check release", "seam",
                                 "corner", "block"])
                        grade_label = QLabel("Grade")
                        grade_label.setObjectName(result[0].replace(" ", "") + "offlabel")
                        grade = QComboBox()
                        path_label = QLabel("Path:")
                        path_label.setObjectName(result[0].replace(" ", "") + "offlabel")
                        self.pictureform.addRow(path_label, player)
                        grade.addItems(["10", "9", "8", "7", "6", "5", "4", "3", "2", "1"])
                        grade.setObjectName(result[0].replace(" ", "") + "offCombo")
                        self.pictureform.addRow(grade_label, grade)

                        self.edits.append(tuple((self.formation, self.play, "offense", player, self.path_pic)))

                        # main
                        self.image_hori_layout.addLayout(image_vert_layout)
                        self.image_hori_layout.addWidget(self.offframe)
                        # left Vert
                        image_vert_layout.addWidget(route_pic)
                        image_vert_layout.addWidget(self.path_pic)
                        # rightform
                        self.addLayout(self.image_hori_layout, x, y)
                        count += 1
                    else:
                        self.defframe = QFrame()
                        self.defframe.setObjectName(result[1].replace(" ", ""))
                        image_vert_layout = QVBoxLayout()
                        image_vert_layout.setContentsMargins(0, 15, 0, 15)
                        self.image_hori_layout = QHBoxLayout()
                        self.pictureform = QFormLayout(self.defframe)

                        # left vertical
                        route_pic = QLabel()
                        route_pic.setPixmap(QPixmap(image_away1))
                        self.path_def_pic = QLabel()
                        self.path_def_pic.style().unpolish(self.path_def_pic)
                        self.path_def_pic.style().polish(self.path_def_pic)
                        self.path_def_pic.setPixmap(QPixmap('images/paths/spot.png'))

                        self.name_label = LabelClass("Last, First #" + str(z[0]) + ", " + z[1])
                        self.name_label.setObjectName(result[1].replace(" ", "") + "defname")
                        self.pictureform.addRow(self.name_label)
                        self.name_label.setAlignment(Qt.AlignHCenter)
                        self.playerid_label = QLabel("Player Id:")
                        self.playerid_label.setObjectName(result[1].replace(" ", "") + "deflabel")
                        self.playerid = QLabel(str(z[0]))
                        self.playerid.setObjectName(result[1].replace(" ", "") + "defquestions")
                        self.pictureform.addRow(self.playerid_label, self.playerid)
                        formation_label = QLabel("Front:")
                        formation_label.setObjectName(result[1].replace(" ", "") + "deflabel")
                        self.front = EditClass()
                        self.front.setObjectName(result[1].replace(" ", "") + "defquestions")
                        self.pictureform.addRow(formation_label, self.front)
                        play_label = QLabel("Play:")
                        play_label.setObjectName(result[1].replace(" ", "") + "deflabel")
                        self.defplay = EditClass()
                        self.defplay.setObjectName(result[1].replace(" ", "") + "defquestions")
                        self.pictureform.addRow(play_label, self.defplay)
                        player = QComboBox()
                        player.setObjectName(result[1].replace(" ", "") + "defcombo")
                        player.addItems(
                            ["1/4 seam flat", "1/4 hook", "1/4 mid hole", "1/2 hole", "1/2 curl", "1/2 flat",
                             "1/3 deep",
                             "1/3 hook", "1/3 flat", "blitz", "stunt left", "stunt right", "twist"])
                        path_label = QLabel("Path:")
                        path_label.setObjectName(result[1].replace(" ", "") + "deflabel")
                        self.pictureform.addRow(path_label, player)
                        grade_label = QLabel("Grade")
                        grade_label.setObjectName(result[1].replace(" ", "") + "deflabel")
                        grade = QComboBox()
                        grade.addItems(["10", "9", "8", "7", "6", "5", "4", "3", "2", "1"])
                        grade.setObjectName(result[1].replace(" ", "") + "defcombo")
                        self.pictureform.addRow(grade_label, grade)

                        self.edits.append(tuple((self.front, self.defplay, "defense", player, self.path_def_pic)))

                        # main
                        self.image_hori_layout.addLayout(image_vert_layout)
                        self.image_hori_layout.addWidget(self.defframe)

                        # left Vert
                        image_vert_layout.addWidget(route_pic)
                        image_vert_layout.addWidget(self.path_def_pic)
                        # rightform

                        self.addLayout(self.image_hori_layout, x, y)
                        count += 1

                except:
                    continue

    def startTimer(self, interval: int, timerType: Qt.TimerType = ...) -> int:
        self.timer.start()

    def stopTimer(self, interval: int, timerType: Qt.TimerType = ...) -> int:
        self.timer.form.stop()

    def update_path(self):
        for i in range(self.count()):
            if self.edits[i][2] == "defense":
                spot = (["1/4 seam flat", "1/4 hook", "1/4 mid hole", "1/2 curl", "1/2 flat",  "1/3 hook", "1/3 flat"])
                deep = (["1/4 deep", "1/3 deep"])
                line = (["blitz", "stunt left", "stunt right", "twist"])
                if self.edits[i][3].currentText() in spot:
                    self.edits[i][4].setPixmap(QPixmap('images/paths/spot.png'))
                elif self.edits[i][3].currentText() in deep:
                    self.edits[i][4].setPixmap(QPixmap('images/paths/deep.png'))
                elif self.edits[i][3].currentText() in line:
                    if self.edits[i][3].currentText() == "blitz":
                        self.edits[i][4].setPixmap(QPixmap('images/paths/fire.png').transformed(QtGui.QTransform().rotate(45)))
                    elif self.edits[i][3].currentText() == "slant right":
                        self.edits[i][4].setPixmap(QPixmap('images/paths/blitz.png'))
                    elif self.edits[i][3].currentText() == "slant left":
                        img = cv2.imread('images/paths/blitz.png')
                        img_flip_lr = cv2.flip(img, 1)
                        height, width, channel = img_flip_lr.shape
                        bytesPerLine = 3 * width
                        qImg = QImage(img_flip_lr.data, width, height, bytesPerLine, QImage.Format_RGB888)
                        self.edits[i][4].setPixmap(QPixmap(qImg))
                    elif self.edits[i][3].currentText() == "twist":
                        self.edits[i][4].setPixmap(QPixmap('images/paths/loop.png'))

            else:
                if self.edits[i][3].currentText() == "slant" or self.edits[i][3].currentText() == "post" or self.edits[i][3].currentText() == "corner":
                    self.edits[i][4].setPixmap(QPixmap('images/paths/slant.png'))
                elif self.edits[i][3].currentText() == "wheel":
                    self.edits[i][4].setPixmap(QPixmap('images/paths/wheel.png'))
                elif self.edits[i][3].currentText() == "dig" or self.edits[i][3].currentText() == "in" or self.edits[i][3].currentText() == "out":
                    self.edits[i][4].setPixmap(QPixmap('images/paths/dig.png'))
                elif self.edits[i][3].currentText() == "drag":
                    self.edits[i][4].setPixmap(QPixmap('images/paths/dig.png'))
                elif self.edits[i][3].currentText() == "whip":
                    self.edits[i][4].setPixmap(QPixmap('images/paths/whip.png'))
                elif self.edits[i][3].currentText() == "jerk":
                    self.edits[i][4].setPixmap(QPixmap('images/paths/jerk.png'))
                elif self.edits[i][3].currentText() == "bubble" or self.edits[i][3].currentText() == "swing":
                    self.edits[i][4].setPixmap(QPixmap('images/paths/bubble.png'))
                elif self.edits[i][3].currentText() == "comeback" or self.edits[i][3].currentText() == "curl" or self.edits[i][3].currentText() == "hitch":
                    self.edits[i][4].setPixmap(QPixmap('images/paths/comeback.png'))
                elif self.edits[i][3].currentText() == "check release":
                    self.edits[i][4].setPixmap(QPixmap('images/paths/check.png'))
                elif self.edits[i][3].currentText() == "slide left" or self.edits[i][3].currentText() == "slide right":
                    if self.edits[i][3].currentText() == "slide right":
                        img = cv2.imread('images/paths/slideleft.png')
                        img_flip_lr = cv2.flip(img, 1)
                        height, width, channel = img_flip_lr.shape
                        bytesPerLine = 3 * width
                        qImg = QImage(img_flip_lr.data, width, height, bytesPerLine, QImage.Format_RGB888)
                        self.edits[i][4].setPixmap(QPixmap(qImg))
                    else:
                        self.edits[i][4].setPixmap(QPixmap('images/paths/slideleft.png'))
                elif self.edits[i][3].currentText() == "man" or self.edits[i][3].currentText() == "block" or self.edits[i][3].currentText() == "block right" or self.edits[i][3].currentText() == "block left":
                    if self.edits[i][3].currentText() == "block right":
                        self.edits[i][4].setPixmap(QPixmap('images/paths/block.png'))
                    elif self.edits[i][3].currentText() == "block left":
                        self.edits[i][4].setPixmap(QPixmap('images/paths/block.png').transformed(QtGui.QTransform().rotate(-45)))
                    elif self.edits[i][3].currentText() == "block" or self.edits[i][3].currentText() == "man":
                        if self.edits[i][3].currentText() == "block":
                            self.edits[i][4].setPixmap(QPixmap('images/paths/man.png').transformed(QtGui.QTransform().rotate(180)))
                        else:
                            self.edits[i][4].setPixmap(QPixmap('images/paths/man.png'))
                elif self.edits[i][3].currentText() == "pull":
                    self.edits[i][4].setPixmap(QPixmap('images/paths/pull.png'))
                elif self.edit[i][3].currentText() == "fade":
                    self.edits[i][4].setPixmap(QPixmap('images/paths/fade.png'))
                elif self.edit[i][3].currentText() == "seam":
                    self.edits[i][4].setPixmap(QPixmap('images/paths/seam.png'))


    def update_players(self):
        for i_widget in range(self.count()):
            if len(tableitems) > 0:
                if i_widget == int(tableitems[0][7]):
                    self.name_label = self.labels[i_widget]
                    self.name_label.name_label_class.clear()
                    self.name_label.setText(
                        tableitems[0][0].text() + ", " + tableitems[0][1].text() + " #" + tableitems[0][
                            2].text() + " " + tableitems[0][3].text())

    def update_front(self):
        try:
            for a in range(0, 100):
                self.front = self.edits[a][0]
                self.defplay = self.edits[a][1]
                for i in range(0, 100):
                    if self.edits[a][2] == "defense":
                        if self.edits[i][2] == "offense":
                            pass
                        else:
                            self.frontdef = self.edits[i][0]
                            self.frontdef.setText(self.front.text())
                            self.defplays = self.edits[i][1]
                            self.defplays.setText(self.defplay.text())
                return
            return
        except:
            pass

    def update_form(self):
        try:
            for a in range(0, 100):
                self.form = self.edits[a][0]
                self.play = self.edits[a][1]
                for i in range(0, 100):
                    if self.edits[a][2] == self.edits[i][2]:
                        self.formation = self.edits[i][0]
                        self.formation.setText(self.form.text())
                        self.plays = self.edits[i][1]
                        self.plays.setText(self.play.text())
                    else:
                        pass
                return
            return
        except:
            pass

    def keyPressedEvent(self, event):
        if event.key() == QtCore.Qt.Key_Backspace:
            self.formation.clear()
            self.play.clear()
            self.front.clear()
            self.defplay.clear()


class PhotoViewer(QGraphicsView):
    photoClicked = pyqtSignal(QPoint)

    def __init__(self):
        super(PhotoViewer, self).__init__()
        self._zoom = 0
        self._empty = True
        self._scene = QGraphicsScene(self)
        self._photo = QGraphicsPixmapItem()
        self._scene.addItem(self._photo)
        self.setScene(self._scene)
        self.setFixedWidth(1200)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setBackgroundBrush(QBrush(QColor(30, 30, 30)))
        self.setFrameShape(QFrame.NoFrame)

    def hasPhoto(self):
        return not self._empty

    def fitInView(self, scale=True, **kwargs):
        rect = QRectF(self._photo.pixmap().rect())
        if not rect.isNull():
            self.setSceneRect(rect)
            if self.hasPhoto():
                unity = self.transform().mapRect(QRectF(0, 0, 1, 1))
                self.scale(1 / unity.width(), 1 / unity.height())
                viewrect = self.viewport().rect()
                scenerect = self.transform().mapRect(rect)
                factor = min(viewrect.width() / scenerect.width(),
                             viewrect.height() / scenerect.height())
                self.scale(factor, factor)
            self._zoom = 0

    def setPhoto(self, pixmap=None):
        self._zoom = 0
        if pixmap and not pixmap.isNull():
            self._empty = False
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            self._photo.setPixmap(pixmap)
        else:
            self._empty = True
            self.setDragMode(QGraphicsView.NoDrag)
            self._photo.setPixmap(QPixmap())
        self.fitInView()

    def wheelEvent(self, event):
        if self.hasPhoto():
            if event.angleDelta().y() > 0:
                factor = 1.25
                self._zoom += 1
            else:
                factor = 0.8
                self._zoom -= 1
            if self._zoom > 0:
                self.scale(factor, factor)
            elif self._zoom == 0:
                self.fitInView()
            else:
                self._zoom = 0

    def toggleDragMode(self):
        if self.dragMode() == QGraphicsView.ScrollHandDrag:
            self.setDragMode(QGraphicsView.NoDrag)
        elif not self._photo.pixmap().isNull():
            self.setDragMode(QGraphicsView.ScrollHandDrag)

    def mousePressEvent(self, event):
        if self._photo.isUnderMouse():
            self.photoClicked.emit(self.mapToScene(event.pos()).toPoint())
        super(PhotoViewer, self).mousePressEvent(event)


class roster_recent(QTableView):
    def __init__(self):
        super().__init__()
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setDragDropOverwriteMode(True)
        self.item = None
        self.id = None
        self.id_row = None

    # Override this method to get the correct row index for insertion
    def dropEvent(self, event):
        tableitems.clear()
        # Default dropEvent method fires dropMimeData with appropriate parameters (we're interested in the row index).
        super().dropEvent(event)
        # Now we know where to insert selected row(s)
        md = event.mimeData()
        fmt = "application/x-qabstractitemmodeldatalist"
        if md.hasFormat(fmt):
            encoded = md.data(fmt)
            stream = QDataStream(encoded, QIODevice.ReadOnly)
            table_items = []
            while not stream.atEnd():
                # row and column where it comes from
                row = stream.readInt32()
                column = stream.readInt32()
                map_items = stream.readInt32()
                it = QTableWidgetItem()

                for i in range(map_items):
                    role = stream.readInt32()
                    value = QVariant()
                    stream >> value
                    it.setData(role, value)
                table_items.append(it)

            index = self.indexAt(event.pos())

            sender = event.source()
            if sender == self:
                if index.isValid():
                    for column_number, data in enumerate(recent_roster_keys):
                        if data == "playerid":
                            self.id = self.model().index(index.row(), 0).data()
                            self.id_row = index.row()
                        else:
                            self.item = QStandardItem(str(table_items[column_number].text()))
                            self.item.setTextAlignment(Qt.AlignCenter)
                            self.model().setItem(index.row(), column_number, self.item)
                        table_items.append(self.id)
                        self.set_items(table_items)
            else:
                if index.isValid():
                    for column_number, data in enumerate(recent_roster_keys):
                        if data == "playerid":
                            self.id = self.model().index(index.row(), 0).data()
                            self.id_row = index.row()
                        else:
                            self.item = QStandardItem(str(table_items[column_number - 1].text()))
                            self.item.setTextAlignment(Qt.AlignCenter)
                            self.model().setItem(index.row(), column_number, self.item)
                        table_items.append(self.id)
                    tableitems.append(table_items)
        event.accept()

    def keyPressEvent(self, event):
        if event.key() == (Qt.Key_Control and Qt.Key_Z):
            for i in range(0, 50):
                if self.id == str(i):
                    cur.execute(
                        "select playid from main_table where playid = (select playid from recently_viewed order by date_added desc limit 1);")
                    result = cur.fetchone()
                    cur.execute(
                        "select playerid, last_name, first_name, jersey, position, height, weight, year from roster where playid = '" +
                        result[0] + "' and playerid = %s;", (i,))
                    play_table_result = cur.fetchall()
                    for column_number in range(0, 7):
                        self.item = QStandardItem(str(play_table_result[0][column_number]))
                        self.item.setTextAlignment(Qt.AlignCenter)
                        self.model().setItem(self.id_row, column_number, self.item)


class home_table(QTableView):

    def __init__(self):
        super(home_table, self).__init__()
        self.setDragEnabled(True)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)

    def dropEvent(self, e):
        position = e.pos()
        QStandardItem.move(position)
        e.setDropAction(Qt.MoveAction)
        e.accept()

    def dragMoveEvent(self, e):
        e.accept()


class away_table(QTableView):
    def __init__(self):
        super(away_table, self).__init__()
        self.setDragEnabled(True)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)

    def dropEvent(self, e):
        position = e.pos()
        QStandardItem.move(position)
        e.setDropAction(Qt.MoveAction)
        e.accept()

    def dragMoveEvent(self, e):
        e.accept()


class SortFilterProxyModel(QSortFilterProxyModel):
    def __init__(self, *args, **kwargs):
        QSortFilterProxyModel.__init__(self, *args, **kwargs)
        self.filters = {}

    def setFilterByColumn(self, regex, column):
        self.filters[column] = regex
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row, source_parent):
        for key, regex in self.filters.items():
            ix = self.sourceModel().index(source_row, key, source_parent)
            if ix.isValid():
                text = self.sourceModel().data(ix).toString()
                if not text.contains(regex):
                    return False
        return True


def end_page():
    app = QApplication(sys.argv)
    QFontDatabase().addApplicationFont("fonts/proxima.ttf")
    window = Window()
    window.set_light_dark_mode()
    window.update_play_table()
    window.update_roster_table()
    sys.exit(app.exec_())


if __name__ == '__main__':
    end_page()
