# -*- coding: utf-8 -*-

################################################################################
## Interfaz gráfica de la estación láser en PySide6 
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QDoubleSpinBox, QFrame,
    QGridLayout, QHBoxLayout, QLabel, QLineEdit,
    QMainWindow, QPushButton, QSizePolicy, QSpacerItem,
    QVBoxLayout, QWidget)

from Custom_Widgets.QCustomQStackedWidget import QCustomQStackedWidget
from Custom_Widgets.QCustomSlideMenu import QCustomSlideMenu

import json
import re
from PySide6.QtCore import QSettings

_ICON_ALIAS_RE = re.compile(r"^:/[^/]+/icons/(.+)$")


def _current_icons_color():
    """Color (sin '#') de los iconos del tema activo, usado para localizar los
    PNG ya coloreados que Custom_Widgets genera en Qss/icons/<color>/...

    setupUi() se ejecuta antes de que Custom_Widgets fije el nombre de
    organizacion/aplicacion (eso ocurre en QAppSettings.updateAppSettings,
    despues de setupUi), asi que QSettings() por defecto todavia no apunta
    al almacen persistente correcto. Lo leemos con el mismo organization/
    application definidos en style.json para encontrar el tema guardado."""
    default_color = "000000"
    org_name = ""
    app_name = ""

    try:
        with open("json-styles/style.json", encoding="utf-8") as f:
            style = json.load(f)
        for qsettings_block in style.get("QSettings", []):
            app_settings = qsettings_block.get("AppSettings", {})
            org_name = str(app_settings.get("OrginizationName", ""))
            app_name = str(app_settings.get("ApplicationName", ""))
            for theme_settings in qsettings_block.get("ThemeSettings", []):
                for theme in theme_settings.get("CustomTheme", []):
                    if theme.get("Default-Theme"):
                        default_color = str(theme.get("Icons-color", default_color)).replace("#", "")
    except Exception:
        pass

    settings = QSettings(org_name, app_name) if org_name and app_name else QSettings()
    color = settings.value("ICONS-COLOR")
    if color:
        return str(color).replace("#", "")

    return default_color


