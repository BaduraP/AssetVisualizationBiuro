import tkinter as tk
from tkinter import ttk
from form_logic import (
    init_state, start_room, save_desk, next_room,
    save_all_to_xml, load_from_xml
)
from preview_logic import (
    setup_preview_frame, toggle_view
)

def build_gui(root):
    root.title("Office Equipment Tracker")
    root.geometry("1100x750")
    root.minsize(950, 600)

    main_frame = ttk.Frame(root)
    main_frame.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    main_frame.columnconfigure(0, weight=0)
    main_frame.columnconfigure(1, weight=1)
    main_frame.rowconfigure(0, weight=1)

    input_frame = ttk.Frame(main_frame)
    input_frame.grid(row=0, column=0, sticky='nw')

    room_frame = ttk.LabelFrame(input_frame, text="Room Setup")
    room_frame.grid(row=0, column=0, sticky='ew', pady=5)

    global room_name_entry, desk_count_entry
    room_name_entry = ttk.Entry(room_frame)
    ttk.Label(room_frame, text="Room Name:").grid(row=0, column=0)
    room_name_entry.grid(row=0, column=1)

    desk_count_entry = ttk.Entry(room_frame)
    ttk.Label(room_frame, text="Number of Desks:").grid(row=1, column=0)
    desk_count_entry.grid(row=1, column=1)

    ttk.Button(room_frame, text="Start Room", command=start_room).grid(row=2, column=0, columnspan=2, pady=5)

    desk_frame = ttk.LabelFrame(input_frame, text="Desk Equipment")
    desk_frame.grid(row=1, column=0, sticky='ew', pady=5)

    computer_var = tk.BooleanVar(root)
    monitors_entry = tk.Entry(desk_frame)
    monitors_entry.insert(0, "0")
    docking_monitors_entry = tk.Entry(desk_frame)
    docking_monitors_entry.insert(0, "0")
    docking_var = tk.BooleanVar(root)
    desk_label = tk.Label(desk_frame)

    init_state(root, desk_frame, desk_label, computer_var, monitors_entry, docking_monitors_entry, docking_var)

    desk_label.config(text="Desk 1")
    desk_label.grid(row=0, column=0, columnspan=2)

    ttk.Checkbutton(desk_frame, text="Computer", variable=computer_var).grid(row=1, column=0, columnspan=2)
    ttk.Label(desk_frame, text="Monitors:").grid(row=2, column=0)
    monitors_entry.grid(row=2, column=1)
    ttk.Label(desk_frame, text="Docking Monitors:").grid(row=3, column=0)
    docking_monitors_entry.grid(row=3, column=1)
    ttk.Checkbutton(desk_frame, text="Docking Station", variable=docking_var).grid(row=4, column=0, columnspan=2)

    ttk.Button(input_frame, text="Save Desk", command=save_desk).grid(row=2, column=0, pady=5, sticky='ew')
    ttk.Button(input_frame, text="Save Room", command=next_room).grid(row=3, column=0, pady=5, sticky='ew')
    ttk.Button(input_frame, text="Save All", command=save_all_to_xml).grid(row=4, column=0, pady=5, sticky='ew')
    ttk.Button(input_frame, text="Load from XML", command=load_from_xml).grid(row=5, column=0, pady=5, sticky='ew')
    ttk.Button(input_frame, text="Toggle View", command=toggle_view).grid(row=6, column=0, pady=5, sticky='ew')

    setup_preview_frame(main_frame)

def get_entries():
    # Delayed import to avoid circular dependency
    import gui
    return gui.room_name_entry, gui.desk_count_entry