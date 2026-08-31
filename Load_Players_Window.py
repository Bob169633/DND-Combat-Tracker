import random
import tkinter as tk
from tkinter import messagebox

from Create_Chars import createChar


COLUMN_WIDTHS = {
  "name": 160,
  "type": 70,
  "bonus": 90,
  "max_hp": 80,
  "current_hp": 90,
  "initiative": 90
}


class LoadPlayersWindow:
  def __init__(self, root, players, on_add_characters, background_color="black", mouse_x=None, mouse_y=None):
    self.root = root
    self.players = players
    self.on_add_characters = on_add_characters
    self.background_color = background_color
    self.rows = []

    self.window = tk.Toplevel(root)
    self.window.title("Load Players Into Combat")
    self.window.geometry("760x500")
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

  def make_label(self, parent, text, anchor="center"):
    return tk.Label(
      parent,
      text=text,
      anchor=anchor,
      bg=self.background_color,
      fg="white"
    )

  def build_window(self):
    outer = tk.Frame(self.window, bg=self.background_color)
    outer.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    self.entries_canvas = tk.Canvas(
      outer,
      bg=self.background_color,
      highlightthickness=0
    )
    self.entries_scrollbar = tk.Scrollbar(
      outer,
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

    header = tk.Frame(self.entries_frame, bg=self.background_color)
    header.pack(fill=tk.X, pady=2)

    self.make_label(self.make_cell(header, COLUMN_WIDTHS["name"]), "Name").pack(fill=tk.BOTH, expand=True)
    self.make_label(self.make_cell(header, COLUMN_WIDTHS["type"]), "Type").pack(fill=tk.BOTH, expand=True)
    self.make_label(self.make_cell(header, COLUMN_WIDTHS["bonus"]), "Init Bonus").pack(fill=tk.BOTH, expand=True)
    self.make_label(self.make_cell(header, COLUMN_WIDTHS["max_hp"]), "Max HP").pack(fill=tk.BOTH, expand=True)
    self.make_label(self.make_cell(header, COLUMN_WIDTHS["current_hp"]), "Current HP").pack(fill=tk.BOTH, expand=True)
    self.make_label(self.make_cell(header, COLUMN_WIDTHS["initiative"]), "Init Roll").pack(fill=tk.BOTH, expand=True)

    first_entry = None

    for player in self.players:
      row_frame = tk.Frame(self.entries_frame, bg=self.background_color)
      row_frame.pack(fill=tk.X, pady=2)

      current_hp = getattr(player, "current_hp", "")
      max_hp = getattr(player, "max_hp", "")

      if current_hp == "":
        current_hp = max_hp

      name_var = tk.StringVar(value=player.name)
      type_var = tk.StringVar(value=player.chType)
      bonus_var = tk.StringVar(value=str(getattr(player, "bonus", 0)))
      max_hp_var = tk.StringVar(value=str(max_hp))
      current_hp_var = tk.StringVar(value=str(current_hp))
      initiative_var = tk.StringVar(value="")

      name_cell = self.make_cell(row_frame, COLUMN_WIDTHS["name"])
      tk.Label(name_cell, textvariable=name_var, anchor="w").pack(fill=tk.BOTH, expand=True)

      type_cell = self.make_cell(row_frame, COLUMN_WIDTHS["type"])
      tk.Label(type_cell, textvariable=type_var, anchor="center").pack(fill=tk.BOTH, expand=True)

      bonus_cell = self.make_cell(row_frame, COLUMN_WIDTHS["bonus"])
      tk.Label(bonus_cell, textvariable=bonus_var, anchor="center").pack(fill=tk.BOTH, expand=True)

      max_hp_cell = self.make_cell(row_frame, COLUMN_WIDTHS["max_hp"])
      tk.Label(max_hp_cell, textvariable=max_hp_var, anchor="center").pack(fill=tk.BOTH, expand=True)

      current_hp_cell = self.make_cell(row_frame, COLUMN_WIDTHS["current_hp"])
      current_hp_entry = tk.Entry(current_hp_cell, textvariable=current_hp_var)
      current_hp_entry.pack(fill=tk.BOTH, expand=True)

      if first_entry is None:
        first_entry = current_hp_entry

      initiative_cell = self.make_cell(row_frame, COLUMN_WIDTHS["initiative"])
      initiative_entry = tk.Entry(initiative_cell, textvariable=initiative_var)
      initiative_entry.pack(fill=tk.BOTH, expand=True)

      self.rows.append({
        "source": player,
        "name": name_var,
        "type": type_var,
        "bonus": bonus_var,
        "max_hp": max_hp_var,
        "current_hp": current_hp_var,
        "initiative": initiative_var
      })

    bottom_frame = tk.Frame(self.window, bg=self.background_color)
    bottom_frame.pack(fill=tk.X, padx=10, pady=10)

    add_button = tk.Button(
      bottom_frame,
      text="Add Players to Combat",
      command=self.add_players
    )
    add_button.pack(side=tk.RIGHT, padx=5)

    cancel_button = tk.Button(
      bottom_frame,
      text="Cancel",
      command=self.window.destroy
    )
    cancel_button.pack(side=tk.RIGHT, padx=5)

    if first_entry is not None:
      first_entry.focus_set()

  def resize_entries_frame(self, event):
    self.entries_canvas.itemconfig(self.entries_canvas_window, width=event.width)

  def add_players(self):
    characters_to_add = []

    for row in self.rows:
      source = row["source"]
      name = row["name"].get().strip()
      chType = row["type"].get().strip()

      try:
        bonus = int(row["bonus"].get())
      except ValueError:
        bonus = 0

      max_hp = row["max_hp"].get().strip()
      current_hp = row["current_hp"].get().strip()
      initiative_text = row["initiative"].get().strip()

      if not current_hp:
        current_hp = max_hp

      try:
        int(current_hp)
      except ValueError:
        messagebox.showerror("Invalid HP", f"{name} has an invalid current HP.")
        return

      if initiative_text:
        try:
          initiative_roll = int(initiative_text)
        except ValueError:
          messagebox.showerror("Invalid Initiative", f"{name} has an invalid initiative roll.")
          return
      else:
        initiative_roll = random.randint(1, 20)

      char = createChar(
        name=name,
        chType=chType,
        bonus=bonus,
        initiative=initiative_roll,
        max_hp=max_hp,
        current_hp=current_hp,
        permanent_statuses=getattr(source, "permanent_statuses", [])
      )

      characters_to_add.append(char)

    self.on_add_characters(characters_to_add)
    self.window.destroy()
