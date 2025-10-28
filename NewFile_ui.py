# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'NewFile.ui'
##
## Created by: Qt User Interface Compiler version 6.5.2
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QComboBox, QDialog,
    QDialogButtonBox, QGroupBox, QLabel, QRadioButton,
    QSizePolicy, QTextEdit, QWidget)

class Ui_NewFile(object):
    def setupUi(self, NewFile):
        if not NewFile.objectName():
            NewFile.setObjectName(u"NewFile")
        NewFile.resize(340, 500)
        self.buttonBox = QDialogButtonBox(NewFile)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setGeometry(QRect(20, 380, 300, 80))
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
        self.groupBox_unit = QGroupBox(NewFile)
        self.groupBox_unit.setObjectName(u"groupBox_unit")
        self.groupBox_unit.setGeometry(QRect(20, 100, 300, 80))
        self.radioButton_mum = QRadioButton(self.groupBox_unit)
        self.radioButton_mum.setObjectName(u"radioButton_mum")
        self.radioButton_mum.setGeometry(QRect(60, 0, 60, 30))
        self.radioButton_mm = QRadioButton(self.groupBox_unit)
        self.radioButton_mm.setObjectName(u"radioButton_mm")
        self.radioButton_mm.setGeometry(QRect(120, 0, 60, 30))
        self.label_9 = QLabel(self.groupBox_unit)
        self.label_9.setObjectName(u"label_9")
        self.label_9.setGeometry(QRect(0, 0, 60, 30))
        self.groupBox = QGroupBox(NewFile)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setGeometry(QRect(20, 20, 300, 80))
        self.label_8 = QLabel(self.groupBox)
        self.label_8.setObjectName(u"label_8")
        self.label_8.setGeometry(QRect(0, 0, 60, 30))
        self.comboBox_backend = QComboBox(self.groupBox)
        self.comboBox_backend.addItem("")
        self.comboBox_backend.addItem("")
        self.comboBox_backend.addItem("")
        self.comboBox_backend.addItem("")
        self.comboBox_backend.addItem("")
        self.comboBox_backend.addItem("")
        self.comboBox_backend.addItem("")
        self.comboBox_backend.addItem("")
        self.comboBox_backend.addItem("")
        self.comboBox_backend.addItem("")
        self.comboBox_backend.setObjectName(u"comboBox_backend")
        self.comboBox_backend.setGeometry(QRect(60, 0, 150, 50))
        self.groupBox_2 = QGroupBox(NewFile)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.groupBox_2.setGeometry(QRect(20, 260, 300, 80))
        self.label_2 = QLabel(self.groupBox_2)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(0, 0, 60, 30))
        self.textEdit_name = QTextEdit(self.groupBox_2)
        self.textEdit_name.setObjectName(u"textEdit_name")
        self.textEdit_name.setGeometry(QRect(60, 0, 150, 50))
        self.label_13 = QLabel(self.groupBox_2)
        self.label_13.setObjectName(u"label_13")
        self.label_13.setGeometry(QRect(220, 20, 60, 30))
        self.label_3 = QLabel(self.groupBox_2)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(0, 48, 200, 30))
        self.groupBox_3 = QGroupBox(NewFile)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.groupBox_3.setGeometry(QRect(20, 180, 300, 80))
        self.label_10 = QLabel(self.groupBox_3)
        self.label_10.setObjectName(u"label_10")
        self.label_10.setGeometry(QRect(0, 0, 60, 30))
        self.radioButton_fs = QRadioButton(self.groupBox_3)
        self.radioButton_fs.setObjectName(u"radioButton_fs")
        self.radioButton_fs.setGeometry(QRect(60, 0, 60, 30))
        self.radioButton_ps = QRadioButton(self.groupBox_3)
        self.radioButton_ps.setObjectName(u"radioButton_ps")
        self.radioButton_ps.setGeometry(QRect(120, 0, 60, 30))
        self.radioButton_ns = QRadioButton(self.groupBox_3)
        self.radioButton_ns.setObjectName(u"radioButton_ns")
        self.radioButton_ns.setGeometry(QRect(180, 0, 60, 30))

        self.retranslateUi(NewFile)
        self.buttonBox.accepted.connect(NewFile.accept)
        self.buttonBox.rejected.connect(NewFile.reject)

        QMetaObject.connectSlotsByName(NewFile)
    # setupUi

    def retranslateUi(self, NewFile):
        NewFile.setWindowTitle(QCoreApplication.translate("NewFile", u"\u65b0\u5efa\u4eff\u771f", None))
        self.groupBox_unit.setTitle("")
        self.radioButton_mum.setText(QCoreApplication.translate("NewFile", u"\u03bcm", None))
        self.radioButton_mm.setText(QCoreApplication.translate("NewFile", u"mm", None))
        self.label_9.setText(QCoreApplication.translate("NewFile", u"\u7a7a\u95f4\u5355\u4f4d\uff1a", None))
        self.groupBox.setTitle("")
        self.label_8.setText(QCoreApplication.translate("NewFile", u"\u4f7f\u7528\u7b97\u6cd5\uff1a", None))
        self.comboBox_backend.setItemText(0, QCoreApplication.translate("NewFile", u"FDTD", None))
        self.comboBox_backend.setItemText(1, QCoreApplication.translate("NewFile", u"ADI-FDTD", None))
        self.comboBox_backend.setItemText(2, QCoreApplication.translate("NewFile", u"CN-FDTD", None))
        self.comboBox_backend.setItemText(3, QCoreApplication.translate("NewFile", u"SS-FDTD", None))
        self.comboBox_backend.setItemText(4, QCoreApplication.translate("NewFile", u"LOD-FDTD", None))
        self.comboBox_backend.setItemText(5, QCoreApplication.translate("NewFile", u"WCS-FDTD", None))
        self.comboBox_backend.setItemText(6, QCoreApplication.translate("NewFile", u"HIE-FDTD", None))
        self.comboBox_backend.setItemText(7, QCoreApplication.translate("NewFile", u"CDLT-FDTD", None))
        self.comboBox_backend.setItemText(8, QCoreApplication.translate("NewFile", u"SO-FDTD", None))
        self.comboBox_backend.setItemText(9, QCoreApplication.translate("NewFile", u"PITD-FDTD", None))

        self.groupBox_2.setTitle("")
        self.label_2.setText(QCoreApplication.translate("NewFile", u"\u6587\u4ef6\u540d\uff1a", None))
        self.textEdit_name.setPlaceholderText("")
        self.label_13.setText(QCoreApplication.translate("NewFile", u".json", None))
        self.label_3.setText(QCoreApplication.translate("NewFile", u"\uff08\u9ed8\u8ba4\u4f4d\u4e8eemulation\u76ee\u5f55\u4e0b\uff09", None))
        self.groupBox_3.setTitle("")
        self.label_10.setText(QCoreApplication.translate("NewFile", u"\u65f6\u95f4\u5355\u4f4d\uff1a", None))
        self.radioButton_fs.setText(QCoreApplication.translate("NewFile", u"fs", None))
        self.radioButton_ps.setText(QCoreApplication.translate("NewFile", u"ps", None))
        self.radioButton_ns.setText(QCoreApplication.translate("NewFile", u"ns", None))
    # retranslateUi

