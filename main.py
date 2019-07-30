import sys
import time

from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QIntValidator, QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import (
    QAction, QApplication, QCheckBox, QComboBox, QDialog, QGridLayout, QLabel,
    QLineEdit, QMainWindow, QMessageBox, QPushButton, QTableView, QWidget)

from distribution import Distribution
from douban import Movie, Spider


class SpiderThread(QThread):
    status = pyqtSignal(str)
    result = pyqtSignal(list)

    def __init__(self, params, amount, statusChange,
                 threadFinish, concurrent=None):
        """
        ClickThread(params, amount, statusChange,\
threadFinish, concurrent=None)
        #### 参数：
                 params:爬虫参数
                 amount:电影数量
                 statusChange:status信号响应方法
                 threadFinish:result信号响应方法
        """
        super(SpiderThread, self).__init__()
        self.params = params
        self.amount = amount
        self.concurrent = concurrent
        self.status.connect(statusChange)
        self.result.connect(threadFinish)

    def run(self):
        spider = Spider.begin(self.params, self.amount,
                              self.status, self.concurrent)
        self.result.emit(spider.movies)
        print("已爬完")


class DistributionThread(QThread):
    def __init__(self, movieList):
        """
        DistributionThread(movieList)
        #### 参数：
                 movieList:电影(douban.Movie)列表
        """
        super(DistributionThread, self).__init__()
        self.movieList = movieList

    def run(self):
        Distribution.begin(self.movieList)


class TableWidget(QWidget):
    def __init__(self, movieList, parent=None):
        """
        TableWidget(movieList, parent=None)
        #### 参数：
                 movieList:电影(douban.Movie)列表
                 parent:指定父窗口，默认无
        """
        super(TableWidget, self).__init__(parent)
        self.table = QTableView(self)
        self.movieList = movieList
        self.initUI()

    def initUI(self):
        """
        #### 功能：初始化控件属性
        #### 参数：None
        #### 返回：None
        """
        self.handleData()
        self.setWindowTitle("所有电影详细信息")
        self.resize(1200, 600)
        gridLayout = QGridLayout()
        gridLayout.addWidget(self.table, 1, 1)
        self.setLayout(gridLayout)

    def handleData(self):
        """
        #### 功能：处理电影列表里的数据，并显示
        #### 参数：None
        #### 返回：None
        """
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
        """
        #### 功能：响应删除按钮，删除对应行的电影信息
        #### 参数：None
        #### 返回：None
        """
        sender = self.sender()
        row = sender.property("row")
        del self.movieList[row]
        self.handleData()


