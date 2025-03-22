import sys
import threading
import os
import shutil
import subprocess
import zipfile
import tempfile
import keyboard
import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from veyon import *

root = None
status_var = None
status_label = None 

def set_globals(main_root, main_status_var, main_status_label=None):
    global root, status_var, status_label
    root = main_root
    status_var = main_status_var
    status_label = main_status_label

# ---------------------- Functions ----------------------
def resource_path(relative_path):
    """Für das Handling von Ressourcen innerhalb der EXE"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.abspath(relative_path)

# Icon Fix
try:
    icon_path = resource_path("icon.ico")
except Exception as e:
    print(f"⚠️ Icon konnte nicht gesetzt werden: {e}")

def start_protonvpn_portable():
    try:
        zip_path = resource_path("ProtonVPN.zip")
        temp_dir = os.path.join(tempfile.gettempdir(), "eait_protonvpn")
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        os.makedirs(temp_dir, exist_ok=True)

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        vpn_exe_path = os.path.join(temp_dir, "ProtonVPN.exe")
        subprocess.Popen(vpn_exe_path).wait()
        shutil.rmtree(temp_dir)
        status_var.set("ProtonVPN beendet & bereinigt.")
    except Exception as e:
        status_var.set(f"Fehler bei ProtonVPN: {e}")

def install_adblock():
    try:
        ublock_url = "https://addons.mozilla.org/firefox/downloads/latest/ublock-origin/latest.xpi"
        subprocess.Popen(["start", "", ublock_url], shell=True)
        status_var.set("uBlock Origin Add-on wurde geöffnet. Bitte im Firefox bestätigen.")
    except Exception as e:
        status_var.set(f"Fehler bei Adblock Setup: {e}")

def start_toolbox_portable():
    try:
        zip_path = resource_path("jetbrains_toolbox.zip")
        temp_dir = os.path.join(tempfile.gettempdir(), "eait_toolbox")
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        os.makedirs(temp_dir, exist_ok=True)
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        toolbox_exe = os.path.join(temp_dir, "jetbrains_toolbox.exe")
        env = os.environ.copy()
        env["JETBRAINS_TOOLBOX_HOME"] = os.path.join(temp_dir, "data")
        subprocess.Popen(toolbox_exe, env=env).wait()
        shutil.rmtree(temp_dir)
        status_var.set("JetBrains ToolBox beendet & bereinigt.")
    except Exception as e:
        status_var.set(f"Fehler bei Jetbrains ToolBox: {e}")

def start_brave_and_cleanup():
    try:
        zip_path = resource_path("brave.zip")
        temp_dir = os.path.join(tempfile.gettempdir(), "eait_brave")
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        os.makedirs(temp_dir, exist_ok=True)
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        brave_path = os.path.join(temp_dir, "brave", "brave-portable.exe")
        ublock_path = os.path.join(temp_dir, "brave", "ublock")
        if not os.path.exists(brave_path):
            status_var.set("❌ Brave fehlt")
            return
        profile_dir = os.path.join(temp_dir, "user_data", "Default")
        os.makedirs(profile_dir, exist_ok=True)
        proc = subprocess.Popen([
            brave_path,
            f"--load-extension={ublock_path}",
            f"--user-data-dir={os.path.join(temp_dir, 'user_data')}",
            "--no-first-run",
            "--disable-first-run-ui"
        ])
        proc.wait()
        shutil.rmtree(temp_dir)
        status_var.set("Brave wurde beendet und temporär gelöscht.")
    except Exception as e:
        status_var.set(f"Fehler bei Brave: {e}")
    
def start_brave_and_cleanup_threaded():
    threading.Thread(target=start_brave_and_cleanup, daemon=True).start()

def restart_as_admin():
    try:
        script = sys.executable
        args = " ".join([f'"{arg}"' for arg in sys.argv])
        remove_tray_icon()  
        subprocess.Popen(f'"{script}" {args}', shell=True)
        root.quit()
        sys.exit(0) 
    except Exception as e:
        messagebox.showerror("Fehler beim Neustart", str(e))

def start_stop_hotkeys():
    try:
        keyboard.unhook_all() 
    except AttributeError:
        print("⚠️ Keine aktiven Hotkeys zum Entfernen gefunden.")

    def safe_suspend():
        try:
            toggle_process_state(True)
        except Exception as e:
            print(f"Hotkey Suspend Fehler: {e}")

    def safe_start():
        try:
            clear_and_restart_veyon()
            create_tray_icon("active")
            show_start_popup()  # ✅ Popup anzeigen
        except Exception as e:
            print(f"Hotkey Start Fehler: {e}")

    keyboard.add_hotkey('ctrl+f9', lambda: threading.Thread(target=safe_suspend, daemon=True).start(), suppress=True)
    keyboard.add_hotkey('ctrl+f12', lambda: threading.Thread(target=safe_start, daemon=True).start(), suppress=True)

    print("✅ Hotkeys wurden erfolgreich registriert.")

# -------------------------- Darkmode & Lightmode --------------------------
THEME = {"mode": "dark"}
COLORS = {
    "dark": {
        "BG": "#1e1e1e",
        "TEXT": "#f5f5f5",
        "ACCENT": "#4a90e2",
        "WARNING": "#e74c3c",
        "BTN_BG": "#2c2c2c",
    },
    "light": {
        "BG": "#f8f9fa",
        "TEXT": "#222",
        "ACCENT": "#4a90e2",
        "WARNING": "#e74c3c",
        "BTN_BG": "#ffffff",
    }
}

FONT_FAMILY = "Arial"
def apply_theme():
    theme = COLORS[THEME["mode"]]
    root.configure(bg=theme["BG"])

    style = ttk.Style()
    style.theme_use('clam')

    style.configure('TFrame', background=theme["BG"])
    style.configure('TLabel', background=theme["BG"], foreground=theme["TEXT"], font=(FONT_FAMILY, 9))
    style.configure('TButton', background=theme["BTN_BG"], foreground=theme["TEXT"], font=(FONT_FAMILY, 10))
    style.map('TButton',
              background=[('active', theme["BTN_BG"]), ('!disabled', theme["BTN_BG"])],
              foreground=[('!disabled', theme["TEXT"])],
              bordercolor=[('active', theme["ACCENT"])])

    if status_label:
        status_label.config(bg=theme["BG"], fg=theme["WARNING"])

def toggle_theme(theme_btn_text=None):
    THEME["mode"] = "light" if THEME["mode"] == "dark" else "dark"
    apply_theme()
    if theme_btn_text:
        theme_btn_text.set("🌙" if THEME["mode"] == "light" else "     ☀️")

def set_custom_cursors(widget, normal_cursor_path="adobe_normal.cur", click_cursor_path="adobe_click.cur"):
    normal_path = resource_path(normal_cursor_path).replace("\\", "/")
    click_path = resource_path(click_cursor_path).replace("\\", "/")
    normal_cursor = f"@{normal_path}"
    click_cursor = f"@{click_path}"

    print(f"✅ Normal Cursor: {normal_cursor}")
    print(f"✅ Click Cursor: {click_cursor}")

    # Root-Fenster auf Normal setzen
    try:
        widget.config(cursor=normal_cursor)
    except Exception as e:
        print(f"⚠️ Root-Cursor-Setzen fehlgeschlagen: {e}")
        widget.config(cursor="arrow")

    def apply_cursor_recursive(w):
        try:
            # BUTTONS bekommen hover = adobe_click
            if isinstance(w, (tk.Button, ttk.Button)):
                w.config(cursor=normal_cursor)  # default ist normal
                w.bind("<Enter>", lambda e: e.widget.configure(cursor=click_cursor))
                w.bind("<Leave>", lambda e: e.widget.configure(cursor=normal_cursor))

            # Alles andere bleibt einfach mit normal_cursor (auch bei Hover)
            elif isinstance(w, (tk.Entry, tk.Text, tk.Spinbox, tk.Listbox, ttk.Combobox,
                                ttk.Entry, ttk.Spinbox, ttk.Label, tk.Label, ttk.Scrollbar, tk.Scrollbar)):
                w.config(cursor=normal_cursor)

            # Fallback für Rest
            else:
                w.config(cursor=normal_cursor)

        except Exception as err:
            print(f"⚠️ Cursor-Zuweisung Fehler bei {w}: {err}")

        # Rekursiv auf Kinder anwenden
        for child in w.winfo_children():
            apply_cursor_recursive(child)

    apply_cursor_recursive(widget)
    print("✅ Adobe Cursor Style aktiv: Normal überall, Click nur bei Buttons")