def _icon_path(alias):
    """Convierte un alias de recurso Qt (':/prefix/icons/style/name.png') en la
    ruta real, en disco, del icono coloreado para el tema activo. El proyecto
    no compila un archivo .qrc, así que las rutas ':/...' no se resuelven."""
    match = _ICON_ALIAS_RE.match(alias)
    if not match:
        return alias
    return f"Qss/icons/{_current_icons_color()}/{match.group(1)}"


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1006, 558)
        font = QFont()
        font.setFamilies([u"Sitka Small"])
        font.setPointSize(10)
        MainWindow.setFont(font)
        MainWindow.setAutoFillBackground(False)
        MainWindow.setStyleSheet(u"")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.centralwidget.setMinimumSize(QSize(628, 376))
        self.horizontalLayout = QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(10, 10, 10, 10)
        self.leftMenu = QCustomSlideMenu(self.centralwidget)
        self.leftMenu.setObjectName(u"leftMenu")
        self.leftMenu.setMinimumSize(QSize(0, 0))
        self.verticalLayout = QVBoxLayout(self.leftMenu)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.widget = QWidget(self.leftMenu)
        self.widget.setObjectName(u"widget")
        self.widget.setMinimumSize(QSize(103, 30))
        self.verticalLayout_2 = QVBoxLayout(self.widget)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(5, 5, 0, 5)
        self.menuBtn = QPushButton(self.widget)
        self.menuBtn.setObjectName(u"menuBtn")
        self.menuBtn.setEnabled(True)
        icon = QIcon()
        icon.addFile(_icon_path(u":/feather/icons/feather/menu.png"), QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.menuBtn.setIcon(icon)
        self.menuBtn.setCheckable(True)
        self.menuBtn.setAutoExclusive(True)

        self.verticalLayout_2.addWidget(self.menuBtn, 0, Qt.AlignLeft)


        self.verticalLayout.addWidget(self.widget)

        self.widget_3 = QWidget(self.leftMenu)
        self.widget_3.setObjectName(u"widget_3")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.widget_3.sizePolicy().hasHeightForWidth())
        self.widget_3.setSizePolicy(sizePolicy)
        self.widget_3.setMinimumSize(QSize(130, 0))
        self.verticalLayout_4 = QVBoxLayout(self.widget_3)
        self.verticalLayout_4.setSpacing(5)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(5, 5, 0, 5)
        self.homeBtn = QPushButton(self.widget_3)
        self.homeBtn.setObjectName(u"homeBtn")
        self.homeBtn.setStyleSheet(u"")
        icon1 = QIcon()
        icon1.addFile(_icon_path(u":/feather/icons/feather/home.png"), QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.homeBtn.setIcon(icon1)
        self.homeBtn.setCheckable(True)
        self.homeBtn.setAutoExclusive(True)

        self.verticalLayout_4.addWidget(self.homeBtn)

        self.manualBtn = QPushButton(self.widget_3)
        self.manualBtn.setObjectName(u"manualBtn")
        self.manualBtn.setEnabled(True)
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.manualBtn.sizePolicy().hasHeightForWidth())
        self.manualBtn.setSizePolicy(sizePolicy1)
        self.manualBtn.setMinimumSize(QSize(0, 0))
        self.manualBtn.setStyleSheet(u"")
        icon2 = QIcon()
        icon2.addFile(_icon_path(u":/material_design/icons/material_design/mode.png"), QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.manualBtn.setIcon(icon2)
        self.manualBtn.setCheckable(True)
        self.manualBtn.setAutoExclusive(True)

        self.verticalLayout_4.addWidget(self.manualBtn)

        self.autoBtn = QPushButton(self.widget_3)
        self.autoBtn.setObjectName(u"autoBtn")
        self.autoBtn.setMinimumSize(QSize(0, 0))
        self.autoBtn.setStyleSheet(u"")
        icon3 = QIcon()
        icon3.addFile(_icon_path(u":/material_design/icons/material_design/auto_mode.png"), QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.autoBtn.setIcon(icon3)
        self.autoBtn.setCheckable(True)
        self.autoBtn.setAutoExclusive(True)

        self.verticalLayout_4.addWidget(self.autoBtn)

        self.gcodeBtn = QPushButton(self.widget_3)
        self.gcodeBtn.setObjectName(u"gcodeBtn")
        self.gcodeBtn.setStyleSheet(u"")
        icon4 = QIcon()
        icon4.addFile(_icon_path(u":/feather/icons/feather/code.png"), QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.gcodeBtn.setIcon(icon4)
        self.gcodeBtn.setCheckable(True)
        self.gcodeBtn.setAutoExclusive(False)

        self.verticalLayout_4.addWidget(self.gcodeBtn)

        self.autoBtn.raise_()
        self.gcodeBtn.raise_()
        self.homeBtn.raise_()
        self.manualBtn.raise_()

        self.verticalLayout.addWidget(self.widget_3, 0, Qt.AlignTop)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.widget_2 = QWidget(self.leftMenu)
        self.widget_2.setObjectName(u"widget_2")
        self.widget_2.setMinimumSize(QSize(130, 0))
        self.verticalLayout_3 = QVBoxLayout(self.widget_2)
        self.verticalLayout_3.setSpacing(5)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(4, 5, 0, 5)
        self.settingsBtn = QPushButton(self.widget_2)
        self.settingsBtn.setObjectName(u"settingsBtn")
        self.settingsBtn.setEnabled(True)
        self.settingsBtn.setMinimumSize(QSize(0, 0))
        self.settingsBtn.setStyleSheet(u"")
        icon5 = QIcon()
        icon5.addFile(_icon_path(u":/feather/icons/feather/settings.png"), QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.settingsBtn.setIcon(icon5)
        self.settingsBtn.setCheckable(True)
        self.settingsBtn.setAutoExclusive(True)

        self.verticalLayout_3.addWidget(self.settingsBtn)

        self.helpBtn = QPushButton(self.widget_2)
        self.helpBtn.setObjectName(u"helpBtn")
        self.helpBtn.setStyleSheet(u"")
        icon6 = QIcon()
        icon6.addFile(_icon_path(u":/feather/icons/feather/help-circle.png"), QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.helpBtn.setIcon(icon6)
        self.helpBtn.setCheckable(True)
        self.helpBtn.setAutoExclusive(True)

        self.verticalLayout_3.addWidget(self.helpBtn)


        self.verticalLayout.addWidget(self.widget_2, 0, Qt.AlignBottom)

        self.widget_3.raise_()
        self.widget.raise_()
        self.widget_2.raise_()

        self.horizontalLayout.addWidget(self.leftMenu)

        self.centerMenu = QCustomSlideMenu(self.centralwidget)
        self.centerMenu.setObjectName(u"centerMenu")
        self.centerMenu.setMaximumSize(QSize(200, 16777215))
        self.verticalLayout_5 = QVBoxLayout(self.centerMenu)
        self.verticalLayout_5.setSpacing(6)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.widget_4 = QWidget(self.centerMenu)
        self.widget_4.setObjectName(u"widget_4")
        self.horizontalLayout_2 = QHBoxLayout(self.widget_4)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.closeCenterMenuBtn = QPushButton(self.widget_4)
        self.closeCenterMenuBtn.setObjectName(u"closeCenterMenuBtn")
        icon7 = QIcon()
        icon7.addFile(_icon_path(u":/feather/icons/feather/arrow-left-circle.png"), QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.closeCenterMenuBtn.setIcon(icon7)
        self.closeCenterMenuBtn.setCheckable(True)
        self.closeCenterMenuBtn.setAutoExclusive(True)

        self.horizontalLayout_2.addWidget(self.closeCenterMenuBtn, 0, Qt.AlignRight)


        self.verticalLayout_5.addWidget(self.widget_4)

        self.centerMenuPages = QCustomQStackedWidget(self.centerMenu)
        self.centerMenuPages.setObjectName(u"centerMenuPages")
        self.settingsPage = QWidget()
        self.settingsPage.setObjectName(u"settingsPage")
        self.verticalLayout_6 = QVBoxLayout(self.settingsPage)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_6.addItem(self.verticalSpacer_2)

        self.widget_5 = QWidget(self.settingsPage)
        self.widget_5.setObjectName(u"widget_5")
        self.verticalLayout_7 = QVBoxLayout(self.widget_5)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.label_3 = QLabel(self.widget_5)
        self.label_3.setObjectName(u"label_3")
        font1 = QFont()
        font1.setBold(True)
        self.label_3.setFont(font1)
        self.label_3.setStyleSheet(u"")
        self.label_3.setAlignment(Qt.AlignCenter)

        self.verticalLayout_7.addWidget(self.label_3, 0, Qt.AlignHCenter)

        self.frame = QFrame(self.widget_5)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_3 = QHBoxLayout(self.frame)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label_2 = QLabel(self.frame)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setStyleSheet(u"")
        self.label_2.setAlignment(Qt.AlignCenter)

        self.horizontalLayout_3.addWidget(self.label_2)

        self.themeList = QComboBox(self.frame)
        self.themeList.setObjectName(u"themeList")
        self.themeList.setMinimumSize(QSize(63, 0))
        self.themeList.setEditable(False)
        self.themeList.setSizeAdjustPolicy(QComboBox.AdjustToContentsOnFirstShow)
        self.themeList.setMinimumContentsLength(0)

        self.horizontalLayout_3.addWidget(self.themeList)


        self.verticalLayout_7.addWidget(self.frame)


        self.verticalLayout_6.addWidget(self.widget_5)

        self.verticalSpacer_3 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_6.addItem(self.verticalSpacer_3)

        self.centerMenuPages.addWidget(self.settingsPage)
        self.helpPage = QWidget()
        self.helpPage.setObjectName(u"helpPage")
        self.verticalLayout_8 = QVBoxLayout(self.helpPage)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.label_4 = QLabel(self.helpPage)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setStyleSheet(u"")
        self.label_4.setAlignment(Qt.AlignCenter)

        self.verticalLayout_8.addWidget(self.label_4)

        self.centerMenuPages.addWidget(self.helpPage)

        self.verticalLayout_5.addWidget(self.centerMenuPages)

        self.centerMenuPages.raise_()
        self.widget_4.raise_()

        self.horizontalLayout.addWidget(self.centerMenu)

        self.mainBody = QWidget(self.centralwidget)
        self.mainBody.setObjectName(u"mainBody")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.mainBody.sizePolicy().hasHeightForWidth())
        self.mainBody.setSizePolicy(sizePolicy2)
        self.verticalLayout_9 = QVBoxLayout(self.mainBody)
        self.verticalLayout_9.setSpacing(0)
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.verticalLayout_9.setContentsMargins(0, 0, 0, 0)
        self.header = QWidget(self.mainBody)
        self.header.setObjectName(u"header")
        self.header.setMaximumSize(QSize(16777215, 16777215))
        self.horizontalLayout_5 = QHBoxLayout(self.header)
        self.horizontalLayout_5.setSpacing(5)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.horizontalLayout_5.setContentsMargins(5, 0, 0, 5)
        self.usal = QLabel(self.header)
        self.usal.setObjectName(u"usal")
        self.usal.setMaximumSize(QSize(16777215, 35))
        self.usal.setPixmap(QPixmap(u"images/logo_usal1.png"))
        self.usal.setScaledContents(True)

        self.horizontalLayout_5.addWidget(self.usal, 0, Qt.AlignLeft|Qt.AlignVCenter)

        self.frame_2 = QFrame(self.header)
        self.frame_2.setObjectName(u"frame_2")
        self.frame_2.setMaximumSize(QSize(16777215, 16777215))
        self.frame_2.setFrameShape(QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_6 = QHBoxLayout(self.frame_2)
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.connectionBtn = QPushButton(self.frame_2)
        self.connectionBtn.setObjectName(u"connectionBtn")
        icon8 = QIcon()
        icon8.addFile(_icon_path(u":/material_design/icons/material_design/connect_without_contact.png"), QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.connectionBtn.setIcon(icon8)

        self.horizontalLayout_6.addWidget(self.connectionBtn)

        self.calibrationBtn = QPushButton(self.frame_2)
        self.calibrationBtn.setObjectName(u"calibrationBtn")
        icon9 = QIcon()
        icon9.addFile(_icon_path(u":/material_design/icons/material_design/control_camera.png"), QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.calibrationBtn.setIcon(icon9)

        self.horizontalLayout_6.addWidget(self.calibrationBtn)


        self.horizontalLayout_5.addWidget(self.frame_2, 0, Qt.AlignHCenter|Qt.AlignBottom)

        self.frame_3 = QFrame(self.header)
        self.frame_3.setObjectName(u"frame_3")
        self.frame_3.setMaximumSize(QSize(16777215, 16777215))
        self.frame_3.setFrameShape(QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_7 = QHBoxLayout(self.frame_3)
        self.horizontalLayout_7.setSpacing(0)
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.horizontalLayout_7.setContentsMargins(0, 0, 0, 0)
        self.minimizeBtn = QPushButton(self.frame_3)
        self.minimizeBtn.setObjectName(u"minimizeBtn")
        icon10 = QIcon()
        icon10.addFile(_icon_path(u":/feather/icons/feather/window_minimize.png"), QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.minimizeBtn.setIcon(icon10)

        self.horizontalLayout_7.addWidget(self.minimizeBtn)

        self.restoreBtn = QPushButton(self.frame_3)
        self.restoreBtn.setObjectName(u"restoreBtn")
        icon11 = QIcon()
        icon11.addFile(_icon_path(u":/feather/icons/feather/square.png"), QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.restoreBtn.setIcon(icon11)

        self.horizontalLayout_7.addWidget(self.restoreBtn)

        self.closeBtn = QPushButton(self.frame_3)
        self.closeBtn.setObjectName(u"closeBtn")
        icon12 = QIcon()
        icon12.addFile(_icon_path(u":/feather/icons/feather/window_close.png"), QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.closeBtn.setIcon(icon12)

        self.horizontalLayout_7.addWidget(self.closeBtn)


        self.horizontalLayout_5.addWidget(self.frame_3, 0, Qt.AlignRight|Qt.AlignTop)


        self.verticalLayout_9.addWidget(self.header)

        self.mainContents = QWidget(self.mainBody)
        self.mainContents.setObjectName(u"mainContents")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.mainContents.sizePolicy().hasHeightForWidth())
        self.mainContents.setSizePolicy(sizePolicy3)
        self.horizontalLayout_8 = QHBoxLayout(self.mainContents)
        self.horizontalLayout_8.setSpacing(0)
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.horizontalLayout_8.setContentsMargins(5, 0, 5, 0)
        self.mainPagesCont = QWidget(self.mainContents)
        self.mainPagesCont.setObjectName(u"mainPagesCont")
        self.verticalLayout_11 = QVBoxLayout(self.mainPagesCont)
        self.verticalLayout_11.setSpacing(0)
        self.verticalLayout_11.setObjectName(u"verticalLayout_11")
        self.verticalLayout_11.setContentsMargins(0, 5, 0, 5)
        self.mainPages = QCustomQStackedWidget(self.mainPagesCont)
        self.mainPages.setObjectName(u"mainPages")
        self.homePage = QWidget()
        self.homePage.setObjectName(u"homePage")
        sizePolicy4 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.homePage.sizePolicy().hasHeightForWidth())
        self.homePage.setSizePolicy(sizePolicy4)
        self.verticalLayout_home = QVBoxLayout(self.homePage)
        self.verticalLayout_home.setObjectName(u"verticalLayout_home")

        # ── Banner superior de conexión + STO ──────────────────────────
        self.statusBanner = QFrame(self.homePage)
        self.statusBanner.setObjectName(u"statusBanner")
        self.statusBanner.setMinimumSize(QSize(0, 40))
        self.statusBanner.setMaximumSize(QSize(16777215, 48))
        self.statusBanner.setFrameShape(QFrame.StyledPanel)
        self.statusBanner.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_banner = QHBoxLayout(self.statusBanner)
        self.horizontalLayout_banner.setObjectName(u"horizontalLayout_banner")

        self.connectionRow = QFrame(self.statusBanner)
        self.connectionRow.setObjectName(u"connectionRow")
        self.horizontalLayout_connectionRow = QHBoxLayout(self.connectionRow)
        self.horizontalLayout_connectionRow.setObjectName(u"horizontalLayout_connectionRow")
        self.labelConexion = QLabel(self.connectionRow)
        self.labelConexion.setObjectName(u"labelConexion")
        self.horizontalLayout_connectionRow.addWidget(self.labelConexion)

        self.horizontalLayout_banner.addWidget(self.connectionRow, 0, Qt.AlignLeft|Qt.AlignVCenter)

        self.horizontalSpacer_banner = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_banner.addItem(self.horizontalSpacer_banner)

        self.stoRow = QFrame(self.statusBanner)
        self.stoRow.setObjectName(u"stoRow")
        self.horizontalLayout_stoRow = QHBoxLayout(self.stoRow)
        self.horizontalLayout_stoRow.setObjectName(u"horizontalLayout_stoRow")
        self.labelSTO = QLabel(self.stoRow)
        self.labelSTO.setObjectName(u"labelSTO")
        self.horizontalLayout_stoRow.addWidget(self.labelSTO)

        self.horizontalLayout_banner.addWidget(self.stoRow, 0, Qt.AlignRight|Qt.AlignVCenter)

        self.verticalLayout_home.addWidget(self.statusBanner)

        self.horizontalLayout_18 = QHBoxLayout()
        self.horizontalLayout_18.setObjectName(u"horizontalLayout_18")
        self.horizontalSpacer_7 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_18.addItem(self.horizontalSpacer_7)

        self.positionStatus = QWidget(self.homePage)
        self.positionStatus.setObjectName(u"positionStatus")
        self.verticalLayout_20 = QVBoxLayout(self.positionStatus)
        self.verticalLayout_20.setObjectName(u"verticalLayout_20")
        self.posicionZ = QFrame(self.positionStatus)
        self.posicionZ.setObjectName(u"posicionZ")
        self.posicionZ.setFrameShape(QFrame.StyledPanel)
        self.posicionZ.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_12 = QHBoxLayout(self.posicionZ)
        self.horizontalLayout_12.setObjectName(u"horizontalLayout_12")
        self.horizontalLayout_12.setContentsMargins(115, -1, -1, -1)
        self.label_12 = QLabel(self.posicionZ)
        self.label_12.setObjectName(u"label_12")

        self.horizontalLayout_12.addWidget(self.label_12, 0, Qt.AlignRight|Qt.AlignBottom)

        self.valorZ = QLabel(self.posicionZ)
        self.valorZ.setObjectName(u"valorZ")

        self.horizontalLayout_12.addWidget(self.valorZ, 0, Qt.AlignLeft|Qt.AlignBottom)


        self.verticalLayout_20.addWidget(self.posicionZ, 0, Qt.AlignLeft|Qt.AlignVCenter)

        self.ledRowZ = QFrame(self.positionStatus)
        self.ledRowZ.setObjectName(u"ledRowZ")
        self.horizontalLayout_ledRowZ = QHBoxLayout(self.ledRowZ)
        self.horizontalLayout_ledRowZ.setObjectName(u"horizontalLayout_ledRowZ")

        self.verticalLayout_20.addWidget(self.ledRowZ, 0, Qt.AlignHCenter)

        self.posicionY = QFrame(self.positionStatus)
        self.posicionY.setObjectName(u"posicionY")
        self.posicionY.setFrameShape(QFrame.StyledPanel)
        self.posicionY.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_10 = QHBoxLayout(self.posicionY)
        self.horizontalLayout_10.setObjectName(u"horizontalLayout_10")
        self.estacionAerotech = QLabel(self.posicionY)
        self.estacionAerotech.setObjectName(u"estacionAerotech")
        self.estacionAerotech.setPixmap(QPixmap(u"images/Estacion nanoposicionamiento.png"))
        self.estacionAerotech.setScaledContents(True)

        self.horizontalLayout_10.addWidget(self.estacionAerotech, 0, Qt.AlignHCenter|Qt.AlignVCenter)

        self.frame_11 = QFrame(self.posicionY)
        self.frame_11.setObjectName(u"frame_11")
        self.frame_11.setFrameShape(QFrame.StyledPanel)
        self.frame_11.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_14 = QHBoxLayout(self.frame_11)
        self.horizontalLayout_14.setObjectName(u"horizontalLayout_14")
        self.label_14 = QLabel(self.frame_11)
        self.label_14.setObjectName(u"label_14")

        self.horizontalLayout_14.addWidget(self.label_14)

        self.valorY = QLabel(self.frame_11)
        self.valorY.setObjectName(u"valorY")

        self.horizontalLayout_14.addWidget(self.valorY)


        self.horizontalLayout_10.addWidget(self.frame_11, 0, Qt.AlignLeft|Qt.AlignBottom)


        self.verticalLayout_20.addWidget(self.posicionY, 0, Qt.AlignHCenter|Qt.AlignVCenter)

        self.ledRowY = QFrame(self.positionStatus)
        self.ledRowY.setObjectName(u"ledRowY")
        self.horizontalLayout_ledRowY = QHBoxLayout(self.ledRowY)
        self.horizontalLayout_ledRowY.setObjectName(u"horizontalLayout_ledRowY")

        self.verticalLayout_20.addWidget(self.ledRowY, 0, Qt.AlignHCenter)

        self.posicionX = QFrame(self.positionStatus)
        self.posicionX.setObjectName(u"posicionX")
        self.posicionX.setFrameShape(QFrame.StyledPanel)
        self.posicionX.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_11 = QHBoxLayout(self.posicionX)
        self.horizontalLayout_11.setObjectName(u"horizontalLayout_11")
        self.horizontalLayout_11.setContentsMargins(50, -1, -1, -1)
        self.label_16 = QLabel(self.posicionX)
        self.label_16.setObjectName(u"label_16")

        self.horizontalLayout_11.addWidget(self.label_16, 0, Qt.AlignRight)

        self.valorX = QLabel(self.posicionX)
        self.valorX.setObjectName(u"valorX")

        self.horizontalLayout_11.addWidget(self.valorX, 0, Qt.AlignLeft|Qt.AlignVCenter)


        self.verticalLayout_20.addWidget(self.posicionX, 0, Qt.AlignLeft|Qt.AlignVCenter)

        self.ledRowX = QFrame(self.positionStatus)
        self.ledRowX.setObjectName(u"ledRowX")
        self.horizontalLayout_ledRowX = QHBoxLayout(self.ledRowX)
        self.horizontalLayout_ledRowX.setObjectName(u"horizontalLayout_ledRowX")

        self.verticalLayout_20.addWidget(self.ledRowX, 0, Qt.AlignHCenter)


        self.horizontalLayout_18.addWidget(self.positionStatus, 0, Qt.AlignHCenter)

        self.horizontalSpacer_6 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_18.addItem(self.horizontalSpacer_6)

        self.cardsFrame = QWidget(self.homePage)
        self.cardsFrame.setObjectName(u"cardsFrame")
        self.verticalLayout_10 = QVBoxLayout(self.cardsFrame)
        self.verticalLayout_10.setObjectName(u"verticalLayout_10")
        self.verticalSpacer_20 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_10.addItem(self.verticalSpacer_20)

        self.laserOutputCard = QFrame(self.cardsFrame)
        self.laserOutputCard.setObjectName(u"laserOutputCard")
        self.laserOutputCard.setStyleSheet(u"")
        self.laserOutputCard.setFrameShape(QFrame.StyledPanel)
        self.laserOutputCard.setFrameShadow(QFrame.Raised)
        self.verticalLayout_laser = QVBoxLayout(self.laserOutputCard)
        self.verticalLayout_laser.setObjectName(u"verticalLayout_laser")
        self.laserIcon = QLabel(self.laserOutputCard)
        self.laserIcon.setObjectName(u"laserIcon")
        sizePolicy5 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        sizePolicy5.setHorizontalStretch(0)
        sizePolicy5.setVerticalStretch(0)
        sizePolicy5.setHeightForWidth(self.laserIcon.sizePolicy().hasHeightForWidth())
        self.laserIcon.setSizePolicy(sizePolicy5)
        self.laserIcon.setMinimumSize(QSize(50, 50))
        self.laserIcon.setMaximumSize(QSize(50, 50))
        self.laserIcon.setPixmap(QPixmap(_icon_path(u":/feather/icons/feather/zap.png")))
        self.laserIcon.setScaledContents(True)

        self.verticalLayout_laser.addWidget(self.laserIcon, 0, Qt.AlignHCenter|Qt.AlignVCenter)

        self.laserTitleLabel = QLabel(self.laserOutputCard)
        self.laserTitleLabel.setObjectName(u"laserTitleLabel")
        font2 = QFont()
        font2.setPointSize(11)
        font2.setBold(True)
        self.laserTitleLabel.setFont(font2)

        self.verticalLayout_laser.addWidget(self.laserTitleLabel, 0, Qt.AlignHCenter|Qt.AlignVCenter)

        self.laserStateRow = QFrame(self.laserOutputCard)
        self.laserStateRow.setObjectName(u"laserStateRow")
        self.laserStateRow.setFrameShape(QFrame.StyledPanel)
        self.laserStateRow.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_laserState = QHBoxLayout(self.laserStateRow)
        self.horizontalLayout_laserState.setObjectName(u"horizontalLayout_laserState")
        self.labelLaserState = QLabel(self.laserStateRow)
        self.labelLaserState.setObjectName(u"labelLaserState")
        self.horizontalLayout_laserState.addWidget(self.labelLaserState)

        self.verticalLayout_laser.addWidget(self.laserStateRow, 0, Qt.AlignHCenter|Qt.AlignVCenter)

        self.estadoPotencia = QLineEdit(self.laserOutputCard)
        self.estadoPotencia.setObjectName(u"estadoPotencia")
        self.estadoPotencia.setReadOnly(True)
        self.estadoPotencia.setAlignment(Qt.AlignCenter)
        self.estadoPotencia.setFont(QFont("Sitka Small", 9, QFont.Weight.Bold))
        self.estadoPotencia.setMinimumSize(QSize(200, 32))
        self.estadoPotencia.setMaximumSize(QSize(300, 32))
        self.estadoPotencia.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        self.verticalLayout_laser.addWidget(self.estadoPotencia, 0, Qt.AlignHCenter|Qt.AlignVCenter)

        self.laserInterlockRow = QFrame(self.laserOutputCard)
        self.laserInterlockRow.setObjectName(u"laserInterlockRow")
        self.laserInterlockRow.setFrameShape(QFrame.StyledPanel)
        self.laserInterlockRow.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_laserInterlock = QHBoxLayout(self.laserInterlockRow)
        self.horizontalLayout_laserInterlock.setObjectName(u"horizontalLayout_laserInterlock")
        self.labelInterlock = QLabel(self.laserInterlockRow)
        self.labelInterlock.setObjectName(u"labelInterlock")
        self.horizontalLayout_laserInterlock.addWidget(self.labelInterlock)

        self.verticalLayout_laser.addWidget(self.laserInterlockRow, 0, Qt.AlignHCenter|Qt.AlignVCenter)


        self.verticalLayout_10.addWidget(self.laserOutputCard)

        self.verticalSpacer_19 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_10.addItem(self.verticalSpacer_19)


        self.horizontalLayout_18.addWidget(self.cardsFrame, 0, Qt.AlignHCenter)

        self.horizontalSpacer_8 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_18.addItem(self.horizontalSpacer_8)

        self.verticalLayout_home.addLayout(self.horizontalLayout_18)


        self.mainPages.addWidget(self.homePage)
        self.manualPage = QWidget()
        self.manualPage.setObjectName(u"manualPage")
        sizePolicy4.setHeightForWidth(self.manualPage.sizePolicy().hasHeightForWidth())
        self.manualPage.setSizePolicy(sizePolicy4)
        self.horizontalLayout_20 = QHBoxLayout(self.manualPage)
        self.horizontalLayout_20.setObjectName(u"horizontalLayout_20")
        self.movementManual = QWidget(self.manualPage)
        self.movementManual.setObjectName(u"movementManual")
        self.verticalLayout_22 = QVBoxLayout(self.movementManual)
        self.verticalLayout_22.setObjectName(u"verticalLayout_22")
        self.verticalLayout_22.setContentsMargins(30, -1, 25, -1)
        self.frame_19 = QFrame(self.movementManual)
        self.frame_19.setObjectName(u"frame_19")
        self.frame_19.setFrameShape(QFrame.StyledPanel)
        self.frame_19.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_15 = QHBoxLayout(self.frame_19)
        self.horizontalLayout_15.setObjectName(u"horizontalLayout_15")
        self.label_36 = QLabel(self.frame_19)
        self.label_36.setObjectName(u"label_36")
        sizePolicy8 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy8.setHorizontalStretch(0)
        sizePolicy8.setVerticalStretch(0)
        sizePolicy8.setHeightForWidth(self.label_36.sizePolicy().hasHeightForWidth())
        self.label_36.setSizePolicy(sizePolicy8)
        self.label_36.setMinimumSize(QSize(25, 25))
        self.label_36.setMaximumSize(QSize(25, 25))
        self.label_36.setPixmap(QPixmap(_icon_path(u":/feather/icons/feather/mouse-pointer.png")))
        self.label_36.setScaledContents(True)

        self.horizontalLayout_15.addWidget(self.label_36)

        self.label_19 = QLabel(self.frame_19)
        self.label_19.setObjectName(u"label_19")
        self.label_19.setFont(font2)

        self.horizontalLayout_15.addWidget(self.label_19)


        self.verticalLayout_22.addWidget(self.frame_19)

        self.frame_8 = QFrame(self.movementManual)
        self.frame_8.setObjectName(u"frame_8")
        self.frame_8.setFrameShape(QFrame.StyledPanel)
        self.frame_8.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_19 = QHBoxLayout(self.frame_8)
        self.horizontalLayout_19.setObjectName(u"horizontalLayout_19")
        self.frame_4 = QFrame(self.frame_8)
        self.frame_4.setObjectName(u"frame_4")
        self.frame_4.setFrameShape(QFrame.StyledPanel)
        self.frame_4.setFrameShadow(QFrame.Raised)
        self.gridLayout_4 = QGridLayout(self.frame_4)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.label_31 = QLabel(self.frame_4)
        self.label_31.setObjectName(u"label_31")

        self.gridLayout_4.addWidget(self.label_31, 0, 0, 1, 1)

        self.label_32 = QLabel(self.frame_4)
        self.label_32.setObjectName(u"label_32")

        self.gridLayout_4.addWidget(self.label_32, 0, 2, 1, 1)

        self.label_33 = QLabel(self.frame_4)
        self.label_33.setObjectName(u"label_33")

        self.gridLayout_4.addWidget(self.label_33, 0, 4, 1, 1)

        self.scaleList = QComboBox(self.frame_4)
        self.scaleList.setObjectName(u"scaleList")
        sizePolicy1.setHeightForWidth(self.scaleList.sizePolicy().hasHeightForWidth())
        self.scaleList.setSizePolicy(sizePolicy1)
        self.scaleList.setMinimumSize(QSize(0, 0))
        self.scaleList.setMaximumSize(QSize(16777215, 16777215))
        self.scaleList.setStyleSheet(u"outline: none")

        self.gridLayout_4.addWidget(self.scaleList, 1, 0, 1, 1)

        self.acceleration = QDoubleSpinBox(self.frame_4)
        self.acceleration.setObjectName(u"acceleration")
        sizePolicy1.setHeightForWidth(self.acceleration.sizePolicy().hasHeightForWidth())
        self.acceleration.setSizePolicy(sizePolicy1)
        self.acceleration.setMinimumSize(QSize(0, 0))
        self.acceleration.setMaximumSize(QSize(16777215, 16777215))

        self.gridLayout_4.addWidget(self.acceleration, 1, 4, 1, 1)

        self.velocity = QDoubleSpinBox(self.frame_4)
        self.velocity.setObjectName(u"velocity")
        sizePolicy1.setHeightForWidth(self.velocity.sizePolicy().hasHeightForWidth())
        self.velocity.setSizePolicy(sizePolicy1)
        self.velocity.setMinimumSize(QSize(0, 0))
        self.velocity.setMaximumSize(QSize(16777215, 16777215))

        self.gridLayout_4.addWidget(self.velocity, 1, 2, 1, 1)

        self.horizontalSpacer_2 = QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_4.addItem(self.horizontalSpacer_2, 1, 1, 1, 1)

        self.horizontalSpacer_11 = QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_4.addItem(self.horizontalSpacer_11, 1, 3, 1, 1)

        self.horizontalSpacer_5 = QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_4.addItem(self.horizontalSpacer_5, 1, 5, 1, 1)


        self.horizontalLayout_19.addWidget(self.frame_4)

        self.confirmBtn = QPushButton(self.frame_8)
        self.confirmBtn.setObjectName(u"confirmBtn")
        sizePolicy8.setHeightForWidth(self.confirmBtn.sizePolicy().hasHeightForWidth())
        self.confirmBtn.setSizePolicy(sizePolicy8)
        self.confirmBtn.setMinimumSize(QSize(64, 64))
        self.confirmBtn.setMaximumSize(QSize(64, 64))
        icon13 = QIcon()
        icon13.addFile(_icon_path(u":/feather/icons/feather/check-circle.png"), QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.confirmBtn.setIcon(icon13)

        self.horizontalLayout_19.addWidget(self.confirmBtn)


        self.verticalLayout_22.addWidget(self.frame_8, 0, Qt.AlignHCenter)

        self.verticalSpacer_5 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_22.addItem(self.verticalSpacer_5)

        self.widget_8 = QWidget(self.movementManual)
        self.widget_8.setObjectName(u"widget_8")
        self.horizontalLayout_16 = QHBoxLayout(self.widget_8)
        self.horizontalLayout_16.setObjectName(u"horizontalLayout_16")
        self.frameCircular = QFrame(self.widget_8)
        self.frameCircular.setObjectName(u"frameCircular")
        sizePolicy8.setHeightForWidth(self.frameCircular.sizePolicy().hasHeightForWidth())
        self.frameCircular.setSizePolicy(sizePolicy8)
        self.frameCircular.setMinimumSize(QSize(240, 240))
        self.frameCircular.setMaximumSize(QSize(240, 240))
        self.frameCircular.setStyleSheet(u"")
        self.frameCircular.setFrameShape(QFrame.StyledPanel)
        self.frameCircular.setFrameShadow(QFrame.Raised)
        self.gridLayout_3 = QGridLayout(self.frameCircular)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.gridLayout_6 = QGridLayout()
        self.gridLayout_6.setSpacing(4)
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.gridLayout_6.setContentsMargins(0, 0, 0, 0)
        self.labelXMinus = QLabel(self.frameCircular)
        self.labelXMinus.setObjectName(u"labelXMinus")
        sizePolicy8.setHeightForWidth(self.labelXMinus.sizePolicy().hasHeightForWidth())
        self.labelXMinus.setSizePolicy(sizePolicy8)
        self.labelXMinus.setMinimumSize(QSize(25, 25))
        self.labelXMinus.setMaximumSize(QSize(25, 25))
        font3 = QFont()
        font3.setFamilies([u"Sitka Small"])
        font3.setPointSize(9)
        font3.setBold(False)
        self.labelXMinus.setFont(font3)
        self.labelXMinus.setAlignment(Qt.AlignCenter)

        self.gridLayout_6.addWidget(self.labelXMinus, 2, 0, 1, 1, Qt.AlignHCenter|Qt.AlignVCenter)

        self.labelYPlus = QLabel(self.frameCircular)
        self.labelYPlus.setObjectName(u"labelYPlus")
        sizePolicy8.setHeightForWidth(self.labelYPlus.sizePolicy().hasHeightForWidth())
        self.labelYPlus.setSizePolicy(sizePolicy8)
        self.labelYPlus.setMinimumSize(QSize(25, 25))
        self.labelYPlus.setMaximumSize(QSize(25, 25))
        self.labelYPlus.setFont(font3)
        self.labelYPlus.setAlignment(Qt.AlignCenter)
        self.labelYPlus.setMargin(0)

        self.gridLayout_6.addWidget(self.labelYPlus, 0, 2, 1, 1, Qt.AlignHCenter|Qt.AlignVCenter)

        self.xyUpBtn = QPushButton(self.frameCircular)
        self.xyUpBtn.setObjectName(u"xyUpBtn")
        self.xyUpBtn.setEnabled(True)
        sizePolicy8.setHeightForWidth(self.xyUpBtn.sizePolicy().hasHeightForWidth())
        self.xyUpBtn.setSizePolicy(sizePolicy8)
        self.xyUpBtn.setMinimumSize(QSize(40, 40))
        self.xyUpBtn.setMaximumSize(QSize(40, 40))
        icon14 = QIcon()
        icon14.addFile(_icon_path(u":/feather/icons/feather/arrow_up.png"), QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.xyUpBtn.setIcon(icon14)
        self.xyUpBtn.setCheckable(False)
        self.xyUpBtn.setAutoExclusive(False)

        self.gridLayout_6.addWidget(self.xyUpBtn, 1, 2, 1, 1, Qt.AlignHCenter|Qt.AlignVCenter)

        self.xyLeftBtn = QPushButton(self.frameCircular)
        self.xyLeftBtn.setObjectName(u"xyLeftBtn")
        sizePolicy8.setHeightForWidth(self.xyLeftBtn.sizePolicy().hasHeightForWidth())
        self.xyLeftBtn.setSizePolicy(sizePolicy8)
        self.xyLeftBtn.setMinimumSize(QSize(40, 40))
        self.xyLeftBtn.setMaximumSize(QSize(40, 40))
        icon15 = QIcon()
        icon15.addFile(_icon_path(u":/feather/icons/feather/arrow_left.png"), QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.xyLeftBtn.setIcon(icon15)
        self.xyLeftBtn.setCheckable(False)
        self.xyLeftBtn.setAutoExclusive(False)

        self.gridLayout_6.addWidget(self.xyLeftBtn, 2, 1, 1, 1, Qt.AlignHCenter|Qt.AlignVCenter)

        self.xyZeroBtn = QPushButton(self.frameCircular)
        self.xyZeroBtn.setObjectName(u"xyZeroBtn")
        sizePolicy8.setHeightForWidth(self.xyZeroBtn.sizePolicy().hasHeightForWidth())
        self.xyZeroBtn.setSizePolicy(sizePolicy8)
        self.xyZeroBtn.setMinimumSize(QSize(30, 30))
        self.xyZeroBtn.setMaximumSize(QSize(30, 30))
        self.xyZeroBtn.setStyleSheet(u"")
        icon16 = QIcon()
        icon16.addFile(_icon_path(u":/feather/icons/feather/stop-circle.png"), QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.xyZeroBtn.setIcon(icon16)
        self.xyZeroBtn.setCheckable(False)
        self.xyZeroBtn.setAutoExclusive(False)

        self.gridLayout_6.addWidget(self.xyZeroBtn, 2, 2, 1, 1, Qt.AlignHCenter|Qt.AlignVCenter)

        self.xyRightBtn = QPushButton(self.frameCircular)
        self.xyRightBtn.setObjectName(u"xyRightBtn")
        sizePolicy8.setHeightForWidth(self.xyRightBtn.sizePolicy().hasHeightForWidth())
        self.xyRightBtn.setSizePolicy(sizePolicy8)
        self.xyRightBtn.setMinimumSize(QSize(40, 40))
        self.xyRightBtn.setMaximumSize(QSize(40, 40))
        icon17 = QIcon()
        icon17.addFile(_icon_path(u":/feather/icons/feather/arrow_right.png"), QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.xyRightBtn.setIcon(icon17)
        self.xyRightBtn.setCheckable(False)
        self.xyRightBtn.setAutoExclusive(False)

        self.gridLayout_6.addWidget(self.xyRightBtn, 2, 3, 1, 1, Qt.AlignHCenter|Qt.AlignVCenter)

        self.xyDownBtn = QPushButton(self.frameCircular)
        self.xyDownBtn.setObjectName(u"xyDownBtn")
        sizePolicy8.setHeightForWidth(self.xyDownBtn.sizePolicy().hasHeightForWidth())
        self.xyDownBtn.setSizePolicy(sizePolicy8)
        self.xyDownBtn.setMinimumSize(QSize(40, 40))
        self.xyDownBtn.setMaximumSize(QSize(40, 40))
        icon18 = QIcon()
        icon18.addFile(_icon_path(u":/feather/icons/feather/arrow_down.png"), QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.xyDownBtn.setIcon(icon18)
        self.xyDownBtn.setCheckable(False)
        self.xyDownBtn.setAutoExclusive(False)

        self.gridLayout_6.addWidget(self.xyDownBtn, 3, 2, 1, 1, Qt.AlignHCenter|Qt.AlignVCenter)

        self.labelXPlus = QLabel(self.frameCircular)
        self.labelXPlus.setObjectName(u"labelXPlus")
        sizePolicy8.setHeightForWidth(self.labelXPlus.sizePolicy().hasHeightForWidth())
        self.labelXPlus.setSizePolicy(sizePolicy8)
        self.labelXPlus.setMinimumSize(QSize(25, 25))
        self.labelXPlus.setMaximumSize(QSize(25, 25))
        self.labelXPlus.setFont(font3)
        self.labelXPlus.setAlignment(Qt.AlignCenter)

        self.gridLayout_6.addWidget(self.labelXPlus, 2, 4, 1, 1, Qt.AlignHCenter|Qt.AlignVCenter)

        self.labelYMinus = QLabel(self.frameCircular)
        self.labelYMinus.setObjectName(u"labelYMinus")
        sizePolicy8.setHeightForWidth(self.labelYMinus.sizePolicy().hasHeightForWidth())
        self.labelYMinus.setSizePolicy(sizePolicy8)
        self.labelYMinus.setMinimumSize(QSize(25, 25))
        self.labelYMinus.setMaximumSize(QSize(25, 25))
        self.labelYMinus.setFont(font3)
        self.labelYMinus.setAlignment(Qt.AlignCenter)

        self.gridLayout_6.addWidget(self.labelYMinus, 4, 2, 1, 1, Qt.AlignHCenter|Qt.AlignVCenter)


        self.gridLayout_3.addLayout(self.gridLayout_6, 0, 0, 1, 1)


        self.horizontalLayout_16.addWidget(self.frameCircular)

        self.horizontalSpacer_12 = QSpacerItem(30, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_16.addItem(self.horizontalSpacer_12)

        self.frameRectangular = QFrame(self.widget_8)
        self.frameRectangular.setObjectName(u"frameRectangular")
        self.frameRectangular.setStyleSheet(u"")
        self.frameRectangular.setFrameShape(QFrame.StyledPanel)
        self.frameRectangular.setFrameShadow(QFrame.Raised)
        self.verticalLayout_13 = QVBoxLayout(self.frameRectangular)
        self.verticalLayout_13.setObjectName(u"verticalLayout_13")
        self.frame_20 = QFrame(self.frameRectangular)
        self.frame_20.setObjectName(u"frame_20")
        sizePolicy.setHeightForWidth(self.frame_20.sizePolicy().hasHeightForWidth())
        self.frame_20.setSizePolicy(sizePolicy)
        self.frame_20.setStyleSheet(u"")
        self.frame_20.setFrameShape(QFrame.StyledPanel)
        self.frame_20.setFrameShadow(QFrame.Raised)
        self.verticalLayout_23 = QVBoxLayout(self.frame_20)
        self.verticalLayout_23.setObjectName(u"verticalLayout_23")
        self.labelZPlus = QLabel(self.frame_20)
        self.labelZPlus.setObjectName(u"labelZPlus")
        self.labelZPlus.setFont(font3)

        self.verticalLayout_23.addWidget(self.labelZPlus, 0, Qt.AlignHCenter|Qt.AlignTop)

        self.zUpBtn = QPushButton(self.frame_20)
        self.zUpBtn.setObjectName(u"zUpBtn")
        font4 = QFont()
        font4.setPointSize(9)
        self.zUpBtn.setFont(font4)
        self.zUpBtn.setIcon(icon14)
        self.zUpBtn.setCheckable(False)
        self.zUpBtn.setAutoExclusive(False)

        self.verticalLayout_23.addWidget(self.zUpBtn, 0, Qt.AlignHCenter|Qt.AlignVCenter)

        self.label_35 = QLabel(self.frame_20)
        self.label_35.setObjectName(u"label_35")
        sizePolicy8.setHeightForWidth(self.label_35.sizePolicy().hasHeightForWidth())
        self.label_35.setSizePolicy(sizePolicy8)
        self.label_35.setMinimumSize(QSize(16, 16))
        self.label_35.setMaximumSize(QSize(16, 24))
        font5 = QFont()
        font5.setPointSize(14)
        font5.setBold(True)
        self.label_35.setFont(font5)
        self.label_35.setScaledContents(True)
        self.label_35.setAlignment(Qt.AlignCenter)

        self.verticalLayout_23.addWidget(self.label_35, 0, Qt.AlignHCenter|Qt.AlignVCenter)

        self.zDownBtn = QPushButton(self.frame_20)
        self.zDownBtn.setObjectName(u"zDownBtn")
        self.zDownBtn.setIcon(icon18)
        self.zDownBtn.setCheckable(False)
        self.zDownBtn.setAutoExclusive(False)

        self.verticalLayout_23.addWidget(self.zDownBtn, 0, Qt.AlignHCenter|Qt.AlignVCenter)

        self.labelZMinus = QLabel(self.frame_20)
        self.labelZMinus.setObjectName(u"labelZMinus")
        self.labelZMinus.setFont(font3)

        self.verticalLayout_23.addWidget(self.labelZMinus, 0, Qt.AlignHCenter)


        self.verticalLayout_13.addWidget(self.frame_20)


        self.horizontalLayout_16.addWidget(self.frameRectangular)


        self.verticalLayout_22.addWidget(self.widget_8, 0, Qt.AlignHCenter)

        self.verticalSpacer_10 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_22.addItem(self.verticalSpacer_10)


        self.horizontalLayout_20.addWidget(self.movementManual)

        self.horizontalSpacer_9 = QSpacerItem(25, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_20.addItem(self.horizontalSpacer_9)

        self.shutterManual = QFrame(self.manualPage)
        self.shutterManual.setObjectName(u"shutterManual")
        self.shutterManual.setFrameShape(QFrame.StyledPanel)
        self.shutterManual.setFrameShadow(QFrame.Raised)
        self.verticalLayout_21 = QVBoxLayout(self.shutterManual)
        self.verticalLayout_21.setObjectName(u"verticalLayout_21")
        self.verticalLayout_21.setContentsMargins(6, -1, -1, -1)
        self.frame_6 = QFrame(self.shutterManual)
        self.frame_6.setObjectName(u"frame_6")
        self.frame_6.setFrameShape(QFrame.StyledPanel)
        self.frame_6.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_17 = QHBoxLayout(self.frame_6)
        self.horizontalLayout_17.setObjectName(u"horizontalLayout_17")
        self.label_8 = QLabel(self.frame_6)
        self.label_8.setObjectName(u"label_8")
        sizePolicy8.setHeightForWidth(self.label_8.sizePolicy().hasHeightForWidth())
        self.label_8.setSizePolicy(sizePolicy8)
        self.label_8.setMinimumSize(QSize(25, 25))
        self.label_8.setMaximumSize(QSize(25, 25))
        self.label_8.setPixmap(QPixmap(_icon_path(u":/font_awesome_solid/icons/font_awesome/solid/bolt.png")))
        self.label_8.setScaledContents(True)
        self.label_8.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.horizontalLayout_17.addWidget(self.label_8)

        self.label_7 = QLabel(self.frame_6)
        self.label_7.setObjectName(u"label_7")
        self.label_7.setFont(font2)

        self.horizontalLayout_17.addWidget(self.label_7)


        self.verticalLayout_21.addWidget(self.frame_6)

        self.verticalSpacer_11 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_21.addItem(self.verticalSpacer_11)

        self.laserOC = QLabel(self.shutterManual)
        self.laserOC.setObjectName(u"laserOC")
        sizePolicy9 = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)
        sizePolicy9.setHorizontalStretch(0)
        sizePolicy9.setVerticalStretch(0)
        sizePolicy9.setHeightForWidth(self.laserOC.sizePolicy().hasHeightForWidth())
        self.laserOC.setSizePolicy(sizePolicy9)
        self.laserOC.setMinimumSize(QSize(80, 80))
        self.laserOC.setMaximumSize(QSize(130, 130))
        self.laserOC.setStyleSheet(u"")
        self.laserOC.setPixmap(QPixmap(u"images/laserOC4.png"))
        self.laserOC.setScaledContents(True)
        self.laserOC.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.laserOC.setMargin(3)

        self.verticalLayout_21.addWidget(self.laserOC)

        self.verticalSpacer_12 = QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_21.addItem(self.verticalSpacer_12)

        self.frame_7 = QFrame(self.shutterManual)
        self.frame_7.setObjectName(u"frame_7")
        sizePolicy4.setHeightForWidth(self.frame_7.sizePolicy().hasHeightForWidth())
        self.frame_7.setSizePolicy(sizePolicy4)
        self.frame_7.setFrameShape(QFrame.StyledPanel)
        self.frame_7.setFrameShadow(QFrame.Raised)
        self.verticalLayout_34 = QVBoxLayout(self.frame_7)
        self.verticalLayout_34.setObjectName(u"verticalLayout_34")
        self.openShutterBtn = QPushButton(self.frame_7)
        self.openShutterBtn.setObjectName(u"openShutterBtn")
        self.openShutterBtn.setFont(font1)
        self.openShutterBtn.setCheckable(False)
        self.openShutterBtn.setAutoExclusive(False)

        self.verticalLayout_34.addWidget(self.openShutterBtn)

        self.closeShutterBtn = QPushButton(self.frame_7)
        self.closeShutterBtn.setObjectName(u"closeShutterBtn")
        self.closeShutterBtn.setFont(font1)
        self.closeShutterBtn.setCheckable(False)
        self.closeShutterBtn.setAutoExclusive(False)

        self.verticalLayout_34.addWidget(self.closeShutterBtn)


        self.verticalLayout_21.addWidget(self.frame_7, 0, Qt.AlignVCenter)

        self.verticalSpacer_16 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_21.addItem(self.verticalSpacer_16)


        self.horizontalLayout_20.addWidget(self.shutterManual)

        self.horizontalSpacer_10 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_20.addItem(self.horizontalSpacer_10)

        self.mainPages.addWidget(self.manualPage)
        self.autoPage = QWidget()
        self.autoPage.setObjectName(u"autoPage")
        sizePolicy4.setHeightForWidth(self.autoPage.sizePolicy().hasHeightForWidth())
        self.autoPage.setSizePolicy(sizePolicy4)
        self.horizontalLayout_27 = QHBoxLayout(self.autoPage)
        self.horizontalLayout_27.setObjectName(u"horizontalLayout_27")
        self.movementAuto = QFrame(self.autoPage)
        self.movementAuto.setObjectName(u"movementAuto")
        self.movementAuto.setFrameShape(QFrame.StyledPanel)
        self.movementAuto.setFrameShadow(QFrame.Raised)
        self.verticalLayout_30 = QVBoxLayout(self.movementAuto)
        self.verticalLayout_30.setObjectName(u"verticalLayout_30")
        self.verticalLayout_30.setContentsMargins(30, -1, 25, -1)
        self.frame_12 = QFrame(self.movementAuto)
        self.frame_12.setObjectName(u"frame_12")
        self.frame_12.setFrameShape(QFrame.StyledPanel)
        self.frame_12.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_22 = QHBoxLayout(self.frame_12)
        self.horizontalLayout_22.setObjectName(u"horizontalLayout_22")
        self.label_37 = QLabel(self.frame_12)
        self.label_37.setObjectName(u"label_37")
        sizePolicy8.setHeightForWidth(self.label_37.sizePolicy().hasHeightForWidth())
        self.label_37.setSizePolicy(sizePolicy8)
        self.label_37.setMinimumSize(QSize(25, 25))
        self.label_37.setMaximumSize(QSize(25, 25))
        self.label_37.setPixmap(QPixmap(_icon_path(u":/feather/icons/feather/mouse-pointer.png")))
        self.label_37.setScaledContents(True)
        self.label_37.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.horizontalLayout_22.addWidget(self.label_37)

        self.label_15 = QLabel(self.frame_12)
        self.label_15.setObjectName(u"label_15")
        self.label_15.setFont(font2)

        self.horizontalLayout_22.addWidget(self.label_15)


        self.verticalLayout_30.addWidget(self.frame_12)

        self.frame_18 = QFrame(self.movementAuto)
        self.frame_18.setObjectName(u"frame_18")
        self.frame_18.setFrameShape(QFrame.StyledPanel)
        self.frame_18.setFrameShadow(QFrame.Raised)
        self.verticalLayout_14 = QVBoxLayout(self.frame_18)
        self.verticalLayout_14.setObjectName(u"verticalLayout_14")
        self.verticalLayout_14.setContentsMargins(-1, 0, -1, -1)
        self.frame_23 = QFrame(self.frame_18)
        self.frame_23.setObjectName(u"frame_23")
        self.frame_23.setFrameShape(QFrame.StyledPanel)
        self.frame_23.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_23 = QHBoxLayout(self.frame_23)
        self.horizontalLayout_23.setObjectName(u"horizontalLayout_23")
        self.frame_21 = QFrame(self.frame_23)
        self.frame_21.setObjectName(u"frame_21")
        self.frame_21.setFrameShape(QFrame.StyledPanel)
        self.frame_21.setFrameShadow(QFrame.Raised)
        self.gridLayout_5 = QGridLayout(self.frame_21)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.velocity_2 = QDoubleSpinBox(self.frame_21)
        self.velocity_2.setObjectName(u"velocity_2")

        self.gridLayout_5.addWidget(self.velocity_2, 2, 1, 1, 1)

        self.label_38 = QLabel(self.frame_21)
        self.label_38.setObjectName(u"label_38")

        self.gridLayout_5.addWidget(self.label_38, 0, 0, 1, 1)

        self.label_40 = QLabel(self.frame_21)
        self.label_40.setObjectName(u"label_40")

        self.gridLayout_5.addWidget(self.label_40, 2, 0, 1, 1)

        self.label_39 = QLabel(self.frame_21)
        self.label_39.setObjectName(u"label_39")

        self.gridLayout_5.addWidget(self.label_39, 3, 0, 1, 1)

        self.scaleList_2 = QComboBox(self.frame_21)
        self.scaleList_2.setObjectName(u"scaleList_2")
        sizePolicy1.setHeightForWidth(self.scaleList_2.sizePolicy().hasHeightForWidth())
        self.scaleList_2.setSizePolicy(sizePolicy1)

        self.gridLayout_5.addWidget(self.scaleList_2, 0, 1, 1, 1)

        self.acceleration_2 = QDoubleSpinBox(self.frame_21)
        self.acceleration_2.setObjectName(u"acceleration_2")

        self.gridLayout_5.addWidget(self.acceleration_2, 3, 1, 1, 1)


        self.horizontalLayout_23.addWidget(self.frame_21)

        self.confirmBtn_2 = QPushButton(self.frame_23)
        self.confirmBtn_2.setObjectName(u"confirmBtn_2")
        sizePolicy.setHeightForWidth(self.confirmBtn_2.sizePolicy().hasHeightForWidth())
        self.confirmBtn_2.setSizePolicy(sizePolicy)
        self.confirmBtn_2.setMinimumSize(QSize(0, 0))
        self.confirmBtn_2.setMaximumSize(QSize(16777215, 16777215))
        self.confirmBtn_2.setIcon(icon13)

        self.horizontalLayout_23.addWidget(self.confirmBtn_2)


        self.verticalLayout_14.addWidget(self.frame_23, 0, Qt.AlignHCenter)

        self.verticalSpacer_13 = QSpacerItem(20, 50, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_14.addItem(self.verticalSpacer_13)

        self.frame_22 = QFrame(self.frame_18)
        self.frame_22.setObjectName(u"frame_22")
        self.frame_22.setFrameShape(QFrame.StyledPanel)
        self.frame_22.setFrameShadow(QFrame.Raised)
        self.verticalLayout_35 = QVBoxLayout(self.frame_22)
        self.verticalLayout_35.setObjectName(u"verticalLayout_35")
        self.label_13 = QLabel(self.frame_22)
        self.label_13.setObjectName(u"label_13")

        self.verticalLayout_35.addWidget(self.label_13, 0, Qt.AlignHCenter)

        self.widget_7 = QWidget(self.frame_22)
        self.widget_7.setObjectName(u"widget_7")
        sizePolicy.setHeightForWidth(self.widget_7.sizePolicy().hasHeightForWidth())
        self.widget_7.setSizePolicy(sizePolicy)
        self.widget_7.setMinimumSize(QSize(0, 0))
        self.gridLayout = QGridLayout(self.widget_7)
        self.gridLayout.setObjectName(u"gridLayout")
        self.label_17 = QLabel(self.widget_7)
        self.label_17.setObjectName(u"label_17")

        self.gridLayout.addWidget(self.label_17, 0, 0, 1, 1, Qt.AlignHCenter)

        self.label_26 = QLabel(self.widget_7)
        self.label_26.setObjectName(u"label_26")

        self.gridLayout.addWidget(self.label_26, 0, 4, 1, 1, Qt.AlignHCenter)

        self.yPosition = QDoubleSpinBox(self.widget_7)
        self.yPosition.setObjectName(u"yPosition")

        self.gridLayout.addWidget(self.yPosition, 1, 2, 1, 1)

        self.xPosition = QDoubleSpinBox(self.widget_7)
        self.xPosition.setObjectName(u"xPosition")

        self.gridLayout.addWidget(self.xPosition, 1, 0, 1, 1)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer, 1, 1, 1, 1)

        self.zPosition = QDoubleSpinBox(self.widget_7)
        self.zPosition.setObjectName(u"zPosition")

        self.gridLayout.addWidget(self.zPosition, 1, 4, 1, 1)

        self.label_25 = QLabel(self.widget_7)
        self.label_25.setObjectName(u"label_25")

        self.gridLayout.addWidget(self.label_25, 0, 2, 1, 1, Qt.AlignHCenter)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer_3, 1, 3, 1, 1)


        self.verticalLayout_35.addWidget(self.widget_7)

        self.resetBtn = QPushButton(self.frame_22)
        self.resetBtn.setObjectName(u"resetBtn")
        icon19 = QIcon()
        icon19.addFile(_icon_path(u":/material_design/icons/material_design/restart_alt.png"), QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.resetBtn.setIcon(icon19)

        self.verticalLayout_35.addWidget(self.resetBtn)

        self.moveBtn = QPushButton(self.frame_22)
        self.moveBtn.setObjectName(u"moveBtn")
        icon20 = QIcon()
        icon20.addFile(_icon_path(u":/feather/icons/feather/move.png"), QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.moveBtn.setIcon(icon20)

        self.verticalLayout_35.addWidget(self.moveBtn)


        self.verticalLayout_14.addWidget(self.frame_22, 0, Qt.AlignHCenter)

        self.verticalSpacer_14 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_14.addItem(self.verticalSpacer_14)


        self.verticalLayout_30.addWidget(self.frame_18, 0, Qt.AlignLeft)


        self.horizontalLayout_27.addWidget(self.movementAuto)

        self.horizontalSpacer_17 = QSpacerItem(25, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_27.addItem(self.horizontalSpacer_17)

        self.shutterAuto = QFrame(self.autoPage)
        self.shutterAuto.setObjectName(u"shutterAuto")
        self.shutterAuto.setFrameShape(QFrame.StyledPanel)
        self.shutterAuto.setFrameShadow(QFrame.Raised)
        self.verticalLayout_31 = QVBoxLayout(self.shutterAuto)
        self.verticalLayout_31.setObjectName(u"verticalLayout_31")
        self.verticalLayout_31.setContentsMargins(6, -1, -1, -1)
        self.frame_24 = QFrame(self.shutterAuto)
        self.frame_24.setObjectName(u"frame_24")
        self.frame_24.setFrameShape(QFrame.StyledPanel)
        self.frame_24.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_24 = QHBoxLayout(self.frame_24)
        self.horizontalLayout_24.setObjectName(u"horizontalLayout_24")
        self.horizontalLayout_24.setContentsMargins(-1, 8, -1, -1)
        self.label_41 = QLabel(self.frame_24)
        self.label_41.setObjectName(u"label_41")
        sizePolicy8.setHeightForWidth(self.label_41.sizePolicy().hasHeightForWidth())
        self.label_41.setSizePolicy(sizePolicy8)
        self.label_41.setMinimumSize(QSize(25, 25))
        self.label_41.setMaximumSize(QSize(25, 25))
        self.label_41.setPixmap(QPixmap(_icon_path(u":/font_awesome_solid/icons/font_awesome/solid/bolt.png")))
        self.label_41.setScaledContents(True)

        self.horizontalLayout_24.addWidget(self.label_41)

        self.label_27 = QLabel(self.frame_24)
        self.label_27.setObjectName(u"label_27")
        self.label_27.setFont(font2)

        self.horizontalLayout_24.addWidget(self.label_27)


        self.verticalLayout_31.addWidget(self.frame_24, 0, Qt.AlignHCenter)

        self.frame_25 = QFrame(self.shutterAuto)
        self.frame_25.setObjectName(u"frame_25")
        self.frame_25.setFrameShape(QFrame.StyledPanel)
        self.frame_25.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_25 = QHBoxLayout(self.frame_25)
        self.horizontalLayout_25.setObjectName(u"horizontalLayout_25")
        self.horizontalLayout_25.setContentsMargins(20, -1, -1, -1)
        self.label_42 = QLabel(self.frame_25)
        self.label_42.setObjectName(u"label_42")

        self.horizontalLayout_25.addWidget(self.label_42)

        self.horizontalSpacer_15 = QSpacerItem(5, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_25.addItem(self.horizontalSpacer_15)

        self.scaleListTime = QComboBox(self.frame_25)
        self.scaleListTime.setObjectName(u"scaleListTime")

        self.horizontalLayout_25.addWidget(self.scaleListTime)


        self.verticalLayout_31.addWidget(self.frame_25, 0, Qt.AlignHCenter)

        self.verticalSpacer_23 = QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_31.addItem(self.verticalSpacer_23)

        self.frame_26 = QFrame(self.shutterAuto)
        self.frame_26.setObjectName(u"frame_26")
        self.frame_26.setFrameShape(QFrame.StyledPanel)
        self.frame_26.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_26 = QHBoxLayout(self.frame_26)
        self.horizontalLayout_26.setObjectName(u"horizontalLayout_26")
        self.timeGraph = QLabel(self.frame_26)
        self.timeGraph.setObjectName(u"timeGraph")
        sizePolicy10 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        sizePolicy10.setHorizontalStretch(0)
        sizePolicy10.setVerticalStretch(0)
        sizePolicy10.setHeightForWidth(self.timeGraph.sizePolicy().hasHeightForWidth())
        self.timeGraph.setSizePolicy(sizePolicy10)
        self.timeGraph.setPixmap(QPixmap(u"images/time.png"))
        self.timeGraph.setScaledContents(True)

        self.horizontalLayout_26.addWidget(self.timeGraph)

        self.horizontalSpacer_16 = QSpacerItem(5, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_26.addItem(self.horizontalSpacer_16)

        self.frame_5 = QFrame(self.frame_26)
        self.frame_5.setObjectName(u"frame_5")
        self.frame_5.setFrameShape(QFrame.StyledPanel)
        self.frame_5.setFrameShadow(QFrame.Raised)
        self.verticalLayout_37 = QVBoxLayout(self.frame_5)
        self.verticalLayout_37.setObjectName(u"verticalLayout_37")
        self.label_28 = QLabel(self.frame_5)
        self.label_28.setObjectName(u"label_28")

        self.verticalLayout_37.addWidget(self.label_28, 0, Qt.AlignHCenter)

        self.label_29 = QLabel(self.frame_5)
        self.label_29.setObjectName(u"label_29")
        font6 = QFont()
        font6.setPointSize(8)
        font6.setItalic(True)
        self.label_29.setFont(font6)
        self.label_29.setWordWrap(True)

        self.verticalLayout_37.addWidget(self.label_29)

        self.verticalSpacer_17 = QSpacerItem(20, 25, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_37.addItem(self.verticalSpacer_17)

        self.timeShutter = QDoubleSpinBox(self.frame_5)
        self.timeShutter.setObjectName(u"timeShutter")

        self.verticalLayout_37.addWidget(self.timeShutter)

        self.acceptBtn = QPushButton(self.frame_5)
        self.acceptBtn.setObjectName(u"acceptBtn")
        icon21 = QIcon()
        icon21.addFile(_icon_path(u":/feather/icons/feather/checkbox_checked.png"), QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.acceptBtn.setIcon(icon21)

        self.verticalLayout_37.addWidget(self.acceptBtn)


        self.horizontalLayout_26.addWidget(self.frame_5)


        self.verticalLayout_31.addWidget(self.frame_26, 0, Qt.AlignHCenter)

        self.verticalSpacer_21 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_31.addItem(self.verticalSpacer_21)


        self.horizontalLayout_27.addWidget(self.shutterAuto)

        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_27.addItem(self.horizontalSpacer_4)

        self.mainPages.addWidget(self.autoPage)
        self.gcodePage = QWidget()
        self.gcodePage.setObjectName(u"gcodePage")
        sizePolicy4.setHeightForWidth(self.gcodePage.sizePolicy().hasHeightForWidth())
        self.gcodePage.setSizePolicy(sizePolicy4)
        self.verticalLayout_15 = QVBoxLayout(self.gcodePage)
        self.verticalLayout_15.setObjectName(u"verticalLayout_15")
        self.frame_9 = QFrame(self.gcodePage)
        self.frame_9.setObjectName(u"frame_9")
        self.frame_9.setFrameShape(QFrame.StyledPanel)
        self.frame_9.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_21 = QHBoxLayout(self.frame_9)
        self.horizontalLayout_21.setObjectName(u"horizontalLayout_21")
        self.label_20 = QLabel(self.frame_9)
        self.label_20.setObjectName(u"label_20")
        sizePolicy8.setHeightForWidth(self.label_20.sizePolicy().hasHeightForWidth())
        self.label_20.setSizePolicy(sizePolicy8)
        self.label_20.setMinimumSize(QSize(25, 25))
        self.label_20.setMaximumSize(QSize(25, 25))
        self.label_20.setPixmap(QPixmap(_icon_path(u":/feather/icons/feather/code.png")))
        self.label_20.setScaledContents(True)

        self.horizontalLayout_21.addWidget(self.label_20)

        self.label_9 = QLabel(self.frame_9)
        self.label_9.setObjectName(u"label_9")
        self.label_9.setFont(font2)
        self.label_9.setStyleSheet(u"")
        self.label_9.setAlignment(Qt.AlignCenter)

        self.horizontalLayout_21.addWidget(self.label_9)


        self.verticalLayout_15.addWidget(self.frame_9, 0, Qt.AlignHCenter|Qt.AlignTop)

        self.verticalSpacer_4 = QSpacerItem(20, 30, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.verticalLayout_15.addItem(self.verticalSpacer_4)

        self.frameGcode = QFrame(self.gcodePage)
        self.frameGcode.setObjectName(u"frameGcode")
        self.frameGcode.setFrameShape(QFrame.StyledPanel)
        self.frameGcode.setFrameShadow(QFrame.Raised)
        self.verticalLayout_24 = QVBoxLayout(self.frameGcode)
        self.verticalLayout_24.setObjectName(u"verticalLayout_24")
        self.verticalLayout_24.setContentsMargins(20, -1, 20, 10)
        self.dragYdrop = QFrame(self.frameGcode)
        self.dragYdrop.setObjectName(u"dragYdrop")
        sizePolicy11 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.MinimumExpanding)
        sizePolicy11.setHorizontalStretch(0)
        sizePolicy11.setVerticalStretch(3)
        sizePolicy11.setHeightForWidth(self.dragYdrop.sizePolicy().hasHeightForWidth())
        self.dragYdrop.setSizePolicy(sizePolicy11)
        self.dragYdrop.setMinimumSize(QSize(0, 150))
        self.dragYdrop.setMaximumSize(QSize(16777215, 16777215))
        self.dragYdrop.setAcceptDrops(True)
        self.dragYdrop.setStyleSheet(u"background-color: rgb(175, 175, 175);")
        self.dragYdrop.setFrameShape(QFrame.StyledPanel)
        self.dragYdrop.setFrameShadow(QFrame.Raised)
        self.verticalLayout_33 = QVBoxLayout(self.dragYdrop)
        self.verticalLayout_33.setObjectName(u"verticalLayout_33")
        self.verticalLayout_33.setContentsMargins(-1, -1, -1, 7)
        self.label_6 = QLabel(self.dragYdrop)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setFont(font)

        self.verticalLayout_33.addWidget(self.label_6, 0, Qt.AlignHCenter|Qt.AlignVCenter)


        self.verticalLayout_24.addWidget(self.dragYdrop)

        self.verticalSpacer_8 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_24.addItem(self.verticalSpacer_8)

        self.selectFileBtn = QPushButton(self.frameGcode)
        self.selectFileBtn.setObjectName(u"selectFileBtn")
        font7 = QFont()
        font7.setBold(False)
        self.selectFileBtn.setFont(font7)
        icon22 = QIcon()
        icon22.addFile(_icon_path(u":/font_awesome_solid/icons/font_awesome/solid/file-import.png"), QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.selectFileBtn.setIcon(icon22)

        self.verticalLayout_24.addWidget(self.selectFileBtn)

        self.editBtn = QPushButton(self.frameGcode)
        self.editBtn.setObjectName(u"editBtn")
        self.editBtn.setFont(font7)
        icon23 = QIcon()
        icon23.addFile(_icon_path(u":/feather/icons/feather/edit.png"), QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.editBtn.setIcon(icon23)

        self.verticalLayout_24.addWidget(self.editBtn)


        self.verticalLayout_15.addWidget(self.frameGcode)

        self.startBtn = QPushButton(self.gcodePage)
        self.startBtn.setObjectName(u"startBtn")
        self.startBtn.setFont(font1)
        icon24 = QIcon()
        icon24.addFile(_icon_path(u":/feather/icons/feather/play-circle.png"), QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.startBtn.setIcon(icon24)
        self.startBtn.setCheckable(True)
        self.startBtn.setAutoExclusive(True)

        self.verticalLayout_15.addWidget(self.startBtn)

        self.mainPages.addWidget(self.gcodePage)

        self.verticalLayout_11.addWidget(self.mainPages)


        self.horizontalLayout_8.addWidget(self.mainPagesCont)

        self.rightMenu = QCustomSlideMenu(self.mainContents)
        self.rightMenu.setObjectName(u"rightMenu")
        sizePolicy3.setHeightForWidth(self.rightMenu.sizePolicy().hasHeightForWidth())
        self.rightMenu.setSizePolicy(sizePolicy3)
        self.rightMenu.setMinimumSize(QSize(200, 0))
        self.verticalLayout_16 = QVBoxLayout(self.rightMenu)
        self.verticalLayout_16.setSpacing(5)
        self.verticalLayout_16.setObjectName(u"verticalLayout_16")
        self.verticalLayout_16.setContentsMargins(0, 5, 3, 5)
        self.widget_6 = QWidget(self.rightMenu)
        self.widget_6.setObjectName(u"widget_6")
        self.horizontalLayout_9 = QHBoxLayout(self.widget_6)
        self.horizontalLayout_9.setSpacing(0)
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.horizontalLayout_9.setContentsMargins(0, 0, 0, 0)
        self.closeRightMenuBtn = QPushButton(self.widget_6)
        self.closeRightMenuBtn.setObjectName(u"closeRightMenuBtn")
        icon25 = QIcon()
        icon25.addFile(_icon_path(u":/feather/icons/feather/arrow-right-circle.png"), QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.closeRightMenuBtn.setIcon(icon25)
        self.closeRightMenuBtn.setCheckable(True)
        self.closeRightMenuBtn.setAutoExclusive(True)

        self.horizontalLayout_9.addWidget(self.closeRightMenuBtn, 0, Qt.AlignRight)


        self.verticalLayout_16.addWidget(self.widget_6)

        self.rightMenuPages = QCustomQStackedWidget(self.rightMenu)
        self.rightMenuPages.setObjectName(u"rightMenuPages")
        self.connectionPage = QWidget()
        self.connectionPage.setObjectName(u"connectionPage")
        sizePolicy4.setHeightForWidth(self.connectionPage.sizePolicy().hasHeightForWidth())
        self.connectionPage.setSizePolicy(sizePolicy4)
        self.verticalLayout_18 = QVBoxLayout(self.connectionPage)
        self.verticalLayout_18.setObjectName(u"verticalLayout_18")
        self.verticalLayout_18.setContentsMargins(-1, -1, 0, -1)
        self.label_11 = QLabel(self.connectionPage)
        self.label_11.setObjectName(u"label_11")
        font8 = QFont()
        font8.setFamilies([u"Sitka Small"])
        font8.setPointSize(11)
        font8.setBold(True)
        self.label_11.setFont(font8)
        self.label_11.setStyleSheet(u"")
        self.label_11.setAlignment(Qt.AlignCenter)

        self.verticalLayout_18.addWidget(self.label_11, 0, Qt.AlignHCenter|Qt.AlignTop)

        self.verticalSpacer_6 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_18.addItem(self.verticalSpacer_6)

        self.frame_13 = QFrame(self.connectionPage)
        self.frame_13.setObjectName(u"frame_13")
        self.frame_13.setFrameShape(QFrame.StyledPanel)
        self.frame_13.setFrameShadow(QFrame.Raised)
        self.verticalLayout_12 = QVBoxLayout(self.frame_13)
        self.verticalLayout_12.setSpacing(4)
        self.verticalLayout_12.setObjectName(u"verticalLayout_12")
        self.verticalLayout_12.setContentsMargins(-1, 6, -1, 6)
        self.label_21 = QLabel(self.frame_13)
        self.label_21.setObjectName(u"label_21")
        sizePolicy12 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy12.setHorizontalStretch(0)
        sizePolicy12.setVerticalStretch(0)
        sizePolicy12.setHeightForWidth(self.label_21.sizePolicy().hasHeightForWidth())
        self.label_21.setSizePolicy(sizePolicy12)

        self.verticalLayout_12.addWidget(self.label_21)

        self.comPort = QComboBox(self.frame_13)
        self.comPort.setObjectName(u"comPort")

        self.verticalLayout_12.addWidget(self.comPort)


        self.verticalLayout_18.addWidget(self.frame_13)

        self.frame_14 = QFrame(self.connectionPage)
        self.frame_14.setObjectName(u"frame_14")
        self.frame_14.setFrameShape(QFrame.StyledPanel)
        self.frame_14.setFrameShadow(QFrame.Raised)
        self.verticalLayout_25 = QVBoxLayout(self.frame_14)
        self.verticalLayout_25.setObjectName(u"verticalLayout_25")
        self.label_22 = QLabel(self.frame_14)
        self.label_22.setObjectName(u"label_22")
        sizePolicy12.setHeightForWidth(self.label_22.sizePolicy().hasHeightForWidth())
        self.label_22.setSizePolicy(sizePolicy12)

        self.verticalLayout_25.addWidget(self.label_22)

        self.baudRate = QComboBox(self.frame_14)
        self.baudRate.setObjectName(u"baudRate")

        self.verticalLayout_25.addWidget(self.baudRate)


        self.verticalLayout_18.addWidget(self.frame_14)

        self.verticalSpacer_7 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_18.addItem(self.verticalSpacer_7)

        self.connectBtn = QPushButton(self.connectionPage)
        self.connectBtn.setObjectName(u"connectBtn")
        self.connectBtn.setFont(font1)

        self.verticalLayout_18.addWidget(self.connectBtn)

        self.rightMenuPages.addWidget(self.connectionPage)
        self.calibrationPage = QWidget()
        self.calibrationPage.setObjectName(u"calibrationPage")
        sizePolicy4.setHeightForWidth(self.calibrationPage.sizePolicy().hasHeightForWidth())
        self.calibrationPage.setSizePolicy(sizePolicy4)
        self.verticalLayout_17 = QVBoxLayout(self.calibrationPage)
        self.verticalLayout_17.setObjectName(u"verticalLayout_17")
        self.verticalLayout_17.setContentsMargins(-1, -1, 0, -1)
        self.label_10 = QLabel(self.calibrationPage)
        self.label_10.setObjectName(u"label_10")
        self.label_10.setFont(font2)
        self.label_10.setStyleSheet(u"")
        self.label_10.setAlignment(Qt.AlignCenter)

        self.verticalLayout_17.addWidget(self.label_10, 0, Qt.AlignHCenter|Qt.AlignTop)

        self.verticalSpacer_15 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_17.addItem(self.verticalSpacer_15)

        self.frame_15 = QFrame(self.calibrationPage)
        self.frame_15.setObjectName(u"frame_15")
        self.frame_15.setFrameShape(QFrame.StyledPanel)
        self.frame_15.setFrameShadow(QFrame.Raised)
        self.verticalLayout_27 = QVBoxLayout(self.frame_15)
        self.verticalLayout_27.setObjectName(u"verticalLayout_27")
        self.label_23 = QLabel(self.frame_15)
        self.label_23.setObjectName(u"label_23")
        sizePolicy12.setHeightForWidth(self.label_23.sizePolicy().hasHeightForWidth())
        self.label_23.setSizePolicy(sizePolicy12)
        self.label_23.setWordWrap(False)

        self.verticalLayout_27.addWidget(self.label_23, 0, Qt.AlignHCenter)

        self.widget_9 = QWidget(self.frame_15)
        self.widget_9.setObjectName(u"widget_9")
        sizePolicy.setHeightForWidth(self.widget_9.sizePolicy().hasHeightForWidth())
        self.widget_9.setSizePolicy(sizePolicy)
        self.verticalLayout_26 = QVBoxLayout(self.widget_9)
        self.verticalLayout_26.setObjectName(u"verticalLayout_26")
        self.frame_17 = QFrame(self.widget_9)
        self.frame_17.setObjectName(u"frame_17")
        sizePolicy.setHeightForWidth(self.frame_17.sizePolicy().hasHeightForWidth())
        self.frame_17.setSizePolicy(sizePolicy)
        self.frame_17.setFrameShape(QFrame.StyledPanel)
        self.frame_17.setFrameShadow(QFrame.Raised)
        self.verticalLayout_28 = QVBoxLayout(self.frame_17)
        self.verticalLayout_28.setObjectName(u"verticalLayout_28")
        self.zUpFocusing = QPushButton(self.frame_17)
        self.zUpFocusing.setObjectName(u"zUpFocusing")
        sizePolicy12.setHeightForWidth(self.zUpFocusing.sizePolicy().hasHeightForWidth())
        self.zUpFocusing.setSizePolicy(sizePolicy12)
        self.zUpFocusing.setMinimumSize(QSize(0, 17))
        icon26 = QIcon()
        icon26.addFile(_icon_path(u":/feather/icons/feather/arrow-up.png"), QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.zUpFocusing.setIcon(icon26)

        self.verticalLayout_28.addWidget(self.zUpFocusing)

        self.zDownFocusing = QPushButton(self.frame_17)
        self.zDownFocusing.setObjectName(u"zDownFocusing")
        sizePolicy12.setHeightForWidth(self.zDownFocusing.sizePolicy().hasHeightForWidth())
        self.zDownFocusing.setSizePolicy(sizePolicy12)
        self.zDownFocusing.setMinimumSize(QSize(0, 17))
        icon27 = QIcon()
        icon27.addFile(_icon_path(u":/feather/icons/feather/arrow-down.png"), QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.zDownFocusing.setIcon(icon27)

        self.verticalLayout_28.addWidget(self.zDownFocusing)


        self.verticalLayout_26.addWidget(self.frame_17)

        self.calibratedBtn = QPushButton(self.widget_9)
        self.calibratedBtn.setObjectName(u"calibratedBtn")
        sizePolicy12.setHeightForWidth(self.calibratedBtn.sizePolicy().hasHeightForWidth())
        self.calibratedBtn.setSizePolicy(sizePolicy12)
        self.calibratedBtn.setMinimumSize(QSize(0, 17))

        self.verticalLayout_26.addWidget(self.calibratedBtn)


        self.verticalLayout_27.addWidget(self.widget_9)


        self.verticalLayout_17.addWidget(self.frame_15)

        self.frame_16 = QFrame(self.calibrationPage)
        self.frame_16.setObjectName(u"frame_16")
        sizePolicy.setHeightForWidth(self.frame_16.sizePolicy().hasHeightForWidth())
        self.frame_16.setSizePolicy(sizePolicy)
        self.frame_16.setFrameShape(QFrame.StyledPanel)
        self.frame_16.setFrameShadow(QFrame.Raised)
        self.verticalLayout_29 = QVBoxLayout(self.frame_16)
        self.verticalLayout_29.setObjectName(u"verticalLayout_29")
        self.label_24 = QLabel(self.frame_16)
        self.label_24.setObjectName(u"label_24")
        sizePolicy12.setHeightForWidth(self.label_24.sizePolicy().hasHeightForWidth())
        self.label_24.setSizePolicy(sizePolicy12)

        self.verticalLayout_29.addWidget(self.label_24, 0, Qt.AlignHCenter)

        self.zeroXBtn = QPushButton(self.frame_16)
        self.zeroXBtn.setObjectName(u"zeroXBtn")
        sizePolicy12.setHeightForWidth(self.zeroXBtn.sizePolicy().hasHeightForWidth())
        self.zeroXBtn.setSizePolicy(sizePolicy12)
        self.zeroXBtn.setMinimumSize(QSize(0, 17))

        self.verticalLayout_29.addWidget(self.zeroXBtn)

        self.zeroYBtn = QPushButton(self.frame_16)
        self.zeroYBtn.setObjectName(u"zeroYBtn")
        sizePolicy12.setHeightForWidth(self.zeroYBtn.sizePolicy().hasHeightForWidth())
        self.zeroYBtn.setSizePolicy(sizePolicy12)
        self.zeroYBtn.setMinimumSize(QSize(0, 17))

        self.verticalLayout_29.addWidget(self.zeroYBtn)


        self.verticalLayout_17.addWidget(self.frame_16)

        self.verticalSpacer_9 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_17.addItem(self.verticalSpacer_9)

        self.rightMenuPages.addWidget(self.calibrationPage)

        self.verticalLayout_16.addWidget(self.rightMenuPages)


        self.horizontalLayout_8.addWidget(self.rightMenu)


        self.verticalLayout_9.addWidget(self.mainContents)

        self.footer = QWidget(self.mainBody)
        self.footer.setObjectName(u"footer")
        sizePolicy.setHeightForWidth(self.footer.sizePolicy().hasHeightForWidth())
        self.footer.setSizePolicy(sizePolicy)
        self.footer.setMinimumSize(QSize(0, 0))
        self.horizontalLayout_4 = QHBoxLayout(self.footer)
        self.horizontalLayout_4.setSpacing(5)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(5, 5, 0, 0)
        self.label_5 = QLabel(self.footer)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setStyleSheet(u"font: 8pt;\n"
"")

        self.horizontalLayout_4.addWidget(self.label_5, 0, Qt.AlignLeft|Qt.AlignBottom)

        self.size_grip = QPushButton(self.footer)
        self.size_grip.setObjectName(u"size_grip")
        sizePolicy1.setHeightForWidth(self.size_grip.sizePolicy().hasHeightForWidth())
        self.size_grip.setSizePolicy(sizePolicy1)
        self.size_grip.setMinimumSize(QSize(15, 15))
        self.size_grip.setMaximumSize(QSize(15, 15))

        self.horizontalLayout_4.addWidget(self.size_grip, 0, Qt.AlignRight|Qt.AlignBottom)


        self.verticalLayout_9.addWidget(self.footer, 0, Qt.AlignBottom)


        self.horizontalLayout.addWidget(self.mainBody)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        self.centerMenuPages.setCurrentIndex(0)
        self.mainPages.setCurrentIndex(1)
        self.rightMenuPages.setCurrentIndex(1)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
#if QT_CONFIG(tooltip)
        self.menuBtn.setToolTip("")
#endif // QT_CONFIG(tooltip)
        self.menuBtn.setText("")
        self.homeBtn.setText(QCoreApplication.translate("MainWindow", u"Home", None))
        self.manualBtn.setText(QCoreApplication.translate("MainWindow", u"Manual Mode", None))
        self.autoBtn.setText(QCoreApplication.translate("MainWindow", u"Auto Mode", None))
        self.gcodeBtn.setText(QCoreApplication.translate("MainWindow", u"G-Code", None))
        self.settingsBtn.setText(QCoreApplication.translate("MainWindow", u"Settings", None))
        self.helpBtn.setText(QCoreApplication.translate("MainWindow", u"Help", None))
        self.closeCenterMenuBtn.setText("")
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"Settings", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Theme", None))
        self.themeList.setCurrentText("")
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"Help", None))
        self.usal.setText("")
#if QT_CONFIG(tooltip)
        self.connectionBtn.setToolTip(QCoreApplication.translate("MainWindow", u"Connections", None))
#endif // QT_CONFIG(tooltip)
        self.connectionBtn.setText("")
#if QT_CONFIG(tooltip)
        self.calibrationBtn.setToolTip(QCoreApplication.translate("MainWindow", u"Calibration", None))
#endif // QT_CONFIG(tooltip)
        self.calibrationBtn.setText("")
        self.minimizeBtn.setText("")
        self.restoreBtn.setText("")
        self.closeBtn.setText("")
        self.labelConexion.setText(QCoreApplication.translate("MainWindow", u"Desconectado", None))
        self.labelSTO.setText(QCoreApplication.translate("MainWindow", u"Seguridad OK", None))
        self.label_12.setText(QCoreApplication.translate("MainWindow", u"Z (mm):", None))
        self.valorZ.setText(QCoreApplication.translate("MainWindow", u"—", None))
        self.estacionAerotech.setText("")
        self.label_14.setText(QCoreApplication.translate("MainWindow", u"Y (mm):", None))
        self.valorY.setText(QCoreApplication.translate("MainWindow", u"—", None))
        self.label_16.setText(QCoreApplication.translate("MainWindow", u"X (mm):", None))
        self.valorX.setText(QCoreApplication.translate("MainWindow", u"—", None))
        self.laserIcon.setText("")
        self.laserTitleLabel.setText(QCoreApplication.translate("MainWindow", u"Salida Láser:", None))
        self.labelLaserState.setText(QCoreApplication.translate("MainWindow", u"OFF", None))
        self.estadoPotencia.setText(QCoreApplication.translate("MainWindow", u"0% · 0 mW (consigna)", None))
        self.labelInterlock.setText(QCoreApplication.translate("MainWindow", u"Interlock: N/D", None))
        self.label_36.setText("")
        self.label_19.setText(QCoreApplication.translate("MainWindow", u"Movement XYZ", None))
        self.label_31.setText(QCoreApplication.translate("MainWindow", u"Scale", None))
        self.label_32.setText(QCoreApplication.translate("MainWindow", u"Velocity", None))
        self.label_33.setText(QCoreApplication.translate("MainWindow", u"Acceleration", None))
        self.confirmBtn.setText(QCoreApplication.translate("MainWindow", u"Confirm", None))
        self.labelXMinus.setText(QCoreApplication.translate("MainWindow", u"X-", None))
        self.labelYPlus.setText(QCoreApplication.translate("MainWindow", u"Y+", None))
        self.xyUpBtn.setText("")
        self.xyLeftBtn.setText("")
        self.xyZeroBtn.setText("")
        self.xyRightBtn.setText("")
        self.xyDownBtn.setText("")
        self.labelXPlus.setText(QCoreApplication.translate("MainWindow", u"X+", None))
        self.labelYMinus.setText(QCoreApplication.translate("MainWindow", u"Y-", None))
        self.labelZPlus.setText(QCoreApplication.translate("MainWindow", u"Z+", None))
        self.zUpBtn.setText("")
        self.label_35.setText(QCoreApplication.translate("MainWindow", u"|", None))
        self.zDownBtn.setText("")
        self.labelZMinus.setText(QCoreApplication.translate("MainWindow", u"Z-", None))
        self.label_8.setText("")
        self.label_7.setText(QCoreApplication.translate("MainWindow", u"Shutter", None))
        self.laserOC.setText("")
        self.openShutterBtn.setText(QCoreApplication.translate("MainWindow", u"OPEN", None))
        self.closeShutterBtn.setText(QCoreApplication.translate("MainWindow", u"CLOSE", None))
        self.label_37.setText("")
        self.label_15.setText(QCoreApplication.translate("MainWindow", u"Movement XYZ", None))
        self.label_38.setText(QCoreApplication.translate("MainWindow", u"Scale", None))
        self.label_40.setText(QCoreApplication.translate("MainWindow", u"Velocity", None))
        self.label_39.setText(QCoreApplication.translate("MainWindow", u"Acceleration", None))
        self.confirmBtn_2.setText(QCoreApplication.translate("MainWindow", u"Confirm", None))
        self.label_13.setText(QCoreApplication.translate("MainWindow", u"Absolute Motion", None))
        self.label_17.setText(QCoreApplication.translate("MainWindow", u"X position", None))
        self.label_26.setText(QCoreApplication.translate("MainWindow", u"Z position", None))
        self.label_25.setText(QCoreApplication.translate("MainWindow", u"Y position", None))
        self.resetBtn.setText(QCoreApplication.translate("MainWindow", u"Reset", None))
        self.moveBtn.setText(QCoreApplication.translate("MainWindow", u"Move to position", None))
        self.label_41.setText("")
        self.label_27.setText(QCoreApplication.translate("MainWindow", u"Shutter", None))
        self.label_42.setText(QCoreApplication.translate("MainWindow", u"Scale", None))
        self.timeGraph.setText("")
        self.label_28.setText(QCoreApplication.translate("MainWindow", u"Delay time", None))
        self.label_29.setText(QCoreApplication.translate("MainWindow", u"Time from automatically opening shutter until it closes.", None))
        self.acceptBtn.setText(QCoreApplication.translate("MainWindow", u"Accept", None))
        self.label_20.setText("")
        self.label_9.setText(QCoreApplication.translate("MainWindow", u"Upload the G-Code file", None))
        self.label_6.setText(QCoreApplication.translate("MainWindow", u"Drag and drop your file", None))
        self.selectFileBtn.setText(QCoreApplication.translate("MainWindow", u"Select File", None))
        self.editBtn.setText(QCoreApplication.translate("MainWindow", u"Edit", None))
        self.startBtn.setText(QCoreApplication.translate("MainWindow", u"Start", None))
        self.closeRightMenuBtn.setText("")
        self.label_11.setText(QCoreApplication.translate("MainWindow", u"Connection Page", None))
        self.label_21.setText(QCoreApplication.translate("MainWindow", u"Select COM Port:", None))
        self.label_22.setText(QCoreApplication.translate("MainWindow", u"Select Baud Rate:", None))
        self.connectBtn.setText(QCoreApplication.translate("MainWindow", u"Connect", None))
        self.label_10.setText(QCoreApplication.translate("MainWindow", u"Calibration Page", None))
        self.label_23.setText(QCoreApplication.translate("MainWindow", u"Focusing Z - Axis", None))
        self.zUpFocusing.setText("")
        self.zDownFocusing.setText("")
        self.calibratedBtn.setText(QCoreApplication.translate("MainWindow", u"Calibrated", None))
        self.label_24.setText(QCoreApplication.translate("MainWindow", u"X/Y Axis Calibration", None))
        self.zeroXBtn.setText(QCoreApplication.translate("MainWindow", u"Zero X", None))
        self.zeroYBtn.setText(QCoreApplication.translate("MainWindow", u"Zero Y", None))
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"ETSII B\u00e9jar | Ingenier\u00eda Electr\u00f3nica Industrial y Autom\u00e1tica | Christine Marie Quan Jo", None))
        self.size_grip.setText("")
    # retranslateUi

