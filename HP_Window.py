import tkinter as tk
from tkinter import messagebox


class HPWindow:
  def __init__(
    self,
    root,
    char,
    on_hp_changed,
    on_temp_hp_changed=None,
    background_color="black",
    mouse_x=None,
    mouse_y=None
  ):
    self.root = root
    self.char = char
    self.on_hp_changed = on_hp_changed
    self.on_temp_hp_changed = on_temp_hp_changed
    self.background_color = background_color

    self.window = tk.Toplevel(root)
    self.window.title(f"Adjust HP - {char.name}")
    self.window.geometry("360x270")
    self.window.configure(bg=self.background_color)
    self.window.grab_set()

    self.amount_var = tk.StringVar(value="")
    self.temp_hp_var = tk.StringVar(
      value=str(getattr(char, "temp_hp", 0) or 0)
    )

    self.build_window()
    self.place_window_at_mouse(mouse_x, mouse_y)
    self.grab_window_attention()

  def place_window_at_mouse(self, mouse_x=None, mouse_y=None):
    if mouse_x is None or mouse_y is None:
      return

    self.window.update_idletasks()
    self.window.geometry(
      f"+{mouse_x + 20}+{mouse_y + 20}"
    )

  def grab_window_attention(self):
    self.window.lift()
    self.window.focus_force()
    self.window.attributes("-topmost", True)
    self.window.after(
      250,
      lambda: self.window.attributes("-topmost", False)
    )

  def build_window(self):
    current_hp = getattr(self.char, "current_hp", "")
    max_hp = getattr(self.char, "max_hp", "")
    temp_hp = getattr(self.char, "temp_hp", 0) or 0

    tk.Label(
      self.window,
      text=self.char.name,
      font=("Arial", 14, "bold"),
      bg=self.background_color,
      fg="white"
    ).pack(pady=(12, 4))

    tk.Label(
      self.window,
      text=(
        f"Current HP: {current_hp}/{max_hp}"
        if max_hp
        else "Current HP: —"
      ),
      bg=self.background_color,
      fg="white"
    ).pack(pady=2)

    tk.Label(
      self.window,
      text=f"Temp HP: {temp_hp}",
      bg=self.background_color,
      fg="white"
    ).pack(pady=2)

    amount_entry = tk.Entry(
      self.window,
      textvariable=self.amount_var,
      width=12,
      justify="center"
    )
    amount_entry.pack(pady=8)
    amount_entry.focus_set()

    button_frame = tk.Frame(
      self.window,
      bg=self.background_color
    )
    button_frame.pack(pady=6)

    tk.Button(
      button_frame,
      text="Damage",
      width=10,
      command=self.damage
    ).pack(side=tk.LEFT, padx=5)

    tk.Button(
      button_frame,
      text="Heal",
      width=10,
      command=self.heal
    ).pack(side=tk.LEFT, padx=5)

    if self.char.chType != "LA":
      temp_frame = tk.Frame(
        self.window,
        bg=self.background_color
      )
      temp_frame.pack(pady=8)

      tk.Label(
        temp_frame,
        text="Set Temp HP:",
        bg=self.background_color,
        fg="white"
      ).pack(side=tk.LEFT, padx=5)

      tk.Entry(
        temp_frame,
        textvariable=self.temp_hp_var,
        width=8,
        justify="center"
      ).pack(side=tk.LEFT, padx=5)

      tk.Button(
        temp_frame,
        text="Set",
        width=8,
        command=self.set_temp_hp
      ).pack(side=tk.LEFT, padx=5)

  def get_amount(self):
    try:
      amount = int(self.amount_var.get())
    except ValueError:
      messagebox.showerror(
        "Invalid HP",
        "Enter a whole number.",
        parent=self.window
      )
      return None

    if amount < 0:
      messagebox.showerror(
        "Invalid HP",
        "Enter a positive number.",
        parent=self.window
      )
      return None

    return amount

  def damage(self):
    amount = self.get_amount()

    if amount is None:
      return

    self.on_hp_changed(
      self.char,
      -amount
    )
    self.window.destroy()

  def heal(self):
    amount = self.get_amount()

    if amount is None:
      return

    self.on_hp_changed(
      self.char,
      amount
    )
    self.window.destroy()

  def set_temp_hp(self):
    try:
      temp_hp = int(
        self.temp_hp_var.get() or 0
      )
    except ValueError:
      messagebox.showerror(
        "Invalid Temp HP",
        "Temp HP must be a whole number.",
        parent=self.window
      )
      return

    if temp_hp < 0:
      messagebox.showerror(
        "Invalid Temp HP",
        "Temp HP cannot be negative.",
        parent=self.window
      )
      return

    if self.on_temp_hp_changed is not None:
      self.on_temp_hp_changed(
        self.char,
        temp_hp
      )

    self.window.destroy()
