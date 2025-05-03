import os
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

OS_OPTIONS = {
    "Linux": "Linux_64",
    "Mac OS X": "MacOS_64",
    "Windows 10": "Windows10_64",
    "Windows 7": "Windows7_64"
}

VBOXMANAGE_PATH = r"C:\Program Files\Oracle\VirtualBox\VBoxManage.exe"

def create_vm(name, os_type, memory, cpus, disk_path):
    if not os.path.exists(VBOXMANAGE_PATH):
        messagebox.showerror("Error", f"VBoxManage not found at:\n{VBOXMANAGE_PATH}")
        return

    try:
        subprocess.run(
            [VBOXMANAGE_PATH, "createvm", "--name", name, "--ostype", os_type, "--register"],
            check=True
        )
        subprocess.run(
            [VBOXMANAGE_PATH, "modifyvm", name, "--memory", memory, "--cpus", cpus],
            check=True
        )
        subprocess.run(
            [VBOXMANAGE_PATH, "storagectl", name,
             "--name", "SATA Controller", "--add", "sata", "--controller", "IntelAhci"],
            check=True
        )
        subprocess.run(
            [VBOXMANAGE_PATH, "storageattach", name,
             "--storagectl", "SATA Controller", "--port", "0", "--device", "0",
             "--type", "hdd", "--medium", disk_path],
            check=True
        )
        messagebox.showinfo("Success", f"VM '{name}' created and disk attached:\n{disk_path}")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Failed to create VM:\n{e}")

def browse_disk(var: tk.StringVar):
    path = filedialog.askopenfilename(
        title="Select virtual disk",
        filetypes=[("Virtual Disks", "*.vdi *.vhd *.qcow2 *.vmdk"), ("All files", "*.*")]
    )
    if path:
        var.set(path)

def adjust_var(var: tk.StringVar, delta: int):
    """Increment or decrement an integer StringVar by delta, not going below 1."""
    try:
        val = max(1, int(var.get()) + delta)
    except ValueError:
        val = max(1, delta if delta > 0 else 1)
    var.set(str(val))

def main():
    root = tk.Tk()
    root.title("Virtual Machine Creator")
    # Center window
    W, H = 520, 360
    ws, hs = root.winfo_screenwidth(), root.winfo_screenheight()
    root.geometry(f"{W}x{H}+{(ws-W)//2}+{(hs-H)//2}")
    root.resizable(False, False)
    root.configure(bg="#f0f0f0")

    # Styles
    style = ttk.Style()
    style.configure("TLabel", font=("Segoe UI", 11), background="#f0f0f0")
    style.configure("TEntry", font=("Segoe UI", 11))
    style.configure("TCombobox", font=("Segoe UI", 11))

    frm = tk.Frame(root, bg="#f0f0f0")
    frm.place(relx=0.5, rely=0.5, anchor="center")

    # Grid configuration
    for i in range(3):
        frm.columnconfigure(i, pad=10)

    pady = 8

    # Row 0: VM Name
    ttk.Label(frm, text="VM Name:").grid(row=0, column=0, sticky="e", pady=pady)
    name_entry = ttk.Entry(frm, width=30)
    name_entry.grid(row=0, column=1, columnspan=2, sticky="w", pady=pady)

    # Row 1: Select OS
    ttk.Label(frm, text="Select OS:").grid(row=1, column=0, sticky="e", pady=pady)
    os_var = tk.StringVar(value=list(OS_OPTIONS.keys())[0])
    os_combo = ttk.Combobox(
        frm, textvariable=os_var, values=list(OS_OPTIONS.keys()),
        state="readonly", width=28
    )
    os_combo.grid(row=1, column=1, columnspan=2, sticky="w", pady=pady)

    # Row 2: Memory with +/- buttons
    ttk.Label(frm, text="Memory (MB):").grid(row=2, column=0, sticky="e", pady=pady)
    mem_var = tk.StringVar(value="2048")
    mem_frame = tk.Frame(frm, bg="#f0f0f0")
    mem_frame.grid(row=2, column=1, sticky="w", pady=pady)
    tk.Button(mem_frame, text="–", width=3, command=lambda: adjust_var(mem_var, -256)).pack(side="left")
    ttk.Entry(mem_frame, textvariable=mem_var, width=12, justify="center").pack(side="left", padx=5)
    tk.Button(mem_frame, text="+", width=3, command=lambda: adjust_var(mem_var, 256)).pack(side="left")

    # Row 3: CPUs with +/- buttons
    ttk.Label(frm, text="CPUs:").grid(row=3, column=0, sticky="e", pady=pady)
    cpu_var = tk.StringVar(value="2")
    cpu_frame = tk.Frame(frm, bg="#f0f0f0")
    cpu_frame.grid(row=3, column=1, sticky="w", pady=pady)
    tk.Button(cpu_frame, text="–", width=3, command=lambda: adjust_var(cpu_var, -1)).pack(side="left")
    ttk.Entry(cpu_frame, textvariable=cpu_var, width=12, justify="center").pack(side="left", padx=5)
    tk.Button(cpu_frame, text="+", width=3, command=lambda: adjust_var(cpu_var, 1)).pack(side="left")

    # Row 4: Disk selection
    ttk.Label(frm, text="Disk File:").grid(row=4, column=0, sticky="e", pady=pady)
    disk_var = tk.StringVar()
    ttk.Entry(frm, textvariable=disk_var, width=30).grid(row=4, column=1, sticky="w", pady=pady)
    tk.Button(
        frm, text="Browse…", bg="#2196F3", fg="white",
        command=lambda: browse_disk(disk_var)
    ).grid(row=4, column=2, pady=pady)

    # Row 5: Create VM
    tk.Button(
        frm, text="Create Virtual Machine",
        bg="#4CAF50", fg="white", font=("Segoe UI", 12, "bold"),
        command=lambda: create_vm(
            name_entry.get().strip(),
            OS_OPTIONS.get(os_var.get()),
            mem_var.get().strip(),
            cpu_var.get().strip(),
            disk_var.get().strip()
        )
    ).grid(row=5, column=0, columnspan=3, pady=20)

    root.mainloop()

if __name__ == "__main__":
    main()
