import tkinter as tk
from tkinter import messagebox, filedialog
import xml.etree.ElementTree as ET

data = []
current_room_data = {'room_name': '', 'desk_count': 0, 'desks': []}
current_desk_index = 0

computer_var = None
monitors_entry = None
docking_monitors_entry = None
docking_var = None
desk_label = None
preview_text = None

def init_state(master, desk_frame, label, comp_var, mon_entry, dock_mon_entry, dock_var):
    global computer_var, monitors_entry, docking_monitors_entry, docking_var, desk_label
    computer_var = comp_var
    monitors_entry = mon_entry
    docking_monitors_entry = dock_mon_entry
    docking_var = dock_var
    desk_label = label

def update_preview():
    from preview_logic import preview_text
    preview_text.delete("1.0", tk.END)
    for room in data + ([current_room_data] if current_room_data['room_name'] else []):
        preview_text.insert(tk.END, f"Room: {room['room_name']} (Desks: {room['desk_count']})\n")
        for i, desk in enumerate(room['desks']):
            preview_text.insert(tk.END, f"  Desk {i+1}: {desk}\n")
        preview_text.insert(tk.END, "\n")

def clear_desk_form():
    computer_var.set(False)
    monitors_entry.delete(0, tk.END)
    monitors_entry.insert(0, "0")
    docking_monitors_entry.delete(0, tk.END)
    docking_monitors_entry.insert(0, "0")
    docking_var.set(False)

def start_room():
    global current_desk_index
    room_name_entry, desk_count_entry = get_entries()
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
    current_desk_index = 0
    clear_desk_form()
    desk_label.config(text="Desk 1")
    update_preview()

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

def reset_form():
    global current_room_data, current_desk_index
    current_room_data = {'room_name': '', 'desk_count': 0, 'desks': []}
    current_desk_index = 0
    room_name_entry, desk_count_entry = get_entries()
    room_name_entry.delete(0, tk.END)
    desk_count_entry.delete(0, tk.END)
    clear_desk_form()
    desk_label.config(text="Desk 1")

def save_all_to_xml():
    if not data:
        messagebox.showwarning("Warning", "No data to save.")
        return
    file_path = filedialog.asksaveasfilename(defaultextension=".xml", filetypes=[("XML files", "*.xml")], title="Save XML File")
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

def load_from_xml():
    global data
    from preview_logic import is_preview, draw_visual_preview
    file_path = filedialog.askopenfilename(filetypes=[("XML files", "*.xml")], title="Open XML File")
    if not file_path:
        return
    try:
        tree = ET.parse(file_path)
        root_el = tree.getroot()
        data = []
        for room_el in root_el.findall("Room"):
            room_data = {
                'room_name': room_el.get('name'),
                'desk_count': int(room_el.get('desks')),
                'desks': []
            }
            for desk_el in room_el.findall("Desk"):
                desk_data = {
                    'Computer': desk_el.findtext("Computer") == "True",
                    'Monitors': int(desk_el.findtext("Monitors") or 0),
                    'Docking Monitors': int(desk_el.findtext("Docking_Monitors") or 0),
                    'Docking Station': desk_el.findtext("Docking_Station") == "True"
                }
                room_data['desks'].append(desk_data)
            data.append(room_data)
        update_preview()
        if not is_preview:
            draw_visual_preview()
        messagebox.showinfo("Loaded", f"Data loaded from {file_path}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load XML: {e}")

def get_data():
    return data + ([current_room_data] if current_room_data['room_name'] else [])
