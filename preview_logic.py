import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
from form_logic import get_data

preview_text = None
canvas = None
canvas_frame = None
canvas_scrollbar = None
is_preview = True
loaded_images = {}

def preload_images():
    global loaded_images
    base_path = os.path.dirname(os.path.abspath(__file__))
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

    canvas = tk.Canvas(canvas_frame, background="white", scrollregion=(0, 0, 3000, 2000))
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
    canvas.image_refs = []

    room_padding = 20
    desk_width, desk_height = 110, 110
    desk_margin = 20
    icon_size = 32
    max_desks_per_row = 6

    current_y = room_padding

    room_data = get_data()
    for room in room_data:
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

            num_icons = len(icons)
            icons_per_row = 3
            rows = (num_icons - 1) // icons_per_row + 1 if num_icons > 0 else 1
            cols = min(num_icons, icons_per_row)

            icon_area_width = cols * (icon_size + 2)
            icon_area_height = rows * (icon_size + 2)

            icon_x = dx + (desk_width - icon_area_width) // 2
            icon_y = dy + (desk_height - icon_area_height) // 2

            for idx, img in enumerate(icons):
                row_offset = idx // icons_per_row
                col_offset = idx % icons_per_row
                img_x = icon_x + col_offset * (icon_size + 2)
                img_y = icon_y + row_offset * (icon_size + 2)
                canvas.create_image(img_x, img_y, anchor="nw", image=img)
                canvas.image_refs.append(img)

        current_y += room_height + 50