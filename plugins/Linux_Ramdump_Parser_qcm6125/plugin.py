from loguru import logger
from app.common.utils import generate_uuid
from plugins.Linux_Ramdump_Parser_qcm6125.LinuxRamdumpParserinterface import LinuxRamdumpParserInterface as LRDP
from plugins.Linux_Ramdump_Parser_qcm6125.LinuxRamdumpParserinterface import LinuxRamdumpParserCardsInfo
import os

UNIQUE_NAME = "Linux Ramdump Parser qcm6125"
CURRENT_PLUGIN_DIR = os.path.dirname(__file__)

def get_route_key():
    """
    Generate a unique route key for the plugin.
    """
    return f"{UNIQUE_NAME} {generate_uuid()}"


def register(main_window):

    def on_open():

        routekey = get_route_key()
        interface = LRDP(mainWindow=main_window)
        interface.addTab(routeKey=routekey, text=routekey, icon='logo.png')

        # 将插件的路由键添加到 main_window 的 TabRouteKeys 中, 以便於处理 Tab 切换
        main_window.TabRouteKeys.append(routekey)

    def on_tab_changed(route_key: str):
        state = -1
        for TabRouteKey in main_window.TabRouteKeys:
            if TabRouteKey == route_key:
                logger.info("[TAB CHANGED] Tab change to {}".format(TabRouteKey))
                widget = main_window.showInterface.findChild(LinuxRamdumpParserCardsInfo, TabRouteKey)
                main_window.showInterface.setCurrentWidget(widget)
                state = 1
                break

        if state != 1:
                logger.warning(f"[TAB WARNING] can not handle Tab change，can not find route_key={route_key}")

    main_window.qcomInterface.addCard(
        os.path.join(CURRENT_PLUGIN_DIR, "logo.png"),
        "Linux Ramdump Parser qcm6125",
        '@designed by heps.',
        UNIQUE_NAME,
    )

    main_window.registerPluginOpener(UNIQUE_NAME, on_open)
    main_window.registerTabChangedHandler(UNIQUE_NAME, on_tab_changed)
