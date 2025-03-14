# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'MDF_main_window.ui'
##
## Created by: Qt User Interface Compiler version 6.5.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QDoubleSpinBox, QFrame, QGridLayout,
    QHBoxLayout, QHeaderView, QLCDNumber, QLayout,
    QMainWindow, QMenu, QMenuBar, QPushButton,
    QSizePolicy, QSpacerItem, QSplitter, QStatusBar,
    QTextBrowser, QToolBar, QTreeWidget, QTreeWidgetItem,
    QVBoxLayout, QWidget)

from pyqtgraph import PlotWidget

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1142, 883)
        MainWindow.setAcceptDrops(True)
        self.actionOpen = QAction(MainWindow)
        self.actionOpen.setObjectName(u"actionOpen")
        self.actionFit_Window = QAction(MainWindow)
        self.actionFit_Window.setObjectName(u"actionFit_Window")
        self.actionFit_Window.setEnabled(False)
        self.actionInfo = QAction(MainWindow)
        self.actionInfo.setObjectName(u"actionInfo")
        self.actionChannel_name = QAction(MainWindow)
        self.actionChannel_name.setObjectName(u"actionChannel_name")
        self.actionChannel_name.setEnabled(False)
        self.actionStack_all = QAction(MainWindow)
        self.actionStack_all.setObjectName(u"actionStack_all")
        self.actionStack_all.setEnabled(False)
        self.actionIntegration = QAction(MainWindow)
        self.actionIntegration.setObjectName(u"actionIntegration")
        self.actionIntegration.setEnabled(False)
        self.actionGradient = QAction(MainWindow)
        self.actionGradient.setObjectName(u"actionGradient")
        self.actionGradient.setEnabled(False)
        self.actionMultiplication = QAction(MainWindow)
        self.actionMultiplication.setObjectName(u"actionMultiplication")
        self.actionMultiplication.setEnabled(False)
        self.actionSummation = QAction(MainWindow)
        self.actionSummation.setObjectName(u"actionSummation")
        self.actionSummation.setEnabled(False)
        self.actionGain = QAction(MainWindow)
        self.actionGain.setObjectName(u"actionGain")
        self.actionGain.setEnabled(False)
        self.actionLoad_Configuration = QAction(MainWindow)
        self.actionLoad_Configuration.setObjectName(u"actionLoad_Configuration")
        self.actionSave_Configuration = QAction(MainWindow)
        self.actionSave_Configuration.setObjectName(u"actionSave_Configuration")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.centralwidget.setAcceptDrops(True)
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.pushButton = QPushButton(self.centralwidget)
        self.pushButton.setObjectName(u"pushButton")

        self.horizontalLayout.addWidget(self.pushButton)

        self.pushButton_2 = QPushButton(self.centralwidget)
        self.pushButton_2.setObjectName(u"pushButton_2")

        self.horizontalLayout.addWidget(self.pushButton_2)

        self.pushButton_5 = QPushButton(self.centralwidget)
        self.pushButton_5.setObjectName(u"pushButton_5")
        self.pushButton_5.setEnabled(True)
        self.pushButton_5.setMaximumSize(QSize(16777215, 16777215))

        self.horizontalLayout.addWidget(self.pushButton_5)

        self.stack_all_btn = QPushButton(self.centralwidget)
        self.stack_all_btn.setObjectName(u"stack_all_btn")

        self.horizontalLayout.addWidget(self.stack_all_btn)

        self.Shift_Sig_Button = QPushButton(self.centralwidget)
        self.Shift_Sig_Button.setObjectName(u"Shift_Sig_Button")

        self.horizontalLayout.addWidget(self.Shift_Sig_Button)

        self.Shift_Sig_X = QDoubleSpinBox(self.centralwidget)
        self.Shift_Sig_X.setObjectName(u"Shift_Sig_X")
        self.Shift_Sig_X.setMaximumSize(QSize(16777215, 16777215))
        self.Shift_Sig_X.setDecimals(5)
        self.Shift_Sig_X.setMinimum(-999999.989999999990687)
        self.Shift_Sig_X.setMaximum(999999.989999999990687)

        self.horizontalLayout.addWidget(self.Shift_Sig_X)

        self.Shift_Sig_Y = QDoubleSpinBox(self.centralwidget)
        self.Shift_Sig_Y.setObjectName(u"Shift_Sig_Y")
        self.Shift_Sig_Y.setDecimals(5)
        self.Shift_Sig_Y.setMinimum(-999999.989999999990687)
        self.Shift_Sig_Y.setMaximum(999999.989999999990687)

        self.horizontalLayout.addWidget(self.Shift_Sig_Y)

        self.horizontalSpacer_2 = QSpacerItem(20, 20, QSizePolicy.Preferred, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_2)

        self.pushButton_3 = QPushButton(self.centralwidget)
        self.pushButton_3.setObjectName(u"pushButton_3")
        font = QFont()
        font.setBold(False)
        font.setKerning(False)
        self.pushButton_3.setFont(font)

        self.horizontalLayout.addWidget(self.pushButton_3)

        self.pushButton_4 = QPushButton(self.centralwidget)
        self.pushButton_4.setObjectName(u"pushButton_4")
        font1 = QFont()
        font1.setBold(False)
        font1.setItalic(False)
        font1.setUnderline(False)
        font1.setStrikeOut(False)
        self.pushButton_4.setFont(font1)
        self.pushButton_4.setAutoFillBackground(False)
        self.pushButton_4.setFlat(False)

        self.horizontalLayout.addWidget(self.pushButton_4)

        self.text_Time = QTextBrowser(self.centralwidget)
        self.text_Time.setObjectName(u"text_Time")
        self.text_Time.setMaximumSize(QSize(100, 25))
        font2 = QFont()
        font2.setPointSize(10)
        self.text_Time.setFont(font2)
        self.text_Time.setLayoutDirection(Qt.LeftToRight)
        self.text_Time.setAutoFillBackground(False)
        self.text_Time.setStyleSheet(u"background: transparent")
        self.text_Time.setFrameShape(QFrame.NoFrame)
        self.text_Time.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.text_Time.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.horizontalLayout.addWidget(self.text_Time)

        self.delta_Time = QTextBrowser(self.centralwidget)
        self.delta_Time.setObjectName(u"delta_Time")
        self.delta_Time.setEnabled(True)
        self.delta_Time.setMaximumSize(QSize(100, 25))
        self.delta_Time.setFont(font2)
        self.delta_Time.setLayoutDirection(Qt.LeftToRight)
        self.delta_Time.setStyleSheet(u"background: transparent")
        self.delta_Time.setFrameShape(QFrame.NoFrame)
        self.delta_Time.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.delta_Time.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.horizontalLayout.addWidget(self.delta_Time)

        self.delta_Y = QTextBrowser(self.centralwidget)
        self.delta_Y.setObjectName(u"delta_Y")
        self.delta_Y.setMaximumSize(QSize(100, 25))
        self.delta_Y.setFont(font2)
        self.delta_Y.setStyleSheet(u"background: transparent")
        self.delta_Y.setFrameShape(QFrame.NoFrame)
        self.delta_Y.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.delta_Y.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.horizontalLayout.addWidget(self.delta_Y)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)


        self.gridLayout.addLayout(self.horizontalLayout, 1, 0, 1, 1)

        self.splitter_list_plot = QSplitter(self.centralwidget)
        self.splitter_list_plot.setObjectName(u"splitter_list_plot")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.splitter_list_plot.sizePolicy().hasHeightForWidth())
        self.splitter_list_plot.setSizePolicy(sizePolicy)
        self.splitter_list_plot.setOrientation(Qt.Horizontal)
        self.layoutWidget = QWidget(self.splitter_list_plot)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.verticalLayout = QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.current_ch = QTextBrowser(self.layoutWidget)
        self.current_ch.setObjectName(u"current_ch")
        self.current_ch.setMaximumSize(QSize(110, 25))
        self.current_ch.setBaseSize(QSize(0, 0))
        self.current_ch.setFont(font2)
        self.current_ch.setStyleSheet(u"background: transparent")
        self.current_ch.setFrameShape(QFrame.NoFrame)
        self.current_ch.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.current_ch.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.verticalLayout.addWidget(self.current_ch)

        self.lcdNumber = QLCDNumber(self.layoutWidget)
        self.lcdNumber.setObjectName(u"lcdNumber")
        palette = QPalette()
        brush = QBrush(QColor(0, 0, 255, 255))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.WindowText, brush)
        brush1 = QBrush(QColor(0, 0, 0, 255))
        brush1.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Text, brush1)
        palette.setBrush(QPalette.Inactive, QPalette.WindowText, brush)
        palette.setBrush(QPalette.Inactive, QPalette.Text, brush1)
        self.lcdNumber.setPalette(palette)
        self.lcdNumber.setLineWidth(0)
        self.lcdNumber.setMidLineWidth(0)
        self.lcdNumber.setDigitCount(7)
        self.lcdNumber.setProperty("intValue", 0)

        self.verticalLayout.addWidget(self.lcdNumber)

        self.list_lcd = QWidget(self.layoutWidget)
        self.list_lcd.setObjectName(u"list_lcd")

        self.verticalLayout.addWidget(self.list_lcd)

        self.treeWidget = QTreeWidget(self.layoutWidget)
        __qtreewidgetitem = QTreeWidgetItem()
        __qtreewidgetitem.setText(0, u"1");
        self.treeWidget.setHeaderItem(__qtreewidgetitem)
        self.treeWidget.setObjectName(u"treeWidget")
        self.treeWidget.setMinimumSize(QSize(200, 0))
        self.treeWidget.setAcceptDrops(True)

        self.verticalLayout.addWidget(self.treeWidget)

        self.splitter_list_plot.addWidget(self.layoutWidget)
        self.graphicsView = PlotWidget(self.splitter_list_plot)
        self.graphicsView.setObjectName(u"graphicsView")
        self.splitter_list_plot.addWidget(self.graphicsView)

        self.gridLayout.addWidget(self.splitter_list_plot, 0, 0, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1142, 22))
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName(u"menuFile")
        self.menuHelp = QMenu(self.menubar)
        self.menuHelp.setObjectName(u"menuHelp")
        self.menuView = QMenu(self.menubar)
        self.menuView.setObjectName(u"menuView")
        self.menuConffigure = QMenu(self.menubar)
        self.menuConffigure.setObjectName(u"menuConffigure")
        self.menuCalculation = QMenu(self.menubar)
        self.menuCalculation.setObjectName(u"menuCalculation")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.toolBar = QToolBar(MainWindow)
        self.toolBar.setObjectName(u"toolBar")
        MainWindow.addToolBar(Qt.TopToolBarArea, self.toolBar)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuView.menuAction())
        self.menubar.addAction(self.menuConffigure.menuAction())
        self.menubar.addAction(self.menuCalculation.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        self.menuFile.addAction(self.actionOpen)
        self.menuHelp.addAction(self.actionInfo)
        self.menuView.addAction(self.actionFit_Window)
        self.menuView.addAction(self.actionStack_all)
        self.menuConffigure.addAction(self.actionChannel_name)
        self.menuConffigure.addAction(self.actionLoad_Configuration)
        self.menuConffigure.addAction(self.actionSave_Configuration)
        self.menuCalculation.addAction(self.actionIntegration)
        self.menuCalculation.addAction(self.actionGradient)
        self.menuCalculation.addAction(self.actionMultiplication)
        self.menuCalculation.addAction(self.actionSummation)
        self.menuCalculation.addAction(self.actionGain)

        self.retranslateUi(MainWindow)

        self.pushButton_3.setDefault(False)
        self.pushButton_4.setDefault(False)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.actionOpen.setText(QCoreApplication.translate("MainWindow", u"Open", None))
        self.actionFit_Window.setText(QCoreApplication.translate("MainWindow", u"Fit Window", None))
        self.actionInfo.setText(QCoreApplication.translate("MainWindow", u"Info", None))
        self.actionChannel_name.setText(QCoreApplication.translate("MainWindow", u"Channel", None))
        self.actionStack_all.setText(QCoreApplication.translate("MainWindow", u"Stack all", None))
        self.actionIntegration.setText(QCoreApplication.translate("MainWindow", u"Integration", None))
        self.actionGradient.setText(QCoreApplication.translate("MainWindow", u"Gradient", None))
        self.actionMultiplication.setText(QCoreApplication.translate("MainWindow", u"Multiplication", None))
        self.actionSummation.setText(QCoreApplication.translate("MainWindow", u"Summation", None))
        self.actionGain.setText(QCoreApplication.translate("MainWindow", u"Gain", None))
        self.actionLoad_Configuration.setText(QCoreApplication.translate("MainWindow", u"Load ", None))
        self.actionSave_Configuration.setText(QCoreApplication.translate("MainWindow", u"Export", None))
        self.pushButton.setText(QCoreApplication.translate("MainWindow", u"Clear", None))
        self.pushButton_2.setText(QCoreApplication.translate("MainWindow", u"Fit ", None))
        self.pushButton_5.setText(QCoreApplication.translate("MainWindow", u"Scale ", None))
        self.stack_all_btn.setText(QCoreApplication.translate("MainWindow", u"Stack", None))
        self.Shift_Sig_Button.setText(QCoreApplication.translate("MainWindow", u"Shift  X , Y ", None))
        self.pushButton_3.setText(QCoreApplication.translate("MainWindow", u"X1", None))
        self.pushButton_4.setText(QCoreApplication.translate("MainWindow", u"X2 ", None))
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", u"File", None))
        self.menuHelp.setTitle(QCoreApplication.translate("MainWindow", u"Help", None))
        self.menuView.setTitle(QCoreApplication.translate("MainWindow", u"View", None))
        self.menuConffigure.setTitle(QCoreApplication.translate("MainWindow", u"Configure", None))
        self.menuCalculation.setTitle(QCoreApplication.translate("MainWindow", u"Operations", None))
        self.toolBar.setWindowTitle(QCoreApplication.translate("MainWindow", u"toolBar", None))
    # retranslateUi

