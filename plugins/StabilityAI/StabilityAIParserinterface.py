from PyQt6.QtCore import Qt, QThread
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from qfluentwidgets import CardWidget
import sys
from pathlib import Path
import os
import subprocess
import yaml

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

def load_config(config_path):
    """加载 YAML 配置文件，支持环境变量展开"""
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    # 尝试多种编码
    for encoding in ['utf-8', 'utf-8-sig', 'latin-1']:
        try:
            with open(config_path, 'r', encoding=encoding) as f:
                content = f.read()
            break
        except (UnicodeDecodeError, LookupError):
            continue
    else:
        # 最后尝试二进制读取并强制 UTF-8 解码
        with open(config_path, 'rb') as f:
            content = f.read().decode('utf-8', errors='replace')
    
    # 展开环境变量 ${VAR_NAME}
    import re
    def replace_env(match):
        var_name = match.group(1)
        return os.environ.get(var_name, match.group(0))
    
    content = re.sub(r'\$\{([^}]+)\}', replace_env, content)
    
    # 解析 YAML
    config = yaml.safe_load(content)
    return config or {}


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

        self.nameLabel = TitleLabel('Stability-AI', self)

        #self.installButton = PrimaryPushButton('执行', self)
        #self.installButton.clicked.connect(self.installButtonClicked)
        #self.installButtonStateTooltip = None

        #self.companyLabel = HyperlinkLabel(
        #    QUrl('https://qfluentwidgets.com'), 'Shokokawaii Inc.', self)
        self.companyLabel = CaptionLabel('@Designed by iliuqi.', self)
        #self.installButton.setFixedWidth(160)

        #self.scoreWidget = StatisticsWidget('平均', '5.0', self)
        #self.separator = VerticalSeparator(self)
        #self.commentWidget = StatisticsWidget('评论数', '3K', self)

        self.descriptionLabel = BodyLabel(
            '一款利用AI自动分析内核日志，并生成详细报告的工具，帮助用户快速定位和解决问题。', self)
        self.descriptionLabel.setWordWrap(True)

        self.tagButton = PillPushButton('QCOM', self)
        self.tagButton.setCheckable(False)
        setFont(self.tagButton, 12)
        self.tagButton.setFixedSize(80, 32)

        self.tagButton2 = PillPushButton('AI', self)
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

class  Worker(QThread):
    signal = pyqtSignal(str)

    def __init__(self, command, shell=True, env=None):
        super().__init__()
        self.command = command
        self.shell = shell
        self.env = env

    def run(self):
        logger.info("Worker Thread ID: {}".format(QThread.currentThreadId()))
        #logger.info("Run command: {}".format(self.command))

        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        if self.shell == True:
            command = "start cmd /K {}".format(self.command)
        else:
            command = self.command
        #logger.info("Run command: {}".format(self.command))

        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, env=self.env)
        
        while True:
            line = process.stdout.readline()
            if not line:
                break
            logger.info(line.decode('gbk').strip())

        self.signal.emit("SUCCESS")
        #self.signal.emit("ERROR")


