import os
import subprocess
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import ctypes
import sys

# Check for admin privileges
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

# Path to VBoxManage — adjust this if needed
VBOXMANAGE_PATH = r"C:\Program Files\Oracle\VirtualBox\VBoxManage.exe"

def create_vhd(vhd_path: str, size_mb: int, variant: str):
    full_path = os.path.abspath(vhd_path)
    full_path_q = f'"{full_path}"'
    label_name = os.path.splitext(os.path.basename(vhd_path))[0]
    disk_type = "fixed" if variant == "Fixed-Size" else "expandable"

    os.makedirs(os.path.dirname(full_path), exist_ok=True)

    script = f'''
create vdisk file={full_path_q} maximum={size_mb} type={disk_type}
select vdisk file={full_path_q}
attach vdisk
create partition primary
format fs=ntfs label="{label_name}" quick
assign
exit
'''
    tmp = os.path.join(os.getenv("TEMP"), "dp_script.txt")
    with open(tmp, "w") as f:
        f.write(script)

    try:
        subprocess.run(["diskpart", "/s", tmp], check=True)
    finally:
        os.remove(tmp)

def create_vbox_disk(path: str, size_mb: int, fmt: str, variant: str):
    if not os.path.exists(VBOXMANAGE_PATH):
        raise FileNotFoundError(f"VBoxManage.exe not found:\n{VBOXMANAGE_PATH}")

    os.makedirs(os.path.dirname(path), exist_ok=True)
    var_arg = "Fixed" if variant == "Fixed-Size" else "Standard"

    subprocess.run([
        VBOXMANAGE_PATH, "createhd",
        "--filename", path,
        "--size", str(size_mb),
        "--format", fmt,
        "--variant", var_arg
    ], check=True)

def create_disk(path: str, size_gb: float, fmt: str, variant: str):
    size_mb = int(size_gb * 1024)

    if fmt == "VHD":
        create_vhd(path, size_mb, variant)
    else:  # VDI or VMDK
        create_vbox_disk(path, size_mb, fmt, variant)

def browse_path(entry, fmt_combo):
    ext_map = {"VDI": "vdi", "VHD": "vhd", "VMDK": "vmdk"}
    ext = ext_map.get(fmt_combo.get(), "")
    file_path = filedialog.asksaveasfilename(
        defaultextension=f".{ext}",
        filetypes=[(f"{ext.upper()} files", f"*.{ext}"), ("All files", "*.*")]
    )
    if file_path:
        entry.delete(0, tk.END)
        entry.insert(0, file_path)

def on_create(path_e, size_e, fmt_c, var_c):
    p = path_e.get().strip()
    s = size_e.get().strip()
    f = fmt_c.get().strip()
    v = var_c.get().strip()

    if not p or not s or not f or not v:
        messagebox.showwarning("Missing Information", "Please fill in all fields.")
        return

    try:
        gb = float(s)
        create_disk(p, gb, f, v)
        messagebox.showinfo("Success", f"{f} disk ({v}) created:\n{p}")
    except ValueError:
        messagebox.showerror("Invalid Size", "Size must be a number (e.g., 0.5, 1.0).")
    except FileNotFoundError as fnf:
        messagebox.showerror("Error", str(fnf))
    except subprocess.CalledProcessError as cpe:
        messagebox.showerror("Disk Creation Failed", str(cpe))
    except Exception as e:
        messagebox.showerror("Error", str(e))

def run_gui():
    root = tk.Tk()
    root.title("Virtual Disk Creator")
    root.geometry("520x260")
    root.resizable(False, False)

    # --- Disk File Path ---
    ttk.Label(root, text="Disk File Path:").place(x=10, y=10)
    path_e = ttk.Entry(root, width=50)
    path_e.place(x=130, y=10)
    ttk.Button(root, text="Browse…",
               command=lambda: browse_path(path_e, fmt_c)).place(x=430, y=8)

    # --- Size in GB ---
    ttk.Label(root, text="Size (GB):").place(x=10, y=50)
    size_e = ttk.Entry(root, width=20)
    size_e.insert(0, "1")
    size_e.place(x=130, y=50)

    # --- Format ---
    ttk.Label(root, text="Format:").place(x=10, y=90)
    fmt_c = ttk.Combobox(root, values=["VDI", "VHD", "VMDK"], state="readonly", width=17)
    fmt_c.set("VDI")
    fmt_c.place(x=130, y=90)

    # --- Type ---
    ttk.Label(root, text="Type:").place(x=10, y=130)
    var_c = ttk.Combobox(root, values=["Fixed-Size", "Dynamic-Size"], state="readonly", width=17)
    var_c.set("Dynamic-Size")
    var_c.place(x=130, y=130)

    # --- Create Button ---
    ttk.Button(root, text="Create Disk", command=lambda: on_create(path_e, size_e, fmt_c, var_c))\
        .place(x=220, y=180)

    root.mainloop()

if __name__ == "__main__":
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, __file__, None, 1
        )
    else:
        run_gui()

