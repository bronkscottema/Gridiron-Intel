from urllib.request import urlopen
from PyQt5.QtWidgets import *
import all
import os
import sys

import end
from collegeFBTeams import *
from collegeFBGames import *
from end import *
from getNFLGames import *
from Roster import *
from psycopg2 import connect
from qtwidgets import AnimatedToggle
from dotenv import load_dotenv

load_dotenv()
# prod
# conn = connect(dbname="footballiq", host="52.91.161.249", user="postgres", password="F00tball")
# testing
conn = connect(dbname=os.getenv('DATABASE_NAME'), host=os.getenv('DATABASE_HOST'), user=os.getenv('DATABASE_USER'), password=os.getenv('DATABASE_PASSWORD'))
conn.autocommit = True
cur = conn.cursor()
images = []
collegeheaders = ["Game Id", "Play Id", "Play Number", "Offense", "Defense", "Quarter", "Clock", "Down", "Distance", "Yard Line", "Play Type", "Play Text"]
keys = ["game_id", "id", "play_number", "offense", "defense", "period", "clock", "down", "distance", "yard_line",
        "play_type", "play_text"]
nflheaders = ["Id", "Play Type", "Away Score", "Home Score", "Quarter", "Clock", "Down", "Distance", "Yard Line", "Play Text"]
nflkeys = ["id", "type", "awayScore", "homeScore", "period", "clock", "start", "shortText"]


