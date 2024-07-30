import sys
from typing import Optional
from monitoring.exceptions import FatalError

def get_current_window_linux() -> Optional[dict]:
    from monitoring import xlib
    window = xlib.get_current_window()
    if window is None:
        cls = "unknown"
        name = "unknown"
    else:
        cls = xlib.get_window_class(window)
        name = xlib.get_window_name(window)
    return {"app": cls, "title": name}

def get_current_window_macos(strategy: str) -> Optional[dict]:
    if strategy == "jxa":
        from monitoring import macos_jxa
        return macos_jxa.getInfo()
    elif strategy == "applescript":
        from monitoring import macos_applescript
        return macos_applescript.getInfo()
    else:
        raise FatalError(f"invalid strategy '{strategy}'")

def get_current_window_windows() -> Optional[dict]:
    from monitoring import windows
    window_handle = windows.get_active_window_handle()
    try:
        app = windows.get_app_name(window_handle)
    except Exception:
        app = windows.get_app_name_wmi(window_handle)
    title = windows.get_window_title(window_handle)
    if app is None:
        app = "unknown"
    if title is None:
        title = "unknown"
    return {"app": app, "title": title}

def get_current_window(strategy: Optional[str] = None) -> Optional[dict]:
    if sys.platform.startswith("linux"):
        return get_current_window_linux()
    elif sys.platform == "darwin":
        if strategy is None:
            raise FatalError("macOS strategy not specified")
        return get_current_window_macos(strategy)
    elif sys.platform in ["win32", "cygwin"]:
        return get_current_window_windows()
    else:
        raise FatalError(f"Unknown platform: {sys.platform}")
