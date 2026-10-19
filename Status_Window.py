import tkinter as tk
from tkinter import messagebox


PERMANENT_TRIGGERS = ["none", "start_turn", "end_turn"]
STATUS_EFFECTS = ["none", "heal", "damage", "temp HP"]
TEMPORARY_TRIGGERS = ["Start of Turn", "End of Turn"]

COLUMN_WIDTHS = {
  "caster": 145,
  "status": 155,
  "duration": 75,
  "target": 145,
  "effect_trigger": 115,
  "permanent": 80,
  "amount": 70,
  "effect": 90
}


class StatusWindow:
  def __init__(
    self,
    root,
    combat,
    on_add_statuses,
    background_color="black",
    mouse_x=None,
    mouse_y=None
  ):
    self.root = root
    self.combat = combat
    self.on_add_statuses = on_add_statuses
    self.background_color = background_color
    self.rows = []
    self.character_options = []
    self.character_display_to_id = {}

    self.window = tk.Toplevel(root)
    self.window.title("Add Statuses")
    self.window.geometry("1100x520")
    self.window.configure(bg=self.background_color)
    self.window.grab_set()

    self.build_character_options()
    self.build_window()
    self.place_window_at_mouse(mouse_x, mouse_y)
    self.grab_window_attention()

  def build_character_options(self):
    name_counts = {}

    for char in self.combat:
      name_counts[char.name] = name_counts.get(char.name, 0) + 1

    seen = {}

    for char in self.combat:
      display_name = char.name

      if name_counts.get(char.name, 0) > 1:
        seen[char.name] = seen.get(char.name, 0) + 1
        display_name = f"{char.name} #{seen[char.name]}"

      self.character_options.append(display_name)
      self.character_display_to_id[display_name] = getattr(
        char,
        "combat_id",
        None
      )

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
    self.window.after(
      250,
      lambda: self.window.attributes("-topmost", False)
    )

  def make_cell(self, parent, width, height=34):
    cell = tk.Frame(
      parent,
      width=width,
      height=height,
      bg=self.background_color
    )
    cell.pack(side=tk.LEFT, padx=2)
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
    top_frame = tk.Frame(
      self.window,
      bg=self.background_color
    )
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

    tk.Button(
      top_frame,
      text="Build Entries",
      command=self.build_entries
    ).pack(side=tk.LEFT, padx=5)

    self.entries_canvas_outer = tk.Frame(
      self.window,
      bg=self.background_color
    )
    self.entries_canvas_outer.pack(
      fill=tk.BOTH,
      expand=True,
      padx=10,
      pady=5
    )

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
    self.entries_frame = tk.Frame(
      self.entries_canvas,
      bg=self.background_color
    )
    self.entries_frame.bind(
      "<Configure>",
      lambda e: self.entries_canvas.configure(
        scrollregion=self.entries_canvas.bbox("all")
      )
    )
    self.entries_canvas_window = self.entries_canvas.create_window(
      (0, 0),
      window=self.entries_frame,
      anchor="nw"
    )
    self.entries_canvas.configure(
      yscrollcommand=self.entries_scrollbar.set
    )
    self.entries_canvas.pack(
      side=tk.LEFT,
      fill=tk.BOTH,
      expand=True
    )
    self.entries_scrollbar.pack(
      side=tk.RIGHT,
      fill=tk.Y
    )
    self.entries_canvas.bind(
      "<Configure>",
      self.resize_entries_frame
    )

    bottom_frame = tk.Frame(
      self.window,
      bg=self.background_color
    )
    bottom_frame.pack(fill=tk.X, padx=10, pady=10)

    tk.Button(
      bottom_frame,
      text="Add Statuses to Combat",
      command=self.add_statuses
    ).pack(side=tk.RIGHT, padx=5)

    tk.Button(
      bottom_frame,
      text="Cancel",
      command=self.window.destroy
    ).pack(side=tk.RIGHT, padx=5)

    self.build_entries()

  def resize_entries_frame(self, event):
    self.entries_canvas.itemconfig(
      self.entries_canvas_window,
      width=event.width
    )

  def build_entries(self):
    for widget in self.entries_frame.winfo_children():
      widget.destroy()

    self.rows = []

    if not self.character_options:
      messagebox.showerror(
        "No Characters",
        "Add characters before adding statuses."
      )
      self.window.destroy()
      return

    try:
      entry_count = int(
        self.entry_count_var.get()
      )
    except ValueError:
      messagebox.showerror(
        "Invalid Entry Count",
        "Number of status entries must be a number."
      )
      return

    if entry_count < 1:
      messagebox.showerror(
        "Invalid Entry Count",
        "Number of status entries must be at least 1."
      )
      return

    header = tk.Frame(
      self.entries_frame,
      bg=self.background_color,
      height=34
    )
    header.pack(
      fill=tk.X,
      pady=2
    )
    header.pack_propagate(False)

    headers = [
      ("caster", "Caster"),
      ("status", "Status"),
      ("duration", "Duration"),
      ("target", "Target"),
      ("effect_trigger", "Effect Trigger"),
      ("permanent", "Permanent"),
      ("amount", "Amount"),
      ("effect", "Effect")
    ]

    for key, label in headers:
      self.make_label(
        self.make_cell(
          header,
          COLUMN_WIDTHS[key],
          height=34
        ),
        label
      ).pack(fill=tk.BOTH, expand=True)

    first_status_entry = None

    for index in range(entry_count):
      row_frame = tk.Frame(
        self.entries_frame,
        bg=self.background_color,
        height=38
      )
      row_frame.pack(
        fill=tk.X,
        pady=2
      )
      row_frame.pack_propagate(False)

      caster_var = tk.StringVar(
        value=self.character_options[0]
      )
      status_var = tk.StringVar()
      duration_var = tk.StringVar(value="1")
      target_var = tk.StringVar(
        value=self.character_options[0]
      )
      effect_trigger_var = tk.StringVar(
        value="End of Turn"
      )
      permanent_var = tk.BooleanVar(
        value=False
      )
      amount_var = tk.StringVar(
        value="0"
      )
      effect_var = tk.StringVar(
        value="none"
      )

      caster_cell = self.make_cell(
        row_frame,
        COLUMN_WIDTHS["caster"],
        height=38
      )
      tk.OptionMenu(
        caster_cell,
        caster_var,
        *self.character_options
      ).pack(fill=tk.BOTH, expand=True)

      status_cell = self.make_cell(
        row_frame,
        COLUMN_WIDTHS["status"],
        height=38
      )
      status_entry = tk.Entry(
        status_cell,
        textvariable=status_var
      )
      status_entry.pack(fill=tk.BOTH, expand=True)

      if first_status_entry is None:
        first_status_entry = status_entry

      duration_cell = self.make_cell(
        row_frame,
        COLUMN_WIDTHS["duration"],
        height=38
      )
      tk.Entry(
        duration_cell,
        textvariable=duration_var
      ).pack(fill=tk.BOTH, expand=True)

      target_cell = self.make_cell(
        row_frame,
        COLUMN_WIDTHS["target"],
        height=38
      )
      tk.OptionMenu(
        target_cell,
        target_var,
        *self.character_options
      ).pack(fill=tk.BOTH, expand=True)

      trigger_cell = self.make_cell(
        row_frame,
        COLUMN_WIDTHS["effect_trigger"],
        height=38
      )
      tk.OptionMenu(
        trigger_cell,
        effect_trigger_var,
        *TEMPORARY_TRIGGERS
      ).pack(fill=tk.BOTH, expand=True)

      permanent_cell = self.make_cell(
        row_frame,
        COLUMN_WIDTHS["permanent"],
        height=38
      )
      permanent_button = tk.Button(
        permanent_cell,
        text="☐",
        font=("Arial", 16),
        relief=tk.RAISED
      )

      def toggle_permanent(
        variable=permanent_var,
        button=permanent_button
      ):
        variable.set(
          not variable.get()
        )
        button.configure(
          text="☑" if variable.get() else "☐"
        )

      permanent_button.configure(
        command=toggle_permanent
      )
      permanent_button.pack(
        fill=tk.BOTH,
        expand=True
      )

      amount_cell = self.make_cell(
        row_frame,
        COLUMN_WIDTHS["amount"],
        height=38
      )
      tk.Entry(
        amount_cell,
        textvariable=amount_var
      ).pack(fill=tk.BOTH, expand=True)

      effect_cell = self.make_cell(
        row_frame,
        COLUMN_WIDTHS["effect"],
        height=38
      )
      tk.OptionMenu(
        effect_cell,
        effect_var,
        *STATUS_EFFECTS
      ).pack(fill=tk.BOTH, expand=True)

      self.rows.append({
        "caster": caster_var,
        "status": status_var,
        "duration": duration_var,
        "target": target_var,
        "effect_trigger": effect_trigger_var,
        "permanent": permanent_var,
        "amount": amount_var,
        "effect": effect_var
      })

    if first_status_entry is not None:
      first_status_entry.focus_set()

  def add_statuses(self):
    statuses_to_add = []

    for row in self.rows:
      caster_display = row[
        "caster"
      ].get().strip()
      target_display = row[
        "target"
      ].get().strip()
      status_name = row[
        "status"
      ].get().strip()
      is_permanent = row[
        "permanent"
      ].get()

      if not caster_display:
        messagebox.showerror(
          "Missing Caster",
          "Every status needs a caster."
        )
        return

      if not target_display:
        messagebox.showerror(
          "Missing Target",
          "Every status needs a target."
        )
        return

      if not status_name:
        messagebox.showerror(
          "Missing Status",
          "Every status entry needs a status name."
        )
        return

      caster_id = self.character_display_to_id.get(
        caster_display
      )
      target_id = self.character_display_to_id.get(
        target_display
      )

      try:
        duration = int(
          row["duration"].get()
        )
      except ValueError:
        messagebox.showerror(
          "Invalid Duration",
          f"{status_name} has an invalid duration."
        )
        return

      if duration < 1:
        messagebox.showerror(
          "Invalid Duration",
          f"{status_name} must have a duration of at least 1."
        )
        return

      try:
        amount = int(
          row["amount"].get() or 0
        )
      except ValueError:
        messagebox.showerror(
          "Invalid Amount",
          f"{status_name} has an invalid amount."
        )
        return

      trigger_phase = (
        "start_turn"
        if row["effect_trigger"].get() == "Start of Turn"
        else "end_turn"
      )

      statuses_to_add.append({
        "caster_id": caster_id,
        "target_id": target_id,
        "character": target_display.split(" #")[0],
        "status": status_name,
        "duration": duration,
        "permanent": is_permanent,
        "trigger_character_id": caster_id,
        "trigger_phase": trigger_phase,
        "trigger": trigger_phase,
        "effect": row["effect"].get(),
        "amount": amount
      })

    self.on_add_statuses(
      statuses_to_add
    )
    self.window.destroy()