def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon(self.resource_path('images/favicon.ico')))
        self.ok_btn = QPushButton("Submit")

        self.toggle_2 = AnimatedToggle(
            checked_color="#4400B0EE",
            pulse_checked_color="#4400B0EE"
        )
        self.toggle_2.setStyleSheet("max-width: 75px;")
        self.toggle_2.setObjectName("toggle")
        self.toggle_2.clicked.connect(self.set_light_dark_mode)

        self.offense_left_or_right_label = QLabel("Is the offense going from Left to Right on Screen?")
        self.offense_left_or_right_label.setWordWrap(True)
        self.offense_left_or_right_label.setObjectName("questions")
        self.offense_left_or_right = QComboBox(self)

        self.hashmark_number_label = QLabel("Hashmarks of Numbers?")
        self.hashmark_number_label.setWordWrap(True)
        self.hashmark_number_label.setObjectName("questions")
        self.hashmark_number = QComboBox(self)

        self.opponent_label = QLabel("Who is the opponent?")
        self.opponent_label.setObjectName("questions")
        self.opponent_label.setWordWrap(True)
        self.opponent = QComboBox(self)

        self.regular_post_label = QLabel("Was it regular season or postseason?")
        self.regular_post_label.setWordWrap(True)
        self.regular_post_label.setObjectName("questions")
        self.regular_post = QComboBox(self)

        self.offense_label = QLabel("Which team is on offense?")
        self.offense_label.setObjectName("questions")
        self.offense_label.setWordWrap(True)
        self.offense = QComboBox(self)

        self.year_label = QLabel("Which Year was the game?")
        self.year_label.setWordWrap(True)
        self.year_label.setObjectName("questions")
        self.year = QComboBox(self)

        self.leaque_label = QLabel("Which League?")
        self.leaque_label.setWordWrap(True)
        self.leaque_label.setObjectName("questions")
        self.league = QComboBox(self)

        self.value = 0
        self.timer = QTimer()
        self.league_pic = QLabel(self)
        self.league_pic.style().unpolish(self.league_pic)
        self.league_pic.style().polish(self.league_pic)
        self.setGeometry(0, 0, 1920, 1080)
        self.setWindowTitle("Audible Analytics")
        self.table_font = QFont("proxima", 12)
        self.font = QFont("proxima", 18)
        self.offense.setStyleSheet('QLineEdit {background-color:white}')

        self.ui()

    def ui(self):
        #layout section
        main_layout = QVBoxLayout()
        top_layout = QHBoxLayout()
        toggle_layout = QVBoxLayout()
        top_left_layout = QVBoxLayout()
        top_right_layout = QFormLayout()
        middle_layout = QHBoxLayout()
        main_layout.addLayout(top_layout)
        top_layout.addLayout(toggle_layout)
        top_layout.addLayout(top_left_layout)
        top_layout.addLayout(top_right_layout)
        top_layout.insertWidget(10, self.toggle_2, 0, alignment=Qt.AlignTop)
        main_layout.addLayout(middle_layout)

        # top Left
        self.league_pic.setPixmap(QPixmap(self.resource_path('images/ncaa.png')))
        self.league_pic.setMaximumSize(500, 500)
        top_left_layout.addWidget(self.league_pic)
        top_left_layout.setAlignment(Qt.AlignCenter)

        # Timer for images
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.change_image)

        # top Right
        # league question
        top_right_layout.addRow(self.leaque_label, self.league)
        self.league.addItems(["NCAA", "NFL"])
        self.league.currentIndexChanged.connect(self.league_change)

        # year question
        self.year.addItems(["2022", "2021", "2020", "2019", "2018", "2017", "2016", "2015",
                            "2014", "2013", "2012", "2011", "2010", "2009"])
        top_right_layout.addRow(self.year_label, self.year)

        self.offense.addItems(getTeam())
        self.offense.currentIndexChanged.connect(self.start)
        self.offense.currentIndexChanged.connect(self.set_light_dark_mode)
        top_right_layout.addRow(self.offense_label, self.offense)

        self.regular_post.addItems(["regular", "postseason"])
        top_right_layout.addRow(self.regular_post_label, self.regular_post)

        self.opponent.addItems(getOpponent(self.year.currentText(), self.regular_post.currentText(), self.offense.currentText()))
        top_right_layout.addRow(self.opponent_label, self.opponent)

        self.hashmark_number.addItems(["Hashmark", "Numbers"])
        top_right_layout.addRow(self.hashmark_number_label, self.hashmark_number)

        self.offense_left_or_right.addItems(["Offense Left", "Offense Right"])
        top_right_layout.addRow(self.offense_left_or_right_label, self.offense_left_or_right)
        top_right_layout.setAlignment(Qt.AlignCenter)

        # update calls
        self.year.currentIndexChanged.connect(self.update_opponent)
        self.regular_post.currentIndexChanged.connect(self.update_opponent)
        self.offense.currentIndexChanged.connect(self.update_opponent)
        self.league.currentIndexChanged.connect(self.update_opponent)
        self.year.currentIndexChanged.connect(self.update_table)
        self.regular_post.currentIndexChanged.connect(self.update_table)
        self.league.currentIndexChanged.connect(self.update_table)
        self.opponent.currentIndexChanged.connect(self.update_table)

        # middle widget Table
        self.api_table = QTableWidget(0,len(keys))
        self.header = self.api_table.horizontalHeader()
        self.api_table.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)
        self.api_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.api_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.api_table.horizontalHeader().setFont(self.table_font)
        self.api_table.setAlternatingRowColors(True)
        self.api_table.verticalHeader().setVisible(False)
        self.header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.header.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        self.header.setSectionResizeMode(7, QHeaderView.ResizeToContents)
        self.header.setSectionResizeMode(8, QHeaderView.ResizeToContents)
        self.header.setSectionResizeMode(9, QHeaderView.ResizeToContents)
        self.header.setSectionResizeMode(10, QHeaderView.ResizeToContents)
        self.header.setSectionResizeMode(11, QHeaderView.Stretch)
        self.api_table.clicked.connect(self.set_submit_button)
        middle_layout.addWidget(self.api_table)
        self.setLayout(main_layout)

        self.ok_btn.setFont(self.font)
        self.ok_btn.setVisible(False)
        self.ok_btn.setObjectName("push")
        top_right_layout.addWidget(self.ok_btn)
        self.ok_btn.clicked.connect(self.submit_pushed)
        top_right_layout.setContentsMargins(200, 75, 200, 0)
        self.show()

    def update_table(self, ix):
        self.api_table.setRowCount(0)
        self.api_table.setSortingEnabled(False)

        if self.league.currentText() == 'NFL':
            self.api_table.setColumnCount(len(nflheaders))
            self.week = getNFLWeek(yearOf=self.year.currentText(), teamName=self.offense.currentText(), opponent=self.opponent.currentText())
            result = getNFLGameData(self.offense.currentText(), self.year.currentText(), self.opponent.currentText())
            try:
                self.api_table.setHorizontalHeaderLabels(nflheaders)
                for n, key in enumerate(result):
                    self.api_table.insertRow(n)
                    for column_number, data in enumerate(nflkeys):
                        if data == "type":
                            item = QTableWidgetItem(str(key[data]['text']))
                            item.setTextAlignment(4)
                            item.setFont(self.table_font)
                            self.api_table.setItem(n, column_number, item)
                        elif data == "period":
                            item = QTableWidgetItem(str(key[data]['number']))
                            item.setTextAlignment(4)
                            item.setFont(self.table_font)
                            self.api_table.setItem(n, column_number, item)

                        elif data == "clock":
                            item = QTableWidgetItem(str(key[data]['displayValue']))
                            item.setTextAlignment(4)
                            item.setFont(self.table_font)
                            self.api_table.setItem(n, column_number, item)

                        elif data == "start":
                            item = QTableWidgetItem(str(key[data]['down']))
                            item.setTextAlignment(4)
                            item.setFont(self.table_font)
                            self.api_table.setItem(n, column_number, item)
                            item2 = QTableWidgetItem(str(key[data]['distance']))
                            item2.setTextAlignment(4)
                            item2.setFont(self.table_font)
                            self.api_table.setItem(n, column_number+1, item2)
                            item3 = QTableWidgetItem(str(key[data]['yardLine']))
                            item3.setTextAlignment(4)
                            item3.setFont(self.table_font)
                            self.api_table.setItem(n, column_number+2, item3)
                        elif data == "shortText":
                            item = QTableWidgetItem(str(key[data]))
                            item.setTextAlignment(4)
                            item.setFont(self.table_font)
                            self.api_table.setItem(n, column_number+2, item)
                        else:
                            item = QTableWidgetItem(str(key[data]))
                            item.setTextAlignment(4)
                            item.setFont(self.table_font)
                            self.api_table.setItem(n, column_number, item)
            except:
                pass
        else:
            self.api_table.setColumnCount(len(keys))
            self.header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
            self.header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
            self.header.setSectionResizeMode(6, QHeaderView.ResizeToContents)
            self.header.setSectionResizeMode(7, QHeaderView.ResizeToContents)
            self.header.setSectionResizeMode(8, QHeaderView.ResizeToContents)
            self.header.setSectionResizeMode(9, QHeaderView.ResizeToContents)
            self.header.setSectionResizeMode(10, QHeaderView.ResizeToContents)
            self.header.setSectionResizeMode(11, QHeaderView.Stretch)

            try:
                self.week = getWeek(yearOf=self.year.currentText(), regOrPost=self.regular_post.currentText(),
                               teamName=self.offense.currentText(), opponent=self.opponent.currentText())
                result = getGameData(year=int(self.year.currentText()), team=self.offense.currentText(),
                                     opponent=self.opponent.currentText(), regOrPost=self.regular_post.currentText(),
                                     week=int(self.week[0]))
                self.api_table.setHorizontalHeaderLabels(collegeheaders)
                for n, key in enumerate(result):
                    self.api_table.insertRow(n)
                    for column_number, data in enumerate(keys):
                        item = QTableWidgetItem(str(key.__getattribute__(data)))
                        if data == 'clock':
                            item1 = str(key.__getattribute__(data).__getattribute__("minutes")) + ":" + str(
                                key.__getattribute__(data).__getattribute__("seconds"))
                            item = QTableWidgetItem(str(item1))
                            item.setTextAlignment(4)
                            item.setFont(self.table_font)
                            self.api_table.setItem(n, column_number, item)
                        else:
                            item.setTextAlignment(4)
                            item.setFont(self.table_font)
                            self.api_table.setItem(n, column_number, item)
            except:
                pass

    def set_submit_button(self):
        self.current_row = self.api_table.currentRow()
        if self.league.currentText() == 'NFL':
            self.gameid_value = self.api_table.item(self.current_row, 0).text()[0:8]
            self.playid_value = self.api_table.item(self.current_row, 0).text()
            self.yard_value = self.api_table.item(self.current_row, 7).text()
            self.play_text = self.api_table.item(self.current_row, 9).text()
            self.ok_btn.setVisible(True)
        else:
            self.gameid_value = self.api_table.item(self.current_row, 0).text()
            self.playid_value = self.api_table.item(self.current_row, 1).text()
            self.yard_value = self.api_table.item(self.current_row, 9).text()
            self.play_text = self.api_table.item(self.current_row, 11).text()
            self.ok_btn.setVisible(True)

    def submit_pushed(self):
        url = QFileDialog.getOpenFileName(self, "Open a file", "", "All Files(*);;")

        all.opencv(url[0], hash_or_num=self.hashmark_number.currentText(), gameid_number=self.gameid_value, playid_number=self.playid_value,
                   offense_l_or_r=self.offense_left_or_right.currentText(), yard_line=int(self.yard_value), offense=self.offense.currentText(),
                   defense=self.opponent.currentText(), league=self.league.currentText(), year=self.year.currentText(),
                   week=self.week[0], regular_post=self.regular_post.currentText(), play_text=self.play_text)
        self.w = end.End()
        self.w.show()

    def update_opponent(self, ix):
        if self.league.currentText() == 'NFL' and ix == 0:
            self.opponent.clear()
            self.opponent.addItems(getNFLOpponent(self.year.currentText(), self.offense.currentText()))
        elif self.league.currentText() == 'NCAA' and ix == 0:
            self.opponent.clear()
            self.opponent.addItems(
                getOpponent(self.year.currentText(), self.regular_post.currentText(), self.offense.currentText()))
        elif self.league.currentText() == 'NCAA':
            self.opponent.clear()
            self.opponent.addItems(
                getOpponent(self.year.currentText(), self.regular_post.currentText(), self.offense.currentText()))

    def league_change(self, ix):
        if self.league.currentText() == 'NCAA' and ix == 0:
            self.offense.clear()
            self.offense.addItems(getTeam())
        else:
            self.offense.clear()
            self.offense.addItems(["Arizona Cardinals", "Atlanta Falcons", "Baltimore Ravens", "Buffalo Bills",
                                   "Carolina Panthers", "Chicago Bears", "Cincinnati Bengals", "Cleveland Browns",
                                   "Dallas Cowboys", "Denver Broncos", "Detroit Lions", "Green Bay Packers",
                                   "Houston Texans", "Indianapolis Colts", "Jacksonville Jaguars", "Kansas City Chiefs",
                                   "Las Vegas Raiders", "Los Angeles Chargers", "Los Angeles Rams", "Miami Dolphins",
                                   "Minnesota Vikings", "New England Patriots", "New Orleans Saints", "New York Giants",
                                   "New York Jets", "Philadelphia Eagles", "Pittsburgh Steelers", "San Francisco 49ers",
                                   "Seattle Seahawks", "Tampa Bay Buccaneers", "Tennessee Titans",
                                   "Washington Commanders"])

    def change_image(self):
        if self.value == 0:
            if self.league.currentText() == 'NFL':
                pixmap = QPixmap(self.resource_path('images/nfl.png'))
                pixmap = pixmap.scaled(500, 500)
                self.league_pic.setPixmap(pixmap)
                self.value = 1
            else:
                pixmap = QPixmap(self.resource_path('images/ncaa.png'))
                pixmap = pixmap.scaled(500, 500)
                self.league_pic.setPixmap(pixmap)
                self.value = 1
        elif self.value == 1:
            if self.league.currentText() == 'NFL':
                cur.execute("select url from nfl_team_colors where team_name = %s;", (self.offense.currentText(),))
                url = cur.fetchone()
                data = urllib.request.urlopen(url[0]).read()
                image = QtGui.QImage()
                image.loadFromData(data)
                self.league_pic.setPixmap(QPixmap(image))
                self.value = 2
            else:
                cur.execute("select logo from college_team_colors where team_name = %s;", (self.offense.currentText(),))
                url = cur.fetchone()
                data = urllib.request.urlopen(url[0]).read()
                image = QtGui.QImage()
                image.loadFromData(data)
                self.league_pic.setPixmap(QPixmap(image))
                self.value = 2
        elif self.value == 2:
            if self.league.currentText() == 'NFL':
                if len(self.opponent.currentText()) > 0:
                    try:
                        cur.execute("select url from nfl_team_colors where team_name = %s;",
                                    (self.opponent.currentText(),))
                        url = cur.fetchone()
                        data = urllib.request.urlopen(url[0]).read()
                        image = QtGui.QImage()
                        image.loadFromData(data)
                        self.league_pic.setPixmap(QPixmap(image))
                        self.value = 0
                    except:
                        self.value = 0
            else:

                if self.opponent.currentText() == 'Lousiana Monroe':
                    cur.execute("select logo from college_team_colors where team_name = 'Louisiana Monroe';")
                    url = cur.fetchone()
                    data = urllib.request.urlopen(url[0]).read()
                    image = QtGui.QImage()
                    image.loadFromData(data)
                    self.league_pic.setPixmap(QPixmap(image))
                    self.value = 0
                else:
                    try:
                        cur.execute("select logo from college_team_colors where team_name = %s;",
                                    (self.opponent.currentText(),))
                        url = cur.fetchone()
                        data = urllib.request.urlopen(url[0]).read()
                        image = QtGui.QImage()
                        image.loadFromData(data)
                        self.league_pic.setPixmap(QPixmap(image))
                        self.value = 0
                    except:
                        pixmap = QPixmap(self.resource_path('images/fcs.png'))
                        self.league_pic.setPixmap(QPixmap(pixmap))
                        self.value = 0
                self.value = 0

    def start(self):
        self.timer.start()

    def set_light_dark_mode(self):
        if self.toggle_2.checkState() == 2:
            self.style = '''
            QWidget {
                background-color: black;
            }
            QLabel {
                color: white;
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
                font-size: 18px;
            }
            QLabel {
                color: white;
                font-family: Proxima;
                font-size: 18px;
            }
            '''
        else:
            self.style = '''
            QWidget {
                background - color: white;
            }
            QLabel {
                font-family: Proxima;
                font-size: 18px;
            }
            QComboBox {
                background-color: white;
                font-family: Proxima;
                font-size: 18px;
            }
            '''
        if self.offense.currentText() is not None:
            if self.league.currentText() == "NFL":
                team_name = self.offense.currentText()
                team_name = team_name.replace(" ", "").lower()
                # set stylesheet here and uncomment to deploy
                #eamFile = self.resource_path("styles/nfl/" + team_name + ".qss")
                teamFile = self.resource_path("styles/" + team_name + ".qss")

                with open(teamFile, "r") as self.fh:
                        self.setStyleSheet(self.fh.read() + self.style)

            else:
                team_name = self.offense.currentText()
                team_name = team_name.replace(" ", "").lower()
                # set stylesheet here and uncomment to deploy
                #teamFile = self.resource_path("styles/ncaa/" + team_name + ".qss")
                teamFile = self.resource_path("styles/" + team_name + ".qss")

                with open(teamFile, "r") as self.fh:
                        self.setStyleSheet(self.fh.read() + self.style)



    def resource_path(self, relative_path):
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, relative_path)
        return os.path.join(os.path.abspath("."), relative_path)


def main():
    app = QApplication(sys.argv)
    QFontDatabase().addApplicationFont(resource_path('fonts/proxima.ttf'))
    window = Window()
    window.start()
    window.set_light_dark_mode()
    window.update_table(0)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
