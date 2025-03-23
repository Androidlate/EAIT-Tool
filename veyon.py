import ctypes
import threading
import time
import ctypes
import win32api
import psutil
import pystray
import PIL.Image
import pywintypes
import win32api
import tkinter as tk
from tkinter import *
from admin import *
from functions import *

toggle_lock = threading.Lock()
root = None
status_var = None
status_label = None
indicator_window = None

def set_root_ref(r):
    global root
    root = r

def set_status_refs(var, label):
    global status_var, status_label
    status_var = var
    status_label = label

# ---------------------- Veyon GUI Task ----------------------
indicator_window = None

def show_start_popup():
    popup = tk.Toplevel()
    popup.geometry("150x40+10+10")
    popup.overrideredirect(True)
    popup.attributes("-topmost", True)
    popup.configure(bg="green")
    label = tk.Label(popup, text="✅ Veyon läuft", bg="green", fg="white", font=("Segoe UI", 10, "bold"))
    label.pack(expand=True, fill=BOTH)

    def close_after_delay():
        time.sleep(1)
        try:
            popup.destroy()
        except:
            pass

    threading.Thread(target=close_after_delay, daemon=True).start()

tray_icon = None

def create_tray_icon(status="active"):
    global tray_icon
    if tray_icon is not None:  
        try:
            tray_icon.stop()
        except Exception as e:
            print(f"⚠️ Fehler beim Stoppen des Tray-Icons: {e}")
    color = "white" if status == "active" else "red"
    icon_image = PIL.Image.new('RGB', (16, 16), color)
    tray_icon = pystray.Icon("eait_tray", icon_image, f"Veyon {'läuft' if status == 'active' else 'gestoppt'}")    
    icon_thread = threading.Thread(target=tray_icon.run, daemon=True)
    icon_thread.start()

def remove_tray_icon():
    global tray_icon
    if tray_icon is not None:
        try:
            tray_icon.stop()
            tray_icon = None  
        except Exception as e:
            print(f"⚠️ Fehler beim Beenden des Tray-Icons: {e}")

def clear_and_restart_veyon():
    if not toggle_lock.acquire(blocking=False):
        print("🔒 Aktion läuft schon")
        return
    try:
        resumed = []
        killed = []
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                name = proc.info['name']
                pid = proc.info['pid']
                if name and name.lower() in [p.lower() for p in TARGET_PROCESSES]:
                    if resume_process(pid):
                        resumed.append(f"{name} (PID {pid})")
            except Exception as e:
                print(f"❌ Fehler beim Resumen von {proc}: {e}")
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                name = proc.info['name']
                pid = proc.info['pid']
                if name and name.lower() in [p.lower() for p in TARGET_PROCESSES]:
                    proc.kill()
                    killed.append(f"{name} (PID {pid})")
            except Exception as e:
                print(f"❌ Fehler beim Killen von {name}: {e}")
        if not resumed and not killed:
            status_var.set("❌ Keine Veyon-Prozesse gefunden.")
            status_label.config(fg="#888")
            return
        message = "✅ Veyon zurückgesetzt.\n"
        if resumed:
            message += "▶️ Fortgesetzt:\n" + "\n".join(resumed) + "\n"
        status_var.set(message.strip())
        status_label.config(fg="#888")
        set_corner_indicator(False)
        show_start_popup()
        create_tray_icon("active")
    finally :
        toggle_lock.release()

# ---------------------- Veyon Suspend Task ----------------------
TARGET_PROCESSES = ["veyon-service.exe", "veyon-worker.exe", "veyon-server.exe"]

ntdll = ctypes.WinDLL("ntdll")
NtSuspendProcess = ntdll.NtSuspendProcess
NtResumeProcess = ntdll.NtResumeProcess
NtSuspendProcess.argtypes = [ctypes.c_void_p]
NtResumeProcess.argtypes = [ctypes.c_void_p]
NtSuspendProcess.restype = ctypes.c_ulong
NtResumeProcess.restype = ctypes.c_ulong

