from PyQt6.QtCore import Qt, QThread
from PyQt6 import sip
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from qfluentwidgets import CardWidget
import sys
from pathlib import Path
import os
import subprocess
from datetime import datetime

from plugins.minidump_Parser_qcm6125.minidump.ramparse_command import build_ramparse_command

from PyQt6.QtCore import Qt, QPoint, QSize, QUrl, QRect, QPropertyAnimation, pyqtSignal, QObject
from PyQt6.QtGui import QIcon, QFont, QColor, QPainter
from PyQt6.QtWidgets import QApplication, QHBoxLayout, QVBoxLayout, QGraphicsOpacityEffect,QFileDialog

from qfluentwidgets import (CardWidget, setTheme, Theme, IconWidget, BodyLabel, CaptionLabel, PushButton,
                            TransparentToolButton, FluentIcon, RoundMenu, Action, ElevatedCardWidget,
                            ImageLabel, isDarkTheme, FlowLayout, MSFluentTitleBar, SimpleCardWidget,
                            HeaderCardWidget, InfoBarIcon, HyperlinkLabel, HorizontalFlipView, EditableComboBox,
                            PrimaryPushButton, TitleLabel, PillPushButton, setFont, ScrollArea,
                            VerticalSeparator, MSFluentWindow, NavigationItemPosition, GroupHeaderCardWidget,
                            ComboBox, SearchLineEdit, SubtitleLabel, StateToolTip, LineEdit, Flyout)

from qfluentwidgets.components.widgets.acrylic_label import AcrylicBrush

from app.common.config import ROOTPATH
from app.common.logging import logger
from app.common.utils import linuxPath2winPath

GNU_TOOLS_PATH = os.path.join(ROOTPATH, 'tools', 'gnu-tools')
PYTHON_BIN_ROOT = linuxPath2winPath(os.path.join(ROOTPATH, 'tools', 'Python310'))
PYTHON_BIN_PATH = linuxPath2winPath(os.path.join(ROOTPATH, 'tools', 'Python310', 'python.exe'))

CURRENT_PLUGIN_DIR = os.path.dirname(__file__)

# resource文件夹的路径, 位于当前文件的上两级目录
resource_path = 'app/resource'


def isWin11():
    return sys.platform == 'win32' and sys.getwindowsversion().build >= 22000


if isWin11():
    from qframelesswindow import AcrylicWindow as Window
else:
    from qframelesswindow import FramelessWindow as Window

class StatisticsWidget(QWidget):
    """ Statistics widget """

    def __init__(self, title: str, value: str, parent=None):
        super().__init__(parent=parent)
        self.titleLabel = CaptionLabel(title, self)
        self.valueLabel = BodyLabel(value, self)
        self.vBoxLayout = QVBoxLayout(self)

        self.vBoxLayout.setContentsMargins(16, 0, 16, 0)
        self.vBoxLayout.addWidget(self.valueLabel, 0, Qt.AlignmentFlag.AlignTop)
        self.vBoxLayout.addWidget(self.titleLabel, 0, Qt.AlignmentFlag.AlignBottom)

        setFont(self.valueLabel, 18, QFont.Weight.DemiBold)
        self.titleLabel.setTextColor(QColor(96, 96, 96), QColor(206, 206, 206))


