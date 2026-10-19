import random
import tkinter as tk
from tkinter import messagebox

from Create_Chars import createChar
from Roll_HP import roll_hp_formula


VALID_TYPES = ["PC", "SPC", "NPC", "EN", "LA"]

COLUMN_WIDTHS = {
  "name": 160,
  "type": 80,
  "bonus": 80,
  "initiative": 80,
  "count": 70,
  "hp": 90,
  "current_hp": 90,
  "temp_hp": 80
}


class AddCharactersWindow:
  def __init__(self, root, on_add_characters, background_color="black", mouse_x=None, mouse_y=None):
    self.root = root
    self.on_add_characters = on_add_characters
    self.background_color = background_color
    self.rows = []

    self.window = tk.Toplevel(root)
    self.window.title("Add Characters")
    self.window.geometry("1080x500")
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
    label = tk.Label(
      parent,
      text=text,
      anchor="center",
      bg=self.background_color,
      fg="white"
    )
    return label

  def build_window(self):
    top_frame = tk.Frame(self.window, bg=self.background_color)
    top_frame.pack(fill=tk.X, padx=10, pady=10)

    tk.Label(
      top_frame,
      text="Number of character entries:",
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
      text="Add Characters to Combat",
      command=self.add_characters
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

  def build_entries(self):
    for widget in self.entries_frame.winfo_children():
      widget.destroy()

    self.rows = []

    try:
      entry_count = int(self.entry_count_var.get())
    except ValueError:
      messagebox.showerror("Invalid Entry Count", "Number of character entries must be a number.")
      return

    if entry_count < 1:
      messagebox.showerror("Invalid Entry Count", "Number of character entries must be at least 1.")
      return

    header = tk.Frame(
      self.entries_frame,
      bg=self.background_color,
      height=34
    )
    header.pack(fill=tk.X, pady=2)
    header.pack_propagate(False)

    self.make_label(self.make_cell(header, COLUMN_WIDTHS["name"]), "Name").pack(fill=tk.X)
    self.make_label(self.make_cell(header, COLUMN_WIDTHS["type"]), "Type").pack(fill=tk.X)
    self.make_label(self.make_cell(header, COLUMN_WIDTHS["bonus"]), "Init Bonus").pack(fill=tk.X)
    self.make_label(self.make_cell(header, COLUMN_WIDTHS["initiative"]), "Init Roll").pack(fill=tk.X)
    self.make_label(self.make_cell(header, COLUMN_WIDTHS["count"]), "Count").pack(fill=tk.X)
    self.make_label(self.make_cell(header, COLUMN_WIDTHS["hp"]), "HP / Formula").pack(fill=tk.X)
    self.make_label(self.make_cell(header, COLUMN_WIDTHS["current_hp"]), "Current HP").pack(fill=tk.X)
    self.make_label(self.make_cell(header, COLUMN_WIDTHS["temp_hp"]), "Temp HP").pack(fill=tk.X)

    first_entry = None

    for index in range(entry_count):
      row_frame = tk.Frame(
        self.entries_frame,
        bg=self.background_color,
        height=38
      )
      row_frame.pack(fill=tk.X, pady=2)
      row_frame.pack_propagate(False)

      name_var = tk.StringVar()
      type_var = tk.StringVar(value="EN")
      bonus_var = tk.StringVar(value="0")
      initiative_var = tk.StringVar(value="")
      count_var = tk.StringVar(value="1")
      hp_formula_var = tk.StringVar(value="")
      current_hp_var = tk.StringVar(value="")
      temp_hp_var = tk.StringVar(value="0")

      name_cell = self.make_cell(row_frame, COLUMN_WIDTHS["name"])
      name_entry = tk.Entry(name_cell, textvariable=name_var)
      name_entry.pack(fill=tk.BOTH, expand=True)

      if first_entry is None:
        first_entry = name_entry

      type_cell = self.make_cell(row_frame, COLUMN_WIDTHS["type"])
      type_menu = tk.OptionMenu(type_cell, type_var, *VALID_TYPES)
      type_menu.pack(fill=tk.X)

      bonus_cell = self.make_cell(row_frame, COLUMN_WIDTHS["bonus"])
      bonus_entry = tk.Entry(bonus_cell, textvariable=bonus_var)
      bonus_entry.pack(fill=tk.BOTH, expand=True)

      initiative_cell = self.make_cell(row_frame, COLUMN_WIDTHS["initiative"])
      initiative_entry = tk.Entry(initiative_cell, textvariable=initiative_var)
      initiative_entry.pack(fill=tk.BOTH, expand=True)

      count_cell = self.make_cell(row_frame, COLUMN_WIDTHS["count"])
      count_entry = tk.Entry(count_cell, textvariable=count_var)
      count_entry.pack(fill=tk.BOTH, expand=True)

      hp_cell = self.make_cell(row_frame, COLUMN_WIDTHS["hp"])
      hp_formula_entry = tk.Entry(hp_cell, textvariable=hp_formula_var)
      hp_formula_entry.pack(fill=tk.BOTH, expand=True)

      current_hp_cell = self.make_cell(row_frame, COLUMN_WIDTHS["current_hp"])
      current_hp_entry = tk.Entry(current_hp_cell, textvariable=current_hp_var)
      current_hp_entry.pack(fill=tk.BOTH, expand=True)

      temp_hp_cell = self.make_cell(row_frame, COLUMN_WIDTHS["temp_hp"])
      temp_hp_entry = tk.Entry(temp_hp_cell, textvariable=temp_hp_var)
      temp_hp_entry.pack(fill=tk.BOTH, expand=True)

      self.rows.append({
        "name": name_var,
        "type": type_var,
        "bonus": bonus_var,
        "initiative": initiative_var,
        "count": count_var,
        "hp_formula": hp_formula_var,
        "current_hp": current_hp_var,
        "temp_hp": temp_hp_var
      })

    if first_entry is not None:
      first_entry.focus_set()

  def add_characters(self):
    characters_to_add = []

    for row in self.rows:
      name = row["name"].get().strip()
      chType = row["type"].get().strip()

      if not name:
        messagebox.showerror("Missing Name", "Every character entry needs a name.")
        return

      if chType not in VALID_TYPES:
        messagebox.showerror("Invalid Type", f"{name} has an invalid character type.")
        return

      try:
        bonus = int(row["bonus"].get())
      except ValueError:
        messagebox.showerror("Invalid Bonus", f"{name} has an invalid initiative bonus.")
        return

      initiative_text = row["initiative"].get().strip()

      if initiative_text:
        try:
          entered_initiative = int(initiative_text)
        except ValueError:
          messagebox.showerror("Invalid Initiative", f"{name} has an invalid initiative roll.")
          return
      else:
        entered_initiative = None

      try:
        count = int(row["count"].get())
      except ValueError:
        messagebox.showerror("Invalid Count", f"{name} has an invalid creature count.")
        return

      if count < 1:
        messagebox.showerror("Invalid Count", f"{name} must have a count of at least 1.")
        return

      hp_text = row["hp_formula"].get().strip()
      current_hp_text = row["current_hp"].get().strip()
      temp_hp_text = row["temp_hp"].get().strip()

      try:
        temp_hp = int(temp_hp_text) if temp_hp_text else 0
      except ValueError:
        messagebox.showerror("Invalid Temp HP", f"{name} has an invalid Temp HP value.")
        return

      if temp_hp < 0:
        messagebox.showerror("Invalid Temp HP", f"{name} cannot have negative Temp HP.")
        return

      if chType == "LA":
        temp_hp = 0

      uses_direct_hp = chType in ["PC", "SPC"]
      uses_formula_hp = chType in ["NPC", "EN"]

      for creature_number in range(1, count + 1):
        if chType == "LA":
          initiative_roll = 20
        elif entered_initiative is not None:
          initiative_roll = entered_initiative
        else:
          initiative_roll = random.randint(1, 20)

        if count == 1:
          final_name = name
        else:
          final_name = f"{name} {creature_number}"

        max_hp = ""
        current_hp = ""

        if uses_direct_hp:
          if hp_text:
            try:
              max_hp = int(hp_text)
            except ValueError:
              messagebox.showerror("Invalid HP", f"{name} needs a whole-number HP value.")
              return

            current_hp = max_hp

          elif current_hp_text:
            try:
              max_hp = int(current_hp_text)
              current_hp = max_hp
            except ValueError:
              messagebox.showerror("Invalid HP", f"{name} needs a whole-number HP value.")
              return

          if current_hp_text and hp_text:
            try:
              current_hp = int(current_hp_text)
            except ValueError:
              messagebox.showerror("Invalid Current HP", f"{name} has an invalid current HP.")
              return

        elif uses_formula_hp:
          if hp_text:
            try:
              max_hp = roll_hp_formula(hp_text)
            except ValueError as error:
              messagebox.showerror("Invalid HP Formula", f"{name}: {error}")
              return

            current_hp = max_hp

          if current_hp_text:
            try:
              current_hp = int(current_hp_text)
            except ValueError:
              messagebox.showerror("Invalid Current HP", f"{name} has an invalid current HP.")
              return

        characters_to_add.append(
          createChar(
            final_name,
            chType,
            bonus,
            initiative_roll,
            max_hp=max_hp,
            current_hp=current_hp,
            temp_hp=temp_hp
          )
        )

    self.on_add_characters(characters_to_add)
    self.window.destroy()
