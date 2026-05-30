import math as m
import tkinter as tk

from Status_Effects import get_status_text


class CombatCardDisplay:
  def __init__(self, root, on_reorder=None, background_color="black"):
    self.background_color = background_color

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

  def set_background_color(self, color):
    self.background_color = color
    self.outer_frame.config(bg=color)
    self.canvas.config(bg=color)
    self.scrollable_frame.config(bg=color)

  def resize_scrollable_frame(self, event):
    self.canvas.itemconfig(self.canvas_window, width=event.width)

  def on_mousewheel(self, event):
    self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

  def start_drag(self, event, index, char):
    self.drag_start_index = index
    self.dragged_original_card = self.card_widgets[index]

    self.dragged_original_card.config(
      relief=tk.SOLID,
      borderwidth=4,
      padx=14,
      pady=12
    )

    self.create_floating_card(char)
    self.move_floating_card(event)

  def drag_motion(self, event):
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
      self.canvas.after_cancel(self.autoscroll_job)
      self.autoscroll_job = None

  def finish_drag(self, event):
    self.stop_autoscroll()

    if self.drag_start_index is None:
      return

    target_widget = event.widget.winfo_containing(event.x_root, event.y_root)
    target_index = self.find_card_index(target_widget)

    if target_index is None:
      target_index = self.find_edge_drop_index(event)

    self.destroy_floating_card()

    if self.dragged_original_card is not None:
      self.dragged_original_card.config(
        relief=tk.RIDGE,
        borderwidth=2,
        padx=10,
        pady=8
      )

    if target_index is not None and self.on_reorder is not None:
      self.on_reorder(self.drag_start_index, target_index)

    self.drag_start_index = None
    self.dragged_original_card = None

  def create_floating_card(self, char):
    self.destroy_floating_card()

    self.floating_card = tk.Frame(
      self.canvas,
      relief=tk.RAISED,
      borderwidth=4,
      padx=18,
      pady=14,
      bg="white"
    )

    tk.Label(
      self.floating_card,
      text=char.name,
      font=("Arial", 16, "bold"),
      anchor="w",
      bg="white"
    ).pack(anchor="w")

    tk.Label(
      self.floating_card,
      text=f"Type: {char.chType}",
      font=("Arial", 12),
      anchor="w",
      bg="white"
    ).pack(anchor="w")

    tk.Label(
      self.floating_card,
      text=f"Initiative: {m.floor(char.initiative)}",
      font=("Arial", 12),
      anchor="w",
      bg="white"
    ).pack(anchor="w")

    statuses = get_status_text(char)
    status_text = "Statuses: " + ", ".join(statuses) if statuses else "Statuses: None"

    tk.Label(
      self.floating_card,
      text=status_text,
      font=("Arial", 12),
      anchor="w",
      bg="white"
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
      self.canvas.delete(self.floating_window)
      self.floating_window = None

    if self.floating_card is not None:
      self.floating_card.destroy()
      self.floating_card = None

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
      lambda event, i=index, c=char: self.start_drag(event, i, c)
    )
    widget.bind("<B1-Motion>", self.drag_motion)
    widget.bind("<ButtonRelease-1>", self.finish_drag)

  def display_combat_cards(self, state, background_color=None):
    if background_color is not None:
      self.set_background_color(background_color)

    for widget in self.scrollable_frame.winfo_children():
      widget.destroy()

    self.card_widgets = []

    if not state.combat:
      title = tk.Label(
        self.scrollable_frame,
        text="No characters loaded.",
        font=("Arial", 14, "bold"),
        bg=self.background_color,
        fg="white"
      )
      title.pack(anchor="w", pady=5)
      return

    title = tk.Label(
      self.scrollable_frame,
      text=f"Round {state.round} | Turn {state.curr + 1} | Total Turn {state.turns + 1}",
      font=("Arial", 14, "bold"),
      bg=self.background_color,
      fg="white"
    )
    title.pack(anchor="w", pady=5)

    for index, char in enumerate(state.combat):
      card = tk.Frame(
        self.scrollable_frame,
        relief=tk.RIDGE,
        borderwidth=2,
        padx=10,
        pady=8,
        bg="white"
      )
      card.pack(fill=tk.X, pady=5)

      self.card_widgets.append(card)
      self.bind_drag_events(card, index, char)

      name_text = f"▶ {char.name}" if index == state.curr else char.name

      name_label = tk.Label(
        card,
        text=name_text,
        font=("Arial", 13, "bold"),
        anchor="w",
        cursor="hand2",
        bg="white"
      )
      name_label.pack(anchor="w")

      type_label = tk.Label(
        card,
        text=f"Type: {char.chType}",
        anchor="w",
        cursor="hand2",
        bg="white"
      )
      type_label.pack(anchor="w")

      initiative_label = tk.Label(
        card,
        text=f"Initiative: {m.floor(char.initiative)}",
        anchor="w",
        cursor="hand2",
        bg="white"
      )
      initiative_label.pack(anchor="w")

      statuses = get_status_text(char)
      status_text = "Statuses: " + ", ".join(statuses) if statuses else "Statuses: None"

      status_label = tk.Label(
        card,
        text=status_text,
        anchor="w",
        cursor="hand2",
        bg="white"
      )
      status_label.pack(anchor="w")

      self.bind_drag_events(name_label, index, char)
      self.bind_drag_events(type_label, index, char)
      self.bind_drag_events(initiative_label, index, char)
      self.bind_drag_events(status_label, index, char)
