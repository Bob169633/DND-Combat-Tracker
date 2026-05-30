import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog

from Add_Characters_Window import AddCharactersWindow
from Combat_State import CombatState
from Display_Combat import CombatCardDisplay
from Save_Load_Combat import load_combat_from_csv, save_combat_to_csv
from Status_Effects import add_status, tick_statuses_for_turn


BACKGROUND_COLORS = [
  "black",
  "gray15",
  "dark slate gray",
  "navy",
  "midnight blue",
  "maroon",
  "dark green",
  "saddle brown"
]

state = CombatState()
selected_background_color = None


def refresh_display():
  combat_display.display_combat_cards(
    state,
    background_color=selected_background_color.get()
  )


def start_combat():
  state.sort_combat()
  refresh_display()


def return_to_original_sort():
  state.sort_combat()
  refresh_display()


def next_character():
  state.next_character()
  tick_statuses_for_turn(state.combat, state.curr)
  refresh_display()


def reorder_characters(old_index, new_index):
  state.move_character(old_index, new_index)
  refresh_display()


def open_add_characters_window():
  AddCharactersWindow(root, add_characters_to_combat)


def add_characters_to_combat(characters):
  state.add_characters(characters)
  refresh_display()


def add_special_status():
  character_name = simpledialog.askstring("Select Character", "Enter Character Name")

  if not character_name:
    return

  special = simpledialog.askstring("Effect and Duration", "Effect,Duration")

  if not special:
    return

  try:
    effect, duration = [part.strip() for part in special.split(",")]
    duration = int(duration)
  except ValueError:
    return

  add_status(state.combat, character_name, effect, duration, state.curr)
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


def change_background_color(*args):
  color = selected_background_color.get()

  root.configure(bg=color)
  button_area.configure(bg=color)
  button_frame.configure(bg=color)
  save_load_frame.configure(bg=color)
  background_label.configure(bg=color)

  refresh_display()


root = tk.Tk(screenName="Combat Tracker", baseName="Tracker", className="Combat Round Tracker", useTk=1)
root.title("Combat Round Tracker")
root.configure(bg="black")

selected_background_color = tk.StringVar(value="black")

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

add_character_button = tk.Button(
  button_frame,
  text="Add Characters",
  width=18,
  command=open_add_characters_window
)
add_character_button.pack(side=tk.LEFT, padx=3)

next_character_button = tk.Button(button_frame, text="Next Character", width=18, command=next_character)
next_character_button.pack(side=tk.LEFT, padx=3)

status_button = tk.Button(button_frame, text="Special Status", width=18, command=add_special_status)
status_button.pack(side=tk.LEFT, padx=3)

refresh_button = tk.Button(button_frame, text="Refresh Display", width=18, command=refresh_display)
refresh_button.pack(side=tk.LEFT, padx=3)

save_load_frame = tk.Frame(button_area, bg="black")
save_load_frame.pack(anchor=tk.CENTER, pady=(5, 0))

save_button = tk.Button(save_load_frame, text="Save Combat", width=18, command=save_combat)
save_button.pack(side=tk.LEFT, padx=3)

load_button = tk.Button(save_load_frame, text="Load Combat", width=18, command=load_combat)
load_button.pack(side=tk.LEFT, padx=3)

background_label = tk.Label(
  save_load_frame,
  text="Background:",
  bg="black",
  fg="white"
)
background_label.pack(side=tk.LEFT, padx=(15, 3))

background_menu = tk.OptionMenu(
  save_load_frame,
  selected_background_color,
  *BACKGROUND_COLORS,
  command=change_background_color
)
background_menu.config(width=14)
background_menu.pack(side=tk.LEFT, padx=3)

combat_display = CombatCardDisplay(
  root,
  on_reorder=reorder_characters,
  background_color="black"
)

refresh_display()

root.mainloop()
