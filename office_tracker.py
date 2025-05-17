
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import xml.etree.ElementTree as ET
from PIL import Image, ImageTk
import os

# Global variables
data = []
current_room_data = {'room_name': '', 'desk_count': 0, 'desks': []}
current_desk_index = 0
is_preview = True
image_cache = {}

def load_from_xml():
    global data
    file_path = filedialog.askopenfilename(
        filetypes=[("XML files", "*.xml")],
        title="Open XML File"
    )
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
            draw_visualization()
        messagebox.showinfo("Loaded", f"Data loaded from {file_path}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load XML: {e}")

# GUI setup
root = tk.Tk()
root.title("Office Equipment Tracker")

main_frame = ttk.Frame(root)
main_frame.grid(row=0, column=0, padx=10, pady=10)

root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

main_frame.columnconfigure(0, weight=0)  # input_frame — nie rośnie
main_frame.columnconfigure(1, weight=1)  # preview_frame — rośnie!
main_frame.rowconfigure(0, weight=1)

preview_frame.columnconfigure(0, weight=1)
preview_frame.rowconfigure(0, weight=1)

input_frame = ttk.Frame(main_frame)
input_frame.grid(row=0, column=0, sticky='nw')

room_frame = ttk.LabelFrame(input_frame, text="Room Setup")
room_frame.grid(row=0, column=0, sticky='ew', pady=5)

root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
main_frame.columnconfigure(1, weight=1)  # To pozwala preview_frame się rozszerzać
main_frame.rowconfigure(0, weight=1)

ttk.Label(room_frame, text="Room Name:").grid(row=0, column=0)
room_name_entry = ttk.Entry(room_frame)
room_name_entry.grid(row=0, column=1)

ttk.Label(room_frame, text="Number of Desks:").grid(row=1, column=0)
desk_count_entry = ttk.Entry(room_frame)
desk_count_entry.grid(row=1, column=1)

ttk.Button(room_frame, text="Start Room", command=lambda: start_room()).grid(row=2, column=0, columnspan=2, pady=5)

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

ttk.Button(input_frame, text="Save Desk", command=lambda: save_desk()).grid(row=2, column=0, pady=5, sticky='ew')
ttk.Button(input_frame, text="Save Room", command=lambda: next_room()).grid(row=3, column=0, pady=5, sticky='ew')
ttk.Button(input_frame, text="Save All", command=lambda: save_all_to_xml()).grid(row=4, column=0, pady=5, sticky='ew')
ttk.Button(input_frame, text="Load from XML", command=load_from_xml).grid(row=5, column=0, pady=5, sticky='ew')
ttk.Button(input_frame, text="Toggle View", command=lambda: toggle_view()).grid(row=6, column=0, pady=5, sticky='ew')

preview_frame = ttk.LabelFrame(main_frame, text="Live Preview")
preview_frame.grid(row=0, column=1, padx=10, sticky='nsew')

preview_text = tk.Text(preview_frame, width=60, height=30)
preview_text.pack(expand=True, fill='both')

canvas = tk.Canvas(preview_frame, width=600, height=500)
canvas.pack_forget()

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

def toggle_view():
    global is_preview
    is_preview = not is_preview
    if is_preview:
        canvas.pack_forget()
        preview_text.pack(expand=True, fill='both')
    else:
        preview_text.pack_forget()
        canvas.pack(expand=True, fill='both')
        draw_visualization()

def load_image(name):
    if name in image_cache:
        return image_cache[name]

    base_dir = os.path.dirname(os.path.abspath(__file__))  # folder, gdzie jest office_tracker.py
    assets_path = os.path.join(base_dir, "assets", name)

    try:
        img = Image.open(assets_path).resize((32, 32))
        tk_img = ImageTk.PhotoImage(img)
        image_cache[name] = tk_img
        return tk_img
    except FileNotFoundError:
        print(f"Image not found: {assets_path}")
        return None

def setup_scrollable_canvas():
    global canvas

    canvas_frame = tk.Frame(preview_frame)
    canvas_frame.grid(row=0, column=0, sticky='nsew')  # <<< ważne

    y_scrollbar = tk.Scrollbar(canvas_frame, orient='vertical')
    y_scrollbar.grid(row=0, column=1, sticky='ns')

    x_scrollbar = tk.Scrollbar(preview_frame, orient='horizontal')
    x_scrollbar.grid(row=1, column=0, sticky='ew')

    canvas = tk.Canvas(
        canvas_frame,
        background='white',
        yscrollcommand=y_scrollbar.set,
        xscrollcommand=x_scrollbar.set
    )
    canvas.grid(row=0, column=0, sticky='nsew')  # <<< ważne

    canvas_frame.columnconfigure(0, weight=1)
    canvas_frame.rowconfigure(0, weight=1)

    y_scrollbar.config(command=canvas.yview)
    x_scrollbar.config(command=canvas.xview)

    canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