PROCESS_SUSPEND_RESUME = 0x0800  # direkt definieren, falls win32con es nicht hat
def suspend_process(pid):
    try:
        hProc = win32api.OpenProcess(PROCESS_SUSPEND_RESUME, False, pid)
        result = NtSuspendProcess(int(hProc))
        win32api.CloseHandle(hProc)
        return result == 0
    except pywintypes.error as e:
        print(f"Windows API Fehler PID {pid}: {e.winerror} - {e.strerror}")
        return False
    except Exception as e:
        print(f"Kritischer Fehler: {type(e).__name__} - {str(e)}")
        return False
    
def resume_process(pid):
    try:
        hProc = win32api.OpenProcess(PROCESS_SUSPEND_RESUME, False, pid)  
        result = NtResumeProcess(int(hProc))
        win32api.CloseHandle(hProc)
        return result == 0
    except Exception as e:
        print(f"Resume-Fehler bei PID {pid}: {e}")
        return False
    
def toggle_process_state(suspend=True):
    if not toggle_lock.acquire(blocking=False): 
        print("🔒 Aktion läuft schon")
        return
    try:
        action = "PAUSIERT" if suspend else "FORTGESETZT"
        affected = []
        failed = []

        for proc in psutil.process_iter(['pid', 'name']):
            try:
                name = proc.info['name']
                pid = proc.info['pid']
                if not name or name.lower() not in [p.lower() for p in TARGET_PROCESSES]:
                    continue
                # Prozess individuell bearbeiten
                if suspend:
                    success = suspend_process(pid)
                else:
                    success = resume_process(pid)
            
                if success:
                    affected.append(f"{name} (PID {pid})")
                else:
                    failed.append(f"{name} (PID {pid})")
                
            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                print(f"❌ Prozessfehler: {e}")
                failed.append(f"{name if name else 'Unbekannt'} (PID {pid})")
        # Status-Updates mit Thread-Safety
        root.after(0, lambda: update_ui_elements(
            suspend, 
            affected, 
            failed, 
            action
        ))
        # Visuelle Bestätigung nur bei komplettem Erfolg
        if suspend and affected and not failed:
            if wait_until_suspended():
                root.after(0, lambda: set_corner_indicator(True))
                create_tray_icon("off")
            else:
                failed.extend(affected)
                affected.clear()
    finally:
        toggle_lock.release()

def update_ui_elements(suspend, affected, failed, action):
    if root.winfo_exists():
        status_text = f"✅ {len(affected)} Prozesse {action}:\n" + "\n".join(affected)
        if failed:
            status_text += f"\n⚠️ Fehler bei {len(failed)} Prozessen:\n" + "\n".join(failed)
        
        # Farbe basierend auf Erfolgsstatus
        color = "#555" if failed else "green" if not suspend else "red"
        status_var.set(status_text)
        status_label.config(fg=color)
        
        # Popup nur bei vollständigem Erfolg
        if not suspend and not failed:
            show_start_popup()
            set_corner_indicator(False)
    else:
        status_var.set("❌ Keine Prozesse gefunden")
        status_label.config(fg="#888")

corner_indicator = None 

def set_corner_indicator(show):
    global corner_indicator
    if corner_indicator:
        try:
            corner_indicator.destroy()
        except:
            pass
        corner_indicator = None  

    if not show:
        return

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    corner = tk.Toplevel()
    corner.geometry(f"15x15+{screen_width - 25}+{screen_height - 45}")
    corner.overrideredirect(True)
    corner.attributes("-topmost", True)
    corner.configure(bg="blue")

    def keep_on_top():
        if corner.winfo_exists():
            corner.lift()
            corner.after(1000, keep_on_top)  # Check every second
    keep_on_top()
    corner_indicator = corner

def wait_until_suspended(timeout=5):
    start_time = time.time()
    while time.time() - start_time < timeout:
        all_stopped = True
        for proc in psutil.process_iter(['pid', 'name', 'status']):
            try:
                if proc.info['name'].lower() not in [p.lower() for p in TARGET_PROCESSES]:
                    continue
                
                # Genauer Status-Check für Windows
                status = proc.status()
                if sys.platform == "win32":
                    if status != psutil.STATUS_STOPPED:
                        all_stopped = False
                        break
                else:  # Für andere Betriebssysteme
                    if status != psutil.STATUS_SLEEPING:
                        all_stopped = False
                        break
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        if all_stopped:
            return True
        time.sleep(0.2)
    return False
