import os
import sys
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
from tracker import Tracker, setup_db
from PIL import Image, ImageTk, ImageFont
import winsound

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

def set_window_icon(window, icon_path):
    icon = ImageTk.PhotoImage(file=icon_path)
    window.wm_iconphoto(True, icon)

class TrackerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Time Tracker")
        self.root.geometry("600x360")
        self.root.minsize(600, 200)
        self.root.configure(bg="white")

        set_window_icon(self.root, resource_path("icons/logo.png"))

        self.custom_font = ImageFont.truetype(resource_path("fonts/Inter-VariableFont_opsz,wght.ttf"), 30)

        main_frame = tk.Frame(self.root, padx=20, pady=15, bg="white")
        main_frame.pack(fill=tk.BOTH, expand=True)

        self.trackers_frame = tk.Frame(main_frame, width=505, height=290, bg="white")
        self.trackers_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.trackers_frame.pack_propagate(False)

        title_frame = tk.Frame(self.trackers_frame, height=45, bg="white")
        title_frame.pack(fill=tk.X)
        title_label = tk.Label(title_frame, text="Time-trackers", font=("Inter", 30, "bold"), bg="white", fg="#37352F")
        title_label.pack(side=tk.LEFT)
        title_frame.pack_propagate(False)

        self.tracker_list_frame = tk.Frame(self.trackers_frame, bg="white")
        self.tracker_list_frame.pack(fill=tk.BOTH, expand=True)

        toolbar_frame = tk.Frame(main_frame, width=35, height=290, bg="white")
        toolbar_frame.pack(side=tk.RIGHT, fill=tk.Y)
        toolbar_frame.pack_propagate(False)

        self.add_icon = ImageTk.PhotoImage(file=resource_path("icons/add_tracker.png"))
        self.edit_icon = ImageTk.PhotoImage(file=resource_path("icons/edit.png"))
        self.delete_icon = ImageTk.PhotoImage(file=resource_path("icons/delete_tracker.png"))
        self.start_icon = ImageTk.PhotoImage(file=resource_path("icons/start.png"))
        self.stop_icon = ImageTk.PhotoImage(file=resource_path("icons/stop.png"))

        self.add_button = tk.Button(toolbar_frame, image=self.add_icon, command=self.add_tracker, bg="white", borderwidth=0)
        self.add_button.pack(pady=0)
        self.edit_button = tk.Button(toolbar_frame, image=self.edit_icon, command=self.edit_tracker, bg="white", borderwidth=0)
        self.edit_button.pack(pady=15)
        self.delete_button = tk.Button(toolbar_frame, image=self.delete_icon, command=self.delete_tracker, bg="white", borderwidth=0)
        self.delete_button.pack(pady=15)

        self.trackers = []
        self.load_trackers()
        self.update_progress()

    def load_trackers(self):
        for widget in self.tracker_list_frame.winfo_children():
            widget.destroy()

        self.trackers = Tracker.get_all_trackers()
        for tracker in self.trackers:
            self.display_tracker(tracker)

    def display_tracker(self, tracker):
        tracker_frame = tk.Frame(self.tracker_list_frame, pady=15, bg="white")
        tracker_frame.pack(fill=tk.X)

        title_label = tk.Label(tracker_frame, text=tracker.title, font=("Inter", 20, "bold"), fg="#37352F", bg="white")
        title_label.pack(side=tk.LEFT)

        progress_frame = tk.Frame(tracker_frame, width=140, height=13, bg="#EDECEC")
        progress_frame.pack(side=tk.LEFT, padx=10)
        progress_frame.pack_propagate(False)

        progress = tracker.completed_hours / tracker.total_hours * 100
        progress_bar = tk.Frame(progress_frame, width=min(progress, 100) * 140 / 100, height=13, bg="#2EAADC")
        progress_bar.pack(side=tk.LEFT)
        tracker.progress_bar = progress_bar

        progress_label = tk.Label(tracker_frame, text=f"{progress:.2f}% | {tracker.formatted_progress()}/{tracker.total_hours} hours", font=("Inter", 10), fg="#37352F", bg="white")
        progress_label.pack(side=tk.LEFT, padx=10)
        tracker.progress_label = progress_label

        button_image = self.stop_icon if tracker.start_time else self.start_icon
        start_stop_button = tk.Button(tracker_frame, image=button_image, command=lambda: self.toggle_timer(tracker), bg="white", borderwidth=0)
        start_stop_button.image = button_image
        start_stop_button.pack(side=tk.LEFT)
        tracker.start_stop_button = start_stop_button

    def add_tracker(self):
        dialog = TrackerDialog(self.root, title="Add Tracker")
        self.root.wait_window(dialog.top)

        if dialog.result:
            title, total_hours = dialog.result
            tracker = Tracker(None, title, total_hours)
            tracker.save_to_db()
            self.load_trackers()

    def edit_tracker(self):
        selected_tracker = self.select_tracker_dialog("Edit Tracker")
        if selected_tracker:
            dialog = TrackerDialog(self.root, title="Edit Tracker", tracker=selected_tracker)
            self.root.wait_window(dialog.top)

            if dialog.result:
                title, total_hours = dialog.result
                selected_tracker.title = title
                selected_tracker.total_hours = total_hours
                selected_tracker.update_db()
                self.load_trackers()

    def delete_tracker(self):
        selected_tracker = self.select_tracker_dialog("Delete Tracker")
        if selected_tracker:
            if messagebox.askyesno("Delete Tracker", f"Are you sure you want to delete '{selected_tracker.title}'?"):
                selected_tracker.delete_from_db()
                self.load_trackers()

    def select_tracker_dialog(self, title):
        dialog = SelectTrackerDialog(self.root, title=title, trackers=self.trackers)
        self.root.wait_window(dialog.top)

        if dialog.result:
            return dialog.result
        return None

    def toggle_timer(self, tracker):
        if tracker.start_time:
            tracker.stop_timer()
        else:
            tracker.start_timer()
        self.update_tracker_display(tracker)

    def update_tracker_display(self, tracker):
        progress = tracker.completed_hours / tracker.total_hours * 100
        tracker.progress_bar.config(width=min(progress, 100) * 140 / 100)
        tracker.progress_label.config(text=f"{progress:.2f}% | {tracker.formatted_progress()}/{tracker.total_hours} hours")
        if progress >= 100:
            tracker.stop_timer()
            self.congrats()
        tracker.start_stop_button.config(image=self.stop_icon if tracker.start_time else self.start_icon)

    def update_progress(self):
        for tracker in self.trackers:
            if tracker.start_time:
                tracker.stop_timer()
                tracker.start_timer()
                self.update_tracker_display(tracker)
        self.root.after(1000, self.update_progress)

    def congrats(self):
        winsound.PlaySound(resource_path("win.wav"), winsound.SND_FILENAME)

