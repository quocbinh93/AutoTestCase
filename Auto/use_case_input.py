import tkinter as tk
from tkinter import ttk

use_case_data = None # Biến toàn cục để lưu trữ dữ liệu

def save_use_case(use_case_data):
    with open("use_case.txt", "w", encoding="utf-8") as file:
        for key, value in use_case_data.items():
            file.write(f"{key}: {value}\n")

def get_use_case_input():
    global use_case_data  # Sử dụng biến toàn cục

    use_case_data = {
        label: entry_widgets[label].get("1.0", tk.END) if isinstance(entry_widgets[label], tk.Text) else entry_widgets[label].get()
        for label in labels
    }

    save_use_case(use_case_data)
    window.destroy()  # Đóng cửa sổ sau khi đã lấy dữ liệu

# Create main window
window = tk.Tk()
window.title("Use Case Description Tool")

# Create labels and input fields
labels = ["Name", "Goal", "Actors", "Preconditions", "Postconditions", "Invariants",
        "Main Success Scenario", "Variations", "Extensions", "Included Use Cases"]
entry_widgets = {}
for label in labels:
    label_widget = ttk.Label(window, text=label)
    label_widget.pack()
    if label in ["Main Success Scenario", "Variations", "Extensions"]:
        entry_widget = tk.Text(window, height=5)
    else:
        entry_widget = ttk.Entry(window)
    entry_widget.pack()
    entry_widgets[label] = entry_widget

# Create Save button
save_button = ttk.Button(window, text="Save", command=get_use_case_input)
save_button.pack()

window.mainloop()
