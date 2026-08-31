import tkinter as tk
from tkinter import filedialog, messagebox

from Add_Characters_Window import AddCharactersWindow
from Combat_State import CombatState
from Display_Combat import CombatCardDisplay
from HP_Window import HPWindow
from Load_Players_Window import LoadPlayersWindow
from Player_Storage import load_players_from_csv, save_players_to_csv
from Save_Load_Combat import load_combat_from_csv, save_combat_to_csv
from Status_Effects import (
  add_permanent_status,
  add_status,
  apply_permanent_statuses_for_turn,
  remove_permanent_status,
  remove_status,
  tick_statuses_for_turn
)
from Status_Window import StatusWindow


BACKGROUND_COLORS = [
  "black",
  "gray10",
  "gray15",
  "gray20",
  "dark slate gray",
  "slate gray",
  "dim gray",
  "navy",
  "midnight blue",
  "royal blue4",
  "purple4",
  "indigo",
  "maroon",
  "firebrick4",
  "dark red",
  "saddle brown",
  "sienna4",
  "dark olive green",
  "dark green",
  "forest green",
  "sea green4"
]

FONT_CHOICES = [
  "Georgia",
  "Arial",
  "Times New Roman",
  "Garamond",
  "Cambria",
  "Book Antiqua",
  "Palatino Linotype",
  "Verdana",
  "Trebuchet MS",
  "Courier New"
]

state = CombatState()
selected_background_color = None
selected_font_family = None


def get_mouse_position():
  root.update_idletasks()
  return root.winfo_pointerx(), root.winfo_pointery()


def refresh_display():
  combat_display.display_combat_cards(
    state,
    background_color=selected_background_color.get(),
    font_family=selected_font_family.get()
  )


def start_combat():
  state.sort_combat()
  refresh_display()


def return_to_original_sort():
  state.sort_combat()
  refresh_display()


def next_character():
  current_char = state.current_character()

  if current_char is not None:
    apply_permanent_statuses_for_turn(current_char, "end_turn")
    handle_zero_hp(current_char)

  state.next_character()
  tick_statuses_for_turn(state.combat, state.curr)

  current_char = state.current_character()

  if current_char is not None:
    apply_permanent_statuses_for_turn(current_char, "start_turn")

    try:
      current_hp = int(getattr(current_char, "current_hp", 0) or 0)
    except ValueError:
      current_hp = 0

    if current_hp > 0:
      current_char.death_successes = 0
      current_char.death_fails = 0

    handle_zero_hp(current_char)

  refresh_display()


def reorder_characters(old_index, new_index):
  state.move_character(old_index, new_index)
  refresh_display()


def open_add_characters_window():
  mouse_x, mouse_y = get_mouse_position()

  AddCharactersWindow(
    root,
    add_characters_to_combat,
    background_color=selected_background_color.get(),
    mouse_x=mouse_x,
    mouse_y=mouse_y
  )


def add_characters_to_combat(characters):
  state.add_characters(characters)
  refresh_display()


def open_status_window():
  mouse_x, mouse_y = get_mouse_position()

  StatusWindow(
    root,
    state.combat,
    add_statuses_to_combat,
    background_color=selected_background_color.get(),
    mouse_x=mouse_x,
    mouse_y=mouse_y
  )


def add_statuses_to_combat(statuses):
  for status in statuses:
    if status.get("permanent"):
      add_permanent_status(
        state.combat,
        status["character"],
        status["status"],
        status.get("trigger", "none"),
        status.get("effect", "none"),
        status.get("amount", 0)
      )

    else:
      add_status(
        state.combat,
        status["character"],
        status["status"],
        status["duration"],
        state.curr
      )

  refresh_display()


def clear_status(character_index, status_index):
  remove_status(state.combat, character_index, status_index)
  refresh_display()


def clear_permanent_status(character_index, status_index):
  remove_permanent_status(state.combat, character_index, status_index)
  refresh_display()


