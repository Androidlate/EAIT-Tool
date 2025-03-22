import os
import sys
import time
import threading
import tkinter as tk
from tkinter import ttk
from config import VERSION
from admin import *
from functions import *
from veyon import *
import PIL.Image
import PIL.ImageTk

root = tk.Tk()
root.withdraw()

status_var = None
status_label = None
image_refs = {}

def show_loading_screen(parent_root):
    loading = tk.Toplevel(parent_root)
    loading.title("EAIT-Tool is loading...")
    loading.configure(bg="#1e1e1e")
    loading.resizable(False, False)
    loading.attributes("-topmost", True)
    loading.overrideredirect(True)

    # Fenster zentrieren
    win_w, win_h = 400, 120
    screen_w = loading.winfo_screenwidth()
    screen_h = loading.winfo_screenheight()
    x = (screen_w // 2) - (win_w // 2)
    y = (screen_h // 2) - (win_h // 2)
    loading.geometry(f"{win_w}x{win_h}+{x}+{y}")

    # Dunkelblaues Adobe-Theme
    style = ttk.Style(loading)
    style.theme_use('clam')
    style.configure(
        "Adobe.Horizontal.TProgressbar",
        troughcolor="#2A2A2A",
        background="#1A5496",
        bordercolor="#1A5496",
        lightcolor="#1A5496",
        darkcolor="#1A5496",
    )

    label = tk.Label(loading, text="Loading EAIT-Tool...", fg="white", bg="#1e1e1e", font=("Segoe UI", 12))
    label.pack(pady=(20, 5))

    # Wichtig: mode="indeterminate" → Endlos-Balken
    progress = ttk.Progressbar(
        loading,
        orient="horizontal",
        mode="indeterminate",
        length=300,
        style="Adobe.Horizontal.TProgressbar"
    )
    progress.pack(pady=(5, 10))

    progress["value"] = 0
    loading.update()

    # Starte Endlos-Animation
    progress.start(10)  # alle 10ms Schritt; je höher, desto schneller die Animation

    def init_tasks():
        try:
            # ----------------
            # 1) Admin Check
            if not is_admin():
                loading.destroy()
                sys.exit(1)

            # 2) build_main_gui
            build_main_gui()

            # 3) Hotkeys
            start_stop_hotkeys()

            # 4) apply_theme
            apply_theme()

            # 5) Cursor
            set_custom_cursors(parent_root,
                resource_path("data/adobe_normal.cur"),
                resource_path("data/adobe_click.cur")
            )
            # usw... was du willst

        except Exception as e:
            print(f"Fehler: {e}")
            # evtl. label.config(text="Fehler...")
            # und/oder sys.exit
        finally:
            # Alle Tasks fertig → Indeterminate Bar stoppen
            root.after(0, lambda: [
                progress.stop(),
                loading.destroy(),
                parent_root.deiconify()
            ])

    # Thread starten, damit GUI nicht blockiert wird
    threading.Thread(target=init_tasks, daemon=True).start()

def build_main_gui():
    global status_var, status_label

    root.title(f"EAIT-Tool v{VERSION()}")
    mainframe = ttk.Frame(root, padding=25)
    mainframe.grid(row=0, column=0, sticky="nsew")
    status_var = tk.StringVar()

    # Cursor
    cursor_path = resource_path(os.path.join("data", "adobe_normal.cur"))
    try:
        root.config(cursor=f"@{cursor_path.replace(os.sep, '/')}")
    except Exception as e:
        print(f"⚠️ Cursor-Setzen fehlgeschlagen: {e}")
        root.config(cursor="arrow")

    BG_COLOR = "#F3F3F3"
    ACCENT_COLOR = "#4a90e2"
    WARNING_COLOR = "#e74c3c"
    FONT_FAMILY = "Segoe UI"

    # Icon
    try:
        icon_path = resource_path(os.path.join("data", "icon.ico"))
        root.iconbitmap(default=icon_path)
    except:
        pass

    # Root basic setup
    root.configure(bg=BG_COLOR)
    w, h = 565, 520
    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()
    root.geometry(f"{w}x{h}+{(screen_w - w)//2}+{(screen_h - h)//2}")
    root.resizable(False, False)

    # ttk Style
    style = ttk.Style()
    style.theme_use('clam')
    style.configure('TFrame', background=BG_COLOR)
    style.configure('TLabel', background=BG_COLOR, foreground="black", font=(FONT_FAMILY, 10))
    style.configure('TButton', font=(FONT_FAMILY, 10), padding=6)

    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)

    # ---------------- GUI Content ----------------
    header = ttk.Frame(mainframe)
    header.grid(row=0, column=0, columnspan=2, pady=(0, 15), sticky="ew")
    theme_btn_text = tk.StringVar(value="     ☀️")
    ttk.Button(header, textvariable=theme_btn_text, command=lambda: toggle_theme(theme_btn_text)).pack(side="right", padx=10)
    ttk.Label(header, text=f"EAIT-Tool v{VERSION()}", font=(FONT_FAMILY, 16, "bold"), foreground=ACCENT_COLOR).pack()
    ttk.Label(header, text="Sie tragen volle Eigenverantwortung für die Nutzung der Funktionen.", font=(FONT_FAMILY, 10), foreground="#7f8c8d").pack(pady=(5, 0))

    tools = ttk.Frame(mainframe)
    tools.grid(row=1, column=0, columnspan=2, sticky="ew")

    # ProtonVPN Buttons
    ttk.Label(tools, text="ProtonVPN", font=(FONT_FAMILY, 10, "bold")).grid(row=0, column=0, sticky="w", pady=(10,5))
    ttk.Button(tools, text="🚀 Installieren", command=start_protonvpn_portable).grid(row=0, column=1, sticky="e")

    # Adblock Buttons
    ttk.Label(tools, text="Adblock (uBlock Origin)", font=(FONT_FAMILY, 10, "bold")).grid(row=1, column=0, sticky="w", pady=10)
    ttk.Button(tools, text="🛡️ Für Firefox aktivieren", command=install_adblock).grid(row=1, column=1, sticky="e")

    # JetBrains Buttons
    ttk.Label(tools, text="JetBrains Toolbox", font=(FONT_FAMILY, 10, "bold")).grid(row=2, column=0, sticky="w", pady=10)
    ttk.Button(tools, text="⚒️ Installieren", command=start_toolbox_portable).grid(row=2, column=1, sticky="e")

    # Veyon Buttons
    ttk.Label(tools, text="Veyon Steuerung", font=(FONT_FAMILY, 10, "bold")).grid(row=3, column=0, sticky="w", pady=(10,5))
    btn_frame = ttk.Frame(tools)
    btn_frame.grid(row=3, column=1, sticky="e")
    ttk.Button(btn_frame, text="⏸ Stoppen (STRG+F9)", command=lambda: toggle_process_state(True), width=22).pack(side="left", padx=5)
    ttk.Button(btn_frame, text="▶ Starten (STRG+F12)", command=clear_and_restart_veyon, width=22).pack(side="left")

    # Hinweis
    ttk.Label(tools, text="⚠️ Hinweis: Lehrkraft sieht ggf. eingefrorenen Bildschirm! Verwenden Sie Hotkeys zum Steuern.", 
              foreground=WARNING_COLOR, font=(FONT_FAMILY, 8)).grid(row=4, column=0, columnspan=2, sticky="w", pady=(10,20))

    # Status Box
    status_panel = ttk.Frame(mainframe, relief="solid", borderwidth=1)
    status_panel.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(15,0))
    status_label_ = tk.Label(status_panel, textvariable=status_var, fg=WARNING_COLOR, bg="#ffffff", 
                             font=(FONT_FAMILY, 9), padx=15, pady=12, wraplength=550, justify="left", height=6)
    status_label_.pack(fill="both", expand=True)

    # unten links Buttons
    action_frame = ttk.Frame(root)
    action_frame.place(relx=0.0, rely=1.0, anchor="sw", x=20, y=-20)
    try:
        brave_img = PIL.Image.open(resource_path(os.path.join("data", "brave_32x32.png"))).resize((28, 28))
        brave_icon = PIL.ImageTk.PhotoImage(brave_img)
        image_refs["brave"] = brave_icon
        ttk.Button(action_frame, image=brave_icon, command=start_brave_and_cleanup_threaded).pack(side="left", padx=5)
    except:
        pass

    set_root_ref(root)
    set_globals(root, status_var, status_label_)
    from veyon import set_status_refs
    set_status_refs(status_var, status_label_)

    apply_theme()
    set_custom_cursors(root, os.path.join("data", "adobe_normal.cur"), os.path.join("data", "adobe_click.cur"))

def safe_mainloop():
    try:
        root.mainloop()
    except Exception as e:
        import traceback
        import tkinter.messagebox
        tkinter.messagebox.showerror("Fehler", str(e))
        traceback.print_exc()
        input("Drück Enter zum Schließen...")

# ----------------------------------------------
# LAUNCH:
show_loading_screen(root)  # Zeig Ladescreen
safe_mainloop()            # Mainloop
