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
import random
from PIL import Image, ImageTk, ImageSequence

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
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.abspath(relative_path)

# Icon Fix
try:
    icon_path = resource_path(os.path.join("data", "icon.ico"))
except Exception as e:
    print(f"⚠️ Icon konnte nicht gesetzt werden: {e}")

def start_protonvpn_portable():
    try:
        zip_path = resource_path(os.path.join("data", "ProtonVPN.zip"))
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
        zip_path = resource_path(os.path.join("data", "jetbrains_toolbox.zip"))
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
        zip_path = resource_path(os.path.join("data", "brave.zip"))
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
    style.configure('TButton', background=theme["BTN_BG"], foreground=theme["TEXT"], font=(FONT_FAMILY, 10), cursor="arrow")
    style.map('TButton',
              background=[('active', theme["BTN_BG"]), ('!disabled', theme["BTN_BG"])],
              foreground=[('!disabled', theme["TEXT"])],
              bordercolor=[('active', theme["ACCENT"])])

    if status_label:
        status_label.config(bg=theme["BG"], fg=theme["WARNING"])

    set_custom_cursors(root)

def toggle_theme(theme_btn_text=None):
    THEME["mode"] = "light" if THEME["mode"] == "dark" else "dark"
    apply_theme()
    if theme_btn_text:
        theme_btn_text.set("🌙" if THEME["mode"] == "light" else "     ☀️")

def set_custom_cursors(widget, normal_cursor_path="data/adobe_normal.cur", click_cursor_path="data/adobe_click.cur"):
    # Fix: keine temp-Verzeichnisse mehr → direkt original Datei verwenden
    normal_abs = resource_path(normal_cursor_path).replace("\\", "/")
    click_abs = resource_path(click_cursor_path).replace("\\", "/")

    normal_cursor = f"@{normal_abs}" if os.path.exists(normal_abs) else "arrow"
    click_cursor = f"@{click_abs}" if os.path.exists(click_abs) else "hand2"

    print(f"✅ Normal Cursor: {normal_cursor}")
    print(f"✅ Click Cursor: {click_cursor}")

    def apply_recursive(w):
        try:
            w.config(cursor=normal_cursor)
        except Exception as e:
            print(f"⚠️ Cursor set fail: {e}")
        for child in w.winfo_children():
            try:
                child.config(cursor=normal_cursor)
            except:
                pass
            if isinstance(child, (tk.Button, ttk.Button)):
                # Button Hover-Events
                def on_enter(e, c=click_cursor):
                    try:
                        e.widget.config(cursor=c)
                    except: pass
                def on_leave(e, c=normal_cursor):
                    try:
                        e.widget.config(cursor=c)
                    except: pass
                child.bind("<Enter>", on_enter)
                child.bind("<Leave>", on_leave)
            apply_recursive(child)

    apply_recursive(widget)

    # Auch global für Styles
    try:
        style = ttk.Style()
        style.configure("TButton", cursor=normal_cursor)
    except:
        pass

import os
import tkinter as tk
from tkinter import Label, Button, Toplevel
from PIL import Image, ImageTk, ImageSequence
import random

FONT_FAMILY = "Segoe UI"

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.abspath(relative_path)

