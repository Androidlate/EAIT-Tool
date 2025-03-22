# Changelog:
"""
0.2.2 - Resized Main Window & Disabled Window Resizing
0.2.3 - Added Brave
0.2.4 - Added uBlock for Brave
0.2.5 - Added Systemtime Change
0.2.6 - Added Systemtime Change Methods
0.2.7 - Created Portable Versions for VPN and Jetbrains Toolbox, New Veyon Warning Label, Minor Changes
0.2.8 - Icon fixed
0.2.9 - Show UAC Prompt if run as non-Admin
0.3 - Added Hotkey Activation
0.3.1 - Added Systemtray for Hotkey listening + Visual feedback
0.3.2 - Minor Changes
0.3.3 - Improved Veyon process handling
0.3.4 - Visual feedback refined
0.3.5 - Thread safety & error handling improved
0.3.6 - Fixed Styling & Veyon Indicator
0.3.7 - Added Dark / Light Mode Button
0.3.8 - Added Custom Cursor, Styling, Bugfixes
0.3.9 - Removed Change System Time completely as it was not working on school computers
"""
import traceback
from config import VERSION
from admin import *
from functions import *
from veyon import *
from tkinter import *
from tkinter import ttk
import tkinter as tk
import PIL.Image
import PIL.ImageTk
import traceback
from config import VERSION
from admin import *
from functions import *
from veyon import *

# Wichtig für Brave Icon
image_refs = {}

# ---------------------- Window Setup ----------------------

root = tk.Tk()
root.title(f"EAIT-Tool v{VERSION()}")
mainframe = ttk.Frame(root, padding=25)
mainframe.grid(row=0, column=0, sticky="nsew")
status_var = StringVar()

# Custom Cursor
cursor_path = os.path.join(os.path.dirname(__file__), "adobe_normal.cur")
cursor_string = f"@{cursor_path.replace(os.sep, '/')}"  # Windows-kompatibel machen!
try:
    root.config(cursor=cursor_string)
    print("✅ Custom Cursor gesetzt:", cursor_string)
except Exception as e:
    print("❌ Cursor Error:", e)
    root.config(cursor="arrow")

# Modernes Design-Setup
BG_COLOR = "#F3F3F3"
ACCENT_COLOR = "#4a90e2"
WARNING_COLOR = "#e74c3c"
FONT_FAMILY = "Segoe UI"

# Icon setzen
try:
    icon_path = resource_path("icon.ico")
    root.iconbitmap(default=icon_path)
except Exception as e:
    print(f"⚠️ Icon konnte nicht gesetzt werden: {e}")

root.configure(bg=BG_COLOR)
window_width = 565
window_height = 520  

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

center_x = int(screen_width/2 - window_width/2)
center_y = int(screen_height/2 - window_height/2)

root.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")
root.resizable(False, False)

# Style Configuration
style = ttk.Style()
style.theme_use('clam')
style.configure('TFrame', background=BG_COLOR)
style.configure('TLabel', background=BG_COLOR, foreground="black", font=(FONT_FAMILY, 10))
style.configure('TButton', font=(FONT_FAMILY, 10), padding=6)

# Main Frame
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

# ---------------------- GUI Setup ----------------------

# Header Section
header_frame = ttk.Frame(mainframe)
header_frame.grid(row=0, column=0, columnspan=2, pady=(0, 15), sticky="ew")
# Theme Toggle Button im Header
theme_btn_text = StringVar(value="     ☀️")  
theme_btn = ttk.Button(header_frame, textvariable=theme_btn_text, command=lambda: toggle_theme(theme_btn_text))
theme_btn.pack(side="right", padx=10)

ttk.Label(header_frame, 
         text=f"EAIT-Tool v{VERSION()}", 
         font=(FONT_FAMILY, 16, "bold"), 
         foreground=ACCENT_COLOR).pack(side="top")

ttk.Label(header_frame, 
         text="Sie tragen volle Eigenverantwortung für die Nutzung der Funktionen.",
         font=(FONT_FAMILY, 10), 
         foreground="#7f8c8d").pack(side="top", pady=(5, 0))

