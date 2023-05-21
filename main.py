from utils.bot_state import switch_state_hotkey_handler
from config import init_config
# This is required due to config used in imported modules
init_config()

import sys
import tkinter as tk
import threading

from gui.log_window import LogWindow, CustomOutput, gpt3_cmd_handler
from utils.chat import parse_tf2_console_logs
from utils.tf2_context import StatsData


def wrapper():
    from services.source_game import get_status
    import time
    while True:
        get_status()
        time.sleep(20)


def get_my_data():
    import keyboard
    while True:
        keyboard.wait("F10")
        print(StatsData.get_data())


def run_threads():
    root = tk.Tk()
    log_window = LogWindow(root)
    sys.stdout = CustomOutput(log_window)

    threading.Thread(target=parse_tf2_console_logs, daemon=True).start()
    threading.Thread(target=gpt3_cmd_handler, daemon=True).start()
    threading.Thread(target=switch_state_hotkey_handler, daemon=True).start()
    threading.Thread(target=wrapper, daemon=True).start()
    threading.Thread(target=get_my_data, daemon=True).start()

    log_window.pack()
    root.mainloop()


if __name__ == '__main__':
    run_threads()
