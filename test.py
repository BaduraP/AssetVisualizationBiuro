import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import xml.etree.ElementTree as ET

data = []
current_room_data = {'room_name': '', 'desk_count': 0, 'desks': []}
current_desk_index = 0

def update_preview():
    preview_text.delete("1.0", tk.END)
    for room in data + ([current_room_data] if current_room_data['room_name'] else []):
        preview_text.insert(tk.END, f"Room: {room['room_name']} (Desks: {room['desk_count']})\n")
        for i, desk in enumerate(room['desks']):
            preview_text.insert(tk.END, f"  Desk {i+1}: {desk}\n")
        preview_text.insert(tk.END, "\n")

def save_desk():
    global current_desk_index

    try:
        desk = {
            'Computer': computer_var.get(),
            'Monitors': int(monitors_entry.get()),
            'Docking Monitors': int(docking_monitors_entry.get()),
            'Docking Station': docking_var.get()
        }
    except ValueError:
        messagebox.showerror("Error", "Enter valid numbers for monitors.")
        return

    if current_desk_index < current_room_data['desk_count']:
        current_room_data['desks'].append(desk)
        current_desk_index += 1
        update_preview()

    if current_desk_index >= current_room_data['desk_count']:
        clear_desk_form()
        desk_label.config(text=f"Desk {current_desk_index} (Completed)")
        messagebox.showinfo("Info", "All desks added. Press 'Next Room' or 'Save Room'.")
    else:
        clear_desk_form()
        desk_label.config(text=f"Desk {current_desk_index + 1}")

def next_room():
    global current_room_data, current_desk_index
    if len(current_room_data['desks']) < current_room_data['desk_count']:
        messagebox.showwarning("Warning", "Not all desks filled.")
        return

    data.append(current_room_data.copy())
    reset_form()
    update_preview()

def start_room():
    name = room_name_entry.get().strip()
    try:
        count = int(desk_count_entry.get())
    except ValueError:
        messagebox.showerror("Error", "Desk count must be a number.")
        return
    if not name or count < 1:
        messagebox.showerror("Error", "Invalid room name or desk count.")
        return
    current_room_data['room_name'] = name
    current_room_data['desk_count'] = count
    current_room_data['desks'] = []
    global current_desk_index
    current_desk_index = 0
    clear_desk_form()
    desk_label.config(text="Desk 1")
    update_preview()

def reset_form():
    global current_room_data, current_desk_index
    current_room_data = {'room_name': '', 'desk_count': 0, 'desks': []}
    current_desk_index = 0
    room_name_entry.delete(0, tk.END)
    desk_count_entry.delete(0, tk.END)
    clear_desk_form()
    desk_label.config(text="Desk 1")

def clear_desk_form():
    computer_var.set(False)
    monitors_entry.delete(0, tk.END)
    monitors_entry.insert(0, "0")
    docking_monitors_entry.delete(0, tk.END)
    docking_monitors_entry.insert(0, "0")
    docking_var.set(False)

def save_all_to_xml():
    if not data:
        messagebox.showwarning("Warning", "No data to save.")
        return

    file_path = filedialog.asksaveasfilename(
        defaultextension=".xml",
        filetypes=[("XML files", "*.xml")],
        title="Save XML File"
    )
    if not file_path:
        return

    root = ET.Element("OfficeData")
    for room in data:
        room_el = ET.SubElement(root, "Room", name=room['room_name'], desks=str(room['desk_count']))
        for desk in room['desks']:
            desk_el = ET.SubElement(room_el, "Desk")
            for key, val in desk.items():
                ET.SubElement(desk_el, key.replace(" ", "_")).text = str(val)

    tree = ET.ElementTree(root)
    tree.write(file_path)
    messagebox.showinfo("Saved", f"Data saved to {file_path}")

# --- GUI ---
root = tk.Tk()
root.title("Office Equipment Tracker")

main_frame = ttk.Frame(root)
main_frame.grid(row=0, column=0, padx=10, pady=10)

# Left: Input
input_frame = ttk.Frame(main_frame)
input_frame.grid(row=0, column=0, sticky='nw')

# Room setup
room_frame = ttk.LabelFrame(input_frame, text="Room Setup")
room_frame.grid(row=0, column=0, sticky='ew', pady=5)

ttk.Label(room_frame, text="Room Name:").grid(row=0, column=0)
room_name_entry = ttk.Entry(room_frame)
room_name_entry.grid(row=0, column=1)

ttk.Label(room_frame, text="Number of Desks:").grid(row=1, column=0)
desk_count_entry = ttk.Entry(room_frame)
desk_count_entry.grid(row=1, column=1)

ttk.Button(room_frame, text="Start Room", command=start_room).grid(row=2, column=0, columnspan=2, pady=5)

# Desk info
desk_frame = ttk.LabelFrame(input_frame, text="Desk Equipment")
desk_frame.grid(row=1, column=0, sticky='ew', pady=5)

desk_label = ttk.Label(desk_frame, text="Desk 1")
desk_label.grid(row=0, column=0, columnspan=2)

computer_var = tk.BooleanVar()
ttk.Checkbutton(desk_frame, text="Computer", variable=computer_var).grid(row=1, column=0, columnspan=2)

ttk.Label(desk_frame, text="Monitors:").grid(row=2, column=0)
monitors_entry = ttk.Entry(desk_frame)
monitors_entry.insert(0, "0")
monitors_entry.grid(row=2, column=1)

ttk.Label(desk_frame, text="Docking Monitors:").grid(row=3, column=0)
docking_monitors_entry = ttk.Entry(desk_frame)
docking_monitors_entry.insert(0, "0")
docking_monitors_entry.grid(row=3, column=1)

docking_var = tk.BooleanVar()
ttk.Checkbutton(desk_frame, text="Docking Station", variable=docking_var).grid(row=4, column=0, columnspan=2)

# Buttons
ttk.Button(input_frame, text="Save Desk", command=save_desk).grid(row=2, column=0, pady=5, sticky='ew')
ttk.Button(input_frame, text="Save Room", command=next_room).grid(row=3, column=0, pady=5, sticky='ew')
ttk.Button(input_frame, text="Save All", command=save_all_to_xml).grid(row=4, column=0, pady=5, sticky='ew')

# Right: Preview
preview_frame = ttk.LabelFrame(main_frame, text="Live Preview")
preview_frame.grid(row=0, column=1, padx=10, sticky='nsew')

preview_text = tk.Text(preview_frame, width=60, height=30)
preview_text.pack(expand=True, fill='both')

root.mainloop()
