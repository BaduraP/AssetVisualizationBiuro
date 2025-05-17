
def draw_visualization():
    canvas.delete("all")
    x_offset = 20
    y_offset = 20
    room_spacing = 200
    icon_size = 32
    icon_spacing = 3
    icons_per_row = 3
    icon_block = icon_size + icon_spacing
    min_desk_width = 100
    desk_height = 80
    padding = 10

    for room_index, room in enumerate(data + ([current_room_data] if current_room_data['room_name'] else [])):
        x0 = x_offset
        y0 = y_offset + room_index * room_spacing
        canvas.create_rectangle(x0, y0, x0 + 550, y0 + 150, outline="black", width=2)
        canvas.create_text(x0 + 275, y0 + 10, text=f"Room: {room['room_name']}", anchor='n', font=("Arial", 12, "bold"))

        desks = room['desks']
        cols = 5

        for i, desk in enumerate(desks):
            icons = []

            if desk.get('Computer'):
                icons.append(load_image("laptop.png"))
            if desk.get('Docking Station'):
                icons.append(load_image("docking_station.png"))
            for _ in range(desk.get('Monitors', 0)):
                icons.append(load_image("monitor.png"))
            for _ in range(desk.get('Docking Monitors', 0)):
                icons.append(load_image("monitor_d.png"))

            icon_count = len(icons)
            rows = max(1, (icon_count + icons_per_row - 1) // icons_per_row)
            needed_width = max(min_desk_width, min(icons_per_row, icon_count) * icon_block + 10)
            desk_width = needed_width
            row = i // cols
            col = i % cols
            dx = x0 + padding + col * (desk_width + padding)
            dy = y0 + 30 + row * (desk_height + padding)

            canvas.create_rectangle(dx, dy, dx + desk_width, dy + desk_height, fill="#f0f0f0", outline="gray")
            canvas.create_text(dx + desk_width // 2, dy + 10, text=f"Desk {i+1}", font=("Arial", 8, "bold"))

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
