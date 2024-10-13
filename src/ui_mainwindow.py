# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'UI_structure.ui'
##
## Created by: Qt User Interface Compiler version 6.6.2
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
from PySide6.QtWidgets import (QApplication, QDial, QDoubleSpinBox, QLabel,
    QPushButton, QScrollArea, QSizePolicy, QWidget)

from pyqtgraph import PlotWidget

class Ui_Widget(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(800, 600)
        self.graphicsView = PlotWidget(MainWindow)
        self.graphicsView.setObjectName(u"graphicsView")
        self.graphicsView.setGeometry(QRect(230, 50, 531, 531))
        self.loadButton = QPushButton(MainWindow)
        self.loadButton.setObjectName(u"loadButton")
        self.loadButton.setGeometry(QRect(10, 10, 75, 24))
        self.spectraButton = QPushButton(MainWindow)
        self.spectraButton.setObjectName(u"spectraButton")
        self.spectraButton.setGeometry(QRect(220, 10, 75, 24))
        self.paramsButton = QPushButton(MainWindow)
        self.paramsButton.setObjectName(u"paramsButton")
        self.paramsButton.setGeometry(QRect(100, 10, 101, 24))
        self.fitButton = QPushButton(MainWindow)
        self.fitButton.setObjectName(u"fitButton")
        self.fitButton.setGeometry(QRect(320, 10, 75, 24))
        self.displayParams = QScrollArea(MainWindow)
        self.displayParams.setObjectName(u"displayParams")
        self.displayParams.setGeometry(QRect(9, 239, 201, 341))
        self.displayParams.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 199, 339))
        self.displayParams.setWidget(self.scrollAreaWidgetContents)
        self.dialWaveShift = QDial(MainWindow)
        self.dialWaveShift.setObjectName(u"dialWaveShift")
        self.dialWaveShift.setGeometry(QRect(140, 70, 50, 64))
        self.dialBroadening = QDial(MainWindow)
        self.dialBroadening.setObjectName(u"dialBroadening")
        self.dialBroadening.setGeometry(QRect(140, 150, 50, 64))
        self.label = QLabel(MainWindow)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(30, 150, 91, 16))
        self.label_2 = QLabel(MainWindow)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(40, 70, 71, 16))
        self.lineWidthBox = QDoubleSpinBox(MainWindow)
        self.lineWidthBox.setObjectName(u"lineWidthBox")
        self.lineWidthBox.setGeometry(QRect(30, 170, 91, 22))
        self.wavelengthBox = QDoubleSpinBox(MainWindow)
        self.wavelengthBox.setObjectName(u"wavelengthBox")
        self.wavelengthBox.setGeometry(QRect(30, 90, 91, 22))

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("Widget", u"Widget", None))
        self.loadButton.setText(QCoreApplication.translate("Widget", u"Load", None))
        self.spectraButton.setText(QCoreApplication.translate("Widget", u"Save spectra", None))
        self.paramsButton.setText(QCoreApplication.translate("Widget", u"Save parameters", None))
        self.fitButton.setText(QCoreApplication.translate("Widget", u"Fit", None))
        self.label.setText(QCoreApplication.translate("Widget", u"Line width [nm]", None))
        self.label_2.setText(QCoreApplication.translate("Widget", u"\u03bb-shift [nm]", None))
    # retranslateUi