class AppInfoCard(SimpleCardWidget):
    """ App information card """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.iconLabel = ImageLabel(os.path.join(CURRENT_PLUGIN_DIR, "logo.png"), self)
        self.iconLabel.setBorderRadius(8, 8, 8, 8)
        self.iconLabel.scaledToWidth(120)

        self.nameLabel = TitleLabel('Minidump Parser qcm6125', self)

        #self.installButton = PrimaryPushButton('执行', self)
        #self.installButton.clicked.connect(self.installButtonClicked)
        #self.installButtonStateTooltip = None

        #self.companyLabel = HyperlinkLabel(
        #    QUrl('https://qfluentwidgets.com'), 'Shokokawaii Inc.', self)
        self.companyLabel = CaptionLabel('@Designed by heps.', self)
        #self.installButton.setFixedWidth(160)

        #self.scoreWidget = StatisticsWidget('平均', '5.0', self)
        #self.separator = VerticalSeparator(self)
        #self.commentWidget = StatisticsWidget('评论数', '3K', self)

        self.descriptionLabel = BodyLabel(
            '用于拆分高通 QCM6125 平台的 minidump，生成 ap_minidump.elf，同步生成解析输出文件', self)
        self.descriptionLabel.setWordWrap(True)

        self.tagButton = PillPushButton('QCM6125', self)
        self.tagButton.setCheckable(False)
        setFont(self.tagButton, 12)
        self.tagButton.setFixedSize(80, 32)

        self.tagButton2 = PillPushButton('Minidump', self)
        self.tagButton2.setCheckable(False)
        setFont(self.tagButton2, 12)
        self.tagButton2.setFixedSize(80, 32)

        #self.shareButton = TransparentToolButton(FluentIcon.SHARE, self)
        #self.shareButton.setFixedSize(32, 32)
        #self.shareButton.setIconSize(QSize(14, 14))

        self.hBoxLayout = QHBoxLayout(self)
        self.vBoxLayout = QVBoxLayout()
        self.topLayout = QHBoxLayout()
        self.statisticsLayout = QHBoxLayout()
        self.buttonLayout = QHBoxLayout()

        self.initLayout()
        self.setBorderRadius(8)

    def initLayout(self):
        self.hBoxLayout.setSpacing(30)
        self.hBoxLayout.setContentsMargins(34, 24, 24, 24)
        self.hBoxLayout.addWidget(self.iconLabel)
        self.hBoxLayout.addLayout(self.vBoxLayout)

        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.setSpacing(0)

        # name label and install button
        self.vBoxLayout.addLayout(self.topLayout)
        self.topLayout.setContentsMargins(0, 0, 0, 0)
        self.topLayout.addWidget(self.nameLabel)
        #self.topLayout.addWidget(self.installButton, 0, Qt.AlignmentFlag.AlignRight)

        # company label
        self.vBoxLayout.addSpacing(3)
        self.vBoxLayout.addWidget(self.companyLabel)

        # statistics widgets
        self.vBoxLayout.addSpacing(20)
        self.vBoxLayout.addLayout(self.statisticsLayout)
        self.statisticsLayout.setContentsMargins(0, 0, 0, 0)
        self.statisticsLayout.setSpacing(10)
        #self.statisticsLayout.addWidget(self.scoreWidget)
        #self.statisticsLayout.addWidget(self.separator)
        #self.statisticsLayout.addWidget(self.commentWidget)
        self.statisticsLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        # description label
        self.vBoxLayout.addSpacing(20)
        self.vBoxLayout.addWidget(self.descriptionLabel)

        # button
        self.vBoxLayout.addSpacing(12)
        self.buttonLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.addLayout(self.buttonLayout)
        self.buttonLayout.addWidget(self.tagButton, 0, Qt.AlignmentFlag.AlignLeft)
        self.buttonLayout.addWidget(self.tagButton2, 1, Qt.AlignmentFlag.AlignLeft)
        #self.buttonLayout.addWidget(self.shareButton, 0, Qt.AlignmentFlag.AlignRight)

    # def installButtonClicked(self):
    #     if self.installButtonStateTooltip == '已执行':
    #         self.installButtonStateTooltip.setContent('已解析完成')
    #         self.installButtonStateTooltip.setState(True)
    #         self.installButton.setEnabled(True)
    #         self.installButtonStateTooltip = None
    #     else:
    #         self.installButtonStateTooltip = StateToolTip(
    #            '正在解析中', '请耐心等待哦~~', self
    #         )
    #         # 设置点击后不允许再次点击
    #         self.installButton.setDisabled(True)
    #         # set position 在右下角
    #         self.parent.vBoxLayout.addSpacing(12)
    #         self.parent.vBoxLayout.addWidget(self.installButtonStateTooltip, 3, Qt.AlignmentFlag.AlignBottom|Qt.AlignmentFlag.AlignRight)

    #         self.installButtonStateTooltip.show()

