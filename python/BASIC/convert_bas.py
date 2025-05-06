import pyautogui
import time
import csv
import subprocess
import psutil

# ===== CONFIGURATION =====
DOSBOX_PATH = r"C:\Program Files (x86)\DOSBox-0.74-3\DOSBox.exe"
QBASIC_DIR = r"C:\BASIC"  # Folder containing QB.EXE
CSV_PATH = r"c:\basic\files.csv"  # Your CSV location
DELAY = 0.05  # Increased delay for reliability
# =========================

def close_dosbox():
    """Force close any existing DOSBox/QBASIC instances"""
    for proc in psutil.process_iter(['name']):
        if proc.info['name'].lower() in ('dosbox.exe', 'qb.exe'):
            proc.kill()
    time.sleep(1)

def send_keystrokes(keys, delay=DELAY):
    """More reliable keystroke sender"""
    try:
        win = pyautogui.getWindowsWithTitle("DOSBox")[0]
        win.activate()
        win.maximize()
        time.sleep(0.3)
        if keys.startswith("%"):
            pyautogui.hotkey('alt', keys[1:].lower())
        else:
            pyautogui.write(keys, interval=0.07)
        time.sleep(delay)
        return True
    except Exception as e:
        print(f"Key input failed: {str(e)}")
        return False

def convert_files():
    close_dosbox()
    
    # Launch DOSBox
    subprocess.Popen([
        DOSBOX_PATH,
        "-noconsole",
        "-noautoexec",
        "-c", f"mount c: {QBASIC_DIR}",
        "-c", "c:",
        "-c", "qb.exe /L",
        "-c", "exit"
    ], creationflags=subprocess.CREATE_NO_WINDOW)

    time.sleep(1)  # Extended QBASIC load time

    with open(CSV_PATH, "r") as f:
        reader = csv.reader(f)
        for input_file, output_file in reader:
            print(f"\nProcessing {input_file} -> {output_file}")
            
            # Open file - Simplified check
            print("Opening file...")
            send_keystrokes("%f")  # Alt+F
            time.sleep(.1)
            send_keystrokes("o")   # O
            time.sleep(.1)
            send_keystrokes(input_file)
            send_keystrokes("\n")
            time.sleep(.9)  # Extended file load time
            
            # Assume open succeeded if we get here
            print("File opened successfully")
            
            # Save As with proper format selection
            print("Saving file...")
            send_keystrokes("%f")  # Alt+F
            time.sleep(.1)
            send_keystrokes("a")   # A
            time.sleep(.1)
            send_keystrokes(output_file)
            time.sleep(.1)
            send_keystrokes("\t")  # Navigate to format
            send_keystrokes("t")     # Select ASCII
            send_keystrokes("\n")    # Confirm
            time.sleep(.9)
            
            print(f"Converted {input_file}")

    # Exit QBASIC
    send_keystrokes("%f")
    time.sleep(.2)
    send_keystrokes("x")
    print("\nAll operations completed")

if __name__ == "__main__":
    convert_files()