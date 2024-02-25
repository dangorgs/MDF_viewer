# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Sig_Integration.ui'
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
from PySide6.QtWidgets import (QApplication, QGridLayout, QHeaderView, QListWidget,
    QListWidgetItem, QMainWindow, QMenuBar, QSizePolicy,
    QStatusBar, QTableWidget, QTableWidgetItem, QWidget)

class Ui_Sig_Integration(object):
    def setupUi(self, Sig_Integration):
        if not Sig_Integration.objectName():
            Sig_Integration.setObjectName(u"Sig_Integration")
        Sig_Integration.resize(1644, 1167)
        self.centralwidget = QWidget(Sig_Integration)
        self.centralwidget.setObjectName(u"centralwidget")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.listMdf_SigIntg = QListWidget(self.centralwidget)
        self.listMdf_SigIntg.setObjectName(u"listMdf_SigIntg")
        self.listMdf_SigIntg.setMaximumSize(QSize(200, 16777215))

        self.gridLayout.addWidget(self.listMdf_SigIntg, 0, 0, 1, 1)

        self.listCg_SigIntg = QListWidget(self.centralwidget)
        self.listCg_SigIntg.setObjectName(u"listCg_SigIntg")
        self.listCg_SigIntg.setMaximumSize(QSize(300, 16777215))

        self.gridLayout.addWidget(self.listCg_SigIntg, 0, 1, 1, 1)

        self.tableChannels_Integ = QTableWidget(self.centralwidget)
        self.tableChannels_Integ.setObjectName(u"tableChannels_Integ")

        self.gridLayout.addWidget(self.tableChannels_Integ, 0, 2, 1, 1)

        Sig_Integration.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(Sig_Integration)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1644, 22))
        Sig_Integration.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(Sig_Integration)
        self.statusbar.setObjectName(u"statusbar")
        Sig_Integration.setStatusBar(self.statusbar)

        self.retranslateUi(Sig_Integration)

        QMetaObject.connectSlotsByName(Sig_Integration)
    # setupUi

    def retranslateUi(self, Sig_Integration):
        Sig_Integration.setWindowTitle(QCoreApplication.translate("Sig_Integration", u"MainWindow", None))
    # retranslateUi

