import time
import win32gui
import win32con
import pyautogui

CS2_WINDOW_TITLE = "Counter-Strike 2"
CONSOLE_KEY = "`"


def find_cs2_window() -> int | None:
    hwnd = win32gui.FindWindow(None, CS2_WINDOW_TITLE)
    return hwnd if hwnd else None


def focus_cs2() -> bool:
    hwnd = find_cs2_window()
    if not hwnd:
        return False
    if win32gui.IsIconic(hwnd):
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    try:
        win32gui.SetForegroundWindow(hwnd)
    except Exception:
        pyautogui.press("alt")
        win32gui.SetForegroundWindow(hwnd)
    time.sleep(0.12)
    return True


def send_console_command(cmd: str) -> bool:
    if not focus_cs2():
        return False
    pyautogui.press(CONSOLE_KEY)
    time.sleep(0.10)
    pyautogui.typewrite(cmd, interval=0.005)
    pyautogui.press("enter")
    time.sleep(0.05)
    pyautogui.press(CONSOLE_KEY)
    return True
