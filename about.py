from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QGridLayout, QLabel


class About(QDialog):
    """
    关于界面
    """
    def __init__(self, parent=None, flags=Qt.WindowFlags()):
        super().__init__(parent=parent, flags=flags)
        self.edition = "版本：1.2.0 released 2019-8-10"
        self.initUI()

    def initUI(self):
        self.setWindowTitle("关于")
        self.resize(100, 200)
        gridLayout = QGridLayout()
        tips = QLabel("说明：", self)
        tipsText = QLabel("&nbsp;&nbsp;&nbsp;此程序仅用于学习交流之<br/>&nbsp;用！\
<br/>&nbsp;&nbsp;&nbsp;多线（进）程运行可能会<br/>&nbsp;导致程序不稳定，建议数据量<br/>&nbsp;\
不大时不要打开。", self)
        editionLbl = QLabel(self.edition, self)
        url = QLabel(self)
        url.setOpenExternalLinks(True)
        url.setText("\
<a style='color:DeepSkyBlue;' href='https://github.com/Hooooot/doubanSpider'>\
项目地址</a>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;\
<a style='color:DeepSkyBlue;' href='https://github.com/Hooooot/doubanSpider/\
blob/master/LICENSE'>MIT许可证</a>")
        right = QLabel("Copyright (c) 2019 Hooooot", self)

        gridLayout.addWidget(tips, 1, 1)
        gridLayout.addWidget(tipsText, 2, 1)
        gridLayout.addWidget(url, 3, 1)
        gridLayout.addWidget(editionLbl, 4, 1)
        gridLayout.addWidget(right, 5, 1)
        self.setLayout(gridLayout)
