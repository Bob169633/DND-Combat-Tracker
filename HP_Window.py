import tkinter as tk
from tkinter import messagebox


class HPWindow:
  def __init__(self, root, char, on_hp_changed, background_color="black", mouse_x=None, mouse_y=None):
    self.root = root
    self.char = char
    self.on_hp_changed = on_hp_changed
    self.background_color = background_color

    self.window = tk.Toplevel(root)
    self.window.title(f"Adjust HP - {char.name}")
    self.window.geometry("320x180")
    self.window.configure(bg=self.background_color)
    self.window.grab_set()

    self.amount_var = tk.StringVar(value="")

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

  def build_window(self):
    current_hp = getattr(self.char, "current_hp", "")
    max_hp = getattr(self.char, "max_hp", "")

    title = tk.Label(
      self.window,
      text=self.char.name,
      font=("Arial", 14, "bold"),
      bg=self.background_color,
      fg="white"
    )
    title.pack(pady=(12, 4))

    hp_label = tk.Label(
      self.window,
      text=f"Current HP: {current_hp}/{max_hp}" if max_hp else "Current HP: —",
      bg=self.background_color,
      fg="white"
    )
    hp_label.pack(pady=4)

    entry = tk.Entry(
      self.window,
      textvariable=self.amount_var,
      width=12,
      justify="center"
    )
    entry.pack(pady=8)
    entry.focus_set()

    button_frame = tk.Frame(self.window, bg=self.background_color)
    button_frame.pack(pady=8)

    damage_button = tk.Button(
      button_frame,
      text="Damage",
      width=10,
      command=self.damage
    )
    damage_button.pack(side=tk.LEFT, padx=5)

    heal_button = tk.Button(
      button_frame,
      text="Heal",
      width=10,
      command=self.heal
    )
    heal_button.pack(side=tk.LEFT, padx=5)

  def get_amount(self):
    try:
      amount = int(self.amount_var.get())
    except ValueError:
      messagebox.showerror("Invalid HP", "Enter a whole number.")
      return None

    if amount < 0:
      messagebox.showerror("Invalid HP", "Enter a positive number.")
      return None

    return amount

  def damage(self):
    amount = self.get_amount()

    if amount is None:
      return

    self.on_hp_changed(self.char, -amount)
    self.window.destroy()

  def heal(self):
    amount = self.get_amount()

    if amount is None:
      return

    self.on_hp_changed(self.char, amount)
    self.window.destroy()