class TrackerDialog:
    def __init__(self, parent, title, tracker=None):
        self.top = tk.Toplevel(parent)
        self.top.title(title)
        self.top.geometry("400x250")
        self.top.configure(bg="white")
        self.top.grab_set()

        self.result = None

        self.label_font = ("Inter", 12, "bold")
        self.entry_font = ("Inter", 12)

        title_label = tk.Label(self.top, text="Title:", font=self.label_font, bg="white", fg="#37352F")
        title_label.pack(pady=(20, 5))

        entry_frame = tk.Frame(self.top, bg="white", highlightbackground="grey", highlightcolor="#37352F", highlightthickness=1)
        entry_frame.pack(pady=5)

        self.title_entry = tk.Entry(entry_frame, font=self.entry_font, width=28, relief=tk.FLAT, borderwidth=0)
        self.title_entry.pack(padx=1, pady=1)
        self.title_entry.insert(0, tracker.title if tracker else "")

        total_hours_label = tk.Label(self.top, text="Total Hours:", font=self.label_font, bg="white", fg="#37352F")
        total_hours_label.pack(pady=5)

        entry_frame = tk.Frame(self.top, bg="white", highlightbackground="grey", highlightcolor="#37352F", highlightthickness=1)
        entry_frame.pack(pady=5)

        self.total_hours_entry = tk.Entry(entry_frame, font=self.entry_font, width=28, relief=tk.FLAT, borderwidth=0)
        self.total_hours_entry.pack(padx=1, pady=1)
        self.total_hours_entry.insert(0, tracker.total_hours if tracker else "")

        button_frame = tk.Frame(self.top, bg="white")
        button_frame.pack(pady=(20, 10))

        ok_button = tk.Button(button_frame, text="OK", command=self.on_ok, font=self.label_font, bg="white", fg="#2EAADC", relief=tk.FLAT,borderwidth=1)
        ok_button.pack(side=tk.LEFT, padx=10)

        cancel_button = tk.Button(button_frame, text="Cancel", command=self.top.destroy, font=self.label_font, bg="white", fg="#37352F", relief=tk.FLAT, borderwidth=1)
        cancel_button.pack(side=tk.LEFT, padx=10)

    def on_ok(self):
        title = self.title_entry.get()
        total_hours = self.total_hours_entry.get()

        if title and total_hours:
            try:
                total_hours = float(total_hours)
                self.result = (title, total_hours)
                self.top.destroy()
            except ValueError:
                messagebox.showerror("Invalid Input", "Total Hours must be a number.")
        else:
            messagebox.showerror("Invalid Input", "All fields must be filled out.")

class SelectTrackerDialog:
    def __init__(self, parent, title, trackers):
        self.top = tk.Toplevel(parent)
        self.top.title(title)
        self.top.geometry("400x200")
        self.top.configure(bg="white")
        self.top.grab_set()

        self.result = None

        self.label_font = ("Inter", 12, "bold")
        self.entry_font = ("Inter", 12)

        title_label = tk.Label(self.top, text="Select Tracker:", font=self.label_font, bg="white", fg="#37352F")
        title_label.pack(pady=(20, 5))

        self.tracker_var = tk.StringVar(value=trackers[0].title if trackers else "")
        self.tracker_menu = ttk.Combobox(self.top, textvariable=self.tracker_var, values=[tracker.title for tracker in trackers], font=self.entry_font)
        self.tracker_menu.pack(pady=5)

        button_frame = tk.Frame(self.top, bg="white")
        button_frame.pack(pady=(20, 10))

        ok_button = tk.Button(button_frame, text="OK", command=self.on_ok, font=self.label_font, bg="white", fg="#2EAADC", relief=tk.FLAT,borderwidth=1)
        ok_button.pack(side=tk.LEFT, padx=10)

        cancel_button = tk.Button(button_frame, text="Cancel", command=self.top.destroy, font=self.label_font, bg="white", fg="#37352F", relief=tk.FLAT, borderwidth=1)
        cancel_button.pack(side=tk.LEFT, padx=10)

    def on_ok(self):
        selected_title = self.tracker_var.get()
        for tracker in app.trackers:
            if tracker.title == selected_title:
                self.result = tracker
                break
        self.top.destroy()

if __name__ == "__main__":
    try:
        setup_db()
        root = tk.Tk()
        app = TrackerGUI(root)
        print("GUI Initialized")
        root.mainloop()
    except Exception as e:
        print(f"Error: {e}")