def open_hp_window(character_index):
  if character_index < 0 or character_index >= len(state.combat):
    return

  mouse_x, mouse_y = get_mouse_position()

  HPWindow(
    root,
    state.combat[character_index],
    adjust_character_hp,
    background_color=selected_background_color.get(),
    mouse_x=mouse_x,
    mouse_y=mouse_y
  )


def adjust_character_hp(char, amount):
  try:
    current_hp = int(getattr(char, "current_hp", 0) or 0)
  except ValueError:
    current_hp = 0

  try:
    max_hp = int(getattr(char, "max_hp", 0) or 0)
  except ValueError:
    max_hp = 0

  new_hp = current_hp + amount

  if max_hp > 0:
    new_hp = min(new_hp, max_hp)

  new_hp = max(0, new_hp)
  char.current_hp = new_hp

  if new_hp > 0:
    char.death_successes = 0
    char.death_fails = 0

  handle_zero_hp(char)
  refresh_display()


def handle_zero_hp(char):
  try:
    current_hp = int(getattr(char, "current_hp", 0) or 0)
  except ValueError:
    current_hp = 0

  if current_hp != 0:
    return

  if char.chType in ["EN", "NPC"]:
    remove_character(char)
    return

  if char.chType in ["PC", "SPC"]:
    char.death_successes = getattr(char, "death_successes", 0)
    char.death_fails = getattr(char, "death_fails", 0)


def remove_character(char):
  if char not in state.combat:
    return

  index = state.combat.index(char)
  state.remove_character_at_index(index)


def add_death_save(character_index, result):
  if character_index < 0 or character_index >= len(state.combat):
    return

  char = state.combat[character_index]

  if char.chType not in ["PC", "SPC"]:
    return

  try:
    current_hp = int(getattr(char, "current_hp", 0) or 0)
  except ValueError:
    current_hp = 0

  if current_hp > 0:
    return

  if result in ["crit_success", "stabilize"]:
    char.current_hp = 1
    char.death_successes = 0
    char.death_fails = 0
    refresh_display()
    return

  if result == "success":
    char.death_successes += 1

  elif result == "fail":
    char.death_fails += 1

  elif result == "crit_fail":
    char.death_fails += 2

  if char.death_successes >= 3:
    char.current_hp = 1
    char.death_successes = 0
    char.death_fails = 0

  elif char.death_fails >= 3:
    remove_character(char)

  refresh_display()


def save_combat():
  filepath = filedialog.asksaveasfilename(
    title="Save Combat",
    defaultextension=".csv",
    filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
  )

  if not filepath:
    return

  try:
    save_combat_to_csv(filepath, state)
  except Exception as error:
    messagebox.showerror("Save Failed", f"Combat could not be saved:\n{error}")


def load_combat():
  filepath = filedialog.askopenfilename(
    title="Load Combat",
    filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
  )

  if not filepath:
    return

  try:
    loaded_state = load_combat_from_csv(filepath)

    state.load_state(
      loaded_state["combat"],
      loaded_state["round"],
      loaded_state["curr"],
      loaded_state["turns"]
    )

    refresh_display()

  except Exception as error:
    messagebox.showerror("Load Failed", f"Combat could not be loaded:\n{error}")


def save_player_characters():
  filepath = filedialog.asksaveasfilename(
    title="Save Player Characters",
    defaultextension=".csv",
    filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
  )

  if not filepath:
    return

  try:
    save_players_to_csv(filepath, state.combat)
  except Exception as error:
    messagebox.showerror("Save Failed", f"Player characters could not be saved:\n{error}")


def load_player_characters():
  filepath = filedialog.askopenfilename(
    title="Load Player Characters",
    filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
  )

  if not filepath:
    return

  try:
    players = load_players_from_csv(filepath)
    mouse_x, mouse_y = get_mouse_position()

    LoadPlayersWindow(
      root,
      players,
      add_characters_to_combat,
      background_color=selected_background_color.get(),
      mouse_x=mouse_x,
      mouse_y=mouse_y
    )

  except Exception as error:
    messagebox.showerror("Load Failed", f"Player characters could not be loaded:\n{error}")


