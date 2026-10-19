from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox

from Graphics_Options import (
  get_graphics_images,
  get_image_display_name,
  resolve_image_path,
  saveable_image_path
)
from Player_Web_Server import get_player_view_url

try:
  from PIL import Image, ImageTk
  PIL_AVAILABLE = True
except ImportError:
  PIL_AVAILABLE = False


BACKGROUND_COLORS = {
  "Black": "black",
  "Gray 10": "gray10",
  "Gray 20": "gray20",
  "Dark Slate Gray": "dark slate gray",
  "Midnight Blue": "midnight blue",
  "Dark Red": "dark red",
  "Dark Green": "dark green",
  "Saddle Brown": "saddle brown"
}

CHOOSE_IMAGE = "Choose Image..."


class ConfigWindow:
  def __init__(
    self,
    root,
    config,
    font_options,
    on_save,
    background_color="black",
    mouse_x=None,
    mouse_y=None
  ):
    self.root = root
    self.config = config
    self.font_options = font_options
    self.on_save = on_save
    self.background_color = background_color

    self.window = tk.Toplevel(root)
    self.window.title("Configuration")
    self.window.geometry("1540x900")
    self.window.configure(bg=self.background_color)
    self.window.grab_set()

    self.image_display_to_path = {}
    self.custom_image_display_to_path = {}
    self.preview_photo = None
    self.preview_label = None
    self.preview_name_label = None

    self.build_image_options()

    self.background_var = tk.StringVar(
      value=self.get_background_display_value()
    )

    self.font_var = tk.StringVar(
      value=config.get("font", "Georgia")
    )

    self.campaign_name_var = tk.StringVar(
      value=config.get("campaign_name", "D&D Campaign")
    )

    player_web = config.get("player_web", {})

    self.player_web_enabled_var = tk.BooleanVar(
      value=player_web.get("enabled", True)
    )

    self.player_web_port_var = tk.StringVar(
      value=str(player_web.get("port", 8080))
    )

    self.player_web_url_var = tk.StringVar()
    self.player_web_port_var.trace_add(
      "write",
      self.update_player_web_url
    )
    self.update_player_web_url()

    borders = config.get("borders", {})

    self.border_vars = {
      "PC": tk.StringVar(value=self.get_image_display_for_path(borders.get("PC", ""))),
      "SPC": tk.StringVar(value=self.get_image_display_for_path(borders.get("SPC", ""))),
      "NPC": tk.StringVar(value=self.get_image_display_for_path(borders.get("NPC", ""))),
      "EN": tk.StringVar(value=self.get_image_display_for_path(borders.get("EN", ""))),
      "LA": tk.StringVar(value=self.get_image_display_for_path(borders.get("LA", "")))
    }

    self.build_window()
    self.place_window_at_mouse(mouse_x, mouse_y)
    self.grab_window_attention()

  def build_image_options(self):
    self.image_display_to_path = {}

    for image_path in get_graphics_images():
      display_name = get_image_display_name(image_path)
      base_name = display_name
      suffix = 2

      while display_name in self.image_display_to_path:
        display_name = f"{base_name} ({suffix})"
        suffix += 1

      self.image_display_to_path[display_name] = saveable_image_path(image_path)

  def get_image_display_for_path(self, image_path):
    if not image_path:
      return CHOOSE_IMAGE

    for display_name, stored_path in self.image_display_to_path.items():
      if stored_path == image_path:
        return display_name

    for display_name, stored_path in self.custom_image_display_to_path.items():
      if stored_path == image_path:
        return display_name

    display_name = Path(image_path).stem.replace("_", " ").replace("-", " ").title()

    if not display_name:
      display_name = "Custom Image"

    base_name = display_name
    suffix = 2

    while (
      display_name in self.image_display_to_path
      or display_name in self.custom_image_display_to_path
    ):
      display_name = f"{base_name} ({suffix})"
      suffix += 1

    self.custom_image_display_to_path[display_name] = image_path
    return display_name

  def get_background_display_value(self):
    background = self.config.get(
      "background",
      {
        "type": "color",
        "value": "black"
      }
    )

    if background.get("type") == "color":
      background_value = background.get("value", "black")

      for display_name, color_value in BACKGROUND_COLORS.items():
        if color_value == background_value:
          return display_name

      return "Black"

    return self.get_image_display_for_path(
      background.get("value", "")
    )

  def get_all_image_options(self):
    options = list(self.image_display_to_path.keys())

    for display_name in self.custom_image_display_to_path:
      if display_name not in options:
        options.append(display_name)

    options.append(CHOOSE_IMAGE)
    return options

  def get_background_options(self):
    options = list(BACKGROUND_COLORS.keys())

    for display_name in self.get_all_image_options():
      if display_name not in options:
        options.append(display_name)

    return options

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

  def choose_image(self):
    filepath = filedialog.askopenfilename(
      title="Choose Image",
      filetypes=[
        (
          "Image Files",
          "*.jpg *.jpeg *.png *.webp"
        ),
        ("All Files", "*.*")
      ]
    )

    if not filepath:
      return None, None

    stored_path = saveable_image_path(filepath)
    display_name = self.get_image_display_for_path(stored_path)

    return display_name, stored_path

  def show_image_preview(self, display_name, preview_name):
    image_path = self.get_image_path_from_display(
      display_name
    )

    if image_path is None:
      self.clear_preview(preview_name)
      return

    full_path = resolve_image_path(
      image_path
    )

    if (
      not PIL_AVAILABLE
      or full_path is None
      or not full_path.exists()
    ):
      self.clear_preview(preview_name)
      return

    try:
      image = Image.open(full_path)
      image.thumbnail((720, 720))

      self.preview_photo = ImageTk.PhotoImage(
        image
      )

      self.preview_label.configure(
        image=self.preview_photo,
        text=""
      )

      self.preview_name_label.configure(
        text=preview_name
      )

    except Exception:
      self.clear_preview(preview_name)

  def clear_preview(self, preview_name="Preview"):
    self.preview_photo = None

    if self.preview_label is not None:
      self.preview_label.configure(
        image="",
        text="No image preview available"
      )

    if self.preview_name_label is not None:
      self.preview_name_label.configure(
        text=preview_name
      )

  def add_option_row(self, parent, label_text, variable, options, command=None):
    row = tk.Frame(
      parent,
      bg=self.background_color
    )
    row.pack(fill=tk.X, pady=5)

    label = tk.Label(
      row,
      text=label_text,
      width=20,
      anchor="w",
      bg=self.background_color,
      fg="white"
    )
    label.pack(side=tk.LEFT)

    menu = tk.OptionMenu(
      row,
      variable,
      *options,
      command=command
    )
    menu.config(width=28)
    menu.pack(side=tk.LEFT, padx=5)

    return menu

  def handle_background_change(self, selection):
    if selection == CHOOSE_IMAGE:
      display_name, _ = self.choose_image()

      if display_name is None:
        self.background_var.set("Black")
        self.clear_preview(
          "Combat Background"
        )
        return

      self.background_var.set(
        display_name
      )
      selection = display_name

    if selection in BACKGROUND_COLORS:
      self.clear_preview(
        f"Background: {selection}"
      )
      return

    self.show_image_preview(
      selection,
      "Combat Background"
    )

  def handle_border_change(
    self,
    character_type,
    selection
  ):
    if selection == CHOOSE_IMAGE:
      display_name, _ = self.choose_image()

      if display_name is None:
        current_path = self.config.get(
          "borders",
          {}
        ).get(
          character_type,
          "graphics/border.jpg"
        )

        display_name = self.get_image_display_for_path(
          current_path
        )

        self.border_vars[
          character_type
        ].set(display_name)

      else:
        self.border_vars[
          character_type
        ].set(display_name)
        selection = display_name

    labels = {
      "PC": "PC Card",
      "SPC": "SPC Card",
      "NPC": "NPC Card",
      "EN": "Enemy Card",
      "LA": "Lair Action Card"
    }

    self.show_image_preview(
      selection,
      labels.get(
        character_type,
        character_type
      )
    )

  def update_player_web_url(self, *args):
    try:
      port = int(self.player_web_port_var.get())
    except (TypeError, ValueError):
      self.player_web_url_var.set("Invalid port")
      return

    if port < 1 or port > 65535:
      self.player_web_url_var.set("Invalid port")
      return

    self.player_web_url_var.set(
      get_player_view_url(port)
    )

  def copy_player_web_url(self):
    url = self.player_web_url_var.get()

    if not url.startswith("http"):
      return

    self.window.clipboard_clear()
    self.window.clipboard_append(url)
    self.window.update()

  def add_entry_row(self, parent, label_text, variable, width=30):
    row = tk.Frame(
      parent,
      bg=self.background_color
    )
    row.pack(fill=tk.X, pady=5)

    label = tk.Label(
      row,
      text=label_text,
      width=20,
      anchor="w",
      bg=self.background_color,
      fg="white"
    )
    label.pack(side=tk.LEFT)

    entry = tk.Entry(
      row,
      textvariable=variable,
      width=width
    )
    entry.pack(side=tk.LEFT, padx=5)

    return entry

  def build_window(self):
    content = tk.Frame(
      self.window,
      bg=self.background_color
    )
    content.pack(
      fill=tk.BOTH,
      expand=True,
      padx=20,
      pady=15
    )

    settings_frame = tk.Frame(
      content,
      bg=self.background_color
    )
    settings_frame.pack(
      side=tk.LEFT,
      fill=tk.Y,
      padx=(0, 20)
    )

    preview_frame = tk.Frame(
      content,
      bg=self.background_color
    )
    preview_frame.pack(
      side=tk.LEFT,
      fill=tk.BOTH,
      expand=True
    )

    campaign_title = tk.Label(
      settings_frame,
      text="Campaign & Player View",
      font=("Arial", 11, "bold"),
      bg=self.background_color,
      fg="white"
    )
    campaign_title.pack(pady=(0, 8))

    self.add_entry_row(
      settings_frame,
      "Campaign Name:",
      self.campaign_name_var
    )

    web_toggle_row = tk.Frame(
      settings_frame,
      bg=self.background_color
    )
    web_toggle_row.pack(fill=tk.X, pady=5)

    tk.Label(
      web_toggle_row,
      text="Player Web View:",
      width=20,
      anchor="w",
      bg=self.background_color,
      fg="white"
    ).pack(side=tk.LEFT)

    tk.Checkbutton(
      web_toggle_row,
      text="Enabled",
      variable=self.player_web_enabled_var,
      bg=self.background_color,
      fg="white",
      selectcolor="black",
      activebackground=self.background_color,
      activeforeground="white"
    ).pack(side=tk.LEFT, padx=5)

    self.add_entry_row(
      settings_frame,
      "Player View Port:",
      self.player_web_port_var,
      width=10
    )

    link_row = tk.Frame(
      settings_frame,
      bg=self.background_color
    )
    link_row.pack(fill=tk.X, pady=5)

    tk.Label(
      link_row,
      text="Player View Link:",
      width=20,
      anchor="w",
      bg=self.background_color,
      fg="white"
    ).pack(side=tk.LEFT)

    tk.Entry(
      link_row,
      textvariable=self.player_web_url_var,
      width=28,
      state="readonly",
      readonlybackground="white",
      fg="black"
    ).pack(side=tk.LEFT, padx=5)

    tk.Button(
      link_row,
      text="Copy",
      width=8,
      command=self.copy_player_web_url
    ).pack(side=tk.LEFT, padx=3)

    campaign_separator = tk.Frame(
      settings_frame,
      height=2,
      bg="gray50"
    )
    campaign_separator.pack(
      fill=tk.X,
      pady=12
    )

    self.add_option_row(
      settings_frame,
      "Background:",
      self.background_var,
      self.get_background_options(),
      self.handle_background_change
    )

    self.add_option_row(
      settings_frame,
      "Font:",
      self.font_var,
      self.font_options
    )

    separator = tk.Frame(
      settings_frame,
      height=2,
      bg="gray50"
    )
    separator.pack(
      fill=tk.X,
      pady=15
    )

    border_title = tk.Label(
      settings_frame,
      text="Character Card Backgrounds",
      font=("Arial", 11, "bold"),
      bg=self.background_color,
      fg="white"
    )
    border_title.pack(pady=(0, 8))

    labels = {
      "PC": "PC Card:",
      "SPC": "SPC Card:",
      "NPC": "NPC Card:",
      "EN": "Enemy Card:",
      "LA": "Lair Action Card:"
    }

    for character_type in [
      "PC",
      "SPC",
      "NPC",
      "EN",
      "LA"
    ]:
      self.add_option_row(
        settings_frame,
        labels[character_type],
        self.border_vars[character_type],
        self.get_all_image_options(),
        lambda selection, ct=character_type: self.handle_border_change(ct, selection)
      )

    self.preview_name_label = tk.Label(
      preview_frame,
      text="Preview",
      font=("Arial", 11, "bold"),
      bg=self.background_color,
      fg="white"
    )
    self.preview_name_label.pack(
      pady=(5, 10)
    )

    preview_box = tk.Frame(
      preview_frame,
      width=720,
      height=720,
      bg="gray10"
    )
    preview_box.pack()
    preview_box.pack_propagate(False)

    self.preview_label = tk.Label(
      preview_box,
      text="Select an image to preview",
      bg="gray10",
      fg="white"
    )
    self.preview_label.pack(
      fill=tk.BOTH,
      expand=True
    )

    button_frame = tk.Frame(
      self.window,
      bg=self.background_color
    )
    button_frame.pack(
      fill=tk.X,
      padx=20,
      pady=15
    )

    save_button = tk.Button(
      button_frame,
      text="Save",
      width=12,
      command=self.save
    )
    save_button.pack(
      side=tk.RIGHT,
      padx=5
    )

    cancel_button = tk.Button(
      button_frame,
      text="Cancel",
      width=12,
      command=self.window.destroy
    )
    cancel_button.pack(
      side=tk.RIGHT,
      padx=5
    )

    initial_background = self.background_var.get()

    if initial_background not in BACKGROUND_COLORS:
      self.show_image_preview(
        initial_background,
        "Combat Background"
      )

  def get_image_path_from_display(self, display_name):
    if display_name in self.image_display_to_path:
      return self.image_display_to_path[display_name]

    if display_name in self.custom_image_display_to_path:
      return self.custom_image_display_to_path[display_name]

    return None

  def save(self):
    background_selection = self.background_var.get()

    if background_selection in BACKGROUND_COLORS:
      background = {
        "type": "color",
        "value": BACKGROUND_COLORS[background_selection]
      }

    else:
      background_path = self.get_image_path_from_display(
        background_selection
      )

      if background_path is None:
        background = {
          "type": "color",
          "value": "black"
        }
      else:
        background = {
          "type": "image",
          "value": background_path
        }

    borders = {}

    for character_type, variable in self.border_vars.items():
      image_path = self.get_image_path_from_display(
        variable.get()
      )

      if image_path is None:
        image_path = self.config.get("borders", {}).get(
          character_type,
          "graphics/border.jpg"
        )

      borders[character_type] = image_path

    campaign_name = self.campaign_name_var.get().strip()

    if not campaign_name:
      campaign_name = "D&D Campaign"

    try:
      player_web_port = int(
        self.player_web_port_var.get()
      )
    except (TypeError, ValueError):
      messagebox.showerror(
        "Invalid Port",
        "Player View Port must be a number between 1 and 65535.",
        parent=self.window
      )
      return

    if player_web_port < 1 or player_web_port > 65535:
      messagebox.showerror(
        "Invalid Port",
        "Player View Port must be between 1 and 65535.",
        parent=self.window
      )
      return

    new_config = {
      "campaign_name": campaign_name,
      "player_web": {
        "enabled": self.player_web_enabled_var.get(),
        "port": player_web_port
      },
      "background": background,
      "font": self.font_var.get(),
      "borders": borders
    }

    self.on_save(new_config)
    self.window.destroy()
