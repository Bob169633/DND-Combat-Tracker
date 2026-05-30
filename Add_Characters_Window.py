import random
import tkinter as tk
from tkinter import messagebox

from Create_Chars import createChar


VALID_TYPES = ["PC", "NPC", "EN", "LA"]


class AddCharactersWindow:
  def __init__(self, root, on_add_characters):
    self.root = root
    self.on_add_characters = on_add_characters
    self.rows = []

    self.window = tk.Toplevel(root)
    self.window.title("Add Characters")
    self.window.geometry("780x500")
    self.window.grab_set()

    self.build_window()
    self.grab_window_attention()

  def grab_window_attention(self):
    self.window.lift()
    self.window.focus_force()
    self.window.attributes("-topmost", True)
    self.window.after(250, lambda: self.window.attributes("-topmost", False))

  def build_window(self):
    top_frame = tk.Frame(self.window)
    top_frame.pack(fill=tk.X, padx=10, pady=10)

    tk.Label(top_frame, text="Number of character entries:").pack(side=tk.LEFT)

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

    self.entries_canvas_outer = tk.Frame(self.window)
    self.entries_canvas_outer.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    self.entries_canvas = tk.Canvas(self.entries_canvas_outer)
    self.entries_scrollbar = tk.Scrollbar(
      self.entries_canvas_outer,
      orient=tk.VERTICAL,
      command=self.entries_canvas.yview
    )

    self.entries_frame = tk.Frame(self.entries_canvas)

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

    bottom_frame = tk.Frame(self.window)
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

    header = tk.Frame(self.entries_frame)
    header.pack(fill=tk.X, pady=2)

    tk.Label(header, text="Name", width=24, anchor="w").pack(side=tk.LEFT)
    tk.Label(header, text="Type", width=10, anchor="w").pack(side=tk.LEFT)
    tk.Label(header, text="Init Bonus", width=12, anchor="w").pack(side=tk.LEFT)
    tk.Label(header, text="Init Roll", width=12, anchor="w").pack(side=tk.LEFT)
    tk.Label(header, text="Count", width=10, anchor="w").pack(side=tk.LEFT)

    for index in range(entry_count):
      row_frame = tk.Frame(self.entries_frame)
      row_frame.pack(fill=tk.X, pady=2)

      name_var = tk.StringVar()
      type_var = tk.StringVar(value="EN")
      bonus_var = tk.StringVar(value="0")
      initiative_var = tk.StringVar(value="")
      count_var = tk.StringVar(value="1")

      name_entry = tk.Entry(row_frame, textvariable=name_var, width=26)
      name_entry.pack(side=tk.LEFT, padx=2)

      type_menu = tk.OptionMenu(row_frame, type_var, *VALID_TYPES)
      type_menu.config(width=6)
      type_menu.pack(side=tk.LEFT, padx=2)

      bonus_entry = tk.Entry(row_frame, textvariable=bonus_var, width=10)
      bonus_entry.pack(side=tk.LEFT, padx=2)

      initiative_entry = tk.Entry(row_frame, textvariable=initiative_var, width=10)
      initiative_entry.pack(side=tk.LEFT, padx=2)

      count_entry = tk.Entry(row_frame, textvariable=count_var, width=8)
      count_entry.pack(side=tk.LEFT, padx=2)

      self.rows.append({
        "name": name_var,
        "type": type_var,
        "bonus": bonus_var,
        "initiative": initiative_var,
        "count": count_var
      })

    if self.rows:
      first_row = self.entries_frame.winfo_children()[1]
      first_entry = first_row.winfo_children()[0]
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

        characters_to_add.append(
          createChar(final_name, chType, bonus, initiative_roll)
        )

    self.on_add_characters(characters_to_add)
    self.window.destroy()
