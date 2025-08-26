import tkinter as tk
from tkinter import font, simpledialog, scrolledtext
import os
import json
from datetime import datetime

# --- Constants ---
WINDOW_TITLE = "BuJu - Your Digital Journal"
WINDOW_GEOMETRY = "600x700"
APP_FONT = "Helvetica"
FONT_SIZES = {"H1": 22, "P": 18}

# --- Themes ---
# Each theme provides background, foreground, and accent colors
THEMES = {
    "Light": {"BG": "#fdfdfd", "FG": "#2c3e50", "ACCENT": "#3498db", "TEXT_BG": "#ffffff"},
    "Dark": {"BG": "#1f2933", "FG": "#e5e7eb", "ACCENT": "#10b981", "TEXT_BG": "#111827"},
    "Solarized": {"BG": "#fdf6e3", "FG": "#586e75", "ACCENT": "#b58900", "TEXT_BG": "#fffdf5"},
    "Forest": {"BG": "#0b3d2e", "FG": "#e6f4ea", "ACCENT": "#2ecc71", "TEXT_BG": "#052e22"},
}
DEFAULT_THEME_NAME = "Light"
SETTINGS_FILENAME = "buju_settings.json"

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
        # --- Theme state ---
        self.theme_name = DEFAULT_THEME_NAME
        self.colors = THEMES[self.theme_name].copy()
        # Load saved settings (may update theme and window)
        self._settings = {"theme_name": self.theme_name}
        self.load_settings()
        # Restore window size/position/state if available
        saved_window = self._settings.get("window", {})
        width = saved_window.get("width")
        height = saved_window.get("height")
        pos_x = saved_window.get("x")
        pos_y = saved_window.get("y")
        fullscreen = saved_window.get("fullscreen", False)
        zoomed = saved_window.get("zoomed", False)
        try:
            if isinstance(width, int) and isinstance(height, int) and width > 200 and height > 200:
                if isinstance(pos_x, int) and isinstance(pos_y, int):
                    self.root.geometry(f"{width}x{height}+{pos_x}+{pos_y}")
                else:
                    self.root.geometry(f"{width}x{height}")
            # Apply fullscreen/zoomed state last
            if isinstance(fullscreen, bool) and fullscreen:
                try:
                    self.root.attributes("-fullscreen", True)
                except tk.TclError:
                    pass
            elif isinstance(zoomed, bool) and zoomed:
                try:
                    self.root.state('zoomed')
                except tk.TclError:
                    pass
        except tk.TclError:
            pass
        self.root.configure(bg=self.colors["BG"])

        # --- Get today's date for the log file ---
        self.today_str = datetime.now().strftime("%Y-%m-%d")
        self.log_filename = f"{self.today_str}.txt"

        # --- Fonts ---
        self.font_h1 = font.Font(family=APP_FONT, size=FONT_SIZES["H1"], weight="bold")
        self.font_p = font.Font(family=APP_FONT, size=FONT_SIZES["P"])

        # --- Build the UI ---
        self.create_widgets()
        self.build_menu()
        
        # --- Load existing data ---
        self.load_log()
        
        # --- Bind window close event to save function ---
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_widgets(self):
        # --- Header Frame ---
        self.header_frame = tk.Frame(self.root, bg=self.colors["BG"])
        self.header_frame.pack(pady=10, fill="x", padx=20)
        
        self.date_label = tk.Label(
            self.header_frame, 
            text=datetime.now().strftime("%A, %B %d, %Y"), 
            font=self.font_h1, 
            bg=self.colors["BG"], 
            fg=self.colors["FG"]
        )
        self.date_label.pack()

        # --- Controls Frame ---
        self.controls_frame = tk.Frame(self.root, bg=self.colors["BG"])
        self.controls_frame.pack(pady=5, fill="x", padx=20)

        buttons = [
            ("Add Task", lambda: self.add_item(TASK)),
            ("Add Note", lambda: self.add_item(NOTE)),
            ("Add Event", lambda: self.add_item(EVENT))
        ]
        
        self.action_buttons = []
        for text, command in buttons:
            btn = tk.Button(
                self.controls_frame, 
                text=text, 
                command=command, 
                font=(APP_FONT, 15), 
                bg=self.colors["ACCENT"], 
                fg="white", 
                activebackground=self.colors["ACCENT"],
                activeforeground="white",
                relief="flat", 
                padx=10,
                takefocus=False
            )
            btn.pack(side="left", padx=5)
            self.action_buttons.append(btn)

        # --- Main Content Area (ScrolledText with word wrap) ---
        self.text_widget = scrolledtext.ScrolledText(
            self.root,
            font=self.font_p,
            bg=self.colors["TEXT_BG"],
            fg=self.colors["FG"],
            wrap=tk.WORD,  # Enable word wrapping
            borderwidth=0,
            highlightthickness=0,
            padx=10,
            pady=10,
            insertbackground=self.colors["FG"]
        )
        self.text_widget.pack(pady=10, padx=20, fill="both", expand=True)
        
        # --- Bind double-click to toggle task state ---
        self.text_widget.bind("<Double-1>", self.toggle_task_state)

    def build_menu(self):
        menubar = tk.Menu(self.root)
        # Theme menu
        theme_menu = tk.Menu(menubar, tearoff=0)
        for theme_name in THEMES.keys():
            theme_menu.add_command(label=theme_name, command=lambda n=theme_name: self.set_theme(n))
        menubar.add_cascade(label="Theme", menu=theme_menu)
        self.root.config(menu=menubar)

    def set_theme(self, theme_name: str):
        if theme_name not in THEMES:
            return
        self.theme_name = theme_name
        self.colors = THEMES[self.theme_name].copy()
        self.apply_theme()
        self.save_settings()

    def apply_theme(self):
        # Window background
        self.root.configure(bg=self.colors["BG"])

        # Header
        self.header_frame.configure(bg=self.colors["BG"])
        self.date_label.configure(bg=self.colors["BG"], fg=self.colors["FG"])

        # Controls and buttons
        self.controls_frame.configure(bg=self.colors["BG"])
        for btn in self.action_buttons:
            btn.configure(bg=self.colors["ACCENT"], activebackground=self.colors["ACCENT"], fg="white", activeforeground="white")

        # Text area and its colors
        self.text_widget.configure(bg=self.colors["TEXT_BG"], fg=self.colors["FG"], insertbackground=self.colors["FG"])

    def settings_path(self) -> str:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_dir, SETTINGS_FILENAME)

    def load_settings(self):
        try:
            with open(self.settings_path(), "r", encoding="utf-8") as f:
                data = json.load(f)
            saved_theme = data.get("theme_name")
            if saved_theme in THEMES:
                self.theme_name = saved_theme
                self.colors = THEMES[self.theme_name].copy()
            if isinstance(data, dict):
                self._settings.update(data)
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            # Use defaults if settings missing or invalid
            pass

    def save_settings(self):
        try:
            # Merge current runtime settings
            self._settings["theme_name"] = self.theme_name
            # Update window metrics
            w, h, x, y = self.get_current_window_metrics()
            fullscreen = self.get_fullscreen_state()
            zoomed = self.get_zoomed_state()
            window_payload = {}
            if w is not None and h is not None:
                window_payload.update({"width": w, "height": h})
            if x is not None and y is not None:
                window_payload.update({"x": x, "y": y})
            window_payload.update({"fullscreen": fullscreen, "zoomed": zoomed})
            self._settings["window"] = window_payload
            with open(self.settings_path(), "w", encoding="utf-8") as f:
                json.dump(self._settings, f)
        except OSError:
            # Ignore write errors silently
            pass

    def get_current_window_metrics(self):
        try:
            self.root.update_idletasks()
            geo = self.root.winfo_geometry()  # e.g., "600x700+100+100"
            parts = geo.split("+")
            size_part = parts[0]
            w_str, h_str = size_part.split("x")
            w = int(w_str)
            h = int(h_str)
            x = int(parts[1]) if len(parts) > 1 else self.root.winfo_x()
            y = int(parts[2]) if len(parts) > 2 else self.root.winfo_y()
            return w, h, x, y
        except Exception:
            return None, None, None, None

    def get_fullscreen_state(self) -> bool:
        try:
            return bool(self.root.attributes("-fullscreen"))
        except tk.TclError:
            return False

    def get_zoomed_state(self) -> bool:
        try:
            return self.root.state() == 'zoomed'
        except tk.TclError:
            return False

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
        # Save current size and theme before exit
        self.save_settings()
        self.save_log()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = BuJoApp(root)
    root.mainloop()