class Worker(QThread):
    signal = pyqtSignal(str)

    def __init__(self, commands, show_terminal=True, env=None):
        super().__init__()
        self.commands = commands
        self.show_terminal = show_terminal
        self.env = env

    def run(self):
        logger.info("Worker Thread ID: {}".format(QThread.currentThreadId()))
        creationflags = subprocess.CREATE_NEW_CONSOLE if self.show_terminal else subprocess.CREATE_NO_WINDOW

        try:
            commands = self.commands() if callable(self.commands) else self.commands
            for command in commands:
                logger.info("Run command: {}".format(subprocess.list2cmdline(command)))
                result = subprocess.run(command, env=self.env, creationflags=creationflags,
                                        capture_output=not self.show_terminal, text=not self.show_terminal,
                                        errors='replace' if not self.show_terminal else None)
                if result.returncode != 0:
                    logger.error("Command failed (exit {}): {}".format(
                        result.returncode, ((result.stdout or '') + (result.stderr or ''))[-6000:]))
                    self.signal.emit("ERROR")
                    return
        except Exception as error:
            logger.error("Failed to run minidump parser: {}".format(error))
            self.signal.emit("ERROR:{}".format(error))
            return

        self.signal.emit("SUCCESS")


class DescriptionCard(HeaderCardWidget):
    """ Description card """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.descriptionLabel = BodyLabel(
            '选择高通 rawdump/minidump 文件后，可将其中的 md_* 段拆分到输出目录，'
            '生成 ap_minidump.elf；选择 vmlinux 后可解析输出目录中的 Minidump。', self)

        self.descriptionLabel.setWordWrap(True)
        self.viewLayout.addWidget(self.descriptionLabel)
        self.setTitle('描述')
        self.setBorderRadius(8)