class DescriptionCard(HeaderCardWidget):
    """ Description card """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.descriptionLabel = BodyLabel(
            '请自行准备AI调用所需要的API_URL以及API_KEY', self)

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
        self.logdir = ""
        self.vmlinuxfile = ""
        self.symbolsdir = ""
        self.outputdir = ""

        # 设置状态提示
        self.stateTooltip = None
        self.bottomStateLayout = QHBoxLayout()

        # 选择按钮以及输入框部件
        self.logchooseButton = PushButton("选择")
        #self.fileLineEdit = LineEdit()
        self.vmlinuxchooseButton = PushButton("选择")
        self.outputdirchooseButton = PushButton("选择")
        
        # mod_path参数部件
        self.ModlineEdit = LineEdit()

        # 设置Button的点击事件
        self.logchooseButton.clicked.connect(self.logchooseButtonClicked)
        self.vmlinuxchooseButton.clicked.connect(self.vmlinuxchooseButtonClicked)
        self.outputdirchooseButton.clicked.connect(self.outputdirchooseButtonClicked)

        # 显示终端部件
        self.comboBox = ComboBox()
        
        # 平台选择部件
        # self.platformComboBox = EditableComboBox()

        # 入口脚本部件
        self.lineEdit = LineEdit()

        # API_URL以及API_KEY以及API_MODEL部件
        # 从当前目录下的config.yaml中读取ai.base_url以及ai.api_key以及ai.model
        config_path = os.path.join(CURRENT_PLUGIN_DIR, "stability-ai", "config.yaml")
        base_url = ""
        api_key = ""
        model = ""
        try:
            config = load_config(config_path)
            base_url = config.get('ai', {}).get('base_url', '')
            api_key = config.get('ai', {}).get('api_key', '')
            model = config.get('ai', {}).get('model', '')
        except Exception as e:
            logger.error(f"Failed to load config: {e}")

        self.APIURL_lineEdit = LineEdit()
        if base_url != "":
            self.APIURL_lineEdit.setText(base_url)
        else:
            self.APIURL_lineEdit.setPlaceholderText("请输入API_URL")
        self.APIKEY_lineEdit = LineEdit()
        if api_key != "":
            self.APIKEY_lineEdit.setText(api_key)
        else:
            self.APIKEY_lineEdit.setPlaceholderText("请输入API_KEY")
        self.APIMODEL_lineEdit = LineEdit()
        if model != "":
            self.APIMODEL_lineEdit.setText(model)
        else:
            self.APIMODEL_lineEdit.setPlaceholderText("请输入API_MODEL")

        # 设置部件的固定宽度
        self.logchooseButton.setFixedWidth(120)
        self.vmlinuxchooseButton.setFixedWidth(120)
        self.outputdirchooseButton.setFixedWidth(120)
        #self.fileLineEdit.setFixedWidth(320)

        self.lineEdit.setFixedWidth(320)
        self.APIURL_lineEdit.setFixedWidth(320)
        self.APIKEY_lineEdit.setFixedWidth(320)
        self.ModlineEdit.setFixedWidth(320)
        self.comboBox.setFixedWidth(120)
        self.comboBox.addItems(["始终显示", "始终隐藏"])
        # 设置comboBox的选择点击事件
        self.comboBox.currentIndexChanged.connect(self.comboBoxClicked)

        # self.platformComboBox.setPlaceholderText("选择平台")
        # TODO: 从配置文件中读取平台信息
        #items = ['blair', 'khaje', 'parrot', 'pitti']
        # self.platformComboBox.setFixedWidth(120)
        # 设置默认值
        # self.platformComboBox.setCurrentIndex(-1)
    
        #self.platformComboBox.addItems(items)
        # 设置platformComboBox的编辑事件
        #self.platformComboBox.currentTextChanged.connect(logger.info)
        #self.platformComboBox.currentIndexChanged.connect(self.platformComboBoxClicked)

        self.lineEdit.setPlaceholderText("请输入额外的解析参数")

        # 底部运行按钮以及提示
        self.hintIcon = IconWidget(InfoBarIcon.INFORMATION)
        self.hintLabel = BodyLabel("点击运行按钮开始解析")
        self.runButton = PrimaryPushButton(FluentIcon.PLAY_SOLID, "运行")
        self.bottomLayout = QHBoxLayout()

        # 设置底部工具栏布局
        self.hintIcon.setFixedSize(16, 16)
        self.bottomLayout.setSpacing(10)
        self.bottomLayout.setContentsMargins(24, 15, 24, 20)
        self.bottomLayout.addWidget(self.hintIcon, 0, Qt.AlignmentFlag.AlignLeft)
        self.bottomLayout.addWidget(self.hintLabel, 0, Qt.AlignmentFlag.AlignLeft)
        self.bottomLayout.addStretch(1)
        self.bottomLayout.addWidget(self.runButton, 0, Qt.AlignmentFlag.AlignRight)
        self.bottomLayout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        # 设置底部状态布局
        self.bottomStateLayout.setSpacing(10)
        self.bottomStateLayout.setContentsMargins(24, 15, 24, 20)
        self.bottomStateLayout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        self.bottomStateLayout.addStretch(1)


        self.ramdumpGroup = self.addGroup("{}/images/Rocket.svg".format(resource_path), "内核日志文件夹", "选择内核日志文件夹，最好是Linux ramdump parser解析出来的日志目录", self.logchooseButton)
        self.vmlinuxGroup = self.addGroup("{}/images/jsdesign.svg".format(resource_path), "vmlinux文件", "选择vmlinux文件路径", self.vmlinuxchooseButton)
        self.outputdirGroup = self.addGroup("{}/images/Joystick.svg".format(resource_path), "输出目录", "选择输出报告存放目录", self.outputdirchooseButton)
        self.addGroup("{}/images/Joystick.svg".format(resource_path), "模块路径", "请输入模块symbols路径", self.ModlineEdit)
        #self.addGroup("{}/images/Joystick.svg".format(resource_path), "Platform", "选择基线平台", self.platformComboBox)
        self.addGroup("{}/images/Joystick.svg".format(resource_path), "运行终端", "设置是否显示命令行终端", self.comboBox)
        self.addGroup("{}/images/Python.svg".format(resource_path), "额外参数", "请输入额外的解析参数", self.lineEdit)
        self.addGroup("{}/images/Python.svg".format(resource_path), "API URL", "请输入API_URL", self.APIURL_lineEdit)
        self.addGroup("{}/images/Python.svg".format(resource_path), "API KEY", "请输入API_KEY", self.APIKEY_lineEdit)
        self.addGroup("{}/images/Python.svg".format(resource_path), "API MODEL", "请输入API_MODEL", self.APIMODEL_lineEdit)
        self.vBoxLayout.addLayout(self.bottomLayout)

        # 设置运行按钮的点击事件
        self.runButton.clicked.connect(self.runButtonClicked)

    def logchooseButtonClicked(self):
        logger.info("Choose Button Clicked")
        # 弹出windows文件选择框
        self.logdir = QFileDialog.getExistingDirectory(self, "选择文件夹")
        # 转成windows路径
        self.logdir = linuxPath2winPath(self.logdir)
        # 打印选择的文件路径
        logger.info("Choose log Directory: {}".format(self.logdir))
        
        if self.logdir == "":
            self.logchooseButton.setText("选择")
            self.ramdumpGroup.setContent("请选择内核日志目录")
        else:
            # 设置chooseButton的文字显示已选择
            self.logchooseButton.setText("已选择")
            logger.info("path length: {}".format(len(self.logdir)))
            # 判断self.logdir的长度是否大于120
            if len(self.logdir) > 120:
                # 截取前50个字符和后70个字符
                self.ramdumpGroup.setContent("{}.........{}".format(self.logdir[0:50], self.logdir[-70:]))
            else:
                self.ramdumpGroup.setContent(self.logdir)


    def vmlinuxchooseButtonClicked(self):
        logger.info("vmlinux Button Clicked")
        # 弹出windows文件选择框
        self.vmlinuxfile, _ = QFileDialog.getOpenFileName(self, "选择文件", "C:/", "All Files (*);;Text Files (*.txt)")
        # 转成windows路径
        self.vmlinuxfile = linuxPath2winPath(self.vmlinuxfile)
        # 打印选择的文件路径
        logger.info("Choose Vmlinux File: {}".format(self.vmlinuxfile))

        if self.vmlinuxfile == "":
            # 设置vmlinuxButton的文字显示已选择
            self.vmlinuxchooseButton.setText("选择")
            self.vmlinuxGroup.setContent("请选择vmlinux文件")
        else:
            self.vmlinuxchooseButton.setText("已选择")
            # 判断self.vmlinuxfile的长度是否大于150
            logger.info("path length: {}".format(len(self.vmlinuxfile)))
            if len(self.vmlinuxfile) > 120:
                # 截取前50个字符和后70个字符
                self.vmlinuxGroup.setContent("{}.........{}".format(self.vmlinuxfile[0:50], self.vmlinuxfile[-70:]))
            else:
                self.vmlinuxGroup.setContent(self.vmlinuxfile)


    def outputdirchooseButtonClicked(self):
        logger.info("Choose Button Clicked")
        # 弹出windows文件选择框
        self.outputdir = QFileDialog.getExistingDirectory(self, "选择文件夹")
        # 转成windows路径
        self.outputdir = linuxPath2winPath(self.outputdir)
        # 打印选择的文件路径
        logger.info("Choose Dump Directory: {}".format(self.outputdir))
        
        if self.outputdir == "":
            self.outputdirchooseButton.setText("选择")
            self.outputdirGroup.setContent("请选择output的存放目录")
        else:
            # 设置chooseButton的文字显示已选择
            self.outputdirchooseButton.setText("已选择")
            logger.info("path length: {}".format(len(self.outputdir)))
            # 判断self.outputdir的长度是否大于120
            if len(self.outputdir) > 120:
                # 截取前50个字符和后70个字符
                self.outputdirGroup.setContent("{}.........{}".format(self.outputdir[0:50], self.outputdir[-70:]))
            else:
                self.outputdirGroup.setContent(self.outputdir)

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
            title='log file is not selected',
            content="请先选择日志文件",
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
            self.stateTooltip.show()

        elif value == "ERROR":
            self.stateTooltip.setContent('解析失败')
            self.stateTooltip.setState(False)
            self.runButton.setEnabled(True)
            self.stateTooltip.show()
        else:
            logger.info(value)

        # 打开输出目录
        os.system("start {}".format(self.outputdir))

    def start_task(self, command, shell):
        logger.info("Start task")
        self.worker = Worker(command, shell=shell)
        self.worker.signal.connect(self.customSignalHandler)
        self.worker.start()

    def runButtonClicked(self):
        logger.info("Run Button Clicked")
        # 获取chooseButton/ vmlinuxButton/ comboBox/ platformComboBox/ lineEdit的值
        logger.info("log dir: {}".format(self.logdir))
        logger.info("Vmlinux file: {}".format(self.vmlinuxfile))
        logger.info("Mod path: {}".format(self.ModlineEdit.text()))
        #logger.info("platform: {}".format(self.platformComboBox.currentText()))
        logger.info("extend parameters: {}".format(self.lineEdit.text()))

        if self.comboBox.currentText() == "始终显示":
            shell = True
        else:
            shell = False

        logger.info("Display terminal: {}".format(shell))

        if self.logdir == "":
            self.showNoSelectFileFlyout()
            # 如果没有选择logfile, 提示错误
            return

        if self.outputdir == "":
            # 设置outputdir为self.logdir的同级目录下的output_stabilityai_时间戳
            import time
            timestamp = time.strftime("%Y%m%d_%H%M%S", time.localtime())
            self.outputdir = os.path.join(os.path.dirname(self.logdir), "output_stabilityai_{}".format(timestamp))
            os.makedirs(self.outputdir, exist_ok=True)
            logger.info("Output directory not selected, set to: {}".format(self.outputdir))
        
        # elif self.dumpfile.endswith('.zip') == True or self.dumpfile.endswith('.rar') == True:
        #     self.showZipFileTypeErrorFlyout()
        # 如果vmlinuxfile的文件名不为vmlinux
        #elif "vmlinux" not in self.vmlinuxfile:
            # 提示vmlinux文件名不为vmlinux
        #    self.showFileStyleErrorFlyout()
        else:
            self.stateTooltip = StateToolTip('正在解析', '客官请耐心等待哦~~', self)
            # 状态提示放到中心位置
            self.bottomStateLayout.addWidget(self.stateTooltip, 0, Qt.AlignmentFlag.AlignRight)
            self.vBoxLayout.addLayout(self.bottomStateLayout)
            # 显示状态提示
            self.stateTooltip.show()

            # runbuton按钮设置为不可点击
            self.runButton.setDisabled(True)

            # 构造命令行
            logger.info(self.APIURL_lineEdit.text())
            logger.info(self.APIMODEL_lineEdit.text())
            logger.info(self.APIKEY_lineEdit.text())

            command = "{}/stability-ai/stability-ai.exe --config {} --enable-ai -i {} ".format(CURRENT_PLUGIN_DIR, os.path.join(CURRENT_PLUGIN_DIR, "stability-ai", "config.yaml"), self.logdir)

            if self.vmlinuxfile != "":
                command += "--vmlinux {} ".format(self.vmlinuxfile)
            
            if self.symbolsdir != "":
                command += "--symbols {} ".format(self.symbolsdir)

            if self.vmlinuxfile != "":
                command += "--nm {} ".format(os.path.join(GNU_TOOLS_PATH, "bin", "llvm-nm.exe"))
                command += "--addr2line {} ".format(os.path.join(GNU_TOOLS_PATH, "bin", "llvm-addr2line.exe"))

            command += "--yaml {}/output_report.yaml --md {}/output_report.md --html {}/output_report.html".format(self.outputdir, self.outputdir, self.outputdir)


            if self.lineEdit.text() != "":
                command += " {}".format(self.lineEdit.text())

            logger.info("Run command: {}".format(command))

            self.start_task(command, shell)

            #self.start_task(command, shell)

            # 将api_url以及api_key以及model写入config.yaml文件, 保持其他配置不变
            config_path = os.path.join(CURRENT_PLUGIN_DIR, "stability-ai", "config.yaml")
            try:
                # 先读取现有配置
                config = load_config(config_path)
            except Exception as e:
                logger.warning(f"Failed to load existing config, creating new one: {e}")
                config = {}
            
            # 更新ai配置项
            if 'ai' not in config:
                config['ai'] = {}
            config['ai']['base_url'] = self.APIURL_lineEdit.text()
            config['ai']['api_key'] = self.APIKEY_lineEdit.text()
            config['ai']['model'] = self.APIMODEL_lineEdit.text()
            
            # 写回文件
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, allow_unicode=True)

    

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

