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
from PIL import Image, ImageTk

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

def build_slots_ui(window):
    from PIL import Image, ImageTk
    import random
    from tkinter import Label, Button

    symbols = ["🍒", "🍋", "🍊", "🍇", "💎", "7️⃣", "🎰"]
    symbol_values = {"🍒": 1, "🍋": 2, "🍊": 3, "🍇": 5, "💎": 10, "7️⃣": 15, "🎰": 25}
    credits = 100

    bg_image_path = resource_path(os.path.join("data", "casino_background.png"))
    print(f"[DEBUG] Hintergrundpfad: {bg_image_path}")
    print(f"[DEBUG] Existiert Hintergrundbild? {os.path.exists(bg_image_path)}")

    try:
        bg_image = Image.open(bg_image_path).resize((500, 400), Image.LANCZOS)
        bg_photo = ImageTk.PhotoImage(bg_image)
    except Exception as e:
        print(f"⚠️ Fehler beim Laden des Hintergrunds: {e}")
        return

    # Canvas mit Hintergrund
    canvas = tk.Canvas(window, width=500, height=400, highlightthickness=0, bd=0)
    canvas.pack(fill="both", expand=True)
    canvas.create_image(0, 0, image=bg_photo, anchor="nw")
    canvas.bg_photo = bg_photo  # Referenz halten!

    # Credits Label
    credits_label = Label(canvas, text=f"Credits: {credits}", font=(FONT_FAMILY, 16, "bold"), bg="black", fg="white")
    canvas.create_window(250, 30, window=credits_label)

    # Message Label
    message_label = Label(canvas, text="Good luck!", font=(FONT_FAMILY, 12), bg="black", fg="yellow")
    canvas.create_window(250, 60, window=message_label)

    # Slots
    slot_labels = []
    for i in range(3):
        slot = Label(canvas, text="🎰", font=(FONT_FAMILY, 40), bg='black', fg="white", width=2)
        canvas.create_window(150 + i * 100, 140, window=slot)
        slot_labels.append(slot)

    # Check Win Funktion
    def check_win(result):
        if result[0] == result[1] == result[2]:
            return symbol_values.get(result[0], 1) * 10
        elif result[0] == result[1] or result[1] == result[2] or result[0] == result[2]:
            match = result[1] if result[1] == result[2] else result[0]
            return symbol_values.get(match, 1) * 2
        return 0

    # SPIN Funktion
    def spin():
        nonlocal credits
        if credits < 5:
            message_label.config(text="Not enough credits!", fg="red")
            return
        credits -= 5
        credits_label.config(text=f"Credits: {credits}")
        message_label.config(text="Spinning...", fg="yellow")
        spin_button.config(state="disabled")

        def animate(count=0):
            nonlocal credits
            if count < 10:
                for slot in slot_labels:
                    slot.config(text=random.choice(symbols))
                window.after(100, lambda: animate(count + 1))
            else:
                result = [random.choice(symbols) for _ in range(3)]
                for i, s in enumerate(result):
                    slot_labels[i].config(text=s)
                win = check_win(result)
                if win:
                    credits += win
                    message_label.config(text=f"You won {win} credits!", fg="yellow")
                    credits_label.config(text=f"Credits: {credits}")
                else:
                    message_label.config(text="Try again!", fg="white")
                spin_button.config(state="normal")

        animate()

    # RESET Funktion
    def reset_game():
        nonlocal credits
        credits = 100
        credits_label.config(text=f"Credits: {credits}")
        message_label.config(text="Game reset! Good luck!", fg="yellow")
        for slot in slot_labels:
            slot.config(text="🎰")

    # Buttons
    spin_button = Button(canvas, text="SPIN (5 credits)", font=(FONT_FAMILY, 12, "bold"),
                         command=spin, bg="#8B0000", fg="white", relief="raised")
    canvas.create_window(150, 280, window=spin_button)

    reset_button = Button(canvas, text="Reset Game", font=(FONT_FAMILY, 12),
                          command=reset_game, bg="#4B0082", fg="white", relief="raised")
    canvas.create_window(300, 280, window=reset_button)

def create_slots_window():
    root.update_idletasks()
    root_x = root.winfo_rootx()
    root_y = root.winfo_rooty()
    root_width = root.winfo_width()
    root_height = root.winfo_height()

    pos_y = root_y  # exakt gleich hoch starten
    pos_x = root_x + root_width + 5  # minimaler Abstand

    window = Toplevel(root)
    window.transient(root)
    window.focus_force()
    window.title("Casino Slots")
    window.geometry(f"500x400+{pos_x}+{pos_y}")  # gleiche Höhe wie Hauptfenster
    window.resizable(False, False)

    try:
        icon_path = resource_path(os.path.join("data", "icon.ico"))
        window.iconbitmap(icon_path)
    except Exception as e:
        print(f"⚠️ Fehler beim Setzen des Icons: {e}")
    return window

def start_slots_game():
    try:
        slots_window = create_slots_window()
        build_slots_ui(slots_window)
        slots_window.update_idletasks()

        # ✅ FIX gegen Ghost-Window
        slots_window.deiconify()
        slots_window.lift()
        slots_window.focus_force()

        # ✅ CURSOR-FIX: Adobe Cursor auch im Slots-Window aktivieren
        set_custom_cursors(slots_window,
            os.path.join("data", "adobe_normal.cur"),
            os.path.join("data", "adobe_click.cur")
        )

        status_var.set("Casino Slots gestartet")
    except Exception as e:
        status_var.set(f"Fehler beim Starten des Spiels: {e}")
        print(f"⚠️ Casino error: {e}")

def start_slots_game_threaded():
    root.after(0, start_slots_game)
