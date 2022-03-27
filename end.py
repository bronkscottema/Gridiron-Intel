from PyQt5.QtCore import Qt, QSortFilterProxyModel, QDataStream, QIODevice, QVariant, QRectF, \
    pyqtSignal, QPoint
from PyQt5.QtGui import QFont, QPixmap, QIcon, QFontDatabase, QStandardItemModel, QStandardItem, QBrush, QColor
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QApplication, QTableWidgetItem, \
    QTabWidget, QLineEdit, QTableView, QAbstractItemView, QDesktopWidget, QPushButton,  QGraphicsView, QFrame, \
    QGraphicsScene, QGraphicsPixmapItem
from psycopg2 import connect
import psycopg2.extras
from typing import Iterator, Dict, Any
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


class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.viewer = PhotoViewer(self)
        self.image_layout = QVBoxLayout()
        self.away_model = QStandardItemModel(len(team_roster), 1)
        self.away_filter_proxy_model = QSortFilterProxyModel()
        self.filter_proxy_model = QSortFilterProxyModel()
        self.home_model = QStandardItemModel(len(team_roster), 1)
        self.recently_viewed_model = QStandardItemModel(len(roster_labels), 1)
        self.refresh_button = QPushButton('Refresh', self)
        self.submit_button = QPushButton('Submit', self)
        self.search_field = QLineEdit()
        self.away_search_field = QLineEdit()
        self.tab2 = QWidget()
        self.tab1 = QWidget()
        self.tabs = QTabWidget()
        self.recently_viewed_table = roster_recent()
        self.away_roster_table = QTableView()
        self.home_roster_table = home_table()
        self.setWindowIcon(QIcon('images/favicon.ico'))
        screen = QDesktopWidget().screenGeometry()
        self.setGeometry(0, 0, screen.width(), screen.height())
        self.setWindowTitle("Audible Analytics")
        self.font = QFont("proxima", 18)
        self.table_font = QFont("proxima", 11)
        self.fieldpic = QLabel(self)
        self.play_pic = QLabel(self)
        self.ui()

    def ui(self):
        # layout section
        main_layout = QHBoxLayout()
        field_layout = QVBoxLayout()
        self.image_layout = QVBoxLayout()
        move_image_layout = QHBoxLayout()
        roster_layout = QHBoxLayout()
        game_roster_layout = QVBoxLayout()
        api_roster_layout = QVBoxLayout()

        self.fieldpic.setPixmap(QPixmap('dottedfield.jpg'))
        field_layout.addWidget(self.fieldpic)
        main_layout.addLayout(field_layout)

        self.viewer.setPhoto(QPixmap("boxes.jpg"))
        move_image_layout.addWidget(self.viewer)
        self.image_layout.addLayout(move_image_layout)
        # self.height = self.pixmap.height()

        self.image_layout.addWidget(self.play_pic)
        self.image_layout.addLayout(roster_layout)
        roster_layout.addLayout(game_roster_layout)
        roster_layout.addLayout(api_roster_layout)

        self.recently_viewed_table.setModel(self.recently_viewed_model)
        self.recently_viewed_table.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)
        self.recently_viewed_table.horizontalHeader().setFont(self.table_font)
        self.recently_viewed_table.verticalHeader().setVisible(False)
        self.recently_viewed_table.verticalHeader().setVisible(False)
        game_roster_layout.addWidget(self.recently_viewed_table)
        game_roster_layout.addWidget(self.submit_button)
        game_roster_layout.addWidget(self.refresh_button)
        self.submit_button.clicked.connect(self.submit_pushed)
        self.refresh_button.clicked.connect(self.refresh_pushed)


        # api roster data
        cur.execute(
            "select offense,defense from recently_viewed order by date_added desc limit  1;")
        result = cur.fetchall()

        self.tabs.addTab(self.tab1, result[0][0])
        self.tabs.addTab(self.tab2, result[0][1])
        self.tab1.layout = QVBoxLayout()
        self.tab2.layout = QVBoxLayout()

        # tab1/hometeam
        self.filter_proxy_model.setSourceModel(self.home_model)
        self.filter_proxy_model.setFilterKeyColumn(0)
        self.filter_proxy_model.setFilterKeyColumn(1)
        self.filter_proxy_model.setFilterKeyColumn(2)
        self.search_field.setStyleSheet('font-size: 14px; height: 30px;')
        self.search_field.textChanged.connect(self.filter_proxy_model.setFilterRegExp)
        self.home_roster_table.horizontalHeader()
        self.home_roster_table.setModel(self.filter_proxy_model)
        self.home_roster_table.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)
        self.home_roster_table.horizontalHeader().setFont(self.table_font)
        self.home_roster_table.setAlternatingRowColors(True)
        self.home_roster_table.verticalHeader().setVisible(False)

        self.tab1.layout.addWidget(self.search_field)
        self.tab1.layout.addWidget(self.home_roster_table)
        self.tab1.setLayout(self.tab1.layout)

        # tab2/awayteam
        self.away_filter_proxy_model.setSourceModel(self.away_model)
        self.away_filter_proxy_model.setFilterKeyColumn(0)
        self.away_search_field.setStyleSheet('font-size: 14px; height: 30px;')
        self.away_search_field.textChanged.connect(self.away_filter_proxy_model.setFilterRegExp)
        self.away_roster_table.horizontalHeader()
        self.away_roster_table.setModel(self.away_filter_proxy_model)
        self.away_roster_table.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)
        self.away_roster_table.horizontalHeader().setFont(self.table_font)
        self.away_roster_table.setAlternatingRowColors(True)
        self.away_roster_table.verticalHeader().setVisible(False)
        self.tab2.layout.addWidget(self.away_search_field)
        self.tab2.layout.addWidget(self.away_roster_table)
        self.tab2.setLayout(self.tab2.layout)
        api_roster_layout.addWidget(self.tabs)


        main_layout.addLayout(self.image_layout)


        self.setLayout(main_layout)
        self.show()

    def update_play_table(self):
        self.recently_viewed_table.setSortingEnabled(False)
        cur.execute(
            "select playid from main_table where playid = (select playid from recently_viewed order by date_added desc limit 1);")
        result = cur.fetchone()

        cur.execute("select * from roster where playid = '" + result[0] + "';")
        roster_exist = cur.fetchall()

        if len(roster_exist) == 0:
            cur.execute(
                "select gameid, playid, playerid, player_position from main_table where playid = '" + result[0] + "' "
                                                                                                                  "and frame = (select min(frame) from main_table where playid = '" +
                result[0] + "');")
            play_table_result = cur.fetchall()


            #TODO add logic for Dline adding and offensive line
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
                self.recently_viewed_model.setHorizontalHeaderLabels(roster_labels)
                for n, key in enumerate(play_table_result):
                    self.recently_viewed_model.insertRow(n)
                    for column_number, data in enumerate(recent_roster_keys):
                        if data == "first_name" or data == "last_name":
                            item = QStandardItem(str(" "))
                            self.recently_viewed_model.setItem(n, column_number, item)
                        elif data == "playerid":
                            item = QStandardItem(str(key[2]))
                            self.recently_viewed_model.setItem(n, column_number, item)
                        elif data == "jersey" or data == "weight" or data == "year" or data == "height":
                            item = QStandardItem(str(0))
                            self.recently_viewed_model.setItem(n, column_number, item)
                        elif data == "position":
                            item = QStandardItem(str(key[3]))
                            self.recently_viewed_model.setItem(n, column_number, item)
                        else:
                            break
            except:
                pass

        else:
            self.recently_viewed_model.clear()
            cur.execute(
                "select playerid, last_name, first_name, position, height, weight, year from roster where playid = '" +
                result[0] + "' order by playerid;")
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
                            self.recently_viewed_model.setItem(n, column_number, item)
                        elif data == "Position":
                            item = QStandardItem(str(key[3]))
                            self.recently_viewed_model.setItem(n, column_number, item)
                        else:
                            item = QStandardItem(str(key[column_number]))
                            self.recently_viewed_model.setItem(n, column_number, item)
            except:
                pass

    def update_roster_table(self):

        cur.execute(
            "select offense,defense,year,league from recently_viewed order by date_added desc limit  1;")
        result = cur.fetchall()[0]

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
        result = cur.fetchone()

        cur.execute("select min(playerid), max(playerid) from roster where playid = '" + result[0] + "';")
        min_max_playerid = cur.fetchall()[0]

        for i in range(min_max_playerid[0], min_max_playerid[1]):
            for j in enumerate(output):
                if i == j[0]:
                    cur.execute("update roster set last_name = %s, first_name = %s, number = %s,"
                                "position = %s, height = %s, weight = %s, year = %s where playerid = %s;"), \
                    (j[1], j[2], j[3], j[4], j[5], j[6], j[8], j[0])