# Tools Grid
tools_grid = ttk.Frame(mainframe)
tools_grid.grid(row=1, column=0, columnspan=2, sticky="ew")

# VPN Section
ttk.Label(tools_grid, text="ProtonVPN", font=(FONT_FAMILY, 10, "bold")).grid(row=0, column=0, sticky="w", pady=(10,5))
ttk.Button(tools_grid, 
         text="🚀 Installieren", 
         command=start_protonvpn_portable,
         style="Accent.TButton").grid(row=0, column=1, sticky="e")

# Adblock Section
ttk.Label(tools_grid, text="Adblock (uBlock Origin)", font=(FONT_FAMILY, 10, "bold")).grid(row=1, column=0, sticky="w", pady=10)
ttk.Button(tools_grid, 
         text="🛡️ Für Firefox aktivieren", 
         command=install_adblock).grid(row=1, column=1, sticky="e")

# Toolbox Section
ttk.Label(tools_grid, text="JetBrains-ToolBox", font=(FONT_FAMILY, 10, "bold")).grid(row=2, column=0, sticky="w", pady=10)
ttk.Button(tools_grid, 
         text="⚒️ Installieren", 
         command=start_toolbox_portable).grid(row=2, column=1, sticky="e")

# Veyon Section
ttk.Label(tools_grid, text="Veyon Steuerung", font=(FONT_FAMILY, 10, "bold")).grid(row=3, column=0, sticky="w", pady=(10,5))
btn_frame = ttk.Frame(tools_grid)
btn_frame.grid(row=3, column=1, sticky="e")

ttk.Button(btn_frame, 
         text="⏸ Stoppen (STRG + F9)", 
         command=lambda: toggle_process_state(True),
         width=22).pack(side="left", padx=5)
ttk.Button(btn_frame, 
         text="▶ Starten (STRG + F12)", 
         command=clear_and_restart_veyon,
         width=22).pack(side="left")

# Warning Label
ttk.Label(tools_grid, 
         text="⚠️ Hinweis: Lehrkraft sieht ggf. eingefrierten Bildschirm! Verwenden Sie Hotkeys zum Steuern.",
         foreground=WARNING_COLOR,
         font=(FONT_FAMILY, 8)).grid(row=4, column=0, columnspan=2, sticky="w", pady=(10,20))

# Status Panel
status_panel = ttk.Frame(mainframe, relief="solid", borderwidth=1)
status_panel.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(15,0))

status_label = tk.Label(
    status_panel,
    textvariable=status_var,
    fg=WARNING_COLOR,
    bg="#ffffff",
    font=(FONT_FAMILY, 9),
    padx=15,
    pady=12,
    wraplength=550,
    justify="left",
    height=6  
)
status_label.pack(fill="both", expand=True)
set_status_refs(status_var, status_label)

# Action Buttons (unten links)
action_frame = ttk.Frame(root)
action_frame.place(relx=0.0, rely=1.0, anchor="sw", x=20, y=-20)

# Brave Button
try:
    brave_img = PIL.Image.open(resource_path("brave/brave_32x32.png")).resize((28, 28))
    brave_icon = PIL.ImageTk.PhotoImage(brave_img)
    image_refs["brave"] = brave_icon  # ⬅️ Speichert das Icon dauerhaft
    ttk.Button(action_frame, 
               image=brave_icon, 
               command=start_brave_and_cleanup_threaded).pack(side="left", padx=5)
except Exception as e:
    print(f"⚠️ Brave-Icon Fehler: {e}")

set_root_ref(root)
set_globals(root, status_var, status_label)
start_stop_hotkeys()
apply_theme()
set_custom_cursors(root, "adobe_normal.cur", "adobe_click.cur")

def safe_mainloop():
    try:
        root.mainloop()
    except Exception as e:
        import tkinter.messagebox
        tkinter.messagebox.showerror("Fehler", f"{e}")
        traceback.print_exc()
        input("Drücke Enter zum Schließen...")
safe_mainloop()