class SettinsCard(GroupHeaderCardWidget):

    def __init__(self, parent=None, parentvBoxLayout=None):
        super().__init__(parent)

        self.parentvBoxLayout = parentvBoxLayout

        self.setTitle("基本设置")
        self.setBorderRadius(8)

        # 初始化参数
        self.dumpfile = ""
        self.vmlinux_file = ""
        self.output_path = linuxPath2winPath(os.path.join(CURRENT_PLUGIN_DIR, 'minidump', 'minidump_out'))
        os.makedirs(self.output_path, exist_ok=True)

        # 设置状态提示
        self.stateTooltip = None
        self.bottomStateLayout = QHBoxLayout()

        # 选择按钮以及输入框部件
        self.chooseButton = PushButton("选择")
        #self.fileLineEdit = LineEdit()
        self.vmlinuxButton = PushButton("选择")
        self.kernelButton = PushButton("选择")
        self.kernelButton.clicked.connect(self.kernelButtonClicked)

        # mod_path参数部件
        self.ModlineEdit = LineEdit()

        # 设置Button的点击事件
        self.chooseButton.clicked.connect(self.chooseButtonClicked)
        self.vmlinuxButton.clicked.connect(self.vmlinuxButtonClicked)

        # 显示终端部件
        self.comboBox = ComboBox()

        # 平台选择部件
        self.platformComboBox = EditableComboBox()

        # 入口脚本部件
        self.lineEdit = LineEdit()

        # 设置部件的固定宽度
        self.chooseButton.setFixedWidth(120)
        self.vmlinuxButton.setFixedWidth(120)
        self.kernelButton.setFixedWidth(120)
        #self.fileLineEdit.setFixedWidth(320)

        self.lineEdit.setFixedWidth(320)
        self.ModlineEdit.setFixedWidth(320)
        self.comboBox.setFixedWidth(120)
        self.comboBox.addItems(["始终显示", "始终隐藏"])
        self.comboBox.setCurrentIndex(1)
        # 设置comboBox的选择点击事件
        self.comboBox.currentIndexChanged.connect(self.comboBoxClicked)

        self.platformComboBox.setFixedWidth(160)
        self.platformComboBox.addItems(['拆分并生成 ELF', '仅拆分'])
        # 设置platformComboBox的编辑事件
        #self.platformComboBox.currentTextChanged.connect(logger.info)
        self.platformComboBox.currentIndexChanged.connect(self.platformComboBoxClicked)

        self.lineEdit.setPlaceholderText("请输入额外的解析参数")

        # 底部运行按钮以及提示
        self.hintIcon = IconWidget(InfoBarIcon.INFORMATION)
        self.hintLabel = BodyLabel("运行可拆分文件，解析 Minidump 可分析现有输出")
        self.runButton = PrimaryPushButton(FluentIcon.PLAY_SOLID, "解压Minidump")
        self.parseButton = PrimaryPushButton(FluentIcon.PLAY, "解析 Minidump")
        self.bottomLayout = QHBoxLayout()

        # 设置底部工具栏布局
        self.hintIcon.setFixedSize(16, 16)
        self.bottomLayout.setSpacing(10)
        self.bottomLayout.setContentsMargins(24, 15, 24, 20)
        self.bottomLayout.addWidget(self.hintIcon, 0, Qt.AlignmentFlag.AlignLeft)
        self.bottomLayout.addWidget(self.hintLabel, 0, Qt.AlignmentFlag.AlignLeft)
        self.bottomLayout.addStretch(1)
        self.bottomLayout.addWidget(self.runButton, 0, Qt.AlignmentFlag.AlignRight)
        self.bottomLayout.addWidget(self.parseButton, 0, Qt.AlignmentFlag.AlignRight)
        self.bottomLayout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        # 设置底部状态布局
        self.bottomStateLayout.setSpacing(10)
        self.bottomStateLayout.setContentsMargins(24, 15, 24, 20)
        self.bottomStateLayout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        self.bottomStateLayout.addStretch(1)


        self.ramdumpGroup = self.addGroup("{}/images/Rocket.svg".format(resource_path), "Minidump文件", "选择 rawdump/minidump 文件", self.chooseButton)
        self.vmlinuxGroup = self.addGroup("{}/images/jsdesign.svg".format(resource_path), "输出目录", self.output_path, self.vmlinuxButton)
        self.kernelGroup = self.addGroup("{}/images/jsdesign.svg".format(resource_path), "vmlinux", "选择内核符号文件以解析 Minidump", self.kernelButton)
        self.addGroup("{}/images/Joystick.svg".format(resource_path), "解析方式", "选择是否生成 ap_minidump.elf", self.platformComboBox)
        self.addGroup("{}/images/Joystick.svg".format(resource_path), "运行终端", "设置是否显示命令行终端", self.comboBox)
        self.vBoxLayout.addLayout(self.bottomLayout)
        self.vBoxLayout.addLayout(self.bottomStateLayout)

        # 设置运行按钮的点击事件
        self.runButton.clicked.connect(self.runButtonClicked)
        self.parseButton.clicked.connect(self.parseButtonClicked)

    def chooseButtonClicked(self):
        logger.info("Choose Button Clicked")
        self.dumpfile, _ = QFileDialog.getOpenFileName(
            self, "选择 Minidump 文件", "C:/", "Binary Files (*.bin);;All Files (*)")
        self.dumpfile = linuxPath2winPath(self.dumpfile)
        logger.info("Choose Minidump File: {}".format(self.dumpfile))

        if self.dumpfile == "":
            self.chooseButton.setText("选择")
            self.ramdumpGroup.setContent("请选择 rawdump/minidump 文件")
        else:
            self.chooseButton.setText("已选择")
            if len(self.dumpfile) > 120:
                self.ramdumpGroup.setContent("{}.........{}".format(self.dumpfile[0:50], self.dumpfile[-70:]))
            else:
                self.ramdumpGroup.setContent(self.dumpfile)


    def vmlinuxButtonClicked(self):
        logger.info("Output directory Button Clicked")
        selected_path = QFileDialog.getExistingDirectory(self, "选择输出目录", self.output_path)
        if selected_path:
            self.output_path = linuxPath2winPath(selected_path)
        logger.info("Choose Output Directory: {}".format(self.output_path))

        if selected_path:
            self.vmlinuxButton.setText("已选择")
            if len(self.output_path) > 120:
                self.vmlinuxGroup.setContent("{}.........{}".format(self.output_path[0:50], self.output_path[-70:]))
            else:
                self.vmlinuxGroup.setContent(self.output_path)

    def kernelButtonClicked(self):
        selected_path, _ = QFileDialog.getOpenFileName(self, "选择 vmlinux", self.vmlinux_file or "C:/", "All Files (*)")
        if selected_path:
            self.vmlinux_file = linuxPath2winPath(selected_path)
            self.kernelGroup.setContent(self.vmlinux_file)
            self.kernelButton.setText("已选择")

    def comboBoxClicked(self, index):
        logger.info("ComboBox Clicked: {}".format(index))
        # 打印当前选择的值
        logger.info("Current Index: {}".format(self.comboBox.currentText()))

    def platformComboBoxClicked(self, index):
        logger.info("Platform ComboBox Clicked: {}".format(index))
        # 打印当前选择的值
        logger.info("Current Index: {}".format(self.platformComboBox.currentText()))

    def showNoSelectFileFlyout(self):
        Flyout.create(
            icon=InfoBarIcon.ERROR,
            title='未选择输入或输出',
            content="请先选择 minidump 文件和输出目录",
            target=self.runButton,
            parent=self.window()
        )

    def showFileStyleErrorFlyout(self):
        Flyout.create(
            icon=InfoBarIcon.ERROR,
            title='Vmlinux file style error',
            content="vmlinux文件名中不包含vmlinux字串, 请检查后再执行",
            target=self.runButton,
            parent=self.window()
        )

    def showZipFileTypeErrorFlyout(self):
        Flyout.create(
            icon=InfoBarIcon.ERROR,
            title='Dump file type error',
            content="压缩包请先行解压，请检查后再执行",
            target=self.runButton,
            parent=self.window()
        )

    def showNoPython(self):
        Flyout.create(
            icon=InfoBarIcon.ERROR,
            title='No python',
            content="请先安装python3环境并添加到环境变量",
            target=self.runButton,
            parent=self.window()
        )

    def customSignalHandler(self, value):
        # 接收到解析命令结束的信号
        logger.info("Custom signal handler: {}".format(value))
        if value == "SUCCESS":
            self.stateTooltip.setContent('解析完成')
            self.stateTooltip.setState(True)
            self.runButton.setEnabled(True)
            self.parseButton.setEnabled(True)
            self.stateTooltip.show()

        elif value == "ERROR":
            self.stateTooltip.setContent('解析失败')
            self.stateTooltip.setState(False)
            self.runButton.setEnabled(True)
            self.parseButton.setEnabled(True)
            self.stateTooltip.show()
        elif value.startswith("ERROR:"):
            self.stateTooltip.setContent('解析失败: {}'.format(value[6:]))
            self.stateTooltip.setState(False)
            self.runButton.setEnabled(True)
            self.parseButton.setEnabled(True)
            self.stateTooltip.show()
        else:
            logger.info(value)

        # 打开输出目录
        if value == "SUCCESS" and os.path.isdir(self.task_output_path):
            os.startfile(self.task_output_path)

    def start_task(self, commands, show_terminal, env):
        logger.info("Start task")
        self.worker = Worker(commands, show_terminal=show_terminal, env=env)
        self.worker.signal.connect(self.customSignalHandler)
        self.worker.start()

    def showTaskState(self, title, content):
        if self.stateTooltip is not None and not sip.isdeleted(self.stateTooltip):
            self.bottomStateLayout.removeWidget(self.stateTooltip)
            self.stateTooltip.deleteLater()
        self.stateTooltip = StateToolTip(title, content, self)
        self.bottomStateLayout.addWidget(self.stateTooltip, 0, Qt.AlignmentFlag.AlignRight)
        self.stateTooltip.show()

    def parseButtonClicked(self):
        if not self.vmlinux_file or not os.path.isfile(self.vmlinux_file):
            Flyout.create(icon=InfoBarIcon.ERROR, title='缺少 vmlinux',
                          content='请先选择有效的 vmlinux 文件', target=self.parseButton, parent=self.window())
            return

        python_path = PYTHON_BIN_PATH if os.path.isfile(PYTHON_BIN_PATH) else sys.executable
        parser_path = os.path.join(CURRENT_PLUGIN_DIR, 'linux-ramdump-parser-v2', 'ramparse.py')
        if not os.path.isfile(parser_path):
            Flyout.create(icon=InfoBarIcon.ERROR, title='缺少 ramparse',
                          content=parser_path, target=self.parseButton, parent=self.window())
            return
        analysis_path = os.path.join(self.output_path, 'minidump_out_analysis_' + datetime.now().strftime('%Y%m%d%H%M%S'))
        self.task_output_path = analysis_path
        self.showTaskState('正在解析 Minidump', '请耐心等待')
        self.runButton.setDisabled(True)
        self.parseButton.setDisabled(True)

        env = os.environ.copy()
        env['PATH'] = os.pathsep.join([env.get('PATH', ''), PYTHON_BIN_ROOT,
                                      os.path.join(PYTHON_BIN_ROOT, 'Scripts'), GNU_TOOLS_PATH])
        vmlinux_path = self.vmlinux_file
        dump_path = self.output_path

        def prepare_commands():
            command = build_ramparse_command(python_path, parser_path, vmlinux_path,
                                             dump_path, analysis_path)
            os.makedirs(analysis_path, exist_ok=True)
            return [command]

        self.start_task(prepare_commands, self.comboBox.currentText() == '始终显示', env)

    def runButtonClicked(self):
        logger.info("Run Button Clicked")
        # 获取chooseButton/ vmlinuxButton/ comboBox/ platformComboBox/ lineEdit的值
        logger.info("Minidump file: {}".format(self.dumpfile))
        logger.info("Output directory: {}".format(self.output_path))
        logger.info("Parse mode: {}".format(self.platformComboBox.currentText()))

        if self.comboBox.currentText() == "始终显示":
            show_terminal = True
        else:
            show_terminal = False

        logger.info("Display terminal: {}".format(show_terminal))

        if self.dumpfile == "" or self.output_path == "":
            self.showNoSelectFileFlyout()
        else:
            self.showTaskState('正在拆分 Minidump', '请耐心等待')

            # runbuton按钮设置为不可点击
            self.runButton.setDisabled(True)
            self.parseButton.setDisabled(True)
            self.task_output_path = self.output_path

            if not os.path.exists(self.output_path):
                os.makedirs(self.output_path)

            env = os.environ.copy()
            env['PATH'] = os.pathsep.join([os.environ.get('PATH', ''), PYTHON_BIN_ROOT])
            env['PATH'] = os.pathsep.join([env['PATH'], os.path.join(PYTHON_BIN_ROOT, 'Scripts')])
            python_path = PYTHON_BIN_PATH if os.path.isfile(PYTHON_BIN_PATH) else sys.executable
            tool_path = os.path.join(CURRENT_PLUGIN_DIR, 'minidump')
            commands = [[
                python_path,
                os.path.join(tool_path, 'minidump.py'),
                '-s',
                self.dumpfile,
                self.output_path,
            ]]
            if self.platformComboBox.currentText() == '拆分并生成 ELF':
                commands.append([
                    python_path,
                    os.path.join(tool_path, 'generate_appself.py'),
                    self.output_path,
                ])

            self.start_task(commands, show_terminal, env)


