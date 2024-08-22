import os
import win32api
import win32gui
import win32process
import wmi
from typing import Optional
import logging

logging.basicConfig(filename='windows.log', level=logging.ERROR,
                    format='%(asctime)s %(levelname)s:%(message)s')

def get_app_path(hwnd) -> Optional[str]:
    path = None
    _, pid = win32process.GetWindowThreadProcessId(hwnd)
    process = win32api.OpenProcess(0x0400, False, pid)
    try:
        path = win32process.GetModuleFileNameEx(process, 0)
    finally:
        win32api.CloseHandle(process)
    return path

def get_app_name(hwnd) -> Optional[str]:
    path = get_app_path(hwnd)
    if path is None:
        return None
    return os.path.basename(path)

def get_window_title(hwnd):
    return win32gui.GetWindowText(hwnd)

def get_active_window_handle():
    hwnd = win32gui.GetForegroundWindow()
    return hwnd

c = wmi.WMI()

def get_app_name_wmi(hwnd) -> Optional[str]:
    name = None
    _, pid = win32process.GetWindowThreadProcessId(hwnd)
    try:
        for p in c.query("SELECT Name FROM Win32_Process WHERE ProcessId = %s" % str(pid)):
            name = p.Name
            break
        return name
    except Exception as e:
        print(f'error at Moniyoting/Windos.py/get_app_name_wmi: {e.__cause__}, {e.__context__}, {e}')



def get_app_path_wmi(hwnd) -> Optional[str]:
    path = None
    try:
        _, pid = win32process.GetWindowThreadProcessId(hwnd)

        for p in c.query("SELECT ExecutablePath FROM Win32_Process WHERE ProcessId = %s" % str(pid)):
            path = p.ExecutablePath
            break
    except Exception as e:
        print(f'error at Moniyoting/Windos.py/get_app_PATH_wmi: {e.__cause__}, {e.__context__}, {e}')
    return path