class StabilityAIParserCardsInfo(ScrollArea):
    """ Stability AI Parser Subinterface """

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


class StabilityAIParserInterface:
    def __init__(self, parent=None, mainWindow=None):
        self.parent = parent
        self.mainWindow = mainWindow
        
        #self.mainWindow.tabBar.currentChanged.connect(self.onTabChanged)
        #self.mainWindow.stackedWidget.setCurrentWidget(self.mainWindow.showInterface)

    def addTab(self, routeKey, text, icon):
        logger.info('[TAB ADD] {}'.format(routeKey))
        self.mainWindow.tabBar.addTab(routeKey, text, icon)

        # tab左对齐
        self.mainWindow.showInterface.addWidget(StabilityAIParserCardsInfo(routeKey=routeKey))
        self.mainWindow.showInterface.setCurrentWidget(self.mainWindow.showInterface.findChild(StabilityAIParserCardsInfo, routeKey))
        self.mainWindow.stackedWidget.setCurrentWidget(self.mainWindow.showInterface)
        self.mainWindow.tabBar.setCurrentIndex(self.mainWindow.tabBar.count() - 1)

        #logger.info("[LIUQI] CurrentWidget: ".format(self.mainWindow.showInterface.currentWidget()))
        #logger.info("[LIUQI] CurrentWidgetRoutekey: ".format(self.mainWindow.showInterface.currentWidget().objectName()))

    # def onTabChanged(self, index):
    #     objectName = self.mainWindow.tabBar.currentTab().routeKey()
    #     logger.info("[LIUQI1] ObjectName: ", objectName)
    #     logger.info("[LIUQI1] index: ", index)
    #     logger.info("[LIUQI1] CurrentWidget: ", self.mainWindow.showInterface.findChild(StabilityAIParserCardsInfo, objectName))
    #     self.mainWindow.showInterface.setCurrentWidget(self.mainWindow.showInterface.findChild(StabilityAIParserCardsInfo, objectName))
    #     self.mainWindow.stackedWidget.setCurrentWidget(self.mainWindow.showInterface)
    #     self.mainWindow.tabBar.setCurrentIndex(index)
    #     logger.info("[LIUQI1] CurrentWidgetRoutekey: ", self.mainWindow.showInterface.currentWidget().objectName())
