import math as m
import tkinter as tk
from pathlib import Path
from tkinter import TclError

from Status_Effects import get_status_text

try:
  from PIL import Image, ImageTk
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

    self.scrollable_frame = tk.Frame(self.canvas, bg=self.background_color)

    self.scrollable_frame.bind(
      "<Configure>",
      lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    )

    self.canvas_window = self.canvas.create_window(
      (0, 0),
      window=self.scrollable_frame,
      anchor="nw"
    )

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

    self.border_image = None
    self.card_images = []

    self.load_border_image()

  def load_border_image(self):
    if not PIL_AVAILABLE:
      return

    folder = Path(__file__).resolve().parent

    possible_files = [
      folder / "border.jpg",
      folder / "border.jpeg",
      folder / "border.png"
    ]

    image_path = None

    for possible_file in possible_files:
      if possible_file.exists():
        image_path = possible_file
        break

    if image_path is None:
      return

    try:
      self.border_image = Image.open(image_path)
    except Exception:
      self.border_image = None

  def set_background_color(self, color):
    self.background_color = color
    self.outer_frame.config(bg=color)
    self.canvas.config(bg=color)
    self.scrollable_frame.config(bg=color)

  def set_font_family(self, font_family):
    self.font_family = font_family

  def resize_scrollable_frame(self, event):
    self.canvas.itemconfig(self.canvas_window, width=event.width)
    self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    first_visible, last_visible = self.canvas.yview()

    if first_visible < 0:
      self.canvas.yview_moveto(0)

    if last_visible > 1:
      self.canvas.yview_moveto(1)

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
      self.dragged_original_card.config(highlightthickness=0)

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

    statuses = get_status_text(char)
    status_text = "Statuses: " + ", ".join(statuses) if statuses else "Statuses: None"

    tk.Label(
      self.floating_card,
      text=status_text,
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

    for widget in list(self.scrollable_frame.winfo_children()):
      try:
        widget.destroy()
      except TclError:
        pass

    self.card_widgets = []
    self.card_images = []

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

  def draw_card_background(self, card_canvas, width, height):
    card_canvas.delete("background")

    if self.border_image is not None:
      resized = self.border_image.resize((width, height))
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

  def get_status_end_turn_name(self, state, applied_turn_index):
    if not state.combat:
      return "Unknown"

    if applied_turn_index < 0 or applied_turn_index >= len(state.combat):
      return "Unknown"

    return state.combat[applied_turn_index].name

  def create_status_badge(self, card_canvas, x, y, status_text, end_turn_name, character_index, status_index):
    text_width = max(90, len(status_text) * 7 + 32)
    height = 24

    tag = f"status_{character_index}_{status_index}"

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

    label = card_canvas.create_text(
      x + 8,
      y + 12,
      text=status_text,
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
      tags=(tag, "status_badge", "remove_status")
    )

    def show_remove(event):
      hover_text = f"{status_text} | Ends on: {end_turn_name}"
      card_canvas.itemconfig(remove, state=tk.NORMAL)
      card_canvas.itemconfig(label, text=hover_text)

    def hide_remove(event):
      card_canvas.itemconfig(remove, state=tk.HIDDEN)
      card_canvas.itemconfig(label, text=status_text)

    def remove_this_status(event):
      if self.on_remove_status is not None:
        self.on_remove_status(character_index, status_index)

    card_canvas.tag_bind(tag, "<Enter>", show_remove)
    card_canvas.tag_bind(tag, "<Leave>", hide_remove)
    card_canvas.tag_bind(remove, "<Button-1>", remove_this_status)

    return text_width + 8

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

    width = self.card_width

    name_text = f"▶ {char.name}" if index == state.curr else char.name

    card_canvas.create_text(
      width // 2,
      48,
      text=name_text,
      anchor="center",
      fill="#f8f0dc",
      font=(self.font_family, 17, "bold"),
      tags="content"
    )

    card_canvas.create_text(
      width // 2,
      78,
      text=f"Initiative {m.floor(char.initiative)}",
      anchor="center",
      fill="#f8f0dc",
      font=(self.font_family, 14, "bold"),
      tags="content"
    )

    card_canvas.create_text(
      width // 2,
      106,
      text=f"Type: {char.chType}",
      anchor="center",
      fill="#e7d6b0",
      font=("Arial", 11, "bold"),
      tags="content"
    )

    max_hp = getattr(char, "max_hp", "")
    current_hp = getattr(char, "current_hp", "")

    if max_hp:
      hp_text = f"HP: {current_hp}/{max_hp}" if current_hp != "" else f"HP: {max_hp}"
    else:
      hp_text = "HP: —"

    hp_tag = f"hp_{index}"

    hp_item = card_canvas.create_text(
      width // 2,
      134,
      text=hp_text,
      anchor="center",
      fill="#e7d6b0",
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
      status_title_y = 236
      status_badge_y = 258
    else:
      line_y = 162
      status_title_y = 192
      status_badge_y = 214

    card_canvas.create_line(
      48,
      line_y,
      width - 48,
      line_y,
      fill="#b8914b",
      width=1,
      tags="content"
    )

    card_canvas.create_text(
      width // 2,
      status_title_y,
      text="Statuses",
      anchor="center",
      fill="#f8f0dc",
      font=("Arial", 11, "bold"),
      tags="content"
    )

    status_count = len(char.status) // 3
    permanent_statuses = getattr(char, "permanent_statuses", [])

    x = 40
    y = status_badge_y

    if status_count == 0:
      card_canvas.create_text(
        width // 2,
        y + 18,
        text="None",
        anchor="center",
        fill="#d7c397",
        font=("Arial", 10),
        tags="content"
      )
      y += 44

    else:
      for status_index in range(status_count):
        effect = char.status[3 * status_index]
        duration = char.status[3 * status_index + 1]
        applied_turn_index = char.status[3 * status_index + 2]
        status_text = f"{effect}: {duration} rounds"
        end_turn_name = self.get_status_end_turn_name(state, applied_turn_index)

        added_width = self.create_status_badge(
          card_canvas,
          x,
          y,
          status_text,
          end_turn_name,
          index,
          status_index
        )
        x += added_width

        if x > width - 150:
          x = 40
          y += 30

      y += 36

    card_canvas.create_text(
      width // 2,
      y,
      text="Permanent Statuses",
      anchor="center",
      fill="#f8f0dc",
      font=("Arial", 10, "bold"),
      tags="content"
    )

    y += 22
    x = 40

    if not permanent_statuses:
      card_canvas.create_text(
        width // 2,
        y + 18,
        text="None",
        anchor="center",
        fill="#d7c397",
        font=("Arial", 10),
        tags="content"
      )

    else:
      for perm_index, perm_status in enumerate(permanent_statuses):
        name = perm_status.get("name", "Permanent")
        trigger = perm_status.get("trigger", "none")
        effect = perm_status.get("effect", "none")
        amount = perm_status.get("amount", 0)

        if trigger == "none" or effect == "none":
          status_text = name
        else:
          status_text = f"{name}: {effect} {amount}"

        text_width = max(90, len(status_text) * 7 + 32)
        tag = f"perm_{index}_{perm_index}"

        card_canvas.create_rectangle(
          x,
          y,
          x + text_width,
          y + 24,
          fill="#e8dcc0",
          outline="#7a5b2e",
          width=1,
          tags=(tag, "status_badge")
        )

        card_canvas.create_text(
          x + 8,
          y + 12,
          text=status_text,
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
          tags=(tag, "status_badge")
        )

        card_canvas.tag_bind(
          remove,
          "<Button-1>",
          lambda event, i=index, s=perm_index: self.remove_permanent_status_click(i, s)
        )

        x += text_width + 8

        if x > width - 150:
          x = 40
          y += 30

  def configure_card(self, event, card_canvas, char, index, state):
    self.draw_card_background(card_canvas, self.card_width, self.card_height)
    self.draw_card_content(card_canvas, char, index, state)

  def display_combat_cards(self, state, background_color=None, font_family=None):
    if background_color is not None:
      self.set_background_color(background_color)

    if font_family is not None:
      self.set_font_family(font_family)

    self.clear_display_widgets()

    if not state.combat:
      title = tk.Label(
        self.scrollable_frame,
        text="No characters loaded.",
        font=("Arial", 14, "bold"),
        bg=self.background_color,
        fg="white"
      )
      title.grid(row=0, column=0, sticky="w", pady=5)
      self.canvas.update_idletasks()
      self.canvas.configure(scrollregion=self.canvas.bbox("all"))
      self.canvas.yview_moveto(0)
      return

    title = tk.Label(
      self.scrollable_frame,
      text=f"Round {state.round} | Turn {state.curr + 1} | Total Turn {state.turns + 1}",
      font=("Arial", 14, "bold"),
      bg=self.background_color,
      fg="white"
    )
    title.grid(row=0, column=0, columnspan=99, sticky="w", pady=5)

    available_width = max(self.canvas.winfo_width(), self.card_width)
    cards_per_row = max(1, available_width // (self.card_width + self.card_padx * 2))

    for index, char in enumerate(state.combat):
      row = index // cards_per_row
      column = index % cards_per_row

      card = tk.Canvas(
        self.scrollable_frame,
        width=self.card_width,
        height=self.card_height,
        bg=self.background_color,
        highlightthickness=0
      )
      card.grid(
        row=row + 1,
        column=column,
        padx=self.card_padx,
        pady=self.card_pady,
        sticky="n"
      )

      self.card_widgets.append(card)

      self.bind_drag_events(card, index, char)
      self.draw_card_background(card, self.card_width, self.card_height)
      self.draw_card_content(card, char, index, state)

    self.canvas.update_idletasks()
    self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    self.canvas.yview_moveto(0)
