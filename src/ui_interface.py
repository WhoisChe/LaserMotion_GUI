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
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDoubleSpinBox, QFrame,
    QGridLayout, QHBoxLayout, QLabel, QLineEdit, QListWidget,
    QMainWindow, QPushButton, QScrollArea, QSizePolicy, QSlider, QSpacerItem,
    QSpinBox, QStackedWidget, QTextEdit, QVBoxLayout, QWidget)

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


def _scaled_pixmap(path, height):
    """Carga una imagen y la escala a "height" px de alto conservando su
    proporción original (Qt.KeepAspectRatio) — para logos/imágenes cuyo
    ancho debe salir del propio archivo en vez de forzarse aparte, así que
    una sustitución futura con proporciones distintas sigue escalando bien
    a partir de la misma altura."""
    return QPixmap(path).scaledToHeight(height, Qt.SmoothTransformation)


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

        self.helpScrollArea = QScrollArea(self.helpPage)
        self.helpScrollArea.setObjectName(u"helpScrollArea")
        self.helpScrollArea.setWidgetResizable(True)
        self.helpScrollArea.setFrameShape(QFrame.NoFrame)
        self.helpScrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.helpScrollAreaContents = QWidget()
        self.helpScrollAreaContents.setObjectName(u"helpScrollAreaContents")
        self.verticalLayout_help = QVBoxLayout(self.helpScrollAreaContents)
        self.verticalLayout_help.setObjectName(u"verticalLayout_help")
        self.helpContentLabel = QLabel(self.helpScrollAreaContents)
        self.helpContentLabel.setObjectName(u"helpContentLabel")
        self.helpContentLabel.setWordWrap(True)
        self.helpContentLabel.setTextFormat(Qt.RichText)
        self.helpContentLabel.setOpenExternalLinks(True)
        self.helpContentLabel.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        font2 = QFont()
        font2.setPointSize(8)
        self.helpContentLabel.setFont(font2)

        self.verticalLayout_help.addWidget(self.helpContentLabel)

        self.helpScrollArea.setWidget(self.helpScrollAreaContents)

        self.verticalLayout_8.addWidget(self.helpScrollArea)

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
        # Altura fija a 43 px, ancho libre — por debajo del techo que
        # permite el header sin crecer (frame_2/connectionBtn es hoy el
        # hijo más alto, a 58 px). El pixmap ya sale escalado a esa altura
        # conservando su proporción (_scaled_pixmap), así que el QLabel no
        # debe imponer un ancho propio que lo recorte ni
        # setScaledContents(True), que deformaría la imagen si el layout le
        # diera una caja con una proporción distinta a la del pixmap.
        self.usal.setFixedHeight(43)
        self.usal.setPixmap(_scaled_pixmap(u"images/logo_usal1.png", 43))

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
        self.horizontalLayout_18 = QHBoxLayout(self.homePage)
        self.horizontalLayout_18.setObjectName(u"horizontalLayout_18")
        self.horizontalSpacer_7 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_18.addItem(self.horizontalSpacer_7)

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
        self.verticalLayout_laser.setContentsMargins(24, 20, 24, 20)
        self.verticalLayout_laser.setSpacing(14)
        self.laserIcon = QLabel(self.laserOutputCard)
        self.laserIcon.setObjectName(u"laserIcon")
        sizePolicy5 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        sizePolicy5.setHorizontalStretch(0)
        sizePolicy5.setVerticalStretch(0)
        sizePolicy5.setHeightForWidth(self.laserIcon.sizePolicy().hasHeightForWidth())
        self.laserIcon.setSizePolicy(sizePolicy5)
        self.laserIcon.setMinimumSize(QSize(64, 64))
        self.laserIcon.setMaximumSize(QSize(64, 64))
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


        self.verticalLayout_10.addWidget(self.laserOutputCard)

        self.verticalSpacer_19 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_10.addItem(self.verticalSpacer_19)


        self.horizontalLayout_18.addWidget(self.cardsFrame, 0, Qt.AlignHCenter)

        self.horizontalSpacer_6 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_18.addItem(self.horizontalSpacer_6)

        # ── Imagen de la estación (a la derecha de la tarjeta de láser) ──
        # Escalada por altura conservando proporción (_scaled_pixmap, ver
        # también el logo usal más arriba) — sin setScaledContents(True),
        # que deformaría la imagen si el layout le diera una caja con una
        # proporción distinta a la del pixmap ya escalado.
        self.estacionAerotech = QLabel(self.homePage)
        self.estacionAerotech.setObjectName(u"estacionAerotech")
        self.estacionAerotech.setPixmap(_scaled_pixmap(u"images/Estacion nanoposicionamiento.png", 380))

        self.horizontalLayout_18.addWidget(self.estacionAerotech, 0, Qt.AlignHCenter|Qt.AlignVCenter)

        self.horizontalSpacer_8 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_18.addItem(self.horizontalSpacer_8)

        self.mainPages.addWidget(self.homePage)
        # QScrollArea en vez de QWidget plano: el D-pad XY, los
        # controles Z y la columna del láser no siempre caben en el alto
        # disponible en ventanas más pequeñas. El objectName "manualPage" se
        # mantiene en el QScrollArea (no en el widget de contenido) porque
        # la navegación del menú lateral (json-styles/style.json,
        # "manualBtn": "manualPage") busca ese nombre dentro de mainPages.
        self.manualPage = QScrollArea()
        self.manualPage.setObjectName(u"manualPage")
        sizePolicy4.setHeightForWidth(self.manualPage.sizePolicy().hasHeightForWidth())
        self.manualPage.setSizePolicy(sizePolicy4)
        self.manualPage.setWidgetResizable(True)
        self.manualPage.setFrameShape(QFrame.NoFrame)
        self.manualPage.setStyleSheet(u"QScrollArea { background: transparent; border: none; }")
        self.manualPage.viewport().setStyleSheet(u"background: transparent;")
        self.manualPageContents = QWidget()
        self.manualPageContents.setObjectName(u"manualPageContents")
        self.horizontalLayout_20 = QHBoxLayout(self.manualPageContents)
        self.horizontalLayout_20.setObjectName(u"horizontalLayout_20")
        self.movementManual = QWidget(self.manualPageContents)
        self.movementManual.setObjectName(u"movementManual")
        self.verticalLayout_22 = QVBoxLayout(self.movementManual)
        self.verticalLayout_22.setObjectName(u"verticalLayout_22")
        self.verticalLayout_22.setContentsMargins(30, -1, 25, -1)
        # Spacing reducido (por defecto heredaba el del estilo, ~11px, y
        # dejaba demasiado hueco entre "Movement XYZ" y Scale/Velocity) —
        # sube la fila de Scale/Velocity y libera espacio para el D-pad.
        self.verticalLayout_22.setSpacing(6)

        # ── Control por eje: Enable/Disable + Home ───────────────────────
        # Fila 1: encabezados X/Y/Z, cada uno centrado sobre su pareja de
        # botones. Fila 2: los 6 botones (Ena/Home × 3 ejes) en una sola
        # fila — las columnas 2 y 5 son espaciadores más anchos que el
        # spacing normal, para que se lea como 3 grupos de 2 botones y no
        # como 6 botones sueltos.
        self.axisControlManual = QFrame(self.movementManual)
        self.axisControlManual.setObjectName(u"axisControlManual")
        self.axisControlManual.setFrameShape(QFrame.StyledPanel)
        self.axisControlManual.setFrameShadow(QFrame.Raised)
        self.gridLayout_axisControl = QGridLayout(self.axisControlManual)
        self.gridLayout_axisControl.setObjectName(u"gridLayout_axisControl")
        self.gridLayout_axisControl.setHorizontalSpacing(6)
        self.gridLayout_axisControl.setVerticalSpacing(8)

        self.labelAxisX = QLabel(self.axisControlManual)
        self.labelAxisX.setObjectName(u"labelAxisX")
        self.labelAxisX.setAlignment(Qt.AlignCenter)
        self.gridLayout_axisControl.addWidget(self.labelAxisX, 0, 0, 1, 2, Qt.AlignHCenter)

        self.labelAxisY = QLabel(self.axisControlManual)
        self.labelAxisY.setObjectName(u"labelAxisY")
        self.labelAxisY.setAlignment(Qt.AlignCenter)
        self.gridLayout_axisControl.addWidget(self.labelAxisY, 0, 3, 1, 2, Qt.AlignHCenter)

        self.labelAxisZ = QLabel(self.axisControlManual)
        self.labelAxisZ.setObjectName(u"labelAxisZ")
        self.labelAxisZ.setAlignment(Qt.AlignCenter)
        self.gridLayout_axisControl.addWidget(self.labelAxisZ, 0, 6, 1, 2, Qt.AlignHCenter)

        self.toggleXBtn = QPushButton(self.axisControlManual)
        self.toggleXBtn.setObjectName(u"toggleXBtn")
        self.toggleXBtn.setCheckable(True)
        self.gridLayout_axisControl.addWidget(self.toggleXBtn, 1, 0)
        self.homeXBtn = QPushButton(self.axisControlManual)
        self.homeXBtn.setObjectName(u"homeXBtn")
        self.gridLayout_axisControl.addWidget(self.homeXBtn, 1, 1)

        self.toggleYBtn = QPushButton(self.axisControlManual)
        self.toggleYBtn.setObjectName(u"toggleYBtn")
        self.toggleYBtn.setCheckable(True)
        self.gridLayout_axisControl.addWidget(self.toggleYBtn, 1, 3)
        self.homeYBtn = QPushButton(self.axisControlManual)
        self.homeYBtn.setObjectName(u"homeYBtn")
        self.gridLayout_axisControl.addWidget(self.homeYBtn, 1, 4)

        self.toggleZBtn = QPushButton(self.axisControlManual)
        self.toggleZBtn.setObjectName(u"toggleZBtn")
        self.toggleZBtn.setCheckable(True)
        self.gridLayout_axisControl.addWidget(self.toggleZBtn, 1, 6)
        self.homeZBtn = QPushButton(self.axisControlManual)
        self.homeZBtn.setObjectName(u"homeZBtn")
        self.gridLayout_axisControl.addWidget(self.homeZBtn, 1, 7)

        self.gridLayout_axisControl.addItem(
            QSpacerItem(20, 1, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum), 1, 2)
        self.gridLayout_axisControl.addItem(
            QSpacerItem(20, 1, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum), 1, 5)

        self.verticalLayout_22.addWidget(self.axisControlManual)

        self.verticalSpacer_axisControl = QSpacerItem(20, 16, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.verticalLayout_22.addItem(self.verticalSpacer_axisControl)

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
        # "Scale", "Increment" y "Velocity" son las 3 columnas de la misma
        # fila 0 del grid, cada una con su control debajo en la fila 1 —
        # así las 3 etiquetas quedan garantizadas a la misma altura (antes
        # "Increment" vivía en un QVBoxLayout anidado dentro de la fila 1,
        # un nivel más abajo que "Scale"/"Velocity").
        self.label_31 = QLabel(self.frame_4)
        self.label_31.setObjectName(u"label_31")

        self.gridLayout_4.addWidget(self.label_31, 0, 0, 1, 1)

        self.label_increment = QLabel(self.frame_4)
        self.label_increment.setObjectName(u"label_increment")

        self.gridLayout_4.addWidget(self.label_increment, 0, 2, 1, 1)

        self.label_32 = QLabel(self.frame_4)
        self.label_32.setObjectName(u"label_32")

        self.gridLayout_4.addWidget(self.label_32, 0, 4, 1, 1)

        self.scaleList = QComboBox(self.frame_4)
        self.scaleList.setObjectName(u"scaleList")
        sizePolicy1.setHeightForWidth(self.scaleList.sizePolicy().hasHeightForWidth())
        self.scaleList.setSizePolicy(sizePolicy1)
        self.scaleList.setMinimumSize(QSize(0, 0))
        self.scaleList.setMaximumSize(QSize(16777215, 16777215))
        self.scaleList.setStyleSheet(u"outline: none")

        self.gridLayout_4.addWidget(self.scaleList, 1, 0, 1, 1)

        self.scaleMultiplier = QSpinBox(self.frame_4)
        self.scaleMultiplier.setObjectName(u"scaleMultiplier")
        self.scaleMultiplier.setMinimum(1)
        self.scaleMultiplier.setMaximum(999)
        self.scaleMultiplier.setValue(1)

        self.gridLayout_4.addWidget(self.scaleMultiplier, 1, 2, 1, 1)

        self.velocity = QDoubleSpinBox(self.frame_4)
        self.velocity.setObjectName(u"velocity")
        sizePolicy1.setHeightForWidth(self.velocity.sizePolicy().hasHeightForWidth())
        self.velocity.setSizePolicy(sizePolicy1)
        self.velocity.setMinimumSize(QSize(0, 0))
        self.velocity.setMaximumSize(QSize(16777215, 16777215))

        self.gridLayout_4.addWidget(self.velocity, 1, 4, 1, 1)

        self.horizontalSpacer_2 = QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_4.addItem(self.horizontalSpacer_2, 1, 1, 1, 1)

        self.horizontalSpacer_5 = QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_4.addItem(self.horizontalSpacer_5, 1, 3, 1, 1)


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

        self.verticalSpacer_safetyWindow = QSpacerItem(20, 16, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.verticalLayout_22.addItem(self.verticalSpacer_safetyWindow)

        # ── Master Safety Window (antes en Calibration, migrada aquí debajo
        # del D-pad/Z — Calibration como página independiente desapareció).
        # get_safety_window() la siguen consultando "Limit to position
        # window" de Auto y M901 de G-Code, solo cambia desde qué página se
        # define.
        self.frame_safetyWindow = QFrame(self.movementManual)
        self.frame_safetyWindow.setObjectName(u"frame_safetyWindow")
        self.frame_safetyWindow.setFrameShape(QFrame.StyledPanel)
        self.frame_safetyWindow.setFrameShadow(QFrame.Raised)
        self.verticalLayout_safetyWindow = QVBoxLayout(self.frame_safetyWindow)
        self.verticalLayout_safetyWindow.setObjectName(u"verticalLayout_safetyWindow")
        self.label_safetyWindowTitle = QLabel(self.frame_safetyWindow)
        self.label_safetyWindowTitle.setObjectName(u"label_safetyWindowTitle")
        self.verticalLayout_safetyWindow.addWidget(self.label_safetyWindowTitle, 0, Qt.AlignHCenter)

        self.label_safetyWindowHint = QLabel(self.frame_safetyWindow)
        self.label_safetyWindowHint.setObjectName(u"label_safetyWindowHint")
        self.label_safetyWindowHint.setWordWrap(True)
        self.label_safetyWindowHint.setAlignment(Qt.AlignCenter)
        self.verticalLayout_safetyWindow.addWidget(self.label_safetyWindowHint)

        self.horizontalLayout_safetyWindowBody = QHBoxLayout()
        self.horizontalLayout_safetyWindowBody.setObjectName(u"horizontalLayout_safetyWindowBody")

        self.gridLayout_safetyWindow = QGridLayout()
        self.gridLayout_safetyWindow.setObjectName(u"gridLayout_safetyWindow")
        self.label_xMinField = QLabel(self.frame_safetyWindow)
        self.label_xMinField.setObjectName(u"label_xMinField")
        self.gridLayout_safetyWindow.addWidget(self.label_xMinField, 0, 0)
        self.xMinField = QLineEdit(self.frame_safetyWindow)
        self.xMinField.setObjectName(u"xMinField")
        self.xMinField.setReadOnly(True)
        self.xMinField.setAlignment(Qt.AlignCenter)
        self.gridLayout_safetyWindow.addWidget(self.xMinField, 0, 1)
        self.label_xMaxField = QLabel(self.frame_safetyWindow)
        self.label_xMaxField.setObjectName(u"label_xMaxField")
        self.gridLayout_safetyWindow.addWidget(self.label_xMaxField, 1, 0)
        self.xMaxField = QLineEdit(self.frame_safetyWindow)
        self.xMaxField.setObjectName(u"xMaxField")
        self.xMaxField.setReadOnly(True)
        self.xMaxField.setAlignment(Qt.AlignCenter)
        self.gridLayout_safetyWindow.addWidget(self.xMaxField, 1, 1)
        self.label_yMinField = QLabel(self.frame_safetyWindow)
        self.label_yMinField.setObjectName(u"label_yMinField")
        self.gridLayout_safetyWindow.addWidget(self.label_yMinField, 2, 0)
        self.yMinField = QLineEdit(self.frame_safetyWindow)
        self.yMinField.setObjectName(u"yMinField")
        self.yMinField.setReadOnly(True)
        self.yMinField.setAlignment(Qt.AlignCenter)
        self.gridLayout_safetyWindow.addWidget(self.yMinField, 2, 1)
        self.label_yMaxField = QLabel(self.frame_safetyWindow)
        self.label_yMaxField.setObjectName(u"label_yMaxField")
        self.gridLayout_safetyWindow.addWidget(self.label_yMaxField, 3, 0)
        self.yMaxField = QLineEdit(self.frame_safetyWindow)
        self.yMaxField.setObjectName(u"yMaxField")
        self.yMaxField.setReadOnly(True)
        self.yMaxField.setAlignment(Qt.AlignCenter)
        self.gridLayout_safetyWindow.addWidget(self.yMaxField, 3, 1)
        self.horizontalLayout_safetyWindowBody.addLayout(self.gridLayout_safetyWindow)

        # Botones de captura al otro lado de los campos, más largos que en
        # Calibration (panel lateral estrecho) — aquí Manual tiene todo el
        # ancho de la página principal.
        self.verticalLayout_safetyWindowButtons = QVBoxLayout()
        self.verticalLayout_safetyWindowButtons.setObjectName(u"verticalLayout_safetyWindowButtons")
        self.setCorner1Btn = QPushButton(self.frame_safetyWindow)
        self.setCorner1Btn.setObjectName(u"setCorner1Btn")
        self.setCorner2Btn = QPushButton(self.frame_safetyWindow)
        self.setCorner2Btn.setObjectName(u"setCorner2Btn")
        self.verticalLayout_safetyWindowButtons.addWidget(self.setCorner1Btn)
        self.verticalLayout_safetyWindowButtons.addWidget(self.setCorner2Btn)
        self.horizontalLayout_safetyWindowBody.addLayout(self.verticalLayout_safetyWindowButtons)

        self.verticalLayout_safetyWindow.addLayout(self.horizontalLayout_safetyWindowBody)

        self.safetyWindowStatusLabel = QLabel(self.frame_safetyWindow)
        self.safetyWindowStatusLabel.setObjectName(u"safetyWindowStatusLabel")
        self.safetyWindowStatusLabel.setAlignment(Qt.AlignCenter)
        self.verticalLayout_safetyWindow.addWidget(self.safetyWindowStatusLabel)

        self.verticalLayout_22.addWidget(self.frame_safetyWindow)

        self.verticalSpacer_10 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_22.addItem(self.verticalSpacer_10)


        self.horizontalLayout_20.addWidget(self.movementManual)

        self.horizontalSpacer_9 = QSpacerItem(25, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_20.addItem(self.horizontalSpacer_9)

        self.shutterManual = QFrame(self.manualPageContents)
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

        # Antes un spacer Expanding — dejaba el conjunto de abajo (board
        # power/laserOC/slider/Laser ON) centrado verticalmente en el hueco
        # disponible, con un salto grande respecto al título "⚡ Laser". Un
        # spacer fijo y pequeño lo deja pegado al título; el spacer Expanding
        # que sigue a frame_7 (verticalSpacer_16) es el que absorbe el resto
        # del espacio sobrante hacia abajo.
        self.verticalSpacer_11 = QSpacerItem(20, 12, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.verticalLayout_21.addItem(self.verticalSpacer_11)

        self.frame_7 = QFrame(self.shutterManual)
        self.frame_7.setObjectName(u"frame_7")
        sizePolicy4.setHeightForWidth(self.frame_7.sizePolicy().hasHeightForWidth())
        self.frame_7.setSizePolicy(sizePolicy4)
        self.frame_7.setFrameShape(QFrame.StyledPanel)
        self.frame_7.setFrameShadow(QFrame.Raised)
        self.verticalLayout_34 = QVBoxLayout(self.frame_7)
        self.verticalLayout_34.setObjectName(u"verticalLayout_34")

        self.laserBoardPowerBtn = QPushButton(self.frame_7)
        self.laserBoardPowerBtn.setObjectName(u"laserBoardPowerBtn")
        self.laserBoardPowerBtn.setFont(font1)
        self.laserBoardPowerBtn.setCheckable(True)
        self.laserBoardPowerBtn.setChecked(False)
        self.laserBoardPowerBtn.setMinimumSize(QSize(150, 40))

        self.verticalLayout_34.addWidget(self.laserBoardPowerBtn)

        # laserOC entre "Laser board power" y el slider — no al principio de
        # la columna (08_ui_polish_fixes.md ronda 2, §2.4)
        self.laserOC = QLabel(self.frame_7)
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
        self.laserOC.setAlignment(Qt.AlignCenter)
        self.laserOC.setMargin(3)

        self.verticalLayout_34.addWidget(self.laserOC, 0, Qt.AlignHCenter)

        self.laserPowerRow = QFrame(self.frame_7)
        self.laserPowerRow.setObjectName(u"laserPowerRow")
        self.horizontalLayout_laserPowerRow = QHBoxLayout(self.laserPowerRow)
        self.horizontalLayout_laserPowerRow.setObjectName(u"horizontalLayout_laserPowerRow")

        self.laserPowerSlider = QSlider(self.laserPowerRow)
        self.laserPowerSlider.setObjectName(u"laserPowerSlider")
        self.laserPowerSlider.setOrientation(Qt.Horizontal)
        self.laserPowerSlider.setMinimum(0)
        self.laserPowerSlider.setMaximum(100)
        self.laserPowerSlider.setValue(0)

        self.horizontalLayout_laserPowerRow.addWidget(self.laserPowerSlider)

        self.labelLaserPowerManual = QLineEdit(self.laserPowerRow)
        self.labelLaserPowerManual.setObjectName(u"labelLaserPowerManual")
        self.labelLaserPowerManual.setReadOnly(True)
        self.labelLaserPowerManual.setAlignment(Qt.AlignCenter)

        self.horizontalLayout_laserPowerRow.addWidget(self.labelLaserPowerManual)

        self.verticalLayout_34.addWidget(self.laserPowerRow)

        self.laserFireBtn = QPushButton(self.frame_7)
        self.laserFireBtn.setObjectName(u"laserFireBtn")
        self.laserFireBtn.setFont(font1)
        self.laserFireBtn.setCheckable(False)
        self.laserFireBtn.setAutoExclusive(False)
        self.laserFireBtn.setMinimumSize(QSize(150, 60))

        self.verticalLayout_34.addWidget(self.laserFireBtn)


        self.verticalLayout_21.addWidget(self.frame_7, 0, Qt.AlignTop)

        self.verticalSpacer_16 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_21.addItem(self.verticalSpacer_16)


        self.horizontalLayout_20.addWidget(self.shutterManual)

        self.horizontalSpacer_10 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_20.addItem(self.horizontalSpacer_10)

        self.manualPage.setWidget(self.manualPageContents)
        self.mainPages.addWidget(self.manualPage)
        self.autoPage = QWidget()
        self.autoPage.setObjectName(u"autoPage")
        sizePolicy4.setHeightForWidth(self.autoPage.sizePolicy().hasHeightForWidth())
        self.autoPage.setSizePolicy(sizePolicy4)
        self.verticalLayout_autoPage = QVBoxLayout(self.autoPage)
        self.verticalLayout_autoPage.setObjectName(u"verticalLayout_autoPage")
        self.verticalLayout_autoPage.setContentsMargins(20, 12, 20, 12)

        # ── Control por eje: Enable/Disable + Home (copia propia, Auto no
        # comparte estos widgets con Manual) — mismo patrón de fila única
        # ya aplicado en Manual (08_ui_polish_fixes.md §3.1 / ronda 2 §4):
        # fila de encabezados X/Y/Z, fila de 6 botones agrupados de dos en
        # dos por eje. ─────────────────────────────────────────────────
        self.axisControlAuto = QFrame(self.autoPage)
        self.axisControlAuto.setObjectName(u"axisControlAuto")
        self.axisControlAuto.setFrameShape(QFrame.StyledPanel)
        self.axisControlAuto.setFrameShadow(QFrame.Raised)
        self.gridLayout_axisControlAuto = QGridLayout(self.axisControlAuto)
        self.gridLayout_axisControlAuto.setObjectName(u"gridLayout_axisControlAuto")
        self.gridLayout_axisControlAuto.setHorizontalSpacing(6)
        self.gridLayout_axisControlAuto.setVerticalSpacing(8)

        self.labelAxisAutoX = QLabel(self.axisControlAuto)
        self.labelAxisAutoX.setObjectName(u"labelAxisAutoX")
        self.labelAxisAutoX.setAlignment(Qt.AlignCenter)
        self.gridLayout_axisControlAuto.addWidget(self.labelAxisAutoX, 0, 0, 1, 2, Qt.AlignHCenter)

        self.labelAxisAutoY = QLabel(self.axisControlAuto)
        self.labelAxisAutoY.setObjectName(u"labelAxisAutoY")
        self.labelAxisAutoY.setAlignment(Qt.AlignCenter)
        self.gridLayout_axisControlAuto.addWidget(self.labelAxisAutoY, 0, 3, 1, 2, Qt.AlignHCenter)

        self.labelAxisAutoZ = QLabel(self.axisControlAuto)
        self.labelAxisAutoZ.setObjectName(u"labelAxisAutoZ")
        self.labelAxisAutoZ.setAlignment(Qt.AlignCenter)
        self.gridLayout_axisControlAuto.addWidget(self.labelAxisAutoZ, 0, 6, 1, 2, Qt.AlignHCenter)

        self.toggleAutoXBtn = QPushButton(self.axisControlAuto)
        self.toggleAutoXBtn.setObjectName(u"toggleAutoXBtn")
        self.toggleAutoXBtn.setCheckable(True)
        self.gridLayout_axisControlAuto.addWidget(self.toggleAutoXBtn, 1, 0)
        self.homeAutoXBtn = QPushButton(self.axisControlAuto)
        self.homeAutoXBtn.setObjectName(u"homeAutoXBtn")
        self.gridLayout_axisControlAuto.addWidget(self.homeAutoXBtn, 1, 1)

        self.toggleAutoYBtn = QPushButton(self.axisControlAuto)
        self.toggleAutoYBtn.setObjectName(u"toggleAutoYBtn")
        self.toggleAutoYBtn.setCheckable(True)
        self.gridLayout_axisControlAuto.addWidget(self.toggleAutoYBtn, 1, 3)
        self.homeAutoYBtn = QPushButton(self.axisControlAuto)
        self.homeAutoYBtn.setObjectName(u"homeAutoYBtn")
        self.gridLayout_axisControlAuto.addWidget(self.homeAutoYBtn, 1, 4)

        self.toggleAutoZBtn = QPushButton(self.axisControlAuto)
        self.toggleAutoZBtn.setObjectName(u"toggleAutoZBtn")
        self.toggleAutoZBtn.setCheckable(True)
        self.gridLayout_axisControlAuto.addWidget(self.toggleAutoZBtn, 1, 6)
        self.homeAutoZBtn = QPushButton(self.axisControlAuto)
        self.homeAutoZBtn.setObjectName(u"homeAutoZBtn")
        self.gridLayout_axisControlAuto.addWidget(self.homeAutoZBtn, 1, 7)

        self.gridLayout_axisControlAuto.addItem(
            QSpacerItem(20, 1, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum), 1, 2)
        self.gridLayout_axisControlAuto.addItem(
            QSpacerItem(20, 1, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum), 1, 5)

        self.verticalLayout_autoPage.addWidget(self.axisControlAuto)

        # ── Cuerpo: selector de modo + panel por modo (izq.) | preview +
        # botones de salida (der.) ──────────────────────────────────────
        self.horizontalLayout_autoBody = QHBoxLayout()
        self.horizontalLayout_autoBody.setObjectName(u"horizontalLayout_autoBody")

        # QScrollArea con marco oculto — mismo patrón que manualPage: el
        # selector de modo y sus campos (modeStack) no siempre caben en el
        # alto disponible, así que se envuelven en scroll en vez de dejar
        # que se compriman o recorten. setFrameShape(NoFrame) + fondo
        # transparente en el QScrollArea y su viewport para que se vea como
        # una continuación natural de la página, no como una caja aparte.
        self.autoLeftScroll = QScrollArea()
        self.autoLeftScroll.setObjectName(u"autoLeftScroll")
        self.autoLeftScroll.setWidgetResizable(True)
        self.autoLeftScroll.setFrameShape(QFrame.NoFrame)
        self.autoLeftScroll.setStyleSheet(u"QScrollArea { background: transparent; border: none; }")
        self.autoLeftScroll.viewport().setStyleSheet(u"background: transparent;")

        self.autoLeftScrollContents = QWidget()
        self.autoLeftScrollContents.setObjectName(u"autoLeftScrollContents")
        self.verticalLayout_autoLeft = QVBoxLayout(self.autoLeftScrollContents)
        self.verticalLayout_autoLeft.setObjectName(u"verticalLayout_autoLeft")

        self.modeSelectorRow = QFrame(self.autoLeftScrollContents)
        self.modeSelectorRow.setObjectName(u"modeSelectorRow")
        self.horizontalLayout_modeSelectorRow = QHBoxLayout(self.modeSelectorRow)
        self.horizontalLayout_modeSelectorRow.setObjectName(u"horizontalLayout_modeSelectorRow")
        self.label_autoMode = QLabel(self.modeSelectorRow)
        self.label_autoMode.setObjectName(u"label_autoMode")
        self.horizontalLayout_modeSelectorRow.addWidget(self.label_autoMode)
        self.modeSelector = QComboBox(self.modeSelectorRow)
        self.modeSelector.setObjectName(u"modeSelector")
        self.horizontalLayout_modeSelectorRow.addWidget(self.modeSelector)
        self.verticalLayout_autoLeft.addWidget(self.modeSelectorRow)

        self.modeStack = QStackedWidget(self.autoLeftScrollContents)
        self.modeStack.setObjectName(u"modeStack")

        # -- Panel 0: Single point --
        self.panelSinglePoint = QWidget()
        self.panelSinglePoint.setObjectName(u"panelSinglePoint")
        self.verticalLayout_panelSinglePoint = QVBoxLayout(self.panelSinglePoint)
        self.label_spPosition = QLabel(self.panelSinglePoint)
        self.label_spPosition.setObjectName(u"label_spPosition")
        self.verticalLayout_panelSinglePoint.addWidget(self.label_spPosition)
        self.horizontalLayout_spPosition = QHBoxLayout()
        self.spX = QDoubleSpinBox(self.panelSinglePoint)
        self.spX.setObjectName(u"spX")
        self.spY = QDoubleSpinBox(self.panelSinglePoint)
        self.spY.setObjectName(u"spY")
        self.spZ = QDoubleSpinBox(self.panelSinglePoint)
        self.spZ.setObjectName(u"spZ")
        self.horizontalLayout_spPosition.addWidget(self.spX)
        self.horizontalLayout_spPosition.addWidget(self.spY)
        self.horizontalLayout_spPosition.addWidget(self.spZ)
        self.verticalLayout_panelSinglePoint.addLayout(self.horizontalLayout_spPosition)
        self.spFireCheck = QCheckBox(self.panelSinglePoint)
        self.spFireCheck.setObjectName(u"spFireCheck")
        self.verticalLayout_panelSinglePoint.addWidget(self.spFireCheck)
        self.label_spDuration = QLabel(self.panelSinglePoint)
        self.label_spDuration.setObjectName(u"label_spDuration")
        self.verticalLayout_panelSinglePoint.addWidget(self.label_spDuration)
        self.horizontalLayout_spDuration = QHBoxLayout()
        self.spDuration = QDoubleSpinBox(self.panelSinglePoint)
        self.spDuration.setObjectName(u"spDuration")
        self.spDurationScale = QComboBox(self.panelSinglePoint)
        self.spDurationScale.setObjectName(u"spDurationScale")
        self.horizontalLayout_spDuration.addWidget(self.spDuration)
        self.horizontalLayout_spDuration.addWidget(self.spDurationScale)
        self.verticalLayout_panelSinglePoint.addLayout(self.horizontalLayout_spDuration)
        self.verticalLayout_panelSinglePoint.addStretch(1)
        self.modeStack.addWidget(self.panelSinglePoint)

        # -- Panel 1: Fixed-distance firing --
        self.panelFixedDistance = QWidget()
        self.panelFixedDistance.setObjectName(u"panelFixedDistance")
        self.verticalLayout_panelFixedDistance = QVBoxLayout(self.panelFixedDistance)
        self.label_fdStart = QLabel(self.panelFixedDistance)
        self.label_fdStart.setObjectName(u"label_fdStart")
        self.verticalLayout_panelFixedDistance.addWidget(self.label_fdStart)
        self.horizontalLayout_fdStart = QHBoxLayout()
        self.fdStartX = QDoubleSpinBox(self.panelFixedDistance)
        self.fdStartX.setObjectName(u"fdStartX")
        self.fdStartY = QDoubleSpinBox(self.panelFixedDistance)
        self.fdStartY.setObjectName(u"fdStartY")
        self.horizontalLayout_fdStart.addWidget(self.fdStartX)
        self.horizontalLayout_fdStart.addWidget(self.fdStartY)
        self.verticalLayout_panelFixedDistance.addLayout(self.horizontalLayout_fdStart)
        self.label_fdEnd = QLabel(self.panelFixedDistance)
        self.label_fdEnd.setObjectName(u"label_fdEnd")
        self.verticalLayout_panelFixedDistance.addWidget(self.label_fdEnd)
        self.horizontalLayout_fdEnd = QHBoxLayout()
        self.fdEndX = QDoubleSpinBox(self.panelFixedDistance)
        self.fdEndX.setObjectName(u"fdEndX")
        self.fdEndY = QDoubleSpinBox(self.panelFixedDistance)
        self.fdEndY.setObjectName(u"fdEndY")
        self.horizontalLayout_fdEnd.addWidget(self.fdEndX)
        self.horizontalLayout_fdEnd.addWidget(self.fdEndY)
        self.verticalLayout_panelFixedDistance.addLayout(self.horizontalLayout_fdEnd)
        self.label_fdDistance = QLabel(self.panelFixedDistance)
        self.label_fdDistance.setObjectName(u"label_fdDistance")
        self.verticalLayout_panelFixedDistance.addWidget(self.label_fdDistance)
        self.horizontalLayout_fdDistance = QHBoxLayout()
        self.fdDistance = QDoubleSpinBox(self.panelFixedDistance)
        self.fdDistance.setObjectName(u"fdDistance")
        self.fdDistanceScale = QComboBox(self.panelFixedDistance)
        self.fdDistanceScale.setObjectName(u"fdDistanceScale")
        self.horizontalLayout_fdDistance.addWidget(self.fdDistance)
        self.horizontalLayout_fdDistance.addWidget(self.fdDistanceScale)
        self.verticalLayout_panelFixedDistance.addLayout(self.horizontalLayout_fdDistance)
        self.label_fdPulses = QLabel(self.panelFixedDistance)
        self.label_fdPulses.setObjectName(u"label_fdPulses")
        self.verticalLayout_panelFixedDistance.addWidget(self.label_fdPulses)
        self.fdPulses = QSpinBox(self.panelFixedDistance)
        self.fdPulses.setObjectName(u"fdPulses")
        self.verticalLayout_panelFixedDistance.addWidget(self.fdPulses)
        self.label_fdPower = QLabel(self.panelFixedDistance)
        self.label_fdPower.setObjectName(u"label_fdPower")
        self.verticalLayout_panelFixedDistance.addWidget(self.label_fdPower)
        self.fdPower = QDoubleSpinBox(self.panelFixedDistance)
        self.fdPower.setObjectName(u"fdPower")
        self.verticalLayout_panelFixedDistance.addWidget(self.fdPower)
        self.label_fdTravelSpeed = QLabel(self.panelFixedDistance)
        self.label_fdTravelSpeed.setObjectName(u"label_fdTravelSpeed")
        self.verticalLayout_panelFixedDistance.addWidget(self.label_fdTravelSpeed)
        self.fdTravelSpeed = QDoubleSpinBox(self.panelFixedDistance)
        self.fdTravelSpeed.setObjectName(u"fdTravelSpeed")
        self.verticalLayout_panelFixedDistance.addWidget(self.fdTravelSpeed)
        self.fdLimitWindow = QCheckBox(self.panelFixedDistance)
        self.fdLimitWindow.setObjectName(u"fdLimitWindow")
        self.verticalLayout_panelFixedDistance.addWidget(self.fdLimitWindow)
        self.verticalLayout_panelFixedDistance.addStretch(1)
        self.modeStack.addWidget(self.panelFixedDistance)

        # -- Panel 2: Point array --
        self.panelPointArray = QWidget()
        self.panelPointArray.setObjectName(u"panelPointArray")
        self.verticalLayout_panelPointArray = QVBoxLayout(self.panelPointArray)
        self.horizontalLayout_paNewPass = QHBoxLayout()
        self.paAxisCombo = QComboBox(self.panelPointArray)
        self.paAxisCombo.setObjectName(u"paAxisCombo")
        self.paStart = QDoubleSpinBox(self.panelPointArray)
        self.paStart.setObjectName(u"paStart")
        self.paEnd = QDoubleSpinBox(self.panelPointArray)
        self.paEnd.setObjectName(u"paEnd")
        self.paCross = QDoubleSpinBox(self.panelPointArray)
        self.paCross.setObjectName(u"paCross")
        self.horizontalLayout_paNewPass.addWidget(self.paAxisCombo)
        self.horizontalLayout_paNewPass.addWidget(self.paStart)
        self.horizontalLayout_paNewPass.addWidget(self.paEnd)
        self.horizontalLayout_paNewPass.addWidget(self.paCross)
        self.verticalLayout_panelPointArray.addLayout(self.horizontalLayout_paNewPass)
        self.horizontalLayout_paPassButtons = QHBoxLayout()
        self.paAddPassBtn = QPushButton(self.panelPointArray)
        self.paAddPassBtn.setObjectName(u"paAddPassBtn")
        self.paRemovePassBtn = QPushButton(self.panelPointArray)
        self.paRemovePassBtn.setObjectName(u"paRemovePassBtn")
        self.horizontalLayout_paPassButtons.addWidget(self.paAddPassBtn)
        self.horizontalLayout_paPassButtons.addWidget(self.paRemovePassBtn)
        self.verticalLayout_panelPointArray.addLayout(self.horizontalLayout_paPassButtons)
        self.paPassesList = QListWidget(self.panelPointArray)
        self.paPassesList.setObjectName(u"paPassesList")
        self.paPassesList.setMaximumHeight(90)
        self.verticalLayout_panelPointArray.addWidget(self.paPassesList)
        self.label_paDistance = QLabel(self.panelPointArray)
        self.label_paDistance.setObjectName(u"label_paDistance")
        self.verticalLayout_panelPointArray.addWidget(self.label_paDistance)
        self.horizontalLayout_paDistance = QHBoxLayout()
        self.paDistance = QDoubleSpinBox(self.panelPointArray)
        self.paDistance.setObjectName(u"paDistance")
        self.paDistanceScale = QComboBox(self.panelPointArray)
        self.paDistanceScale.setObjectName(u"paDistanceScale")
        self.horizontalLayout_paDistance.addWidget(self.paDistance)
        self.horizontalLayout_paDistance.addWidget(self.paDistanceScale)
        self.verticalLayout_panelPointArray.addLayout(self.horizontalLayout_paDistance)
        self.label_paPulses = QLabel(self.panelPointArray)
        self.label_paPulses.setObjectName(u"label_paPulses")
        self.verticalLayout_panelPointArray.addWidget(self.label_paPulses)
        self.paPulses = QSpinBox(self.panelPointArray)
        self.paPulses.setObjectName(u"paPulses")
        self.verticalLayout_panelPointArray.addWidget(self.paPulses)
        self.label_paPower = QLabel(self.panelPointArray)
        self.label_paPower.setObjectName(u"label_paPower")
        self.verticalLayout_panelPointArray.addWidget(self.label_paPower)
        self.paPower = QDoubleSpinBox(self.panelPointArray)
        self.paPower.setObjectName(u"paPower")
        self.verticalLayout_panelPointArray.addWidget(self.paPower)
        self.label_paTravelSpeed = QLabel(self.panelPointArray)
        self.label_paTravelSpeed.setObjectName(u"label_paTravelSpeed")
        self.verticalLayout_panelPointArray.addWidget(self.label_paTravelSpeed)
        self.paTravelSpeed = QDoubleSpinBox(self.panelPointArray)
        self.paTravelSpeed.setObjectName(u"paTravelSpeed")
        self.verticalLayout_panelPointArray.addWidget(self.paTravelSpeed)
        self.paLimitWindow = QCheckBox(self.panelPointArray)
        self.paLimitWindow.setObjectName(u"paLimitWindow")
        self.verticalLayout_panelPointArray.addWidget(self.paLimitWindow)
        self.modeStack.addWidget(self.panelPointArray)

        # -- Panel 3: Power gradient --
        self.panelPowerGradient = QWidget()
        self.panelPowerGradient.setObjectName(u"panelPowerGradient")
        self.verticalLayout_panelPowerGradient = QVBoxLayout(self.panelPowerGradient)
        self.label_pgType = QLabel(self.panelPowerGradient)
        self.label_pgType.setObjectName(u"label_pgType")
        self.verticalLayout_panelPowerGradient.addWidget(self.label_pgType)
        self.pgTypeCombo = QComboBox(self.panelPowerGradient)
        self.pgTypeCombo.setObjectName(u"pgTypeCombo")
        self.verticalLayout_panelPowerGradient.addWidget(self.pgTypeCombo)

        self.pgTypeStack = QStackedWidget(self.panelPowerGradient)
        self.pgTypeStack.setObjectName(u"pgTypeStack")
        self.pgLinearPanel = QWidget()
        self.pgLinearPanel.setObjectName(u"pgLinearPanel")
        self.verticalLayout_pgLinearPanel = QVBoxLayout(self.pgLinearPanel)
        self.label_pgLinearStart = QLabel(self.pgLinearPanel)
        self.label_pgLinearStart.setObjectName(u"label_pgLinearStart")
        self.verticalLayout_pgLinearPanel.addWidget(self.label_pgLinearStart)
        self.horizontalLayout_pgStart = QHBoxLayout()
        self.pgStartX = QDoubleSpinBox(self.pgLinearPanel)
        self.pgStartX.setObjectName(u"pgStartX")
        self.pgStartY = QDoubleSpinBox(self.pgLinearPanel)
        self.pgStartY.setObjectName(u"pgStartY")
        self.horizontalLayout_pgStart.addWidget(self.pgStartX)
        self.horizontalLayout_pgStart.addWidget(self.pgStartY)
        self.verticalLayout_pgLinearPanel.addLayout(self.horizontalLayout_pgStart)
        self.label_pgLinearEnd = QLabel(self.pgLinearPanel)
        self.label_pgLinearEnd.setObjectName(u"label_pgLinearEnd")
        self.verticalLayout_pgLinearPanel.addWidget(self.label_pgLinearEnd)
        self.horizontalLayout_pgEnd = QHBoxLayout()
        self.pgEndX = QDoubleSpinBox(self.pgLinearPanel)
        self.pgEndX.setObjectName(u"pgEndX")
        self.pgEndY = QDoubleSpinBox(self.pgLinearPanel)
        self.pgEndY.setObjectName(u"pgEndY")
        self.horizontalLayout_pgEnd.addWidget(self.pgEndX)
        self.horizontalLayout_pgEnd.addWidget(self.pgEndY)
        self.verticalLayout_pgLinearPanel.addLayout(self.horizontalLayout_pgEnd)
        self.pgTypeStack.addWidget(self.pgLinearPanel)

        self.pgRadialPanel = QWidget()
        self.pgRadialPanel.setObjectName(u"pgRadialPanel")
        self.verticalLayout_pgRadialPanel = QVBoxLayout(self.pgRadialPanel)
        self.label_pgCenter = QLabel(self.pgRadialPanel)
        self.label_pgCenter.setObjectName(u"label_pgCenter")
        self.verticalLayout_pgRadialPanel.addWidget(self.label_pgCenter)
        self.horizontalLayout_pgCenter = QHBoxLayout()
        self.pgCenterX = QDoubleSpinBox(self.pgRadialPanel)
        self.pgCenterX.setObjectName(u"pgCenterX")
        self.pgCenterY = QDoubleSpinBox(self.pgRadialPanel)
        self.pgCenterY.setObjectName(u"pgCenterY")
        self.horizontalLayout_pgCenter.addWidget(self.pgCenterX)
        self.horizontalLayout_pgCenter.addWidget(self.pgCenterY)
        self.verticalLayout_pgRadialPanel.addLayout(self.horizontalLayout_pgCenter)
        self.label_pgRadius = QLabel(self.pgRadialPanel)
        self.label_pgRadius.setObjectName(u"label_pgRadius")
        self.verticalLayout_pgRadialPanel.addWidget(self.label_pgRadius)
        self.pgRadius = QDoubleSpinBox(self.pgRadialPanel)
        self.pgRadius.setObjectName(u"pgRadius")
        self.verticalLayout_pgRadialPanel.addWidget(self.pgRadius)
        self.pgTypeStack.addWidget(self.pgRadialPanel)

        self.verticalLayout_panelPowerGradient.addWidget(self.pgTypeStack)

        self.label_pgDistance = QLabel(self.panelPowerGradient)
        self.label_pgDistance.setObjectName(u"label_pgDistance")
        self.verticalLayout_panelPowerGradient.addWidget(self.label_pgDistance)
        self.horizontalLayout_pgDistance = QHBoxLayout()
        self.pgDistance = QDoubleSpinBox(self.panelPowerGradient)
        self.pgDistance.setObjectName(u"pgDistance")
        self.pgDistanceScale = QComboBox(self.panelPowerGradient)
        self.pgDistanceScale.setObjectName(u"pgDistanceScale")
        self.horizontalLayout_pgDistance.addWidget(self.pgDistance)
        self.horizontalLayout_pgDistance.addWidget(self.pgDistanceScale)
        self.verticalLayout_panelPowerGradient.addLayout(self.horizontalLayout_pgDistance)
        self.label_pgPower = QLabel(self.panelPowerGradient)
        self.label_pgPower.setObjectName(u"label_pgPower")
        self.verticalLayout_panelPowerGradient.addWidget(self.label_pgPower)
        self.horizontalLayout_pgPower = QHBoxLayout()
        self.pgPowerStart = QDoubleSpinBox(self.panelPowerGradient)
        self.pgPowerStart.setObjectName(u"pgPowerStart")
        self.pgPowerEnd = QDoubleSpinBox(self.panelPowerGradient)
        self.pgPowerEnd.setObjectName(u"pgPowerEnd")
        self.horizontalLayout_pgPower.addWidget(self.pgPowerStart)
        self.horizontalLayout_pgPower.addWidget(self.pgPowerEnd)
        self.verticalLayout_panelPowerGradient.addLayout(self.horizontalLayout_pgPower)
        self.label_pgTravelSpeed = QLabel(self.panelPowerGradient)
        self.label_pgTravelSpeed.setObjectName(u"label_pgTravelSpeed")
        self.verticalLayout_panelPowerGradient.addWidget(self.label_pgTravelSpeed)
        self.pgTravelSpeed = QDoubleSpinBox(self.panelPowerGradient)
        self.pgTravelSpeed.setObjectName(u"pgTravelSpeed")
        self.verticalLayout_panelPowerGradient.addWidget(self.pgTravelSpeed)
        self.verticalLayout_panelPowerGradient.addStretch(1)
        self.modeStack.addWidget(self.panelPowerGradient)

        self.verticalLayout_autoLeft.addWidget(self.modeStack)

        self.autoLeftScroll.setWidget(self.autoLeftScrollContents)
        self.horizontalLayout_autoBody.addWidget(self.autoLeftScroll, 1)

        # ── Vista previa de G-Code + botones de salida ──────────────────
        self.verticalLayout_autoRight = QVBoxLayout()
        self.verticalLayout_autoRight.setObjectName(u"verticalLayout_autoRight")
        self.label_autoPreview = QLabel(self.autoPage)
        self.label_autoPreview.setObjectName(u"label_autoPreview")
        self.verticalLayout_autoRight.addWidget(self.label_autoPreview)
        self.gcodePreviewAuto = QTextEdit(self.autoPage)
        self.gcodePreviewAuto.setObjectName(u"gcodePreviewAuto")
        self.gcodePreviewAuto.setReadOnly(True)
        self.gcodePreviewAuto.setFont(QFont("Courier New", 9))
        self.verticalLayout_autoRight.addWidget(self.gcodePreviewAuto)
        self.horizontalLayout_autoOutputButtons = QHBoxLayout()
        self.openInGCodeBtn = QPushButton(self.autoPage)
        self.openInGCodeBtn.setObjectName(u"openInGCodeBtn")
        self.downloadFileBtn = QPushButton(self.autoPage)
        self.downloadFileBtn.setObjectName(u"downloadFileBtn")
        self.horizontalLayout_autoOutputButtons.addWidget(self.openInGCodeBtn)
        self.horizontalLayout_autoOutputButtons.addWidget(self.downloadFileBtn)
        self.verticalLayout_autoRight.addLayout(self.horizontalLayout_autoOutputButtons)

        self.horizontalLayout_autoBody.addLayout(self.verticalLayout_autoRight, 1)

        self.verticalLayout_autoPage.addLayout(self.horizontalLayout_autoBody)

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

        # "Select File" reubicado encima de los dos recuadros (drag&drop +
        # vista previa) — justo debajo del título de la sección y por
        # encima de frameGcode, ocupando el ancho completo de la página
        # igual que startBtn más abajo.
        self.selectFileBtn = QPushButton(self.gcodePage)
        self.selectFileBtn.setObjectName(u"selectFileBtn")
        font7 = QFont()
        font7.setBold(False)
        self.selectFileBtn.setFont(font7)
        icon22 = QIcon()
        icon22.addFile(_icon_path(u":/font_awesome_solid/icons/font_awesome/solid/file-import.png"), QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.selectFileBtn.setIcon(icon22)

        self.verticalLayout_15.addWidget(self.selectFileBtn)

        self.verticalSpacer_selectFile = QSpacerItem(20, 12, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.verticalLayout_15.addItem(self.verticalSpacer_selectFile)

        self.frameGcode = QFrame(self.gcodePage)
        self.frameGcode.setObjectName(u"frameGcode")
        self.frameGcode.setFrameShape(QFrame.StyledPanel)
        self.frameGcode.setFrameShadow(QFrame.Raised)
        self.verticalLayout_24 = QVBoxLayout(self.frameGcode)
        self.verticalLayout_24.setObjectName(u"verticalLayout_24")
        self.verticalLayout_24.setContentsMargins(20, -1, 20, 10)
        self.horizontalLayout_gcodeSplit = QHBoxLayout()
        self.horizontalLayout_gcodeSplit.setObjectName(u"horizontalLayout_gcodeSplit")

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

        self.horizontalLayout_gcodeSplit.addWidget(self.dragYdrop, 1)

        # ── Vista previa de solo lectura del G-Code cargado (04_gcode.md §1) ──
        self.gcodePreview = QTextEdit(self.frameGcode)
        self.gcodePreview.setObjectName(u"gcodePreview")
        self.gcodePreview.setReadOnly(True)
        self.gcodePreview.setMinimumSize(QSize(0, 150))
        self.gcodePreview.setFont(QFont("Courier New", 9))
        self.horizontalLayout_gcodeSplit.addWidget(self.gcodePreview, 1)

        self.verticalLayout_24.addLayout(self.horizontalLayout_gcodeSplit)

        self.verticalSpacer_8 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_24.addItem(self.verticalSpacer_8)

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

        # ── Dirección IP del controlador iSMC (06_connection.md) ────────
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

        self.hostAddressInput = QLineEdit(self.frame_13)
        self.hostAddressInput.setObjectName(u"hostAddressInput")

        self.verticalLayout_12.addWidget(self.hostAddressInput)


        self.verticalLayout_18.addWidget(self.frame_13)

        self.verticalSpacer_7 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_18.addItem(self.verticalSpacer_7)

        self.connectBtn = QPushButton(self.connectionPage)
        self.connectBtn.setObjectName(u"connectBtn")
        self.connectBtn.setFont(font1)

        self.verticalLayout_18.addWidget(self.connectBtn)

        self.rightMenuPages.addWidget(self.connectionPage)

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
        self.helpContentLabel.setText(QCoreApplication.translate("MainWindow", u"<p style=\"margin-top:0px;\"><b>Manual — Safety Window</b><br>Safety Window: defines the rectangular area (X/Y) where the laser is allowed to fire from Auto and G-Code. Move to a corner with the jog controls, press Set Corner 1; move to the opposite corner, press Set Corner 2. The 4 fields fill in automatically.</p><p><b>Auto — modes</b><br><b>Single point:</b> moves to a position and optionally fires once, at rest.<br><b>Fixed-distance firing:</b> fires at regular distance intervals while moving, without stopping.<br><b>Point array:</b> repeats fixed-distance firing over several axis-aligned passes.<br><b>Power gradient:</b> fires with power that changes step by step along the path.</p><p><b>G-Code — command reference</b><br><b>G0</b> — rapid move, straight line (no firing). X Y Z (destination), F (speed, default 50 mm/s)<br><b>G1</b> — controlled move, straight line (fires while moving). X Y Z (destination), F (speed, default 50 mm/s)<br><b>G4</b> — pause/wait. P (milliseconds)<br><b>G28</b> — homing<br><b>G90</b> — coordinates are absolute<br><b>G91</b> — coordinates are relative to the current point<br><b>M0</b> — program pause, disables all 3 axes<br><b>M3</b> — turns the laser on. S (power, 0-100%)<br><b>M5</b> — turns the laser off<br><b>M900</b> — configures fixed-distance firing. D (distance between shots), P (pulses per event)<br><b>M901</b> — defines a position safety window. X (min/max) and Y (min/max)</p><p>For more information, you can check (in English):<br><a href=\"https://github.com/WhoisChe/LaserMotion_GUI\">https://github.com/WhoisChe/LaserMotion_GUI</a></p>", None))
        self.usal.setText("")
#if QT_CONFIG(tooltip)
        self.connectionBtn.setToolTip(QCoreApplication.translate("MainWindow", u"Connections", None))
#endif // QT_CONFIG(tooltip)
        self.connectionBtn.setText("")
        self.minimizeBtn.setText("")
        self.restoreBtn.setText("")
        self.closeBtn.setText("")
        self.estacionAerotech.setText("")
        self.laserIcon.setText("")
        self.laserTitleLabel.setText(QCoreApplication.translate("MainWindow", u"Laser Output:", None))
        self.labelLaserState.setText(QCoreApplication.translate("MainWindow", u"OFF", None))
        self.label_36.setText("")
        self.labelAxisX.setText(QCoreApplication.translate("MainWindow", u"X", None))
        self.toggleXBtn.setText(QCoreApplication.translate("MainWindow", u"ENABLE", None))
        self.homeXBtn.setText(QCoreApplication.translate("MainWindow", u"Home", None))
        self.labelAxisY.setText(QCoreApplication.translate("MainWindow", u"Y", None))
        self.toggleYBtn.setText(QCoreApplication.translate("MainWindow", u"ENABLE", None))
        self.homeYBtn.setText(QCoreApplication.translate("MainWindow", u"Home", None))
        self.labelAxisZ.setText(QCoreApplication.translate("MainWindow", u"Z", None))
        self.toggleZBtn.setText(QCoreApplication.translate("MainWindow", u"ENABLE", None))
        self.homeZBtn.setText(QCoreApplication.translate("MainWindow", u"Home", None))
        self.label_19.setText(QCoreApplication.translate("MainWindow", u"Movement XYZ", None))
        self.label_31.setText(QCoreApplication.translate("MainWindow", u"Scale", None))
        self.label_increment.setText(QCoreApplication.translate("MainWindow", u"Increment", None))
        self.label_32.setText(QCoreApplication.translate("MainWindow", u"Velocity", None))
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
        self.label_7.setText(QCoreApplication.translate("MainWindow", u"Laser", None))
        self.laserOC.setText("")
        self.laserBoardPowerBtn.setText(QCoreApplication.translate("MainWindow", u"Laser board power: OFF", None))
        self.labelLaserPowerManual.setText(QCoreApplication.translate("MainWindow", u"0% · 0 mW", None))
        self.laserFireBtn.setText(QCoreApplication.translate("MainWindow", u"Laser ON", None))
        self.labelAxisAutoX.setText(QCoreApplication.translate("MainWindow", u"X", None))
        self.toggleAutoXBtn.setText(QCoreApplication.translate("MainWindow", u"ENABLE", None))
        self.homeAutoXBtn.setText(QCoreApplication.translate("MainWindow", u"Home", None))
        self.labelAxisAutoY.setText(QCoreApplication.translate("MainWindow", u"Y", None))
        self.toggleAutoYBtn.setText(QCoreApplication.translate("MainWindow", u"ENABLE", None))
        self.homeAutoYBtn.setText(QCoreApplication.translate("MainWindow", u"Home", None))
        self.labelAxisAutoZ.setText(QCoreApplication.translate("MainWindow", u"Z", None))
        self.toggleAutoZBtn.setText(QCoreApplication.translate("MainWindow", u"ENABLE", None))
        self.homeAutoZBtn.setText(QCoreApplication.translate("MainWindow", u"Home", None))
        self.label_autoMode.setText(QCoreApplication.translate("MainWindow", u"Mode:", None))
        self.label_spPosition.setText(QCoreApplication.translate("MainWindow", u"Position (X, Y, Z)", None))
        self.spFireCheck.setText(QCoreApplication.translate("MainWindow", u"Fire at this point", None))
        self.label_spDuration.setText(QCoreApplication.translate("MainWindow", u"Duration", None))
        self.label_fdStart.setText(QCoreApplication.translate("MainWindow", u"Start point (X, Y)", None))
        self.label_fdEnd.setText(QCoreApplication.translate("MainWindow", u"End point (X, Y)", None))
        self.label_fdDistance.setText(QCoreApplication.translate("MainWindow", u"Distance between events", None))
        self.label_fdPulses.setText(QCoreApplication.translate("MainWindow", u"Pulses per event", None))
        self.label_fdPower.setText(QCoreApplication.translate("MainWindow", u"Power (%)", None))
        self.label_fdTravelSpeed.setText(QCoreApplication.translate("MainWindow", u"Travel speed (mm/s)", None))
        self.fdLimitWindow.setText(QCoreApplication.translate("MainWindow", u"Limit to position window", None))
        self.paAddPassBtn.setText(QCoreApplication.translate("MainWindow", u"Add pass", None))
        self.paRemovePassBtn.setText(QCoreApplication.translate("MainWindow", u"Remove pass", None))
        self.label_paDistance.setText(QCoreApplication.translate("MainWindow", u"Distance between events", None))
        self.label_paPulses.setText(QCoreApplication.translate("MainWindow", u"Pulses per event", None))
        self.label_paPower.setText(QCoreApplication.translate("MainWindow", u"Power (%)", None))
        self.label_paTravelSpeed.setText(QCoreApplication.translate("MainWindow", u"Travel speed (mm/s)", None))
        self.paLimitWindow.setText(QCoreApplication.translate("MainWindow", u"Limit to position window", None))
        self.label_pgType.setText(QCoreApplication.translate("MainWindow", u"Gradient type", None))
        self.label_pgLinearStart.setText(QCoreApplication.translate("MainWindow", u"Start point (X, Y)", None))
        self.label_pgLinearEnd.setText(QCoreApplication.translate("MainWindow", u"End point (X, Y)", None))
        self.label_pgCenter.setText(QCoreApplication.translate("MainWindow", u"Center (X, Y)", None))
        self.label_pgRadius.setText(QCoreApplication.translate("MainWindow", u"Radius", None))
        self.label_pgDistance.setText(QCoreApplication.translate("MainWindow", u"Distance between events", None))
        self.label_pgPower.setText(QCoreApplication.translate("MainWindow", u"Power start % → end %", None))
        self.label_pgTravelSpeed.setText(QCoreApplication.translate("MainWindow", u"Travel speed (mm/s)", None))
        self.label_autoPreview.setText(QCoreApplication.translate("MainWindow", u"G-Code preview", None))
        self.openInGCodeBtn.setText(QCoreApplication.translate("MainWindow", u"Open in G-Code Exec", None))
        self.downloadFileBtn.setText(QCoreApplication.translate("MainWindow", u"Download file", None))
        self.label_20.setText("")
        self.label_9.setText(QCoreApplication.translate("MainWindow", u"Upload the G-Code file", None))
        self.label_6.setText(QCoreApplication.translate("MainWindow", u"Drag and drop your file", None))
        self.selectFileBtn.setText(QCoreApplication.translate("MainWindow", u"Select File", None))
        self.editBtn.setText(QCoreApplication.translate("MainWindow", u"Edit", None))
        self.startBtn.setText(QCoreApplication.translate("MainWindow", u"Start", None))
        self.closeRightMenuBtn.setText("")
        self.label_11.setText(QCoreApplication.translate("MainWindow", u"Connection Page", None))
        self.label_21.setText(QCoreApplication.translate("MainWindow", u"iSMC controller IP address", None))
        self.hostAddressInput.setPlaceholderText(QCoreApplication.translate("MainWindow", u"192.168.7.1", None))
        self.connectBtn.setText(QCoreApplication.translate("MainWindow", u"Connect", None))
        self.label_safetyWindowTitle.setText(QCoreApplication.translate("MainWindow", u"Master Safety Window", None))
        self.label_safetyWindowHint.setText(QCoreApplication.translate("MainWindow", u"Define the safe firing area using two opposite corners. Move there with the jog above, then press the matching button.", None))
        self.label_xMinField.setText(QCoreApplication.translate("MainWindow", u"X min", None))
        self.xMinField.setText(QCoreApplication.translate("MainWindow", u"—", None))
        self.label_xMaxField.setText(QCoreApplication.translate("MainWindow", u"X max", None))
        self.xMaxField.setText(QCoreApplication.translate("MainWindow", u"—", None))
        self.label_yMinField.setText(QCoreApplication.translate("MainWindow", u"Y min", None))
        self.yMinField.setText(QCoreApplication.translate("MainWindow", u"—", None))
        self.label_yMaxField.setText(QCoreApplication.translate("MainWindow", u"Y max", None))
        self.yMaxField.setText(QCoreApplication.translate("MainWindow", u"—", None))
        self.setCorner1Btn.setText(QCoreApplication.translate("MainWindow", u"Set Corner 1 (move here first)", None))
        self.setCorner2Btn.setText(QCoreApplication.translate("MainWindow", u"Set Corner 2 (opposite corner)", None))
        self.safetyWindowStatusLabel.setText(QCoreApplication.translate("MainWindow", u"No corners captured yet", None))
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"ETSII B\u00e9jar | Ingenier\u00eda Electr\u00f3nica Industrial y Autom\u00e1tica | Christine Marie Quan Jo", None))
        self.size_grip.setText("")
    # retranslateUi

