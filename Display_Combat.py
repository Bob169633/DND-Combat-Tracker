import math as m
import tkinter as tk
from tkinter import TclError

from Graphics_Options import resolve_image_path

try:
  from PIL import Image, ImageStat, ImageTk
  PIL_AVAILABLE = True
except ImportError:
  PIL_AVAILABLE = False


class CombatCardDisplay:
  def __init__(
    self,
    root,
    on_reorder=None,
    on_remove_status=None,
    on_remove_permanent_status=None,
    on_adjust_hp=None,
    on_death_save=None,
    background_color="black",
    font_family="Georgia"
  ):
    self.background_color = background_color
    self.font_family = font_family

    self.outer_frame = tk.Frame(root, bg=self.background_color)
    self.outer_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    self.canvas = tk.Canvas(
      self.outer_frame,
      bg=self.background_color,
      highlightthickness=0
    )

    self.scrollbar = tk.Scrollbar(
      self.outer_frame,
      orient=tk.VERTICAL,
      command=self.canvas.yview
    )

    self.card_window_ids = []
    self.title_item_id = None

    self.canvas.configure(yscrollcommand=self.scrollbar.set)

    self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    self.canvas.bind("<Configure>", self.resize_scrollable_frame)
    self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)

    self.on_reorder = on_reorder
    self.on_remove_status = on_remove_status
    self.on_remove_permanent_status = on_remove_permanent_status
    self.on_adjust_hp = on_adjust_hp
    self.on_death_save = on_death_save

    self.drag_start_index = None
    self.card_widgets = []

    self.floating_card = None
    self.floating_window = None
    self.dragged_original_card = None

    self.autoscroll_job = None
    self.autoscroll_direction = 0
    self.autoscroll_margin = 60
    self.autoscroll_delay = 100
    self.autoscroll_units = 1

    self.drag_hold_job = None
    self.pending_drag_event = None
    self.pending_drag_index = None
    self.pending_drag_char = None
    self.drag_started = False
    self.drag_delay_ms = 500

    self.card_width = 360
    self.card_height = 360
    self.card_padx = 10
    self.card_pady = 10

    self.card_images = []
    self.status_tooltip = None
    self.card_background_sources = {}
    self.card_text_colors = {}
    self.border_choices = {}

    self.background_image_path = None
    self.background_image_source = None
    self.background_photo = None
    self.background_image_id = None

  def set_background_color(self, color):
    self.background_color = color
    self.outer_frame.config(bg=color)
    self.canvas.config(bg=color)

  def set_font_family(self, font_family):
    self.font_family = font_family

  def set_border_choices(self, border_choices):
    self.border_choices = border_choices or {}

  def get_card_background_source(self, image_path):
    if not image_path:
      return None

    if image_path in self.card_background_sources:
      return self.card_background_sources[image_path]

    if not PIL_AVAILABLE:
      return None

    full_path = resolve_image_path(image_path)

    if full_path is None or not full_path.exists():
      return None

    try:
      image = Image.open(full_path)
    except Exception:
      return None

    self.card_background_sources[image_path] = image
    return image

  def get_card_image_path(self, char):
    personal_background = getattr(char,"card_background","")
    if char.chType in ["PC","SPC"] and personal_background:
      return personal_background
    return self.border_choices.get(char.chType,"graphics/border.jpg")

  def get_border_image(self, char):
    return self.get_card_background_source(self.get_card_image_path(char))

  def get_card_text_colors(self, char):
    image_path = self.get_card_image_path(char)

    if image_path in self.card_text_colors:
      return self.card_text_colors[image_path]

    background_image = self.get_card_background_source(
      image_path
    )

    if background_image is None:
      colors = {
        "primary": "black",
        "secondary": "#333333",
        "line": "#555555"
      }

      self.card_text_colors[image_path] = colors
      return colors

    sample = background_image.convert("RGB").resize(
      (50, 50)
    )

    stats = ImageStat.Stat(sample)

    red = stats.mean[0]
    green = stats.mean[1]
    blue = stats.mean[2]

    luminance = (
      0.2126 * red
      + 0.7152 * green
      + 0.0722 * blue
    )

    if luminance < 128:
      colors = {
        "primary": "white",
        "secondary": "#eeeeee",
        "line": "#dddddd"
      }
    else:
      colors = {
        "primary": "black",
        "secondary": "#222222",
        "line": "#444444"
      }

    self.card_text_colors[image_path] = colors
    return colors

  def set_background_image(self, image_path):
    if image_path == self.background_image_path:
      return

    self.background_image_path = image_path
    self.background_image_source = None
    self.background_photo = None
    self.background_image_id = None

    if image_path is None:
      self.canvas.delete("combat_background")
      return

    if not PIL_AVAILABLE:
      self.canvas.delete("combat_background")
      return

    full_path = resolve_image_path(image_path)

    if full_path is None or not full_path.exists():
      self.canvas.delete("combat_background")
      return

    try:
      self.background_image_source = Image.open(full_path)
    except Exception:
      self.background_image_source = None
      self.canvas.delete("combat_background")

  def draw_background_image(self):
    self.canvas.delete("combat_background")

    if self.background_image_source is None:
      return

    canvas_width = max(1, self.canvas.winfo_width())
    canvas_height = max(1, self.canvas.winfo_height())

    image_width, image_height = self.background_image_source.size

    if image_width <= 0 or image_height <= 0:
      return

    scale = max(
      canvas_width / image_width,
      canvas_height / image_height
    )

    new_width = max(1, int(image_width * scale))
    new_height = max(1, int(image_height * scale))

    resized = self.background_image_source.resize((new_width, new_height))

    left = max(0, int((new_width - canvas_width) / 2))
    top = max(0, int((new_height - canvas_height) / 2))
    right = left + canvas_width
    bottom = top + canvas_height

    cropped = resized.crop((left, top, right, bottom))
    self.background_photo = ImageTk.PhotoImage(cropped)

    self.background_image_id = self.canvas.create_image(
      0,
      0,
      image=self.background_photo,
      anchor="nw",
      tags="combat_background"
    )

    self.canvas.tag_lower("combat_background")

  def resize_scrollable_frame(self, event):
    self.draw_background_image()
    self.canvas.configure(scrollregion=self.canvas.bbox("all"))

  def on_mousewheel(self, event):
    first_visible, last_visible = self.canvas.yview()

    if first_visible <= 0 and event.delta > 0:
      return

    if last_visible >= 1 and event.delta < 0:
      return

    self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

  def should_skip_drag_queue(self, event):
    widget = event.widget

    if not isinstance(widget, tk.Canvas):
      return False

    current_items = widget.find_withtag("current")

    if not current_items:
      return False

    tags = widget.gettags(current_items[0])

    for tag in tags:
      if tag.startswith("hp_"):
        return True

      if tag.startswith("death_"):
        return True

      if tag.startswith("status_"):
        return True

      if tag.startswith("perm_"):
        return True

    return False

  def queue_drag(self, event, index, char):
    if self.should_skip_drag_queue(event):
      return

    self.cancel_queued_drag()

    self.pending_drag_event = event
    self.pending_drag_index = index
    self.pending_drag_char = char
    self.drag_started = False

    self.drag_hold_job = event.widget.after(
      self.drag_delay_ms,
      self.begin_queued_drag
    )

  def begin_queued_drag(self):
    if self.pending_drag_event is None:
      return

    self.drag_started = True

    self.start_drag(
      self.pending_drag_event,
      self.pending_drag_index,
      self.pending_drag_char
    )

  def cancel_queued_drag(self):
    if self.drag_hold_job is not None:
      try:
        self.canvas.after_cancel(self.drag_hold_job)
      except TclError:
        pass

    self.drag_hold_job = None
    self.pending_drag_event = None
    self.pending_drag_index = None
    self.pending_drag_char = None

  def start_drag(self, event, index, char):
    self.drag_start_index = index
    self.dragged_original_card = self.card_widgets[index]

    self.dragged_original_card.config(
      highlightthickness=3,
      highlightbackground="#f5d76e",
      highlightcolor="#f5d76e"
    )

    self.create_floating_card(char)
    self.move_floating_card(event)

  def drag_motion(self, event):
    if not self.drag_started:
      return

    if self.floating_card is None:
      return

    self.move_floating_card(event)
    self.update_autoscroll(event)

  def update_autoscroll(self, event):
    canvas_top = self.canvas.winfo_rooty()
    canvas_bottom = canvas_top + self.canvas.winfo_height()
    mouse_y = event.y_root

    if mouse_y < canvas_top + self.autoscroll_margin:
      self.start_autoscroll(-1)
    elif mouse_y > canvas_bottom - self.autoscroll_margin:
      self.start_autoscroll(1)
    else:
      self.stop_autoscroll()

  def start_autoscroll(self, direction):
    self.autoscroll_direction = direction

    if self.autoscroll_job is None:
      self.autoscroll()

  def autoscroll(self):
    if self.autoscroll_direction == 0:
      self.autoscroll_job = None
      return

    first_visible, last_visible = self.canvas.yview()

    if self.autoscroll_direction < 0 and first_visible <= 0:
      self.stop_autoscroll()
      return

    if self.autoscroll_direction > 0 and last_visible >= 1:
      self.stop_autoscroll()
      return

    self.canvas.yview_scroll(
      self.autoscroll_direction * self.autoscroll_units,
      "units"
    )

    self.autoscroll_job = self.canvas.after(
      self.autoscroll_delay,
      self.autoscroll
    )

  def stop_autoscroll(self):
    self.autoscroll_direction = 0

    if self.autoscroll_job is not None:
      try:
        self.canvas.after_cancel(self.autoscroll_job)
      except TclError:
        pass

      self.autoscroll_job = None

  def finish_drag(self, event):
    if not self.drag_started:
      self.cancel_queued_drag()
      return

    self.stop_autoscroll()

    if self.drag_start_index is None:
      self.cancel_queued_drag()
      self.drag_started = False
      return

    target_widget = event.widget.winfo_containing(event.x_root, event.y_root)
    target_index = self.find_card_index(target_widget)

    if target_index is None:
      target_index = self.find_edge_drop_index(event)

    self.destroy_floating_card()

    if self.dragged_original_card is not None:
      try:
        self.dragged_original_card.config(highlightthickness=0)
      except TclError:
        pass

    if target_index is not None and self.on_reorder is not None:
      self.on_reorder(self.drag_start_index, target_index)

    self.drag_start_index = None
    self.dragged_original_card = None
    self.cancel_queued_drag()
    self.drag_started = False

  def create_floating_card(self, char):
    self.destroy_floating_card()

    self.floating_card = tk.Frame(
      self.canvas,
      relief=tk.RAISED,
      borderwidth=4,
      padx=18,
      pady=14,
      bg="#f4efe1"
    )

    tk.Label(
      self.floating_card,
      text=char.name,
      font=(self.font_family, 16, "bold"),
      anchor="w",
      bg="#f4efe1"
    ).pack(anchor="w")

    tk.Label(
      self.floating_card,
      text=f"Type: {char.chType}",
      font=("Arial", 12),
      anchor="w",
      bg="#f4efe1"
    ).pack(anchor="w")

    tk.Label(
      self.floating_card,
      text=f"Initiative: {m.floor(char.initiative)}",
      font=("Arial", 12),
      anchor="w",
      bg="#f4efe1"
    ).pack(anchor="w")

    self.floating_window = self.canvas.create_window(
      0,
      0,
      window=self.floating_card,
      anchor="nw"
    )

    self.canvas.tag_raise(self.floating_window)

  def move_floating_card(self, event):
    if self.floating_window is None:
      return

    canvas_x = self.canvas.canvasx(event.x_root - self.canvas.winfo_rootx())
    canvas_y = self.canvas.canvasy(event.y_root - self.canvas.winfo_rooty())

    self.canvas.coords(
      self.floating_window,
      canvas_x + 12,
      canvas_y + 12
    )

  def destroy_floating_card(self):
    if self.floating_window is not None:
      try:
        self.canvas.delete(self.floating_window)
      except TclError:
        pass

      self.floating_window = None

    if self.floating_card is not None:
      try:
        self.floating_card.destroy()
      except TclError:
        pass

      self.floating_card = None

  def clear_display_widgets(self):
    self.stop_autoscroll()
    self.cancel_queued_drag()
    self.destroy_floating_card()

    for widget in list(self.card_widgets):
      try:
        widget.destroy()
      except TclError:
        pass

    for window_id in list(self.card_window_ids):
      try:
        self.canvas.delete(window_id)
      except TclError:
        pass

    if self.title_item_id is not None:
      try:
        self.canvas.delete(self.title_item_id)
      except TclError:
        pass

    try:
      self.canvas.delete("empty_text")
    except TclError:
      pass

    self.card_widgets = []
    self.card_window_ids = []
    self.card_images = []
    self.title_item_id = None

  def find_card_index(self, widget):
    while widget is not None:
      if widget in self.card_widgets:
        return self.card_widgets.index(widget)

      widget = widget.master

    return None

  def find_edge_drop_index(self, event):
    if not self.card_widgets:
      return None

    mouse_y = event.y_root

    first_card = self.card_widgets[0]
    last_card = self.card_widgets[-1]

    first_top = first_card.winfo_rooty()
    last_bottom = last_card.winfo_rooty() + last_card.winfo_height()

    if mouse_y < first_top:
      return 0

    if mouse_y > last_bottom:
      return len(self.card_widgets) - 1

    return None

  def bind_drag_events(self, widget, index, char):
    widget.bind(
      "<ButtonPress-1>",
      lambda event, i=index, c=char: self.queue_drag(event, i, c)
    )
    widget.bind("<B1-Motion>", self.drag_motion)
    widget.bind("<ButtonRelease-1>", self.finish_drag)

  def draw_card_background(self, card_canvas, width, height, char):
    card_canvas.delete("background")

    border_image = self.get_border_image(char)

    if border_image is not None:
      resized = border_image.resize((width, height))
      card_image = ImageTk.PhotoImage(resized)

      self.card_images.append(card_image)

      card_canvas.create_image(
        0,
        0,
        image=card_image,
        anchor="nw",
        tags="background"
      )

    else:
      card_canvas.create_rectangle(
        0,
        0,
        width,
        height,
        fill="#f4efe1",
        outline="#9d7a35",
        width=3,
        tags="background"
      )

    card_canvas.tag_lower("background")

  def hide_status_tooltip(self):
    if self.status_tooltip is not None:
      try:
        self.status_tooltip.destroy()
      except TclError:
        pass

      self.status_tooltip = None

  def show_status_tooltip(self, card_canvas, text):
    self.hide_status_tooltip()

    tooltip = tk.Toplevel(card_canvas)
    tooltip.wm_overrideredirect(True)
    tooltip.attributes("-topmost", True)
    tooltip.configure(bg="#1d1d1d")

    label = tk.Label(
      tooltip,
      text=text,
      justify=tk.LEFT,
      bg="#1d1d1d",
      fg="white",
      relief=tk.SOLID,
      borderwidth=1,
      padx=8,
      pady=5,
      font=("Arial", 9)
    )
    label.pack()

    x = card_canvas.winfo_pointerx() + 14
    y = card_canvas.winfo_pointery() + 14
    tooltip.geometry(f"+{x}+{y}")

    self.status_tooltip = tooltip

  def create_badge(
    self,
    card_canvas,
    x,
    y,
    text,
    hover_text,
    tag,
    remove_callback
  ):
    text_width = max(
      90,
      len(text) * 7 + 32
    )
    height = 24

    card_canvas.create_rectangle(
      x,
      y,
      x + text_width,
      y + height,
      fill="#e8dcc0",
      outline="#7a5b2e",
      width=1,
      tags=(tag, "status_badge")
    )

    card_canvas.create_text(
      x + 8,
      y + 12,
      text=text,
      anchor="w",
      fill="#1f1609",
      font=("Arial", 9, "bold"),
      tags=(tag, "status_badge")
    )

    remove = card_canvas.create_text(
      x + text_width - 12,
      y + 12,
      text="✕",
      anchor="center",
      fill="#9b0000",
      font=("Arial", 10, "bold"),
      state=tk.HIDDEN,
      tags=(
        tag,
        "status_badge",
        "remove_status"
      )
    )

    def show_hover(event):
      card_canvas.itemconfig(
        remove,
        state=tk.NORMAL
      )
      self.show_status_tooltip(
        card_canvas,
        hover_text
      )

    def hide_hover(event):
      card_canvas.itemconfig(
        remove,
        state=tk.HIDDEN
      )
      self.hide_status_tooltip()

    def remove_this_status(event):
      self.hide_status_tooltip()
      remove_callback()

    card_canvas.tag_bind(
      tag,
      "<Enter>",
      show_hover
    )
    card_canvas.tag_bind(
      tag,
      "<Leave>",
      hide_hover
    )
    card_canvas.tag_bind(
      remove,
      "<Button-1>",
      remove_this_status
    )

    return text_width + 8

  def get_status_trigger_name(self, state, status):
    trigger_id = status.get(
      "trigger_character_id"
    )

    for char in state.combat:
      if getattr(char, "combat_id", None) == trigger_id:
        return char.name

    return status.get(
      "trigger_character_name",
      "Unknown"
    )

  def draw_temp_status_badges(
    self,
    card_canvas,
    char,
    index,
    state,
    y,
    secondary_color
  ):
    width = self.card_width
    statuses = getattr(char, "status", [])

    if statuses and not isinstance(
      statuses[0],
      dict
    ):
      converted = []

      for old_index in range(
        0,
        len(statuses),
        3
      ):
        if old_index + 2 >= len(statuses):
          break

        old_trigger_index = statuses[
          old_index + 2
        ]
        trigger_id = None
        trigger_name = "Unknown"

        if (
          isinstance(
            old_trigger_index,
            int
          )
          and 0
          <= old_trigger_index
          < len(state.combat)
        ):
          trigger_char = state.combat[
            old_trigger_index
          ]
          trigger_id = getattr(
            trigger_char,
            "combat_id",
            None
          )
          trigger_name = trigger_char.name

        converted.append({
          "name": statuses[old_index],
          "remaining_triggers": statuses[
            old_index + 1
          ],
          "trigger_character_id": trigger_id,
          "trigger_character_name": trigger_name,
          "trigger_phase": "end_turn",
          "skip_next_trigger": False
        })

      char.status = converted
      statuses = converted

    if not statuses:
      card_canvas.create_text(
        width // 2,
        y + 18,
        text="None",
        anchor="center",
        fill=secondary_color,
        font=("Arial", 10),
        tags="content"
      )
      return y + 38

    x = 40
    current_y = y

    for status_index, status in enumerate(
      statuses
    ):
      try:
        remaining = int(
          status.get(
            "remaining_triggers",
            1
          )
        )
      except (TypeError, ValueError):
        remaining = 1

      effect = status.get("name", "")
      trigger_name = self.get_status_trigger_name(
        state,
        status
      )
      trigger_phase = status.get(
        "trigger_phase",
        "end_turn"
      )
      phase_text = (
        "Start"
        if trigger_phase == "start_turn"
        else "End"
      )

      status_text = (
        f"{effect}: {remaining} round"
        f"{'' if remaining == 1 else 's'}"
      )

      hover_text = (
        f"Ends on: {phase_text} of "
        f"{trigger_name}'s turn"
      )

      tag = (
        f"status_{index}_{status_index}"
      )

      added_width = self.create_badge(
        card_canvas,
        x,
        current_y,
        status_text,
        hover_text,
        tag,
        lambda i=index, s=status_index: self.remove_temp_status_click(i, s)
      )
      x += added_width

      if x > width - 150:
        x = 40
        current_y += 30

    return current_y + 34

  def draw_permanent_status_badges(self, card_canvas, char, index, y, secondary_color):
    width = self.card_width
    permanent_statuses = getattr(char, "permanent_statuses", [])

    if not permanent_statuses:
      card_canvas.create_text(
        width // 2,
        y + 18,
        text="None",
        anchor="center",
        fill=secondary_color,
        font=("Arial", 10),
        tags="content"
      )
      return y + 38

    x = 40
    current_y = y

    for status_index, status in enumerate(permanent_statuses):
      name = status.get("name", "")

      trigger = status.get("trigger", "none")
      effect = status.get("effect", "none")
      amount = status.get("amount", 0)

      if trigger == "none" or effect == "none":
        status_text = name
      else:
        status_text = f"{name}: {effect} {amount}"

      hover_text = f"{name} | Trigger: {trigger} | Effect: {effect} {amount}"
      tag = f"perm_{index}_{status_index}"

      added_width = self.create_badge(
        card_canvas,
        x,
        current_y,
        status_text,
        hover_text,
        tag,
        lambda i=index, s=status_index: self.remove_permanent_status_click(i, s)
      )
      x += added_width

      if x > width - 150:
        x = 40
        current_y += 30

    return current_y + 34

  def remove_temp_status_click(self, character_index, status_index):
    if self.on_remove_status is not None:
      self.on_remove_status(character_index, status_index)

  def remove_permanent_status_click(self, character_index, status_index):
    if self.on_remove_permanent_status is not None:
      self.on_remove_permanent_status(character_index, status_index)

  def add_death_save_click(self, character_index, result):
    if self.on_death_save is not None:
      self.on_death_save(character_index, result)

  def draw_death_saves(self, card_canvas, char, index, width):
    death_text = f"Death Saves: ✓ {char.death_successes}/3 | ✕ {char.death_fails}/3"

    card_canvas.create_text(
      width // 2,
      168,
      text=death_text,
      anchor="center",
      fill="#ffdddd",
      font=("Arial", 10, "bold"),
      tags=("content", f"death_text_{index}")
    )

    death_buttons = [
      {
        "tag": f"death_stabilize_{index}",
        "text": "Stabilize",
        "x": width // 2 - 128,
        "result": "stabilize",
        "fill": "#b8ffb8"
      },
      {
        "tag": f"death_crit_success_{index}",
        "text": "Crit Success",
        "x": width // 2 - 64,
        "result": "crit_success",
        "fill": "#b8ffb8"
      },
      {
        "tag": f"death_success_{index}",
        "text": "Success",
        "x": width // 2,
        "result": "success",
        "fill": "#d7ffd7"
      },
      {
        "tag": f"death_fail_{index}",
        "text": "Fail",
        "x": width // 2 + 64,
        "result": "fail",
        "fill": "#ffd0d0"
      },
      {
        "tag": f"death_crit_fail_{index}",
        "text": "Crit Fail",
        "x": width // 2 + 128,
        "result": "crit_fail",
        "fill": "#ffaaaa"
      }
    ]

    for button in death_buttons:
      card_canvas.create_text(
        button["x"],
        190,
        text=button["text"],
        anchor="center",
        fill=button["fill"],
        font=("Arial", 8, "bold"),
        tags=("content", button["tag"])
      )

      card_canvas.tag_bind(
        button["tag"],
        "<Button-1>",
        lambda event, i=index, r=button["result"]: self.add_death_save_click(i, r)
      )

  def draw_card_content(self, card_canvas, char, index, state):
    card_canvas.delete("content")
    card_canvas.delete("status_badge")

    colors = self.get_card_text_colors(char)

    primary_color = colors["primary"]
    secondary_color = colors["secondary"]
    line_color = colors["line"]

    width = self.card_width

    name_text = f"▶ {char.name}" if index == state.curr else char.name

    card_canvas.create_text(
      width // 2,
      48,
      text=name_text,
      anchor="center",
      fill=primary_color,
      font=(self.font_family, 17, "bold"),
      tags="content"
    )

    card_canvas.create_text(
      width // 2,
      78,
      text=f"Initiative {m.floor(char.initiative)}",
      anchor="center",
      fill=primary_color,
      font=(self.font_family, 14, "bold"),
      tags="content"
    )

    card_canvas.create_text(
      width // 2,
      106,
      text=f"Type: {char.chType}",
      anchor="center",
      fill=secondary_color,
      font=("Arial", 11, "bold"),
      tags="content"
    )

    max_hp = getattr(char, "max_hp", "")
    current_hp = getattr(char, "current_hp", "")

    try:
      temp_hp = int(
        getattr(char, "temp_hp", 0) or 0
      )
    except (TypeError, ValueError):
      temp_hp = 0

    if max_hp:
      hp_text = (
        f"HP: {current_hp}/{max_hp}"
        if current_hp != ""
        else f"HP: {max_hp}"
      )
    else:
      hp_text = "HP: —"

    if temp_hp > 0:
      hp_text += f" | Temp: {temp_hp}"

    hp_tag = f"hp_{index}"

    hp_item = card_canvas.create_text(
      width // 2,
      134,
      text=hp_text,
      anchor="center",
      fill=secondary_color,
      font=("Arial", 11, "bold"),
      tags=("content", hp_tag)
    )

    hp_bbox = card_canvas.bbox(hp_item)

    if hp_bbox is not None:
      pad_x = 10
      pad_y = 5

      hp_button = card_canvas.create_rectangle(
        hp_bbox[0] - pad_x,
        hp_bbox[1] - pad_y,
        hp_bbox[2] + pad_x,
        hp_bbox[3] + pad_y,
        outline="#b8914b",
        width=1,
        tags=("content", hp_tag)
      )

      card_canvas.tag_lower(hp_button, hp_item)

    def open_hp_adjust(event):
      if self.on_adjust_hp is not None:
        self.on_adjust_hp(index)

    card_canvas.tag_bind(hp_tag, "<Button-1>", open_hp_adjust)
    card_canvas.tag_bind(hp_tag, "<Enter>", lambda event: card_canvas.config(cursor="hand2"))
    card_canvas.tag_bind(hp_tag, "<Leave>", lambda event: card_canvas.config(cursor=""))

    try:
      current_hp_value = int(getattr(char, "current_hp", 0) or 0)
    except ValueError:
      current_hp_value = 0

    death_save_active = char.chType in ["PC", "SPC"] and current_hp_value <= 0 and getattr(char, "max_hp", "")

    if death_save_active:
      self.draw_death_saves(card_canvas, char, index, width)
      line_y = 210
      status_title_y = 228
      status_badge_y = 248
    else:
      line_y = 158
      status_title_y = 176
      status_badge_y = 196

    card_canvas.create_line(
      48,
      line_y,
      width - 48,
      line_y,
      fill=line_color,
      width=1,
      tags="content"
    )

    card_canvas.create_text(
      width // 2,
      status_title_y,
      text="Temporary Statuses",
      anchor="center",
      fill=primary_color,
      font=("Arial", 10, "bold"),
      tags="content"
    )

    try:
      next_y = self.draw_temp_status_badges(
        card_canvas,
        char,
        index,
        state,
        status_badge_y,
        secondary_color
      )
    except Exception:
      card_canvas.create_text(
        width // 2,
        status_badge_y + 18,
        text="Status display error",
        anchor="center",
        fill=secondary_color,
        font=("Arial", 9),
        tags="content"
      )
      next_y = status_badge_y + 38

    card_canvas.create_text(
      width // 2,
      next_y,
      text="Permanent Statuses",
      anchor="center",
      fill=primary_color,
      font=("Arial", 10, "bold"),
      tags="content"
    )

    try:
      self.draw_permanent_status_badges(
        card_canvas,
        char,
        index,
        next_y + 20,
        secondary_color
      )
    except Exception:
      card_canvas.create_text(
        width // 2,
        next_y + 38,
        text="Permanent status display error",
        anchor="center",
        fill=secondary_color,
        font=("Arial", 9),
        tags="content"
      )

  def display_combat_cards(
    self,
    state,
    background_color=None,
    background_image_path=None,
    font_family=None,
    border_choices=None
  ):
    if background_color is not None:
      self.set_background_color(background_color)

    self.set_background_image(background_image_path)
    self.set_border_choices(border_choices)

    if font_family is not None:
      self.set_font_family(font_family)

    self.clear_display_widgets()
    self.draw_background_image()

    canvas_width = max(1, self.canvas.winfo_width())
    left_margin = 10
    top_margin = 10
    title_height = 30

    if not state.combat:
      self.title_item_id = self.canvas.create_text(
        left_margin,
        top_margin,
        text="No characters loaded.",
        anchor="nw",
        fill="white",
        font=("Arial", 14, "bold"),
        tags="empty_text"
      )

      self.canvas.configure(scrollregion=(0, 0, canvas_width, 120))
      self.canvas.yview_moveto(0)
      self.draw_background_image()
      return

    self.title_item_id = self.canvas.create_text(
      left_margin,
      top_margin,
      text=f"Round {state.round} | Turn {state.curr + 1} | Total Turn {state.turns + 1}",
      anchor="nw",
      fill="white",
      font=("Arial", 14, "bold")
    )

    usable_width = max(1, canvas_width - 20)
    card_total_width = self.card_width + self.card_padx * 2
    cards_per_row = max(1, usable_width // card_total_width)

    start_y = top_margin + title_height
    max_bottom = start_y

    for index, char in enumerate(state.combat):
      row = index // cards_per_row
      column = index % cards_per_row

      x = left_margin + self.card_padx + column * card_total_width
      y = start_y + self.card_pady + row * (self.card_height + self.card_pady * 2)

      card = tk.Canvas(
        self.canvas,
        width=self.card_width,
        height=self.card_height,
        bg=self.background_color,
        highlightthickness=0,
        bd=0
      )

      self.card_widgets.append(card)

      window_id = self.canvas.create_window(
        x,
        y,
        window=card,
        anchor="nw"
      )
      self.card_window_ids.append(window_id)

      self.bind_drag_events(card, index, char)
      self.draw_card_background(
        card,
        self.card_width,
        self.card_height,
        char
      )
      self.draw_card_content(card, char, index, state)

      max_bottom = max(max_bottom, y + self.card_height + self.card_pady)

    total_height = max(max_bottom + 20, self.canvas.winfo_height())
    self.canvas.configure(scrollregion=(0, 0, canvas_width, total_height))
    self.canvas.yview_moveto(0)
    self.draw_background_image()
