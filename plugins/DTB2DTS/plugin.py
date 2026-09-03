from loguru import logger
import os
import subprocess
UNIQUE_NAME = "DTB2DTS"

CURRENT_PLUGIN_DIR = os.path.dirname(os.path.abspath(__file__))

def register(main_window):

    def on_open():
        command = os.path.join(CURRENT_PLUGIN_DIR, 'dtb2dts.exe')
        logger.info("Executed command : {}".format(command))
        try:
            subprocess.Popen(command, shell=False, creationflags=subprocess.CREATE_NO_WINDOW)
        except Exception as e:
            logger.error(f"Failed to run Hansei GUI: {e}")
            raise e


    main_window.generalInterface.addCard(os.path.join(CURRENT_PLUGIN_DIR, "logo.png"), "DTB2DTS", '@designed by iliuqi.', "DTB2DTS")
    main_window.registerPluginOpener(UNIQUE_NAME, on_open)

