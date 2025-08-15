import tkinter as tk
from tkinter import font, simpledialog, scrolledtext
import os
from datetime import datetime

# --- Constants ---
WINDOW_TITLE = "BuJu - Your Digital Journal"
WINDOW_GEOMETRY = "600x700"
APP_FONT = "Helvetica"
FONT_SIZES = {"H1": 22, "P": 18}
COLORS = {"BG": "#fdfdfd", "FG": "#2c3e50", "ACCENT": "#3498db"}

# --- Core Task Symbols ---
TASK = "•"
NOTE = "–"
EVENT = "o"
COMPLETED = "X"

class BuJoApp:
    def __init__(self, root):
        self.root = root
        self.root.title(WINDOW_TITLE)
        self.root.geometry(WINDOW_GEOMETRY)
        self.root.configure(bg=COLORS["BG"])

        # --- Get today's date for the log file ---
        self.today_str = datetime.now().strftime("%Y-%m-%d")
        self.log_filename = f"{self.today_str}.txt"

        # --- Fonts ---
        self.font_h1 = font.Font(family=APP_FONT, size=FONT_SIZES["H1"], weight="bold")
        self.font_p = font.Font(family=APP_FONT, size=FONT_SIZES["P"])

        # --- Build the UI ---
        self.create_widgets()
        
        # --- Load existing data ---
        self.load_log()
        
        # --- Bind window close event to save function ---
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_widgets(self):
        # --- Header Frame ---
        header_frame = tk.Frame(self.root, bg=COLORS["BG"])
        header_frame.pack(pady=10, fill="x", padx=20)
        
        date_label = tk.Label(
            header_frame, 
            text=datetime.now().strftime("%A, %B %d, %Y"), 
            font=self.font_h1, 
            bg=COLORS["BG"], 
            fg=COLORS["FG"]
        )
        date_label.pack()

        # --- Controls Frame ---
        controls_frame = tk.Frame(self.root, bg=COLORS["BG"])
        controls_frame.pack(pady=5, fill="x", padx=20)

        buttons = [
            ("Add Task", lambda: self.add_item(TASK)),
            ("Add Note", lambda: self.add_item(NOTE)),
            ("Add Event", lambda: self.add_item(EVENT))
        ]
        
        for text, command in buttons:
            btn = tk.Button(
                controls_frame, 
                text=text, 
                command=command, 
                font=(APP_FONT, 15), 
                bg=COLORS["ACCENT"], 
                fg="white", 
                activebackground=COLORS["ACCENT"],  # Keep color when active
                activeforeground="white",           # Keep text white when active
                relief="flat", 
                padx=10,
                takefocus=False  # Prevent buttons from taking focus
            )
            btn.pack(side="left", padx=5)

        # --- Main Content Area (ScrolledText with word wrap) ---
        self.text_widget = scrolledtext.ScrolledText(
            self.root,
            font=self.font_p,
            bg="white",
            fg=COLORS["FG"],
            wrap=tk.WORD,  # Enable word wrapping
            borderwidth=0,
            highlightthickness=0,
            padx=10,
            pady=10,
            insertbackground=COLORS["FG"]  # Set cursor color
        )
        self.text_widget.pack(pady=10, padx=20, fill="both", expand=True)
        
        # --- Bind double-click to toggle task state ---
        self.text_widget.bind("<Double-1>", self.toggle_task_state)

    def add_item(self, prefix):
        """Asks user for input and adds a new item to the text widget."""
        item_text = simpledialog.askstring("Input", f"Enter text for your {prefix} item:")
        if item_text:
            self.text_widget.insert(tk.END, f"  {prefix}  {item_text}\n")
            self.text_widget.see(tk.END)  # Scroll to the bottom
            self.text_widget.focus_set()  # Return focus to text widget

    def toggle_task_state(self, event):
        """Toggles a task between open (•) and completed (X) on double-click."""
        try:
            # Get the current cursor position
            cursor_pos = self.text_widget.index(tk.INSERT)
            line_start = cursor_pos.split('.')[0] + '.0'
            line_end = cursor_pos.split('.')[0] + '.end'
            
            # Get the line content
            line_text = self.text_widget.get(line_start, line_end)
            
            if line_text.strip().startswith(TASK):
                new_text = line_text.replace(TASK, COMPLETED, 1)
            elif line_text.strip().startswith(COMPLETED):
                new_text = line_text.replace(COMPLETED, TASK, 1)
            else:
                # It's a note or event, do nothing
                return

            # Replace the line
            self.text_widget.delete(line_start, line_end)
            self.text_widget.insert(line_start, new_text)
        except tk.TclError:
            # Error accessing text widget
            pass

    def save_log(self):
        """Saves the current text widget content to a text file."""
        content = self.text_widget.get("1.0", tk.END)
        with open(self.log_filename, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Log saved to {self.log_filename}")

    def load_log(self):
        """Loads log data from a text file if it exists."""
        if os.path.exists(self.log_filename):
            with open(self.log_filename, "r", encoding="utf-8") as f:
                content = f.read()
                self.text_widget.insert("1.0", content)
            print(f"Log loaded from {self.log_filename}")

    def on_closing(self):
        """Handles the window closing event."""
        self.save_log()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = BuJoApp(root)
    root.mainloop()