class PhotoViewer(QGraphicsView):
    photoClicked = pyqtSignal(QPoint)

    def __init__(self, parent):
        super(PhotoViewer, self).__init__(parent)
        self._zoom = 0
        self._empty = True
        self._scene = QGraphicsScene(self)
        self._photo = QGraphicsPixmapItem()
        self._scene.addItem(self._photo)
        self.setScene(self._scene)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setBackgroundBrush(QBrush(QColor(30, 30, 30)))
        self.setFrameShape(QFrame.NoFrame)

    def hasPhoto(self):
        return not self._empty

    def fitInView(self, scale=True):
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
                            self.model().setItem(index.row(), column_number, self.item)
            else:
                if index.isValid():
                    for column_number, data in enumerate(recent_roster_keys):
                        if data == "playerid":
                            self.id = self.model().index(index.row(), 0).data()
                            self.id_row = index.row()
                        else:
                            self.item = QStandardItem(str(table_items[column_number - 1].text()))
                            self.model().setItem(index.row(), column_number, self.item)

        event.accept()

    def keyPressEvent(self, event):
        if event.key() == (Qt.Key_Control and Qt.Key_Z):
            for i in range(0, 50):
                if self.id == str(i):
                    cur.execute(
                        "select playid from main_table where playid = (select playid from recently_viewed order by date_added desc limit 1);")
                    result = cur.fetchone()
                    cur.execute(
                        "select playerid, last_name, first_name, number, position, height, weight, year from roster where playid = '" +
                        result[0] + "' and playerid = %s;", (i,))
                    play_table_result = cur.fetchall()
                    for column_number in range(0, 7):
                        self.item = QStandardItem(str(play_table_result[0][column_number]))
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


def end_page():
    app = QApplication(sys.argv)
    QFontDatabase().addApplicationFont("fonts/proxima.ttf")
    window = Window()
    window.update_play_table()
    window.update_roster_table()
    sys.exit(app.exec_())


if __name__ == '__main__':
    end_page()