def draw_visualization():
    canvas.delete("all")
    x_offset = 20
    y_offset = 20
    current_y = y_offset
    icon_size = 32
    icon_spacing = 3
    icons_per_row = 3
    icon_block = icon_size + icon_spacing
    min_desk_width = 100
    padding = 10
    cols = 4

    for room_index, room in enumerate(data + ([current_room_data] if current_room_data['room_name'] else [])):
        desks = room['desks']
        total_desks = len(desks)
        rows_of_desks = (total_desks + cols - 1) // cols

        desk_sizes = []
        for desk in desks:
            icon_count = int(desk.get('Computer', 0)) + int(desk.get('Docking Station', 0))
            icon_count += int(desk.get('Monitors', 0)) + int(desk.get('Docking Monitors', 0))
            icon_rows = max(1, (icon_count + icons_per_row - 1) // icons_per_row)
            desk_height = icon_rows * icon_block + 30
            desk_width = max(min_desk_width, min(icons_per_row, icon_count) * icon_block + 10)
            desk_sizes.append((desk_width, desk_height, icon_count))

        row_heights = []
        for r in range(rows_of_desks):
            heights = [desk_sizes[i][1] for i in range(r * cols, min((r + 1) * cols, total_desks))]
            row_heights.append(max(heights) if heights else 0)

        row_widths = []
        for r in range(rows_of_desks):
            widths = [desk_sizes[i][0] for i in range(r * cols, min((r + 1) * cols, total_desks))]
            row_widths.append(sum(widths) + padding * (len(widths) + 1))

        room_width = max(row_widths) if row_widths else 550
        room_height = sum(row_heights) + padding * (rows_of_desks + 1) + 30

        x0 = x_offset
        y0 = current_y
        canvas.create_rectangle(x0, y0, x0 + room_width, y0 + room_height, outline="black", width=2)
        canvas.create_text(x0 + room_width // 2, y0 + 10, text=f"Room: {room['room_name']}", anchor='n', font=("Arial", 12, "bold"))

        y_cursor = y0 + 30 + padding
        for r in range(rows_of_desks):
            row_height = row_heights[r]
            dx = x0 + padding
            for c in range(cols):
                desk_index = r * cols + c
                if desk_index >= total_desks:
                    break

                desk = desks[desk_index]
                desk_width, desk_height, icon_count = desk_sizes[desk_index]
                dy = y_cursor

                canvas.create_rectangle(dx, dy, dx + desk_width, dy + desk_height, fill="#f0f0f0", outline="gray")
                canvas.create_text(dx + desk_width // 2, dy + 10, text=f"Desk {desk_index + 1}", font=("Arial", 8, "bold"))

                icons = []
                if desk.get('Computer'):
                    icons.append(load_image("laptop.png"))
                if desk.get('Docking Station'):
                    icons.append(load_image("docking_station.png"))
                for _ in range(desk.get('Monitors', 0)):
                    icons.append(load_image("monitor.png"))
                for _ in range(desk.get('Docking Monitors', 0)):
                    icons.append(load_image("monitor_d.png"))

                x_icon_start = dx + 5
                y_icon = dy + 25
                x_icon = x_icon_start

                for idx, img in enumerate(icons):
                    if img:
                        canvas.create_image(x_icon, y_icon, anchor='nw', image=img)
                        x_icon += icon_block
                        if (idx + 1) % icons_per_row == 0:
                            x_icon = x_icon_start
                            y_icon += icon_block

                dx += desk_width + padding

            y_cursor += row_height + padding

        current_y += room_height + 30


# Kluczowe: aktualizacja obszaru przewijania
canvas.update_idletasks()
canvas.configure(scrollregion=canvas.bbox("all"))

setup_scrollable_canvas()  # <-- DODAJ TO TUTAJ

root.geometry("1000x700")  # lub inny rozmiar, który uważasz za sensowny
root.minsize(800, 600)

root.mainloop()
