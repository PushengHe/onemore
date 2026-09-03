from loguru import logger
from app.common.utils import generate_uuid
from plugins.NOC_Debug.NocDecodeinterface import NocDecodeInterface as NOC, CURRENT_PLUGIN_DIR
from plugins.NOC_Debug.NocDecodeinterface import NocDecodeCardsInfo
from pathlib import Path
import os

UNIQUE_NAME = "NOC Decode Tool"
CURRENT_PLUGIN_DIR = Path(__file__).parent

def get_route_key():
    """
    Generate a unique route key for the plugin.
    """
    return f"{UNIQUE_NAME} {generate_uuid()}"


def register(main_window):
    plugin_state = {}

    def on_open():

        routekey = get_route_key()
        interface = NOC(mainWindow=main_window)
        interface.addTab(routeKey=routekey, text=routekey, icon=os.path.join(CURRENT_PLUGIN_DIR, 'logo.png'))

        # 将插件的路由键添加到 main_window 的 TabRouteKeys 中, 以便於处理 Tab 切换
        main_window.TabRouteKeys.append(routekey)

    def on_tab_changed(route_key: str):
        state = -1
        for TabRouteKey in main_window.TabRouteKeys:
            if TabRouteKey == route_key:
                logger.info("[TAB CHANGED] Tab change to {}".format(TabRouteKey))
                widget = main_window.showInterface.findChild(NocDecodeCardsInfo, TabRouteKey)
                main_window.showInterface.setCurrentWidget(widget)
                state = 1
                break

        if state != 1:
                logger.warning(f"can not handle Tab change，can not find route_key={route_key}")

    appcard = main_window.qcomInterface.addCard(os.path.join(CURRENT_PLUGIN_DIR, "logo.png"), "NOC Decode Tool", '@designed by iliuqi.', "NOC Decode Tool")

    main_window.registerPluginOpener(UNIQUE_NAME, on_open)
    main_window.registerTabChangedHandler(UNIQUE_NAME, on_tab_changed)