class LightBox(QWidget):
    """ Light box """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        if isDarkTheme():
            tintColor = QColor(32, 32, 32, 200)
        else:
            tintColor = QColor(255, 255, 255, 160)

        self.acrylicBrush = AcrylicBrush(self, 30, tintColor, QColor(0, 0, 0, 0))

        self.opacityEffect = QGraphicsOpacityEffect(self)
        self.opacityAni = QPropertyAnimation(self.opacityEffect, b"opacity", self)
        self.opacityEffect.setOpacity(1)
        self.setGraphicsEffect(self.opacityEffect)

        self.vBoxLayout = QVBoxLayout(self)
        self.closeButton = TransparentToolButton(FluentIcon.CLOSE, self)
        self.flipView = HorizontalFlipView(self)
        self.nameLabel = BodyLabel('屏幕截图 1', self)
        self.pageNumButton = PillPushButton('1 / 4', self)

        self.pageNumButton.setCheckable(False)
        self.pageNumButton.setFixedSize(80, 32)
        setFont(self.nameLabel, 16, QFont.Weight.DemiBold)

        self.closeButton.setFixedSize(32, 32)
        self.closeButton.setIconSize(QSize(14, 14))
        self.closeButton.clicked.connect(self.fadeOut)

        self.vBoxLayout.setContentsMargins(26, 28, 26, 28)
        self.vBoxLayout.addWidget(self.closeButton, 0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)
        self.vBoxLayout.addWidget(self.flipView, 1)
        self.vBoxLayout.addWidget(self.nameLabel, 0, Qt.AlignmentFlag.AlignHCenter)
        self.vBoxLayout.addSpacing(10)
        self.vBoxLayout.addWidget(self.pageNumButton, 0, Qt.AlignmentFlag.AlignHCenter)

        self.flipView.addImages([
            '{}/images/shoko1.jpg'.format(resource_path), '{}/images/shoko2.jpg'.format(resource_path),
            '{}/images/shoko3.jpg'.format(resource_path), '{}/images/shoko4.jpg'.format(resource_path),
        ])
        self.flipView.currentIndexChanged.connect(self.setCurrentIndex)

    def setCurrentIndex(self, index: int):
        self.nameLabel.setText(f'屏幕截图 {index + 1}')
        self.pageNumButton.setText(f'{index + 1} / {self.flipView.count()}')
        self.flipView.setCurrentIndex(index)

    def paintEvent(self, e):
        if self.acrylicBrush.isAvailable():
            return self.acrylicBrush.paint()

        painter = QPainter(self)
        painter.setPen(Qt.NoPen)
        if isDarkTheme():
            painter.setBrush(QColor(32, 32, 32))
        else:
            painter.setBrush(QColor(255, 255, 255))

        painter.drawRect(self.rect())

    def resizeEvent(self, e):
        w = self.width() - 52
        self.flipView.setItemSize(QSize(w, w * 9 // 16))

    def fadeIn(self):
        rect = QRect(self.mapToGlobal(QPoint()), self.size())
        self.acrylicBrush.grabImage(rect)

        self.opacityAni.setStartValue(0)
        self.opacityAni.setEndValue(1)
        self.opacityAni.setDuration(150)
        self.opacityAni.start()
        self.show()

    def fadeOut(self):
        self.opacityAni.setStartValue(1)
        self.opacityAni.setEndValue(0)
        self.opacityAni.setDuration(150)
        self.opacityAni.finished.connect(self._onAniFinished)
        self.opacityAni.start()

    def _onAniFinished(self):
        self.opacityAni.finished.disconnect()
        self.hide()

class MinidumpParserCardsInfo(ScrollArea):
    """Minidump parser subinterface."""

    def __init__(self, parent=None, routeKey=None):
        super().__init__(parent=parent)

        self.view = QWidget(self)

        self.routeKey = routeKey

        self.vBoxLayout = QVBoxLayout(self.view)
        self.appCard = AppInfoCard(parent=self)
        #self.galleryCard = GalleryCard(self)
        self.descriptionCard = DescriptionCard(self)
        self.settingCard = SettinsCard(self, parentvBoxLayout=self.vBoxLayout)
        #self.systemCard = SystemRequirementCard(self)

        self.lightBox = LightBox(self)
        self.lightBox.hide()
        #self.galleryCard.flipView.itemClicked.connect(self.showLightBox)

        self.setWidget(self.view)
        self.setWidgetResizable(True)
        self.setObjectName(routeKey)

        self.vBoxLayout.setSpacing(25)
        self.vBoxLayout.setContentsMargins(0, 0, 10, 30)
        self.vBoxLayout.addWidget(self.appCard, 0, Qt.AlignmentFlag.AlignTop)
        #self.vBoxLayout.addWidget(self.galleryCard, 0, Qt.AlignmentFlag.AlignTop)
        self.vBoxLayout.addWidget(self.descriptionCard, 1, Qt.AlignmentFlag.AlignTop)
        self.vBoxLayout.addWidget(self.settingCard, 2, Qt.AlignmentFlag.AlignTop)

        #self.vBoxLayout.addWidget(self.systemCard, 0, Qt.AlignmentFlag.AlignTop)

        self.enableTransparentBackground()

    def showLightBox(self):
        index = self.galleryCard.flipView.currentIndex()
        self.lightBox.setCurrentIndex(index)
        self.lightBox.fadeIn()

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self.lightBox.resize(self.size())


class MinidumpParserInterface:
    def __init__(self, parent=None, mainWindow=None):
        self.parent = parent
        self.mainWindow = mainWindow

        #self.mainWindow.tabBar.currentChanged.connect(self.onTabChanged)
        #self.mainWindow.stackedWidget.setCurrentWidget(self.mainWindow.showInterface)

    def addTab(self, routeKey, text, icon):
        logger.info('[TAB ADD] {}'.format(routeKey))
        self.mainWindow.tabBar.addTab(routeKey, text, icon)

        # tab左对齐
        self.mainWindow.showInterface.addWidget(MinidumpParserCardsInfo(routeKey=routeKey))
        self.mainWindow.showInterface.setCurrentWidget(self.mainWindow.showInterface.findChild(MinidumpParserCardsInfo, routeKey))
        self.mainWindow.stackedWidget.setCurrentWidget(self.mainWindow.showInterface)
        self.mainWindow.tabBar.setCurrentIndex(self.mainWindow.tabBar.count() - 1)

        #logger.info("[LIUQI] CurrentWidget: ".format(self.mainWindow.showInterface.currentWidget()))
        #logger.info("[LIUQI] CurrentWidgetRoutekey: ".format(self.mainWindow.showInterface.currentWidget().objectName()))

    # def onTabChanged(self, index):
    #     objectName = self.mainWindow.tabBar.currentTab().routeKey()
    #     logger.info("[LIUQI1] ObjectName: ", objectName)
    #     logger.info("[LIUQI1] index: ", index)
    #     logger.info("[LIUQI1] CurrentWidget: ", self.mainWindow.showInterface.findChild(LinuxRamdumpParserCardsInfo, objectName))
    #     self.mainWindow.showInterface.setCurrentWidget(self.mainWindow.showInterface.findChild(LinuxRamdumpParserCardsInfo, objectName))
    #     self.mainWindow.stackedWidget.setCurrentWidget(self.mainWindow.showInterface)
    #     self.mainWindow.tabBar.setCurrentIndex(index)
    #     logger.info("[LIUQI1] CurrentWidgetRoutekey: ", self.mainWindow.showInterface.currentWidget().objectName())
