import pickle
import sys
import time

from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QIntValidator, QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import (QAction, QApplication, QCheckBox, QComboBox,
                             QGridLayout, QLabel, QLineEdit, QMainWindow,
                             QMenu, QMenuBar, QMessageBox, QPushButton,
                             QTableView, QWidget, QDialog, QProgressBar)

from douban import Movie


def readData():
    with open("./jinwu/dump.dat", "rb") as f:
        movies = pickle.load(f)
    return movies


class TimerThread(QThread):
    def __init__(self, parent=None):
        return super().__init__(parent=parent)

    def run(self):
        pass


class TableWindow(QThread):
    def __init__(self):
        super(TableWindow, self).__init__()

    def run(self):
        tableWidget = TableWidget()
        tableWidget.show()
        time.sleep(1)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.typeCombo = QComboBox(self)
        self.areaCombo = QComboBox(self)
        self.yearCombo = QComboBox(self)
        self.tip = QLabel("最大电影获取数量：", self)
        self.btn = QPushButton("开始", self)
        self.amount = QLineEdit(self)
        self.showAllDataCheck = QCheckBox("显示所有电影信息", self)
        self.spiderThread = None
        self.tableWindow = None
        self.status = self.statusBar()
        self.menu = self.menuBar()
        self.aboutWindow = None
        self.progress = None
        self.usedTimeS = 0
        self.usedTimeM = 0
        self.timeLabel = None
        self.timer = None

        self.initUI()

    def initUI(self):
        # self.setGeometry(1000, 100, 500, 200)
        gridLayout = QGridLayout()
        widget = QWidget()
        self.setWindowTitle("Test Window")
        self.setCentralWidget(widget)
        self.resize(400, 300)
        types = ["全部类型", "剧情", "喜剧", "动作", "爱情", "科幻", "动画", "悬疑",
                 "惊悚", "恐怖", "犯罪", "同性", "音乐", "歌舞", "传记",
                 "历史", "战争", "西部", "奇幻", "冒险", "灾难", "武侠"]
        areas = ["全部地区", "中国大陆", "美国", "香港", "台湾", "日本", "韩国", "英国",
                 "法国", "德国", "意大利", "西班牙", "印度", "泰国", "俄罗斯",
                 "伊朗", "加拿大", "澳大利亚", "爱尔兰", "瑞典", "巴西", "丹麦"]
        years = ["全部年代", "2019", "2018", "2010年代", "2000年代", "90年代",
                 "80年代", "70年代", "60年代", "更早"]

        self.typeCombo.addItems(types)
        self.areaCombo.addItems(areas)
        self.yearCombo.addItems(years)
        self.btn.setToolTip("点击开始爬取")
        self.tip.setAlignment(Qt.AlignRight)

        advanced = self.menu.addMenu("高级")
        concurrent = advanced.addAction("并发")
        concurrent.setCheckable(True)
        concurrent.triggered.connect(self.concurrentCheck)
        help = self.menu.addMenu("帮助")
        help.addAction("关于")
        help.triggered[QAction].connect(self.about)

        intOnly = QIntValidator()
        intOnly.setRange(0, 999)
        self.amount.setValidator(intOnly)
        self.amount.setPlaceholderText("0~999(0:不限制)")
        self.amount.setMaxLength(3)
        self.amount.setMaximumWidth(120)
        self.showAllDataCheck.setCheckState(Qt.Checked)
        self.btn.clicked.connect(self.btnClicked)
        self.amount.returnPressed.connect(lambda: self.btn.clicked.emit())

        gridLayout.addWidget(self.typeCombo, 1, 1)
        gridLayout.addWidget(self.areaCombo, 1, 2)
        gridLayout.addWidget(self.yearCombo, 1, 3)
        gridLayout.addWidget(self.tip, 2, 1)
        gridLayout.addWidget(self.amount, 2, 2)
        gridLayout.addWidget(self.showAllDataCheck, 2, 3)
        gridLayout.addWidget(self.btn, 3, 2)
        self.status.messageChanged.connect(self.status.showMessage)
        self.status.messageChanged.emit("Ready!")
        self.centralWidget().setLayout(gridLayout)

        # self.progress = QProgressBar(self)
        # self.status.addPermanentWidget(self.progress, stretch=0)
        self.timeLabel = QLabel("已用时：" + str(self.usedTimeS) + "秒")
        self.status.addPermanentWidget(self.timeLabel)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateUsedTime)

    def updateUsedTime(self):
        self.usedTimeS += 1
        if self.usedTimeS >= 60:
            self.usedTimeM += 1
            self.usedTimeS = 0
        if self.usedTimeM == 0:
            self.timeLabel.setText("已用时：" + str(self.usedTimeS) + " 秒")
        else:
            self.timeLabel.setText("已用时：" + str(self.usedTimeM) + " 分 " +
                                   str(self.usedTimeS) + " 秒")

    def btnClicked(self):
        # moviesList = readData()
        # self.moviesTable(moviesList)
        # self.tableThread = TableWindow()
        # self.tableThread.start()

        if not self.showAllDataCheck.isChecked():
            self.tableWindow = TableWidget()
            self.tableWindow.show()
        self.status.showMessage("正在获取电影详细信息：（200/200）")
        self.usedTimeM = 0
        self.usedTimeS = 0
        self.timer.start(1000)
        self.showAllDataCheck.setCheckable(False)

    def about(self, qAction):
        self.aboutWindow = About()
        self.aboutWindow.setModal(True)
        self.aboutWindow.show()

    def concurrentCheck(self, check):
        QMessageBox.information(self, "title", str(check))