def build_slots_ui(window):
    FONT_FAMILY = "Segoe UI"
    symbols = ["🍒", "🍋", "🍊", "🍇", "💎", "7️⃣", "🎰"]
    symbol_values = {"🍒": 1, "🍋": 2, "🍊": 3, "🍇": 5, "💎": 10, "7️⃣": 15, "🎰": 25}
    credits = {"value": 20}

    OFFSET_Y = 60

    bg_image_path = resource_path("data/casino_background.png")
    try:
        bg_image = Image.open(bg_image_path).resize((500, 400), Image.LANCZOS)
        bg_photo = ImageTk.PhotoImage(bg_image)
    except Exception as e:
        print(f"⚠️ Hintergrund konnte nicht geladen werden: {e}")
        return

    canvas = tk.Canvas(window, width=500, height=400, highlightthickness=0, bd=0)
    canvas.pack(fill="both", expand=True)
    canvas.create_image(0, 0, image=bg_photo, anchor="nw")
    canvas.bg_photo = bg_photo

    # 🎰 Logo GIF
    try:
        logo_path = resource_path("data/casino_logo.gif")
        logo_gif = Image.open(logo_path)
        frames = [ImageTk.PhotoImage(frame.copy().resize((180, 50), Image.LANCZOS)) for frame in ImageSequence.Iterator(logo_gif)]
        logo_label = Label(canvas, bg="black")
        canvas.create_window(250, 10, window=logo_label, anchor="n")

        def animate_logo(idx=0):
            logo_label.config(image=frames[idx])
            logo_label.image = frames[idx]
            logo_label.after(100, lambda: animate_logo((idx + 1) % len(frames)))

        logo_label.frames = frames
        animate_logo()
    except Exception as e:
        print(f"⚠️ Fehler beim Laden des Casino-Logos: {e}")

    # UI Elemente
    credits_label = Label(canvas, text=f"Credits: {credits['value']}", font=(FONT_FAMILY, 16, "bold"), bg="black", fg="white")
    canvas.create_window(250, 30 + OFFSET_Y, window=credits_label)

    message_label = Label(canvas, text="Good luck!", font=(FONT_FAMILY, 12), bg="black", fg="yellow")
    canvas.create_window(250, 60 + OFFSET_Y, window=message_label)

    slot_labels = []
    for i in range(3):
        slot = Label(canvas, text="🎰", font=(FONT_FAMILY, 40), bg='black', fg="white", width=2)
        canvas.create_window(150 + i * 100, 140 + OFFSET_Y, window=slot)
        slot_labels.append(slot)

    def check_win(result):
        if result[0] == result[1] == result[2]:
            return symbol_values.get(result[0], 1) * 10
        elif result[0] == result[1] or result[1] == result[2] or result[0] == result[2]:
            match = result[1] if result[1] == result[2] else result[0]
            return symbol_values.get(match, 1) * 2
        return 0

    def spin():
        if credits["value"] < 5:
            message_label.config(text="Not enough credits!", fg="red")
            return
        credits["value"] -= 5
        credits_label.config(text=f"Credits: {credits['value']}")
        message_label.config(text="Spinning...", fg="yellow")
        spin_button.config(state="disabled")

        def animate_spin(count=0):
            if count < 10:
                for slot in slot_labels:
                    slot.config(text=random.choice(symbols))
                window.after(100, lambda: animate_spin(count + 1))
            else:
                result = [random.choice(symbols) for _ in range(3)]
                for i, symbol in enumerate(result):
                    slot_labels[i].config(text=symbol)
                win = check_win(result)
                if win:
                    credits["value"] += win
                    message_label.config(text=f"You won {win} credits!", fg="yellow")
                else:
                    message_label.config(text="Try again!", fg="white")
                credits_label.config(text=f"Credits: {credits['value']}")
                spin_button.config(state="normal")

        animate_spin()

    def reset_game():
        credits["value"] = 20
        credits_label.config(text=f"Credits: {credits['value']}")
        message_label.config(text="Game reset! Good luck!", fg="yellow")
        for slot in slot_labels:
            slot.config(text="🎰")

    spin_button = Button(canvas, text="SPIN (5 credits)", font=(FONT_FAMILY, 12, "bold"),
                         command=spin, bg="#8B0000", fg="white", relief="raised")
    canvas.create_window(150, 280 + OFFSET_Y, window=spin_button)

    reset_button = Button(canvas, text="Reset Game", font=(FONT_FAMILY, 12),
                          command=reset_game, bg="#4B0082", fg="white", relief="raised")
    canvas.create_window(300, 280 + OFFSET_Y, window=reset_button)
    set_custom_cursors(window, "data/adobe_normal.cur", "data/adobe_click.cur")

def create_slots_window(parent_root):
    parent_root.update_idletasks()
    root_x = parent_root.winfo_rootx()
    root_y = parent_root.winfo_rooty()
    root_width = parent_root.winfo_width()
    pos_y = root_y
    pos_x = root_x + root_width + 5

    window = Toplevel(parent_root)
    window.transient(parent_root)
    window.title("Casino Slots")
    window.geometry(f"500x400+{pos_x}+{pos_y}")
    window.resizable(False, False)

    try:
        icon_path = resource_path(os.path.join("data", "icon.ico"))
        window.iconbitmap(icon_path)
    except Exception as e:
        print(f"⚠️ Fehler beim Setzen des Icons: {e}")

    return window

def start_slots_game(root):
    window = create_slots_window(root)
    build_slots_ui(window)

    # ✅ Jetzt korrekt: erst UI bauen → dann Cursors
    set_custom_cursors(window, "data/adobe_normal.cur", "data/adobe_click.cur")

    window.deiconify()
    window.lift()
    window.focus_force()

def start_slots_game_threaded():
    root.after(0, lambda: start_slots_game(root))
