import ctypes
import os
import sys
import ctypes
from tkinter import *
from tkinter import messagebox

# ---------------------- Admin ----------------------
def is_admin():
    if os.name == 'nt':  # Windows
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    else:  # Linux/macOS
        return os.geteuid() == 0

if not is_admin():
    # Wenn der Benutzer keine Admin-Rechte hat
    answer = messagebox.askyesno("Administratorrechte erforderlich", 
                                 "Das Tool benötigt Administratorrechte. Möchten Sie es als Administrator ausführen?")
    if answer: 
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit(0)  
    else:
        messagebox.showerror("EAIT-Tool", "Bitte starten Sie das Tool als Administrator.")
        sys.exit(1) 