class TableWidget(QWidget):
    def __init__(self, parent=None):
        super(TableWidget, self).__init__(parent)
        self.table = QTableView(self)
        self.movieList = readData()
        self.initUI()

    def initUI(self):
        self.handleData()
        self.setWindowTitle("所有电影详细信息")
        self.resize(1200, 600)
        gridLayout = QGridLayout()
        gridLayout.addWidget(self.table, 1, 1)
        self.setLayout(gridLayout)

    def handleData(self):
        model = QStandardItemModel()
        self.table.setModel(model)
        model.setHorizontalHeaderLabels(["电影名", "评分", "投票人数", "评分百分比(依次5星~1星)",
                                         "地区", "上映年份", "类型", "长度(分钟)", "链接",
                                         "操作"])
        self.table.setColumnWidth(0, 150)
        self.table.setColumnWidth(1, 50)
        self.table.setColumnWidth(2, 75)
        self.table.setColumnWidth(3, 175)
        self.table.setColumnWidth(4, 175)
        self.table.setColumnWidth(5, 75)
        self.table.setColumnWidth(6, 125)
        self.table.setColumnWidth(7, 75)
        self.table.setColumnWidth(8, 150)
        for row, movie in enumerate(self.movieList):
            for column in range(9):
                item = QStandardItem(movie[column])
                item.setTextAlignment(Qt.AlignCenter)
                model.setItem(row, column, item)
            delete = QPushButton("删除", self)
            delete.setProperty("row", row)
            delete.clicked.connect(self.deleteClicked)
            self.table.setIndexWidget(model.index(row, 9), delete)

    def deleteClicked(self):
        sender = self.sender()
        row = sender.property("row")
        del self.movieList[row]
        self.handleData()


class About(QDialog):
    """
    关于界面
    """
    def __init__(self, parent=None, flags=Qt.WindowFlags()):
        super().__init__(parent=parent, flags=flags)
        self.initUI()

    def initUI(self):
        self.setWindowTitle("关于")
        self.resize(100, 150)
        gridLayout = QGridLayout()
        edition = QLabel("版本：0.1.0", self)
        url = QLabel(self)
        url.setOpenExternalLinks(True)
        url.setText("<a style='color:DeepSkyBlue;' \
href='https://github.com/Hooooot/doubanSpider'>项目地址</a>")
        GPLLicense = QLabel(self)
        GPLLicense.setOpenExternalLinks(True)
        GPLLicense.setText("<a style='color:DeepSkyBlue;' \
href='https://github.com/Hooooot/doubanSpider/blob/master/LICENSE'>MIT许可证</a>")
        right = QLabel("Copyright (c) 2019 Hooooot", self)

        gridLayout.addWidget(edition, 1, 1)
        gridLayout.addWidget(url, 2, 1)
        gridLayout.addWidget(GPLLicense, 3, 1)
        gridLayout.addWidget(right, 4, 1)

        self.setLayout(gridLayout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())
