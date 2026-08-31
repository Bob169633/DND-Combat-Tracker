import tkinter as tk
from tkinter import messagebox


PERMANENT_TRIGGERS = [
  "none",
  "start_turn",
  "end_turn"
]

PERMANENT_EFFECTS = [
  "none",
  "heal",
  "damage"
]

COLUMN_WIDTHS = {
  "character": 145,
  "status": 150,
  "duration": 75,
  "permanent": 80,
  "trigger": 100,
  "effect": 90,
  "amount": 70
}


class StatusWindow:
  def __init__(self, root, combat, on_add_statuses, background_color="black", mouse_x=None, mouse_y=None):
    self.root = root
    self.combat = combat
    self.on_add_statuses = on_add_statuses
    self.background_color = background_color
    self.rows = []

    self.window = tk.Toplevel(root)
    self.window.title("Add Statuses")
    self.window.geometry("840x500")
    self.window.configure(bg=self.background_color)
    self.window.grab_set()

    self.build_window()
    self.place_window_at_mouse(mouse_x, mouse_y)
    self.grab_window_attention()

  def place_window_at_mouse(self, mouse_x=None, mouse_y=None):
    if mouse_x is None or mouse_y is None:
      return

    self.window.update_idletasks()

    window_width = self.window.winfo_reqwidth()
    window_height = self.window.winfo_reqheight()

    virtual_x = self.window.winfo_vrootx()
    virtual_y = self.window.winfo_vrooty()
    virtual_width = self.window.winfo_vrootwidth()
    virtual_height = self.window.winfo_vrootheight()

    x = mouse_x + 20
    y = mouse_y + 20

    min_x = virtual_x
    min_y = virtual_y
    max_x = virtual_x + virtual_width - window_width
    max_y = virtual_y + virtual_height - window_height

    if x > max_x:
      x = max_x

    if y > max_y:
      y = max_y

    if x < min_x:
      x = min_x

    if y < min_y:
      y = min_y

    self.window.geometry(f"+{x}+{y}")

  def grab_window_attention(self):
    self.window.lift()
    self.window.focus_force()
    self.window.attributes("-topmost", True)
    self.window.after(250, lambda: self.window.attributes("-topmost", False))

  def make_cell(self, parent, width, height=30):
    cell = tk.Frame(parent, width=width, height=height, bg=self.background_color)
    cell.pack(side=tk.LEFT, padx=2, pady=2)
    cell.pack_propagate(False)
    return cell

  def make_label(self, parent, text):
    return tk.Label(
      parent,
      text=text,
      anchor="center",
      bg=self.background_color,
      fg="white"
    )

  def build_window(self):
    top_frame = tk.Frame(self.window, bg=self.background_color)
    top_frame.pack(fill=tk.X, padx=10, pady=10)

    tk.Label(
      top_frame,
      text="Number of status entries:",
      bg=self.background_color,
      fg="white"
    ).pack(side=tk.LEFT)

    self.entry_count_var = tk.StringVar(value="1")

    self.entry_count_box = tk.Entry(
      top_frame,
      textvariable=self.entry_count_var,
      width=8
    )
    self.entry_count_box.pack(side=tk.LEFT, padx=5)

    build_button = tk.Button(
      top_frame,
      text="Build Entries",
      command=self.build_entries
    )
    build_button.pack(side=tk.LEFT, padx=5)

    self.entries_canvas_outer = tk.Frame(self.window, bg=self.background_color)
    self.entries_canvas_outer.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    self.entries_canvas = tk.Canvas(
      self.entries_canvas_outer,
      bg=self.background_color,
      highlightthickness=0
    )
    self.entries_scrollbar = tk.Scrollbar(
      self.entries_canvas_outer,
      orient=tk.VERTICAL,
      command=self.entries_canvas.yview
    )

    self.entries_frame = tk.Frame(self.entries_canvas, bg=self.background_color)

    self.entries_frame.bind(
      "<Configure>",
      lambda e: self.entries_canvas.configure(scrollregion=self.entries_canvas.bbox("all"))
    )

    self.entries_canvas_window = self.entries_canvas.create_window(
      (0, 0),
      window=self.entries_frame,
      anchor="nw"
    )

    self.entries_canvas.configure(yscrollcommand=self.entries_scrollbar.set)
    self.entries_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    self.entries_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    self.entries_canvas.bind("<Configure>", self.resize_entries_frame)

    bottom_frame = tk.Frame(self.window, bg=self.background_color)
    bottom_frame.pack(fill=tk.X, padx=10, pady=10)

    add_button = tk.Button(
      bottom_frame,
      text="Add Statuses to Combat",
      command=self.add_statuses
    )
    add_button.pack(side=tk.RIGHT, padx=5)

    cancel_button = tk.Button(
      bottom_frame,
      text="Cancel",
      command=self.window.destroy
    )
    cancel_button.pack(side=tk.RIGHT, padx=5)

    self.build_entries()

  def resize_entries_frame(self, event):
    self.entries_canvas.itemconfig(self.entries_canvas_window, width=event.width)

  def get_character_names(self):
    return [char.name for char in self.combat]

  def build_entries(self):
    for widget in self.entries_frame.winfo_children():
      widget.destroy()

    self.rows = []

    character_names = self.get_character_names()

    if not character_names:
      messagebox.showerror("No Characters", "Add characters before adding statuses.")
      self.window.destroy()
      return

    try:
      entry_count = int(self.entry_count_var.get())
    except ValueError:
      messagebox.showerror("Invalid Entry Count", "Number of status entries must be a number.")
      return

    if entry_count < 1:
      messagebox.showerror("Invalid Entry Count", "Number of status entries must be at least 1.")
      return

    header = tk.Frame(self.entries_frame, bg=self.background_color)
    header.pack(fill=tk.X, pady=2)

    self.make_label(self.make_cell(header, COLUMN_WIDTHS["character"]), "Character").pack(fill=tk.BOTH, expand=True)
    self.make_label(self.make_cell(header, COLUMN_WIDTHS["status"]), "Status").pack(fill=tk.BOTH, expand=True)
    self.make_label(self.make_cell(header, COLUMN_WIDTHS["duration"]), "Duration").pack(fill=tk.BOTH, expand=True)
    self.make_label(self.make_cell(header, COLUMN_WIDTHS["permanent"]), "Permanent").pack(fill=tk.BOTH, expand=True)
    self.make_label(self.make_cell(header, COLUMN_WIDTHS["trigger"]), "Trigger").pack(fill=tk.BOTH, expand=True)
    self.make_label(self.make_cell(header, COLUMN_WIDTHS["effect"]), "Effect").pack(fill=tk.BOTH, expand=True)
    self.make_label(self.make_cell(header, COLUMN_WIDTHS["amount"]), "Amount").pack(fill=tk.BOTH, expand=True)

    first_status_entry = None

    for index in range(entry_count):
      row_frame = tk.Frame(self.entries_frame, bg=self.background_color)
      row_frame.pack(fill=tk.X, pady=2)

      character_var = tk.StringVar(value=character_names[0])
      status_var = tk.StringVar()
      duration_var = tk.StringVar(value="1")
      permanent_var = tk.BooleanVar(value=False)
      trigger_var = tk.StringVar(value="none")
      effect_var = tk.StringVar(value="none")
      amount_var = tk.StringVar(value="0")

      character_cell = self.make_cell(row_frame, COLUMN_WIDTHS["character"])
      character_menu = tk.OptionMenu(character_cell, character_var, *character_names)
      character_menu.pack(fill=tk.BOTH, expand=True)

      status_cell = self.make_cell(row_frame, COLUMN_WIDTHS["status"])
      status_entry = tk.Entry(status_cell, textvariable=status_var)
      status_entry.pack(fill=tk.BOTH, expand=True)

      if first_status_entry is None:
        first_status_entry = status_entry

      duration_cell = self.make_cell(row_frame, COLUMN_WIDTHS["duration"])
      duration_entry = tk.Entry(duration_cell, textvariable=duration_var)
      duration_entry.pack(fill=tk.BOTH, expand=True)

      permanent_cell = self.make_cell(row_frame, COLUMN_WIDTHS["permanent"])
      permanent_check = tk.Checkbutton(
        permanent_cell,
        variable=permanent_var,
        bg=self.background_color
      )
      permanent_check.pack(fill=tk.BOTH, expand=True)

      trigger_cell = self.make_cell(row_frame, COLUMN_WIDTHS["trigger"])
      trigger_menu = tk.OptionMenu(trigger_cell, trigger_var, *PERMANENT_TRIGGERS)
      trigger_menu.pack(fill=tk.BOTH, expand=True)

      effect_cell = self.make_cell(row_frame, COLUMN_WIDTHS["effect"])
      effect_menu = tk.OptionMenu(effect_cell, effect_var, *PERMANENT_EFFECTS)
      effect_menu.pack(fill=tk.BOTH, expand=True)

      amount_cell = self.make_cell(row_frame, COLUMN_WIDTHS["amount"])
      amount_entry = tk.Entry(amount_cell, textvariable=amount_var)
      amount_entry.pack(fill=tk.BOTH, expand=True)

      self.rows.append({
        "character": character_var,
        "status": status_var,
        "duration": duration_var,
        "permanent": permanent_var,
        "trigger": trigger_var,
        "effect": effect_var,
        "amount": amount_var
      })

    if first_status_entry is not None:
      first_status_entry.focus_set()

  def add_statuses(self):
    statuses_to_add = []

    for row in self.rows:
      character_name = row["character"].get().strip()
      status_name = row["status"].get().strip()
      is_permanent = row["permanent"].get()

      if not character_name:
        messagebox.showerror("Missing Character", "Every status needs a target character.")
        return

      if not status_name:
        messagebox.showerror("Missing Status", "Every status entry needs a status name.")
        return

      if is_permanent:
        try:
          amount = int(row["amount"].get() or 0)
        except ValueError:
          messagebox.showerror("Invalid Amount", f"{status_name} has an invalid permanent effect amount.")
          return

        statuses_to_add.append({
          "character": character_name,
          "status": status_name,
          "permanent": True,
          "trigger": row["trigger"].get(),
          "effect": row["effect"].get(),
          "amount": amount
        })

      else:
        try:
          duration = int(row["duration"].get())
        except ValueError:
          messagebox.showerror("Invalid Duration", f"{status_name} has an invalid duration.")
          return

        if duration < 1:
          messagebox.showerror("Invalid Duration", f"{status_name} must have a duration of at least 1.")
          return

        statuses_to_add.append({
          "character": character_name,
          "status": status_name,
          "duration": duration,
          "permanent": False
        })

    self.on_add_statuses(statuses_to_add)
    self.window.destroy()
