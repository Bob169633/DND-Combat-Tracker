import random
import tkinter as tk
from tkinter import filedialog, messagebox

from Create_Chars import createChar


COLUMN_WIDTHS = {
  "name": 175,
  "type": 70,
  "bonus": 85,
  "max_hp": 85,
  "current_hp": 90,
  "temp_hp": 80,
  "initiative": 90,
  "theme": 285
}


class LoadPlayersWindow:
  def __init__(
    self,
    root,
    players,
    on_add_players,
    background_color="black",
    mouse_x=None,
    mouse_y=None
  ):
    self.root = root
    self.players = players
    self.on_add_players = on_add_players
    self.background_color = background_color
    self.rows = []

    self.window = tk.Toplevel(root)
    self.window.title("Load Players Into Combat")
    self.window.geometry("1190x520")
    self.window.configure(bg=self.background_color)
    self.window.grab_set()

    self.build_window()
    self.place_window_at_mouse(mouse_x, mouse_y)
    self.grab_window_attention()

  def place_window_at_mouse(self, mouse_x=None, mouse_y=None):
    if mouse_x is None or mouse_y is None:
      return

    self.window.update_idletasks()
    self.window.geometry(f"+{mouse_x + 20}+{mouse_y + 20}")

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

  def build_window(self):
    outer = tk.Frame(
      self.window,
      bg=self.background_color
    )
    outer.pack(
      fill=tk.BOTH,
      expand=True,
      padx=10,
      pady=10
    )

    canvas = tk.Canvas(
      outer,
      bg=self.background_color,
      highlightthickness=0
    )
    scrollbar = tk.Scrollbar(
      outer,
      orient=tk.VERTICAL,
      command=canvas.yview
    )
    rows_frame = tk.Frame(
      canvas,
      bg=self.background_color
    )

    rows_frame.bind(
      "<Configure>",
      lambda event: canvas.configure(
        scrollregion=canvas.bbox("all")
      )
    )

    canvas_window = canvas.create_window(
      (0, 0),
      window=rows_frame,
      anchor="nw"
    )

    canvas.configure(
      yscrollcommand=scrollbar.set
    )
    canvas.pack(
      side=tk.LEFT,
      fill=tk.BOTH,
      expand=True
    )
    scrollbar.pack(
      side=tk.RIGHT,
      fill=tk.Y
    )

    canvas.bind(
      "<Configure>",
      lambda event: canvas.itemconfig(
        canvas_window,
        width=event.width
      )
    )

    header = tk.Frame(
      rows_frame,
      bg=self.background_color
    )
    header.pack(fill=tk.X, pady=(0, 5))

    for key, label in [
      ("name", "Name"),
      ("type", "Type"),
      ("bonus", "Init Bonus"),
      ("max_hp", "Max HP"),
      ("current_hp", "Current HP"),
      ("temp_hp", "Temp HP"),
      ("initiative", "Init Roll"),
      ("theme", "Theme")
    ]:
      tk.Label(
        self.make_cell(
          header,
          COLUMN_WIDTHS[key]
        ),
        text=label,
        bg=self.background_color,
        fg="white"
      ).pack(expand=True)

    for player in self.players:
      row_frame = tk.Frame(
        rows_frame,
        bg=self.background_color
      )
      row_frame.pack(fill=tk.X, pady=2)

      name_var = tk.StringVar(value=player.name)
      bonus_var = tk.StringVar(
        value=str(getattr(player, "bonus", 0))
      )
      max_hp_var = tk.StringVar(
        value=str(getattr(player, "max_hp", ""))
      )
      current_hp_var = tk.StringVar(
        value=str(getattr(player, "current_hp", ""))
      )
      temp_hp_var = tk.StringVar(
        value=str(getattr(player, "temp_hp", 0) or 0)
      )
      initiative_var = tk.StringVar()
      theme_var = tk.StringVar(
        value=getattr(
          player,
          "theme_audio",
          ""
        )
      )

      tk.Entry(
        self.make_cell(
          row_frame,
          COLUMN_WIDTHS["name"]
        ),
        textvariable=name_var
      ).pack(fill=tk.BOTH, expand=True)

      tk.Label(
        self.make_cell(
          row_frame,
          COLUMN_WIDTHS["type"]
        ),
        text=player.chType,
        bg=self.background_color,
        fg="white"
      ).pack(expand=True)

      tk.Entry(
        self.make_cell(
          row_frame,
          COLUMN_WIDTHS["bonus"]
        ),
        textvariable=bonus_var
      ).pack(fill=tk.BOTH, expand=True)

      tk.Entry(
        self.make_cell(
          row_frame,
          COLUMN_WIDTHS["max_hp"]
        ),
        textvariable=max_hp_var
      ).pack(fill=tk.BOTH, expand=True)

      tk.Entry(
        self.make_cell(
          row_frame,
          COLUMN_WIDTHS["current_hp"]
        ),
        textvariable=current_hp_var
      ).pack(fill=tk.BOTH, expand=True)

      tk.Entry(
        self.make_cell(
          row_frame,
          COLUMN_WIDTHS["temp_hp"]
        ),
        textvariable=temp_hp_var
      ).pack(fill=tk.BOTH, expand=True)

      tk.Entry(
        self.make_cell(
          row_frame,
          COLUMN_WIDTHS["initiative"]
        ),
        textvariable=initiative_var
      ).pack(fill=tk.BOTH, expand=True)

      theme_cell = self.make_cell(
        row_frame,
        COLUMN_WIDTHS["theme"]
      )

      theme_entry = tk.Entry(
        theme_cell,
        textvariable=theme_var
      )
      theme_entry.pack(
        side=tk.LEFT,
        fill=tk.BOTH,
        expand=True
      )

      def choose_theme(
        variable=theme_var
      ):
        filepath = filedialog.askopenfilename(
          title="Choose Character Theme",
          filetypes=[
            (
              "Audio Files",
              "*.mp3 *.wav *.ogg"
            ),
            (
              "All Files",
              "*.*"
            )
          ],
          parent=self.window
        )

        if filepath:
          variable.set(filepath)

      tk.Button(
        theme_cell,
        text="Choose",
        command=choose_theme
      ).pack(
        side=tk.RIGHT,
        fill=tk.Y,
        padx=(4, 0)
      )

      self.rows.append({
        "player": player,
        "name": name_var,
        "bonus": bonus_var,
        "max_hp": max_hp_var,
        "current_hp": current_hp_var,
        "temp_hp": temp_hp_var,
        "initiative": initiative_var,
        "theme": theme_var
      })

    buttons = tk.Frame(
      self.window,
      bg=self.background_color
    )
    buttons.pack(
      fill=tk.X,
      padx=10,
      pady=(0, 10)
    )

    tk.Button(
      buttons,
      text="Reset Current HP to Max HP",
      command=self.reset_current_hp
    ).pack(side=tk.LEFT, padx=5)

    tk.Button(
      buttons,
      text="Add Players",
      command=self.add_players
    ).pack(side=tk.RIGHT, padx=5)

    tk.Button(
      buttons,
      text="Cancel",
      command=self.window.destroy
    ).pack(side=tk.RIGHT, padx=5)

  def reset_current_hp(self):
    for row in self.rows:
      row["current_hp"].set(
        row["max_hp"].get().strip()
      )

  def add_players(self):
    loaded_players = []

    for row in self.rows:
      player = row["player"]
      name = row["name"].get().strip()

      if not name:
        messagebox.showerror(
          "Invalid Name",
          "Player names cannot be blank.",
          parent=self.window
        )
        return

      try:
        bonus = int(
          row["bonus"].get().strip() or 0
        )
      except ValueError:
        messagebox.showerror(
          "Invalid Initiative Bonus",
          f"{name} has an invalid initiative bonus.",
          parent=self.window
        )
        return

      try:
        max_hp = int(
          row["max_hp"].get().strip()
        )
      except ValueError:
        messagebox.showerror(
          "Invalid Max HP",
          f"{name} has an invalid max HP value.",
          parent=self.window
        )
        return

      try:
        current_hp = int(
          row["current_hp"].get().strip()
          or max_hp
        )
      except ValueError:
        messagebox.showerror(
          "Invalid Current HP",
          f"{name} has an invalid current HP value.",
          parent=self.window
        )
        return

      temp_hp_text = row["temp_hp"].get().strip()

      try:
        temp_hp = int(
          temp_hp_text
          if temp_hp_text
          else 0
        )
      except ValueError:
        messagebox.showerror(
          "Invalid Temp HP",
          f"{name} has an invalid Temp HP value.",
          parent=self.window
        )
        return

      if max_hp < 1 or current_hp < 0 or temp_hp < 0:
        messagebox.showerror(
          "Invalid HP",
          f"{name} has an invalid HP value.",
          parent=self.window
        )
        return

      current_hp = min(
        current_hp,
        max_hp
      )

      initiative_text = row[
        "initiative"
      ].get().strip()

      try:
        initiative_roll = (
          random.randint(1, 20)
          if initiative_text == ""
          else int(initiative_text)
        )
      except ValueError:
        messagebox.showerror(
          "Invalid Initiative",
          f"{name} has an invalid initiative roll.",
          parent=self.window
        )
        return

      loaded_players.append(
        createChar(
          name=name,
          chType=player.chType,
          bonus=bonus,
          initiative=initiative_roll,
          max_hp=max_hp,
          current_hp=current_hp,
          permanent_statuses=getattr(
            player,
            "permanent_statuses",
            []
          ),
          card_background=getattr(
            player,
            "card_background",
            ""
          ),
          temp_hp=temp_hp,
          theme_audio=row[
            "theme"
          ].get().strip()
        )
      )

    self.on_add_players(
      loaded_players
    )
    self.window.destroy()
