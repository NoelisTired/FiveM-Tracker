from lib.hook import FiveM
from lib.ocr import ScreenTextDetector
from lib.process import Data
import time
import os
import signal
import keyboard, threading, ctypes


class Main:
    def __init__(self):
        self.__author = "NoelP"
        self.__version = "2.0.0"
        self.fivem = FiveM()
        keyboard.add_hotkey("ctrl+shift+q", self.kill)

    """
        This function is responsible for killing the process. 
        It is called when the user presses "ctrl+shift+q" on the keyboard, pressing the X sometimes doesn't terminate the OCR thread
    """
    def kill(self):
        print("Bye.")
        os.kill(os.getpid(), signal.SIGTERM)

    """
        This function is responsible for checking for updates, it is not working as of now.
    """
    def check_for_updates(self):
        try:
            if "1.0.0" != self.__version:
                return True
            else:
                return False
        except:
            return False

    def start(self):
        time.sleep(1)
        print("Checking for updates...")
        time.sleep(1)
        if self.check_for_updates():
            print("Update Required..")
            os.system('start https://google.com/')
            time.sleep(3)
            self.kill()
        return self.fivem.receive()


if __name__ == "__main__":
    ctypes.windll.kernel32.SetConsoleTitleW("灰分 | Ash - FiveM Tools")
    main = Main()
    credentials = main.start()
    if type(credentials) == tuple:
        dataobj = Data(credentials[0], credentials[1])
        dataobj.menu()