class MainWindow(QMainWindow):
    def __init__(self):
        """
        MainWindow()
        #### 功能：主窗口类
        """
        super().__init__()
        # 电影类型选择框
        self.typeCombo = QComboBox(self)
        # 电影所属区域选择框
        self.areaCombo = QComboBox(self)
        # 电影年代选择框
        self.yearCombo = QComboBox(self)
        # 输入框前的提示
        self.tip = QLabel("最大电影获取数量：", self)
        # 开始按钮
        self.btn = QPushButton("开始", self)
        # 用于输入将要爬取的电影数量
        self.amount = QLineEdit(self)
        # 确定是否显示所有电影信息窗口的复选框
        self.showAllDataCheck = QCheckBox("显示所有电影信息", self)
        # Table窗口，用于显示所有电影的详细信息
        self.tableWindow = None
        # 爬虫线程，用于运行爬虫
        self.spiderThread = None
        # 数据分析线程，用于显示数据分析结果
        self.distributionThread = None
        # 状态栏
        self.status = self.statusBar()
        # 菜单
        self.menu = self.menuBar()
        # 是否使用多线（进）程
        self.concurrent = False
        # 已用时秒
        self.usedTimeS = 0
        # 已用时分
        self.usedTimeM = 0
        # 已用时Label
        self.timeLabel = None
        # 计时器
        self.timer = None
        # 年代显示与爬虫请求参数的映射
        self.yearsDic = {
            "全部年代": "",
            "2019": "2019,2019",
            "2018": "2018,2018",
            "2010年代": "2010,2019",
            "2000年代": "2000,2009",
            "90年代": "1990,1999",
            "80年代": "1980,1989",
            "70年代": "1970,1979",
            "60年代": "1960,1969",
            "更早": "1,1959"
        }
        self.initUI()

    def initUI(self):
        """
        #### 功能：初始化控件属性
        #### 参数：None
        #### 返回：None
        """
        # self.setGeometry(1000, 100, 500, 200)
        gridLayout = QGridLayout()
        widget = QWidget()
        self.setWindowTitle("TOP 200")
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
        self.showAllDataCheck.setCheckState(Qt.Checked)
        intOnly = QIntValidator()
        intOnly.setRange(0, 999)
        self.amount.setValidator(intOnly)
        self.amount.setPlaceholderText("0~999(0:不限制)")
        self.amount.setMaxLength(3)
        self.amount.setMaximumWidth(120)
        self.btn.clicked.connect(self.btnClicked)
        self.amount.returnPressed.connect(lambda: self.btn.clicked.emit())

        advanced = self.menu.addMenu("高级")
        concurrent = advanced.addAction("多线（进）程运行")
        concurrent.setCheckable(True)
        concurrent.triggered.connect(self.concurrentCheck)
        help = self.menu.addMenu("帮助")
        help.addAction("关于")
        help.triggered[QAction].connect(self.about)

        gridLayout.addWidget(self.typeCombo, 1, 1)
        gridLayout.addWidget(self.areaCombo, 1, 2)
        gridLayout.addWidget(self.yearCombo, 1, 3)
        gridLayout.addWidget(self.tip, 2, 1)
        gridLayout.addWidget(self.amount, 2, 2)
        gridLayout.addWidget(self.showAllDataCheck, 2, 3)
        gridLayout.addWidget(self.btn, 3, 2)
        self.status.messageChanged.connect(self.status.showMessage)
        self.status.messageChanged.emit("就绪!")
        self.centralWidget().setLayout(gridLayout)

        self.timeLabel = QLabel("尚未开始！")
        self.status.addPermanentWidget(self.timeLabel)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateUsedTime)

    def btnClicked(self):
        """
        #### 功能：响应开始按钮的点击事件
        #### 参数：None
        #### 返回：None
        """
        sender = self.sender()
        if sender.text() == "开始":
            """
            点击开始，获取条件，并运行爬虫
            """
            if self.amount.text() == '':
                QMessageBox.warning(self, "警告：", "数量不能为空！", QMessageBox.Ok)
                return
            sender.setText("停止")
            sender.setToolTip("点击停止爬取")
            self.amount.setReadOnly(True)
            style = "QLineEdit{background-color:rgb(240, 240, 240);}"
            self.amount.setStyleSheet(style)
            self.statusBar().showMessage("正在运行......")
            params = {
                "sort": "S",
                "range": "0,10",
                "tags": "电影",
                "start": 0,
                "genres": "喜剧",
                "countries": "中国大陆",
                "year_range": "2000,2009"
            }
            if self.typeCombo.currentText() == "全部类型":
                params["genres"] = ""
            else:
                params["genres"] = self.typeCombo.currentText()
            if self.areaCombo.currentText() == "全部地区":
                params["countries"] = ""
            else:
                params["countries"] = self.areaCombo.currentText()
            params["year_range"] = self.yearsDic[self.yearCombo.currentText()]
            self.spiderThread = SpiderThread(params, int(self.amount.text()),
                                             self.status.showMessage,
                                             self.threadFinish,
                                             self.concurrent)
            self.spiderThread.start()
            self.usedTimeM = 0
            self.usedTimeS = 0
            self.timer.start(1000)
        else:
            """
            点击停止，终止爬虫进程
            """
            if not self.spiderThread.isFinished():
                self.status.messageChanged.emit("正在停止......")
                self.spiderThread.terminate()
                time.sleep(1)
            self.spiderThread = None
            sender.setText("开始")
            sender.setToolTip("点击开始爬取")
            self.amount.setReadOnly(False)
            self.amount.setStyleSheet("QLineEdit{background-color: white;}")
            self.status.messageChanged.emit("就绪!")
            self.timer.stop()

    def threadFinish(self, movieList):
        """
        #### 功能：当爬虫线程结束时，将自动调用该方法以处理数据
        #### 参数：
                 movieList:爬虫返回的电影实例(douban.Movie)列表
        #### 返回：None
        """
        self.btn.setText("开始")
        self.btn.setToolTip("点击开始爬取")
        self.amount.setReadOnly(False)
        self.amount.setStyleSheet("QLineEdit{background-color: white;}")
        self.distributionThread = DistributionThread(movieList)
        self.distributionThread.start()
        if self.showAllDataCheck.isChecked():
            self.tableWindow = TableWidget(movieList)
            self.tableWindow.show()
        self.timer.stop()

    def updateUsedTime(self):
        """
        #### 功能：计时器结束时的响应方法，用于更新状态栏的计时栏
        #### 参数：None
        #### 返回：None
        """
        self.usedTimeS += 1
        if self.usedTimeS >= 60:
            self.usedTimeM += 1
            self.usedTimeS = 0
        if self.usedTimeM == 0:
            self.timeLabel.setText("已用时：" + str(self.usedTimeS) + " 秒")
        else:
            self.timeLabel.setText("已用时：" + str(self.usedTimeM) + " 分 " +
                                   str(self.usedTimeS) + " 秒")

    def about(self):
        """
        #### 功能：打开关于窗口
        #### 参数：None
        #### 返回：None
        """
        self.aboutWindow = About()
        self.aboutWindow.setModal(True)
        self.aboutWindow.show()

    def concurrentCheck(self, check):
        """
        #### 功能：多线（进）程运行QAction的响应函数，用于设置是否使用并发
        #### 参数：
                 check:是否使用并发执行
        #### 返回：None
        """
        sender = self.sender()
        if check:
            rs = QMessageBox().warning(self, "警告：",
                                       "开启多线（进）程可能会导致程序不稳定！是否继续开启？",
                                       QMessageBox.Yes | QMessageBox.No)
            if rs == QMessageBox.Yes:
                self.concurrent = check
            else:
                sender.setChecked(False)


