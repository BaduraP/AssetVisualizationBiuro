import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import xml.etree.ElementTree as ET
from PIL import Image, ImageTk
import os

data = []
current_room_data = {'room_name': '', 'desk_count': 0, 'desks': []}
current_desk_index = 0
is_preview = True
loaded_images = {}

computer_var = None
monitors_entry = None
docking_monitors_entry = None
docking_var = None
desk_label = None
preview_text = None
canvas = None
canvas_frame = None
canvas_scrollbar = None


def init_state(master, desk_frame, label, comp_var, mon_entry, dock_mon_entry, dock_var):
    global computer_var, monitors_entry, docking_monitors_entry, docking_var, desk_label
    computer_var = comp_var
    monitors_entry = mon_entry
    docking_monitors_entry = dock_mon_entry
    docking_var = dock_var
    desk_label = label


def preload_images():
    global loaded_images
    base_path = os.path.dirname(os.path.abspath(__file__))  # ← to jest klucz
    icons = ["Laptop.png", "Monitor.png", "Monitor_d.png", "Docking_station.png"]
    for name in icons:
        path = os.path.join(base_path, "assets", name)
        if os.path.exists(path):
            img = Image.open(path).convert("RGBA").resize((32, 32))
            loaded_images[name] = ImageTk.PhotoImage(img)
        else:
            print(f"Image not found: {path}")


def setup_preview_frame(parent):
    global preview_text, canvas, canvas_frame, canvas_scrollbar
    preview_frame = ttk.LabelFrame(parent, text="Live Preview")
    preview_frame.grid(row=0, column=1, padx=10, pady=10, sticky='nsew')
    preview_frame.columnconfigure(0, weight=1)
    preview_frame.rowconfigure(0, weight=1)

    preview_text = tk.Text(preview_frame)
    preview_text.grid(row=0, column=0, sticky='nsew')

    canvas_frame = tk.Frame(preview_frame)
    canvas_frame.grid(row=0, column=0, sticky='nsew')
    canvas_frame.grid_remove()

    canvas = tk.Canvas(canvas_frame, background="white")
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    canvas_scrollbar = tk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=canvas.yview)
    canvas_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    canvas.configure(yscrollcommand=canvas_scrollbar.set)

    canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    canvas.bind_all("<MouseWheel>", _on_mousewheel)
    canvas.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
    canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))

    preload_images()


def toggle_view():
    global is_preview
    is_preview = not is_preview
    if is_preview:
        canvas_frame.grid_remove()
        preview_text.grid()
    else:
        preview_text.grid_remove()
        canvas_frame.grid()
        draw_visual_preview()


def draw_visual_preview():
    global canvas, loaded_images
    if not canvas:
        return
    canvas.delete("all")
    canvas.image_refs = []  # Keep image references alive

    room_padding = 20
    desk_width, desk_height = 110, 110
    desk_margin = 20
    icon_size = 32
    max_desks_per_row = 6

    current_y = room_padding



    for room in data:
        canvas.create_text(room_padding, current_y, anchor="nw",
                           text=f"Room: {room['room_name']}", font=("Arial", 14, "bold"))
        current_y += 30

        num_desks = len(room['desks'])
        rows = (num_desks - 1) // max_desks_per_row + 1
        room_height = max(1, rows) * (desk_height + desk_margin)

        canvas.create_rectangle(room_padding - 10, current_y - 10,
                                room_padding + max_desks_per_row * (desk_width + desk_margin) - desk_margin,
                                current_y + room_height + 10,
                                outline="black", fill="#f5f5f5")

        for i, desk in enumerate(room['desks']):
            col = i % max_desks_per_row
            row = i // max_desks_per_row

            dx = room_padding + col * (desk_width + desk_margin)
            dy = current_y + row * (desk_height + desk_margin)

            canvas.create_rectangle(dx, dy, dx + desk_width, dy + desk_height,
                                    outline="black", fill="lightgray")
            icon_x = dx + 10
            icon_y = dy + 10

            icons = []
            if desk['Computer']:
                img = loaded_images.get("Laptop.png")
                if img:
                    icons.append(img)

            for _ in range(desk['Monitors']):
                img = loaded_images.get("Monitor.png")
                if img:
                    icons.append(img)

            for _ in range(desk['Docking Monitors']):
                img = loaded_images.get("Monitor_d.png")
                if img:
                    icons.append(img)

            if desk['Docking Station']:
                img = loaded_images.get("Docking_station.png")
                if img:
                    icons.append(img)

            for idx, img in enumerate(icons):
                row_offset = idx // 3
                col_offset = idx % 3
                img_x = icon_x + col_offset * (icon_size + 2)
                img_y = icon_y + row_offset * (icon_size + 2)
                canvas.create_image(img_x, img_y, anchor="nw", image=img)
                canvas.image_refs.append(img)

        current_y += room_height + 50

def update_preview():
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
    from gui import get_entries
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
    global current_desk_index
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
    from gui import get_entries
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