def change_background_color(*args):
  color = selected_background_color.get()

  root.configure(bg=color)
  button_area.configure(bg=color)
  button_frame.configure(bg=color)
  save_load_frame.configure(bg=color)
  player_storage_frame.configure(bg=color)
  background_label.configure(bg=color)
  font_label.configure(bg=color)

  refresh_display()


def change_font_family(*args):
  refresh_display()


root = tk.Tk(screenName="Combat Tracker", baseName="Tracker", className="Combat Round Tracker", useTk=1)
root.title("Combat Round Tracker")
root.configure(bg="black")

selected_background_color = tk.StringVar(value="black")
selected_font_family = tk.StringVar(value="Georgia")

button_area = tk.Frame(root, bg="black")
button_area.pack(fill=tk.X, padx=10, pady=5)

button_frame = tk.Frame(button_area, bg="black")
button_frame.pack(anchor=tk.CENTER)

start_button = tk.Button(button_frame, text="Start Combat", width=18, command=start_combat)
start_button.pack(side=tk.LEFT, padx=3)

original_sort_button = tk.Button(
  button_frame,
  text="Return to Original Sort",
  width=20,
  command=return_to_original_sort
)
original_sort_button.pack(side=tk.LEFT, padx=3)

add_character_button = tk.Button(button_frame, text="Add Characters", width=18, command=open_add_characters_window)
add_character_button.pack(side=tk.LEFT, padx=3)

next_character_button = tk.Button(button_frame, text="Next Character", width=18, command=next_character)
next_character_button.pack(side=tk.LEFT, padx=3)

status_button = tk.Button(button_frame, text="Add Statuses", width=18, command=open_status_window)
status_button.pack(side=tk.LEFT, padx=3)

background_label = tk.Label(button_frame, text="Background:", bg="black", fg="white")
background_label.pack(side=tk.LEFT, padx=(15, 3))

background_menu = tk.OptionMenu(button_frame, selected_background_color, *BACKGROUND_COLORS, command=change_background_color)
background_menu.config(width=14)
background_menu.pack(side=tk.LEFT, padx=3)

font_label = tk.Label(button_frame, text="Font:", bg="black", fg="white")
font_label.pack(side=tk.LEFT, padx=(15, 3))

font_menu = tk.OptionMenu(button_frame, selected_font_family, *FONT_CHOICES, command=change_font_family)
font_menu.config(width=14)
font_menu.pack(side=tk.LEFT, padx=3)

save_load_frame = tk.Frame(button_area, bg="black")
save_load_frame.pack(anchor=tk.CENTER, pady=(5, 0))

tk.Button(save_load_frame, text="Save Combat", width=18, command=save_combat).pack(side=tk.LEFT, padx=3)
tk.Button(save_load_frame, text="Load Combat", width=18, command=load_combat).pack(side=tk.LEFT, padx=3)
tk.Button(save_load_frame, text="Refresh Display", width=18, command=refresh_display).pack(side=tk.LEFT, padx=3)

player_storage_frame = tk.Frame(button_area, bg="black")
player_storage_frame.pack(anchor=tk.CENTER, pady=(5, 0))

tk.Button(player_storage_frame, text="Save Players", width=18, command=save_player_characters).pack(side=tk.LEFT, padx=3)
tk.Button(player_storage_frame, text="Load Players", width=18, command=load_player_characters).pack(side=tk.LEFT, padx=3)

combat_display = CombatCardDisplay(
  root,
  on_reorder=reorder_characters,
  on_remove_status=clear_status,
  on_remove_permanent_status=clear_permanent_status,
  on_adjust_hp=open_hp_window,
  on_death_save=add_death_save,
  background_color="black",
  font_family="Georgia"
)

refresh_display()

root.mainloop()
