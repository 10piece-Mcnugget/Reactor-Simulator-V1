import tkinter as tk
from reactor_physics import Reactor
# import winsound  # For future audio alarm on Windows

root = tk.Tk()
root.title("Reactor Control Room")
root.geometry("1600x1000")

# ============================================================
# OLIVE GREEN BACKGROUND FOR ENTIRE UI
# ============================================================

root.configure(bg="#556B2F")  # Dark olive green industrial panel color



reactor = Reactor("reactor_config.json")


# ============================================================
# STATUS READOUTS
# ============================================================

label_style = {"font": ("Arial", 14), "bg": "#556B2F", "fg": "white"}

power_label = tk.Label(root, text=f"Power: {reactor.power} MW", **label_style)
power_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

rod_label = tk.Label(root, text=f"Rods: {reactor.rod_position} % inserted", **label_style)
rod_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")

coolant_label = tk.Label(root, text=f"Coolant Flow: {reactor.coolant_flow} %", **label_style)
coolant_label.grid(row=2, column=0, padx=10, pady=10, sticky="w")

reactivity_label = tk.Label(root, text=f"Reactivity: {reactor.reactivity:.2f}", **label_style)
reactivity_label.grid(row=3, column=0, padx=10, pady=10, sticky="w")


# ============================================================
# SMALL ALARM LAMP (NO OVERLAY YET)
# ============================================================

alarm_canvas = tk.Canvas(root, width=40, height=40, bg="#556B2F", highlightthickness=0)
alarm_light = alarm_canvas.create_oval(5, 5, 35, 35, fill="green")
alarm_canvas.grid(row=0, column=3, padx=10, pady=10)

alarm_label = tk.Label(root, text="Reactivity Alarm", font=("Arial", 12),
                       bg="#556B2F", fg="white")
alarm_label.grid(row=1, column=3, padx=10, pady=5)

alarm_blink_state = False

def blink_alarm_light():
    """Blink the alarm lamp red when reactivity is too high."""
    global alarm_blink_state
    alarm_blink_state = not alarm_blink_state

    if reactor.reactivity > reactor.max_safe_reactivity:
        # Toggle between red and dark red
        color = "red" if alarm_blink_state else "#8B0000"  # dark red
        alarm_canvas.itemconfig(alarm_light, fill=color)

        # Continue blinking
        root.after(500, blink_alarm_light)
    else:
        # Reset to green when safe
        alarm_canvas.itemconfig(alarm_light, fill="green")

# ============================================================
# ALARM UPDATE LOGIC (NO PULSING YET)
# ============================================================

def update_alarm():
    if reactor.reactivity > reactor.max_safe_reactivity:
        blink_alarm_light()  # <-- START BLINKING
    else:
        alarm_canvas.itemconfig(alarm_light, fill="green")

# ============================================================
# UI UPDATE FUNCTION
# ============================================================

def update_ui():
    power_label.config(text=f"Power: {reactor.power} MW")
    rod_label.config(text=f"Rods: {reactor.rod_position} % inserted")
    coolant_label.config(text=f"Coolant Flow: {reactor.coolant_flow} %")
    reactivity_label.config(text=f"Reactivity: {reactor.reactivity:.2f}")
    update_alarm()

def simulation_loop():
    reactor.tick(0.1)
    update_ui()
    root.after(100,simulation_loop)

# ============================================================
# BUTTON PRESS HANDLER
# ============================================================

def handle_button_press(btn, action):
    btn.config(relief=tk.SUNKEN, bg="lightgray")
    btn.after(150, lambda: btn.config(relief=tk.RAISED, bg="SystemButtonFace"))
    action()
    update_ui()


# ============================================================
# CONTROL RODS SECTION
# ============================================================

frame_style = {"font": ("Arial", 12), "bg": "#556B2F", "fg": "white"}

rod_frame = tk.LabelFrame(root, text="Control Rods", **frame_style)
rod_frame.grid(row=4, column=0, padx=10, pady=10, sticky="nw")

insert_btn = tk.Button(rod_frame, text="Insert Rods", font=("Arial", 12),
                       command=lambda: handle_button_press(insert_btn, reactor.insert_rods))
insert_btn.grid(row=0, column=0, padx=5, pady=5)

withdraw_btn = tk.Button(rod_frame, text="Withdraw Rods", font=("Arial", 12),
                         command=lambda: handle_button_press(withdraw_btn, reactor.withdraw_rods))
withdraw_btn.grid(row=0, column=1, padx=5, pady=5)

scram_btn = tk.Button(rod_frame, text="SCRAM", font=("Arial", 12),
                      fg="white", bg="red",
                      command=lambda: handle_button_press(scram_btn, reactor.scram))
scram_btn.grid(row=1, column=0, columnspan=2, padx=5, pady=5)


# ============================================================
# COOLANT SYSTEM SECTION
# ============================================================

coolant_frame = tk.LabelFrame(root, text="Coolant System", **frame_style)
coolant_frame.grid(row=4, column=1, padx=10, pady=10, sticky="nw")

flow_up_btn = tk.Button(coolant_frame, text="Increase Flow", font=("Arial", 12),
                        command=lambda: handle_button_press(flow_up_btn, reactor.increase_coolant))
flow_up_btn.grid(row=0, column=0, padx=5, pady=5)

flow_down_btn = tk.Button(coolant_frame, text="Decrease Flow", font=("Arial", 12),
                          command=lambda: handle_button_press(flow_down_btn, reactor.decrease_coolant))
flow_down_btn.grid(row=0, column=1, padx=5, pady=5)


# ============================================================
# SAFETY / ALARM SECTION
# ============================================================

safety_frame = tk.LabelFrame(root, text="Safety Systems", **frame_style)
safety_frame.grid(row=4, column=2, padx=10, pady=10, sticky="nw")

alarm_ack_btn = tk.Button(safety_frame, text="Acknowledge Alarm", font=("Arial", 12),
                          command=lambda: handle_button_press(alarm_ack_btn, reactor.scram))
alarm_ack_btn.grid(row=0, column=0, padx=5, pady=5)


# ============================================================
# INITIAL UI UPDATE + MAIN LOOP
# ============================================================


update_ui()
simulation_loop()
root.mainloop()