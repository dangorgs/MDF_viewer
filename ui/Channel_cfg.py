# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Channel_cfg.ui'
##
## Created by: Qt User Interface Compiler version 6.5.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractButton, QApplication, QCheckBox, QDialogButtonBox,
    QGridLayout, QHeaderView, QListWidget, QListWidgetItem,
    QMainWindow, QMenuBar, QSizePolicy, QStatusBar,
    QTableWidget, QTableWidgetItem, QWidget)

class Ui_Channel_Cfg(object):
    def setupUi(self, Channel_Cfg):
        if not Channel_Cfg.objectName():
            Channel_Cfg.setObjectName(u"Channel_Cfg")
        Channel_Cfg.resize(1690, 1188)
        self.centralwidget = QWidget(Channel_Cfg)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.listMdf = QListWidget(self.centralwidget)
        self.listMdf.setObjectName(u"listMdf")
        self.listMdf.setMaximumSize(QSize(100, 16777215))
        self.listMdf.setMouseTracking(True)
        self.listMdf.setTabletTracking(True)
        self.listMdf.setAcceptDrops(True)

        self.gridLayout.addWidget(self.listMdf, 0, 0, 1, 1)

        self.listCg = QListWidget(self.centralwidget)
        self.listCg.setObjectName(u"listCg")
        self.listCg.setMaximumSize(QSize(200, 16777215))

        self.gridLayout.addWidget(self.listCg, 0, 1, 1, 1)

        self.tableChannels = QTableWidget(self.centralwidget)
        self.tableChannels.setObjectName(u"tableChannels")

        self.gridLayout.addWidget(self.tableChannels, 0, 2, 1, 2)

        self.dict_All_Sig_Sel = QCheckBox(self.centralwidget)
        self.dict_All_Sig_Sel.setObjectName(u"dict_All_Sig_Sel")
        self.dict_All_Sig_Sel.setEnabled(True)
        font = QFont()
        font.setPointSize(10)
        self.dict_All_Sig_Sel.setFont(font)
        self.dict_All_Sig_Sel.setChecked(True)

        self.gridLayout.addWidget(self.dict_All_Sig_Sel, 1, 2, 1, 1)

        self.Channel_cfg_ButtonBox = QDialogButtonBox(self.centralwidget)
        self.Channel_cfg_ButtonBox.setObjectName(u"Channel_cfg_ButtonBox")
        self.Channel_cfg_ButtonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Save)
        self.Channel_cfg_ButtonBox.setCenterButtons(False)

        self.gridLayout.addWidget(self.Channel_cfg_ButtonBox, 1, 3, 1, 1)

        Channel_Cfg.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(Channel_Cfg)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1690, 22))
        Channel_Cfg.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(Channel_Cfg)
        self.statusbar.setObjectName(u"statusbar")
        Channel_Cfg.setStatusBar(self.statusbar)

        self.retranslateUi(Channel_Cfg)

        QMetaObject.connectSlotsByName(Channel_Cfg)
    # setupUi

    def retranslateUi(self, Channel_Cfg):
        Channel_Cfg.setWindowTitle(QCoreApplication.translate("Channel_Cfg", u"MainWindow", None))
        self.dict_All_Sig_Sel.setText(QCoreApplication.translate("Channel_Cfg", u"All signals", None))
    # retranslateUi