class About(QDialog):
    """
    关于界面
    """
    def __init__(self, parent=None, flags=Qt.WindowFlags()):
        super().__init__(parent=parent, flags=flags)
        self.initUI()

    def initUI(self):
        self.setWindowTitle("关于")
        self.resize(100, 200)
        gridLayout = QGridLayout()
        tips = QLabel("说明：", self)
        tipsText = QLabel("&nbsp;&nbsp;&nbsp;多线（进）程运行可能会<br/>\
&nbsp;导致程序不稳定，建议数据量<br/>&nbsp;不大时不要打开。", self)
        edition = QLabel("版本：1.1.0 released 2019-7-30", self)
        url = QLabel(self)
        url.setOpenExternalLinks(True)
        url.setText("<a style='color:DeepSkyBlue;' \
href='https://github.com/Hooooot/doubanSpider'>项目地址</a>")
        GPLLicense = QLabel(self)
        GPLLicense.setOpenExternalLinks(True)
        GPLLicense.setText("<a style='color:DeepSkyBlue;' \
href='https://github.com/Hooooot/doubanSpider/blob/master/LICENSE'>MIT许可证</a>")
        right = QLabel("Copyright (c) 2019 Hooooot", self)

        gridLayout.addWidget(tips, 1, 1)
        gridLayout.addWidget(tipsText, 2, 1)
        gridLayout.addWidget(url, 3, 1)
        gridLayout.addWidget(GPLLicense, 3, 2)
        gridLayout.addWidget(edition, 4, 1)
        gridLayout.addWidget(right, 5, 1)
        self.setLayout(gridLayout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())
