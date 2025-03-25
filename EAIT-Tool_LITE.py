import os
import sys
import tkinter as tk
import tempfile
import requests
import shutil
import time
import subprocess
import threading
from tkinter import ttk
import random
import tkinter.messagebox
from PIL import Image
from PIL import ImageTk
from PIL import ImageSequence

status_animation_running = False
status_animation_thread = None
casino_window = None

def cleanup_brave_temp():
    try:
        shutil.rmtree("brave_temp", ignore_errors=True)
        print("🧹 Brave-Temp gelöscht.")
    except Exception as e:
        print(f"⚠️ Brave-Cleanup-Fehler: {e}")

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.abspath(relative_path)

def get_temp_icon_path():
    try:
        icon_src = resource_path("data/icon.ico")
        icon_dest = os.path.join(tempfile.gettempdir(), "eait_tool_icon.ico")

        if not os.path.exists(icon_dest):  # Nur wenn nicht schon da
            shutil.copyfile(icon_src, icon_dest)

        return icon_dest
    except Exception as e:
        print(f"⚠️ Icon extrahieren fehlgeschlagen: {e}")
        return None

def center_window(win, width, height):
    screen_w = win.winfo_screenwidth()
    screen_h = win.winfo_screenheight()
    x = (screen_w // 2) - (width // 2)
    y = (screen_h // 2) - (height // 2)
    win.geometry(f"{width}x{height}+{x}+{y}")

def set_custom_cursors(widget, normal_cursor_path="data/adobe_normal.cur", click_cursor_path="data/adobe_click.cur"):
    normal_abs = resource_path(normal_cursor_path).replace("\\", "/")
    click_abs = resource_path(click_cursor_path).replace("\\", "/")

    normal_cursor = f"@{normal_abs}" if os.path.exists(normal_abs) else "arrow"
    click_cursor = f"@{click_abs}" if os.path.exists(click_abs) else "hand2"

    def apply_recursive(w):
        try:
            w.config(cursor=normal_cursor)
        except:
            pass
        for child in w.winfo_children():
            try:
                child.config(cursor=normal_cursor)
            except:
                pass
            if isinstance(child, (tk.Button, ttk.Button)):
                child.bind("<Enter>", lambda e: e.widget.config(cursor=click_cursor))
                child.bind("<Leave>", lambda e: e.widget.config(cursor=normal_cursor))
            apply_recursive(child)

    apply_recursive(widget)

# Direkt nach der start_slots_lite() Funktion einfügen:
def build_slots_ui(window):
    try:
        icon_path = get_temp_icon_path()
        if icon_path:
            try:
                window.iconbitmap(icon_path)
            except Exception as e:
                print(f"⚠️ Icon im Casino konnte nicht gesetzt werden: {e}")

        FONT_FAMILY = "Segoe UI"
        symbols = ["🍒", "🍋", "🍊", "🍇", "💎", "🎱", "🎰"]
        symbol_values = {"🍒": 1, "🍋": 2, "🍊": 3, "🍇": 5, "💎": 10, "🎱": 15, "🎰": 25}
        credits = {"value": 20}

        OFFSET_Y = 60

        # === BACKGROUND ===
        bg_image_path = resource_path("data/casino_background.png")
        bg_image = Image.open(bg_image_path).convert("RGB").resize((500, 400), Image.LANCZOS)
        bg_photo = ImageTk.PhotoImage(bg_image)

        canvas = tk.Canvas(window, width=500, height=400, highlightthickness=0, bd=0)
        canvas.pack(fill="both", expand=True)
        canvas.create_image(0, 0, image=bg_photo, anchor="nw")
        window.bg_photo = bg_photo  # 🔒 REF retten!

        # === GIF Logo ===
        try:
            logo_path = resource_path("data/casino_logo.gif")
            logo_gif = Image.open(logo_path)
            frames = [ImageTk.PhotoImage(f.copy().resize((180, 50), Image.LANCZOS)) for f in ImageSequence.Iterator(logo_gif)]

            logo_label = tk.Label(canvas, bg="black")
            canvas.create_window(250, 10, window=logo_label, anchor="n")

            def animate_logo(idx=0):
                logo_label.config(image=frames[idx])
                logo_label.after(100, lambda: animate_logo((idx + 1) % len(frames)))

            logo_label.frames = frames  # 🔒 wichtig!
            window.logo_ref = frames   # 🔒 wichtig!
            animate_logo()

        except Exception as e:
            print(f"⚠️ Casino GIF Fehler: {e}")

        # Restliche UI bleibt wie du hast...
        # canvas.create_window(... für credits_label, buttons etc.)
                # === UI Elemente ===
        credits_label = tk.Label(canvas, text=f"Credits: {credits['value']}", font=(FONT_FAMILY, 16, "bold"),
                                 bg="black", fg="white")
        canvas.create_window(250, 80, window=credits_label)

        message_label = tk.Label(canvas, text="Good luck!", font=(FONT_FAMILY, 12),
                                 bg="black", fg="yellow")
        canvas.create_window(250, 110, window=message_label)

        slot_labels = []
        for i in range(3):
            slot = tk.Label(canvas, text="🎰", font=(FONT_FAMILY, 40), bg='black', fg="white", width=2)
            canvas.create_window(150 + i * 100, 180, window=slot)
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

        spin_button = tk.Button(canvas, text="SPIN (5 credits)", font=(FONT_FAMILY, 12, "bold"),
                                command=spin, bg="#8B0000", fg="white", relief="raised")
        canvas.create_window(150, 270, window=spin_button)

        reset_button = tk.Button(canvas, text="Reset Game", font=(FONT_FAMILY, 12),
                                 command=reset_game, bg="#4B0082", fg="white", relief="raised")
        canvas.create_window(300, 270, window=reset_button)

        # Mauszeiger korrekt setzen
        set_custom_cursors(window, "data/adobe_normal.cur", "data/adobe_click.cur")

        
    except Exception as e:
        import traceback
        print(f"❌ build_slots_ui Fehler: {e}")
        traceback.print_exc()

def start_slots_lite():
    try:
        global casino_window
        casino_window = tk.Toplevel(root)
        slots_window = casino_window
        slots_window.withdraw()
        slots_window.title("Casino Slots")

        # Fensterposition → schön rechts neben Main
        root.update_idletasks()
        root_x = root.winfo_rootx()
        root_y = root.winfo_rooty()
        root_width = root.winfo_width()
        root_height = root.winfo_height()
        pos_y = root_y + (root_height // 2) - 200
        pos_x = root_x + root_width + 10
        slots_window.geometry(f"500x400+{pos_x}+{pos_y}")
        slots_window.resizable(False, False)

        # Icon
        try:
            ico_data = open(resource_path("data/icon.ico"), "rb").read()

            temp_icon_path = os.path.join(tempfile.gettempdir(), "eait_temp_icon.ico")
            with open(temp_icon_path, "wb") as f:
                f.write(ico_data)

            root.iconbitmap(temp_icon_path)
        except Exception as e:
            print(f"⚠️ Icon konnte nicht gesetzt werden: {e}")

        # Casino UI
        build_slots_ui(slots_window)

        slots_window.update_idletasks()
        slots_window.deiconify()
        status_var.set("Casino Slots gestartet")

        # 👉 Jetzt korrekt: Close Handler mit Cleanup
        def on_casino_close():
            global casino_window
            print("🎰 Casino wird geschlossen.")
            casino_window = None

            if not root.winfo_viewable():
                print("🧹 Alles zu → EXIT.")
                cleanup_brave_temp()  # ✅ Brave Temp löschen!
                root.quit()
            else:
                print("🏠 Main bleibt offen.")
                slots_window.destroy()

        slots_window.protocol("WM_DELETE_WINDOW", on_casino_close)

    except Exception as e:
        status_var.set(f"⚠️ Fehler beim Starten des Spiels: {e}")
        print(f"⚠️ Casino error: {e}")

root = tk.Tk()
root.withdraw()  
root.title(f"EAIT-Tool Lite")
root.geometry("500x350")
root.resizable(False, False)
center_window(root, 500, 350)

# Icon setzen
icon_path = get_temp_icon_path()
if icon_path:
    try:
        root.iconbitmap(icon_path)
    except Exception as e:
        print(f"⚠️ Icon setzen fehlgeschlagen: {e}")

status_var = tk.StringVar(value="Bereit.")

def start_status_animation(base_text):
    global status_animation_running, status_animation_thread

    def animate():
        dots = ["", ".", "..", "...", "..", "."]
        i = 0
        while status_animation_running:
            status_var.set(f"{base_text}{dots[i % len(dots)]}")
            i += 1
            time.sleep(0.4)

    status_animation_running = True
    status_animation_thread = threading.Thread(target=animate, daemon=True)
    status_animation_thread.start()

def stop_status_animation(final_text=None):
    global status_animation_running
    status_animation_running = False
    if final_text:
        status_var.set(final_text)

# ----------------------------------------
# 🛰 Downloader-Funktion
# ----------------------------------------
def threaded_download_and_run(url, filename, is_archive=False):
    def task():
        try:
            status_var.set(f"⚙️ {filename} wird heruntergeladen...")
            temp_dir = tempfile.mkdtemp()
            file_path = os.path.join(temp_dir, filename)

            with requests.get(url, stream=True) as r:
                r.raise_for_status()
                with open(file_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)

            if is_archive:
                status_var.set(f"📦 {filename} wurde heruntergeladen. Manuell entpacken.")
                subprocess.Popen(["explorer", temp_dir])
            else:
                status_var.set(f"🚀 {filename} wird gestartet...")
                subprocess.Popen(file_path)
                status_var.set(f"✅ {filename} gestartet.")
                # Lösche nur wenn keine Archive
                threading.Thread(target=lambda: (time.sleep(5), shutil.rmtree(temp_dir, ignore_errors=True)), daemon=True).start()

        except Exception as e:
            status_var.set(f"❌ Fehler bei {filename}: {e}")

    threading.Thread(target=task, daemon=True).start()

# ----------------------------------------
# 🔘 Button-Aktionen
# ----------------------------------------
def start_protonvpn():
    def task():
        try:
            start_status_animation("🚀 ProtonVPN wird heruntergeladen")
            url = "https://vpn.protondownload.com/download/ProtonVPN_v3.5.3_x64.exe"
            temp_dir = tempfile.mkdtemp()
            file_path = os.path.join(temp_dir, "ProtonVPN.exe")

            with requests.get(url, stream=True, timeout=10) as r:
                r.raise_for_status()
                with open(file_path, "wb") as f:
                    shutil.copyfileobj(r.raw, f)

            stop_status_animation("🚀 ProtonVPN wird gestartet...")
            subprocess.Popen(file_path)
            stop_status_animation("✅ ProtonVPN läuft.")
            threading.Thread(target=lambda: (time.sleep(10), shutil.rmtree(temp_dir, ignore_errors=True)), daemon=True).start()

        except Exception as e:
            stop_status_animation(f"❌ Fehler: {e}")

    threading.Thread(target=task, daemon=True).start()

def start_jetbrains():
    def task():
        try:
            url = "https://download.jetbrains.com/toolbox/jetbrains-toolbox-2.5.4.38621.exe"
            filename = "jetbrains_toolbox.exe"
            start_status_animation("⚙️ JetBrains wird heruntergeladen")

            temp_dir = tempfile.mkdtemp()
            file_path = os.path.join(temp_dir, filename)

            with requests.get(url, stream=True, timeout=10) as r:
                r.raise_for_status()
                with open(file_path, "wb") as f:
                    shutil.copyfileobj(r.raw, f)

            stop_status_animation("🚀 JetBrains wird gestartet...")
            subprocess.Popen(file_path)
            stop_status_animation("✅ JetBrains läuft.")

            threading.Thread(target=lambda: (time.sleep(10), shutil.rmtree(temp_dir, ignore_errors=True)), daemon=True).start()

        except Exception as e:
            stop_status_animation(f"❌ JetBrains Fehler: {e}")
            print(f"❌ JetBrains Exception: {e}")

    threading.Thread(target=task, daemon=True).start()

def start_brave():
    def task():
        try:
            start_status_animation("🌐 Brave wird vorbereitet")
            brave_dir = os.path.join(os.getcwd(), "brave_temp")
            brave_exe = os.path.join(brave_dir, "brave-portable.exe")
            brave_7z = os.path.join(brave_dir, "brave.7z")
            seven_zip = resource_path("data/7z.exe")
            url = "https://github.com/portapps/brave-portable/releases/download/1.71.123-93/brave-portable-win64-1.71.123-93.7z"

            os.makedirs(brave_dir, exist_ok=True)

            # Brave ist schon da
            if os.path.exists(brave_exe):
                stop_status_animation("🚀 Brave wird gestartet (lokal)...")
                subprocess.Popen(brave_exe, cwd=brave_dir)
                return

            was_geladen = False  # 👈 Flag

            # Download wenn nicht da
            if not os.path.exists(brave_7z):
                stop_status_animation()
                start_status_animation("⬇️ Brave wird geladen")
                with requests.get(url, stream=True) as r:
                    r.raise_for_status()
                    with open(brave_7z, "wb") as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            f.write(chunk)
                was_geladen = True  # ✅ merken, dass was geladen wurde

            # Nur entpacken wenn vorher geladen
            if was_geladen:
                stop_status_animation()
                start_status_animation("📦 Brave wird entpackt")
                result = subprocess.run(
                    [seven_zip, "x", brave_7z, f"-o{brave_dir}", "-y"],
                    capture_output=True,
                    text=True
                )

                print("📝 STDOUT:\n", result.stdout)
                print("🛑 STDERR:\n", result.stderr)

                if result.returncode != 0:
                    raise RuntimeError(f"7-Zip Fehlercode: {result.returncode}")

                if not os.path.exists(brave_exe):
                    raise FileNotFoundError(f"❌ brave-portable.exe fehlt in: {brave_dir}")

            # Start Brave nach Entpacken (oder wenn schon entpackt)
            stop_status_animation("🚀 Brave wird gestartet...")
            subprocess.Popen(brave_exe, cwd=brave_dir)
            stop_status_animation("✅ Brave läuft.")

        except Exception as e:
            stop_status_animation(f"❌ Fehler: {e}")
            print(f"❌ Exception: {e}")

    threading.Thread(target=task, daemon=True).start()

def install_adblock():
    try:
        url = "https://addons.mozilla.org/firefox/downloads/latest/ublock-origin/latest.xpi"
        subprocess.Popen(["start", "", url], shell=True)
        status_var.set("Adblock geöffnet – im Firefox bestätigen.")
    except Exception as e:
        status_var.set(f"❌ Fehler: {e}")

# ----------------------------------------
# 🖼 GUI
# ----------------------------------------
frame = tk.Frame(root)
frame.pack(padx=20, pady=20, expand=True, fill="both")

tk.Label(frame, text=f"EAIT-Tool Lite", font=("Segoe UI", 16, "bold")).pack(pady=(0, 5))
tk.Label(frame, text="⚠️ Tools werden live aus dem Internet geladen", font=("Segoe UI Emoji", 10)).pack(pady=(0, 15))

btn_style = {"padding": 6}
tk.Button(frame, text="🚀 ProtonVPN starten", font=("Segoe UI Emoji", 10), command=start_protonvpn).pack(fill="x", pady=4)
tk.Button(frame, text="🛡️ Adblock für Firefox", font=("Segoe UI Emoji", 10), command=install_adblock).pack(fill="x", pady=4)
tk.Button(frame, text="⚒️ JetBrains Toolbox", font=("Segoe UI Emoji", 10), command=start_jetbrains).pack(fill="x", pady=4)
tk.Button(frame, text="🌐 Brave Portable öffnen", font=("Segoe UI Emoji", 10), command=start_brave).pack(fill="x", pady=4)
tk.Button(frame, text="🎰 Casino Slots starten", font=("Segoe UI Emoji", 10), command=start_slots_lite).pack(fill="x", pady=(20, 0))

status_label = tk.Label(root, font=("Segoe UI Emoji", 10), textvariable=status_var, relief="solid", anchor="w")
status_label.pack(fill="x", side="bottom", padx=10, pady=5)

set_custom_cursors(root)

# ----------------------------------------
# 🔚 Exit
# ----------------------------------------

# Crash Handler
def global_crash_handler(exc_type, exc_value, tb):
    import traceback
    error = ''.join(traceback.format_exception(exc_type, exc_value, tb))
    print("🔥 UNHANDLED EXCEPTION:\n", error)
    tkinter.messagebox.showerror("Fehler im Tool", f"Unerwarteter Fehler:\n\n{exc_value}")
    root.destroy()

import sys
sys.excepthook = global_crash_handler

# Exit Handler (einzige richtige Stelle!)
def on_close():
    global casino_window
    print("👋 EAIT Lite Fenster wird geschlossen.")

    # Nur verstecken, wenn Casino läuft
    if casino_window and casino_window.winfo_exists():
        print("🎰 Casino läuft weiter...")
        root.withdraw()  # nur verstecken
    else:
        print("❌ Kein Casino → Alles beenden.")
        try:
            shutil.rmtree("brave_temp", ignore_errors=True)
        except:
            pass
        root.destroy()

# Exit-Hook registrieren (nicht aufrufen!)
root.protocol("WM_DELETE_WINDOW", on_close)
root.deiconify()
root.mainloop()
