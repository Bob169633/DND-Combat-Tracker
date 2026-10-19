import tkinter as tk
import webbrowser

try:
  import qrcode
  from PIL import ImageTk
  QR_AVAILABLE = True
except ImportError:
  QR_AVAILABLE = False
from tkinter import filedialog, messagebox

from Add_Characters_Window import AddCharactersWindow
from Audio_Themes_Window import AudioThemePlayer, AudioThemesWindow, SystemVolumeController
from Combat_State import CombatState
from Config_Storage import load_config, save_config
from Config_Window import BACKGROUND_COLORS, ConfigWindow
from Display_Combat import CombatCardDisplay
from HP_Window import HPWindow
from Load_Players_Window import LoadPlayersWindow
from Player_Storage import load_players_from_csv, save_players_to_csv
from Player_Card_Backgrounds_Window import PlayerCardBackgroundsWindow
from Player_Web_Server import PlayerWebServer, get_player_view_url
from Save_Load_Combat import load_combat_from_csv, save_combat_to_csv
from Status_Effects import (
  add_permanent_status,
  add_status,
  apply_permanent_statuses_for_turn,
  remove_permanent_status,
  remove_status,
  tick_statuses_for_trigger
)
from Status_Window import StatusWindow


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
app_config = load_config()
player_web_server = PlayerWebServer()
audio_theme_player = AudioThemePlayer()
player_web_revision = 0
selected_background_color = None
selected_font_family = None


def get_mouse_position():
  root.update_idletasks()
  return root.winfo_pointerx(), root.winfo_pointery()


def get_selected_background_color():
  background = app_config.get(
    "background",
    {
      "type": "color",
      "value": "black"
    }
  )

  if background.get("type") == "color":
    return background.get("value", "black")

  return "black"


def get_selected_background_image():
  background = app_config.get(
    "background",
    {}
  )

  if background.get("type") == "image":
    return background.get("value")

  return None


def get_campaign_name():
  return app_config.get(
    "campaign_name",
    "D&D Campaign"
  )


def get_campaign_slug():
  campaign_name = get_campaign_name().strip().lower()
  slug = []
  previous_underscore = False

  for char in campaign_name:
    if char.isalnum():
      slug.append(char)
      previous_underscore = False
    elif not previous_underscore:
      slug.append("_")
      previous_underscore = True

  cleaned = "".join(slug).strip("_")
  return cleaned or "dnd_campaign"


def get_player_statuses(char):
  statuses = []
  temporary = getattr(
    char,
    "status",
    []
  )

  if temporary and isinstance(
    temporary[0],
    dict
  ):
    for status in temporary:
      name = str(
        status.get("name", "")
      ).strip()

      if name:
        statuses.append(name)

  else:
    for index in range(
      0,
      len(temporary),
      3
    ):
      if index >= len(temporary):
        break

      name = str(
        temporary[index]
      ).strip()

      if name:
        statuses.append(name)

  for status in getattr(
    char,
    "permanent_statuses",
    []
  ):
    name = str(
      status.get("name", "")
    ).strip()

    if name:
      statuses.append(name)

  return statuses


def build_player_web_state():
  global player_web_revision

  player_web_revision += 1
  characters = []

  for index, char in enumerate(state.combat):
    try:
      initiative = int(char.initiative)
    except (TypeError, ValueError):
      initiative = 0

    character = {
      "id": getattr(char,"combat_id",str(index)),
      "name": char.name,
      "type": char.chType,
      "initiative": initiative,
      "active": index == state.curr,
      "statuses": get_player_statuses(char),
      "bloodied": None,
      "health_text": "",
      "has_card_image": bool(getattr(char,"card_background","") or app_config.get("borders",{}).get(char.chType))
    }

    if char.chType in ["PC", "SPC"]:
      try:
        current_hp = int(
          getattr(char, "current_hp", 0) or 0
        )
      except (TypeError, ValueError):
        current_hp = 0

      try:
        max_hp = int(
          getattr(char, "max_hp", 0) or 0
        )
      except (TypeError, ValueError):
        max_hp = 0

      if max_hp > 0:
        try:
          temp_hp = int(
            getattr(char, "temp_hp", 0) or 0
          )
        except (TypeError, ValueError):
          temp_hp = 0

        character["health_text"] = (
          f"HP: {current_hp}/{max_hp}"
        )

        if temp_hp > 0:
          character["health_text"] += (
            f" | Temp: {temp_hp}"
          )
        character["bloodied"] = (
          current_hp <= max_hp / 2
        )

    elif char.chType in ["NPC", "EN"]:
      try:
        current_hp = int(
          getattr(char, "current_hp", 0) or 0
        )
        max_hp = int(
          getattr(char, "max_hp", 0) or 0
        )
      except (TypeError, ValueError):
        current_hp = 0
        max_hp = 0

      if max_hp > 0:
        character["bloodied"] = (
          current_hp <= max_hp / 2
        )

        character["health_text"] = ""

    characters.append(character)

  background = app_config.get(
    "background",
    {
      "type": "color",
      "value": "black"
    }
  )

  background_type = background.get("type", "color")
  background_value = background.get("value", "black")

  snapshot = {
    "revision": player_web_revision,
    "campaign_name": get_campaign_name(),
    "round": state.round,
    "turn_number": state.curr + 1 if state.combat else 0,
    "font": selected_font_family.get(),
    "background": {
      "type": background_type,
      "value": (
        background_value
        if background_type == "color"
        else "black"
      ),
      "has_image": (
        background_type == "image"
        and bool(background_value)
      )
    },
    "characters": characters
  }

  media_paths = {}

  if background_type == "image" and background_value:
    media_paths["background"] = background_value

  for character_type, image_path in app_config.get(
    "borders",
    {}
  ).items():
    if image_path:
      media_paths[f"card:{character_type}"] = image_path

  for char in state.combat:
    personal_background=getattr(char,"card_background","")
    image_path=personal_background if (char.chType in ["PC","SPC"] and personal_background) else app_config.get("borders",{}).get(char.chType)
    if image_path:
      media_paths[f"character:{getattr(char,'combat_id',char.name)}"] = image_path

  return snapshot, media_paths


def update_player_web_state():
  if not player_web_server.is_running():
    return

  snapshot, media_paths = build_player_web_state()
  player_web_server.update(
    snapshot,
    media_paths
  )


def sync_player_web_server(show_errors=True):
  player_web = app_config.get(
    "player_web",
    {}
  )

  enabled = player_web.get("enabled", True)

  try:
    port = int(
      player_web.get("port", 8080)
    )
  except (TypeError, ValueError):
    port = 8080

  if not enabled:
    player_web_server.stop()
    return

  try:
    player_web_server.start(port)
    update_player_web_state()
  except OSError as error:
    player_web_server.stop()

    if show_errors:
      messagebox.showerror(
        "Player Web View",
        "The player web view could not start on "
        f"port {port}.\n\n{error}"
      )


def refresh_display():
  combat_display.display_combat_cards(
    state,
    background_color=get_selected_background_color(),
    background_image_path=get_selected_background_image(),
    font_family=selected_font_family.get(),
    border_choices=app_config.get("borders", {})
  )

  update_player_web_state()


def start_combat():
  state.sort_combat()
  refresh_display()


def return_to_original_sort():
  state.sort_combat()
  refresh_display()


def next_character():
  current_char = state.current_character()

  if current_char is not None:
    apply_permanent_statuses_for_turn(
      current_char,
      "end_turn"
    )

    tick_statuses_for_trigger(
      state.combat,
      current_char,
      "end_turn"
    )

    handle_zero_hp(current_char)

  state.next_character()

  current_char = state.current_character()

  if current_char is not None:
    tick_statuses_for_trigger(
      state.combat,
      current_char,
      "start_turn"
    )

    apply_permanent_statuses_for_turn(
      current_char,
      "start_turn"
    )

    try:
      current_hp = int(
        getattr(
          current_char,
          "current_hp",
          0
        ) or 0
      )
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
    background_color=get_selected_background_color(),
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
    background_color=get_selected_background_color(),
    mouse_x=mouse_x,
    mouse_y=mouse_y
  )


def add_statuses_to_combat(statuses):
  if not isinstance(statuses, list):
    messagebox.showerror(
      "Status Error",
      "Status data was invalid."
    )
    return

  for status in statuses:
    if not isinstance(status, dict):
      continue

    target_id = status.get(
      "target_id"
    )

    target_char = None

    for char in state.combat:
      if getattr(
        char,
        "combat_id",
        None
      ) == target_id:
        target_char = char
        break

    if target_char is None:
      continue

    if status.get(
      "permanent",
      False
    ):
      permanent_statuses = getattr(
        target_char,
        "permanent_statuses",
        []
      )

      permanent_statuses.append({
        "name": status.get(
          "status",
          ""
        ),
        "trigger": status.get(
          "trigger",
          "none"
        ),
        "effect": status.get(
          "effect",
          "none"
        ),
        "amount": status.get(
          "amount",
          0
        )
      })

      target_char.permanent_statuses = (
        permanent_statuses
      )

    else:
      trigger_character_id = status.get(
        "trigger_character_id"
      )
      trigger_phase = status.get(
        "trigger_phase",
        "end_turn"
      )

      add_status(
        state.combat,
        target_id,
        status.get(
          "status",
          ""
        ),
        status.get(
          "duration",
          1
        ),
        trigger_character_id,
        trigger_phase,
        status.get(
          "effect",
          "none"
        ),
        status.get(
          "amount",
          0
        )
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
    set_character_temp_hp,
    background_color=get_selected_background_color(),
    mouse_x=mouse_x,
    mouse_y=mouse_y
  )


def adjust_character_hp(char, amount):
  try:
    current_hp = int(
      getattr(char, "current_hp", 0) or 0
    )
  except (TypeError, ValueError):
    current_hp = 0

  try:
    max_hp = int(
      getattr(char, "max_hp", 0) or 0
    )
  except (TypeError, ValueError):
    max_hp = 0

  try:
    temp_hp = int(
      getattr(char, "temp_hp", 0) or 0
    )
  except (TypeError, ValueError):
    temp_hp = 0

  if amount < 0:
    damage = abs(amount)
    absorbed = min(
      temp_hp,
      damage
    )

    char.temp_hp = temp_hp - absorbed
    damage -= absorbed

    if damage > 0:
      char.current_hp = max(
        0,
        current_hp - damage
      )

  else:
    new_hp = current_hp + amount

    if max_hp > 0:
      new_hp = min(
        new_hp,
        max_hp
      )

    char.current_hp = max(
      0,
      new_hp
    )

  if getattr(char, "current_hp", 0) > 0:
    char.death_successes = 0
    char.death_fails = 0

  handle_zero_hp(char)
  refresh_display()


def set_character_temp_hp(char, temp_hp):
  if char.chType == "LA":
    char.temp_hp = 0
  else:
    try:
      char.temp_hp = max(
        0,
        int(temp_hp or 0)
      )
    except (TypeError, ValueError):
      char.temp_hp = 0

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
    initialfile=f"{get_campaign_slug()}_combat.csv",
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
    initialfile=f"{get_campaign_slug()}_combat.csv",
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
    initialfile=f"{get_campaign_slug()}_players.csv",
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
    initialfile=f"{get_campaign_slug()}_players.csv",
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
      background_color=get_selected_background_color(),
      mouse_x=mouse_x,
      mouse_y=mouse_y
    )

  except Exception as error:
    messagebox.showerror("Load Failed", f"Player characters could not be loaded:\n{error}")


def apply_main_background():
  color = get_selected_background_color()

  root.configure(bg=color)
  button_area.configure(bg=color)
  button_frame.configure(bg=color)
  save_load_frame.configure(bg=color)
  player_storage_frame.configure(bg=color)


def open_config_window():
  mouse_x, mouse_y = get_mouse_position()

  ConfigWindow(
    root,
    app_config,
    FONT_CHOICES,
    apply_config,
    background_color=get_selected_background_color(),
    mouse_x=mouse_x,
    mouse_y=mouse_y
  )


def apply_config(new_config):
  global app_config

  app_config = new_config
  system_volume_controller.config = app_config

  selected_font_family.set(
    app_config.get("font", "Georgia")
  )

  save_config(app_config)

  root.title(
    f"Combat Round Tracker - {get_campaign_name()}"
  )

  sync_player_web_server()
  apply_main_background()
  refresh_display()


def confirm_quit():
  should_quit = messagebox.askyesno(
    "Quit Combat Tracker",
    "Are you sure you want to quit the Combat Tracker?"
  )

  if should_quit:
    system_volume_controller.cancel()
    audio_theme_player.shutdown()
    player_web_server.stop()
    root.destroy()


def get_player_web_url():
  player_web = app_config.get(
    "player_web",
    {}
  )

  try:
    port = int(
      player_web.get("port", 8080)
    )
  except (TypeError, ValueError):
    port = 8080

  return get_player_view_url(port)


def create_player_web_popup(title, status_text=None):
  player_web = app_config.get(
    "player_web",
    {}
  )

  enabled = player_web.get("enabled", True)
  running = player_web_server.is_running()

  popup = tk.Toplevel(root)
  popup.title(title)
  popup.configure(bg="black")
  popup.resizable(False, False)
  popup.transient(root)
  popup.grab_set()

  content = tk.Frame(
    popup,
    bg="black",
    padx=24,
    pady=20
  )
  content.pack(fill=tk.BOTH, expand=True)

  tk.Label(
    content,
    text=title,
    font=("Arial", 15, "bold"),
    bg="black",
    fg="white"
  ).pack(pady=(0, 12))

  if status_text:
    tk.Label(
      content,
      text=status_text,
      justify=tk.LEFT,
      anchor="w",
      font=("Arial", 10),
      bg="black",
      fg="white"
    ).pack(fill=tk.X, pady=(0, 12))

  if not enabled:
    tk.Label(
      content,
      text="The player web view is disabled in Config.",
      font=("Arial", 10),
      bg="black",
      fg="white"
    ).pack(pady=10)

  elif not running:
    tk.Label(
      content,
      text=(
        "The player web view is enabled, but the server is not running."
      ),
      font=("Arial", 10),
      bg="black",
      fg="white"
    ).pack(pady=10)

  else:
    player_url = get_player_web_url()

    tk.Label(
      content,
      text="Players can scan this QR code or use the link below:",
      font=("Arial", 10),
      bg="black",
      fg="white"
    ).pack(pady=(0, 10))

    if QR_AVAILABLE:
      qr_image = qrcode.make(player_url)
      qr_image = qr_image.resize((260, 260))
      qr_photo = ImageTk.PhotoImage(qr_image)

      qr_label = tk.Label(
        content,
        image=qr_photo,
        bg="white",
        padx=8,
        pady=8
      )
      qr_label.image = qr_photo
      qr_label.pack(pady=(0, 12))
    else:
      tk.Label(
        content,
        text=(
          "QR code unavailable. Install the 'qrcode' package "
          "to enable QR display."
        ),
        font=("Arial", 9),
        bg="black",
        fg="#ffcc66"
      ).pack(pady=(0, 12))

    link_var = tk.StringVar(
      value=player_url
    )

    link_entry = tk.Entry(
      content,
      textvariable=link_var,
      width=42,
      justify="center",
      state="readonly",
      readonlybackground="white",
      fg="black"
    )
    link_entry.pack(pady=(0, 12))

    button_row = tk.Frame(
      content,
      bg="black"
    )
    button_row.pack()

    def copy_link():
      popup.clipboard_clear()
      popup.clipboard_append(player_url)
      popup.update()

    tk.Button(
      button_row,
      text="Copy Link",
      width=12,
      command=copy_link
    ).pack(side=tk.LEFT, padx=5)

    tk.Button(
      button_row,
      text="Open Website",
      width=12,
      command=lambda: webbrowser.open(player_url)
    ).pack(side=tk.LEFT, padx=5)

  tk.Button(
    content,
    text="Close",
    width=12,
    command=popup.destroy
  ).pack(pady=(16, 0))

  popup.update_idletasks()

  x = root.winfo_rootx() + max(
    0,
    (root.winfo_width() - popup.winfo_reqwidth()) // 2
  )
  y = root.winfo_rooty() + max(
    0,
    (root.winfo_height() - popup.winfo_reqheight()) // 2
  )

  popup.geometry(f"+{x}+{y}")
  popup.lift()
  popup.focus_force()


def show_player_web_link():
  create_player_web_popup(
    "Player Website"
  )


def open_player_website():
  player_web = app_config.get(
    "player_web",
    {}
  )

  if not player_web.get("enabled", True):
    messagebox.showinfo(
      "Player Website",
      "The player web view is disabled in Config.",
      parent=root
    )
    return

  if not player_web_server.is_running():
    messagebox.showinfo(
      "Player Website",
      "The player web view is not currently running.",
      parent=root
    )
    return

  webbrowser.open(
    get_player_web_url()
  )


def show_server_status():
  player_web = app_config.get(
    "player_web",
    {}
  )

  enabled = player_web.get("enabled", True)

  try:
    port = int(
      player_web.get("port", 8080)
    )
  except (TypeError, ValueError):
    port = 8080

  running = player_web_server.is_running()

  enabled_text = (
    "Enabled"
    if enabled
    else "Disabled"
  )

  server_text = (
    "Running"
    if running
    else "Stopped"
  )

  link_text = (
    get_player_web_url()
    if running
    else "Unavailable"
  )

  status_text = (
    f"Campaign: {get_campaign_name()}\n"
    f"Player Web View: {enabled_text}\n"
    f"Server: {server_text}\n"
    f"Port: {port}\n"
    f"LAN Link: {link_text}"
  )

  create_player_web_popup(
    "Player Server Status",
    status_text=status_text
  )


def open_audio_themes():
  characters = [
    char
    for char in state.combat
    if char.chType != "LA"
  ]

  mouse_x, mouse_y = get_mouse_position()

  AudioThemesWindow(
    root,
    characters,
    audio_theme_player,
    on_theme_changed=apply_audio_theme_change,
    system_volume=system_volume_controller,
    background_color=get_selected_background_color(),
    mouse_x=mouse_x,
    mouse_y=mouse_y
  )


def apply_audio_theme_change(char):
  # The character object is updated directly by the popup.
  # This hook keeps future persistence/UI refresh behavior centralized.
  return


def open_player_card_backgrounds():
  players=[char for char in state.combat if char.chType in ["PC","SPC"]]
  if not players:
    messagebox.showinfo("Player Card Backgrounds","Load or add player characters before setting individual card backgrounds.",parent=root)
    return
  mouse_x,mouse_y=get_mouse_position()
  PlayerCardBackgroundsWindow(root,players,apply_player_card_backgrounds,background_color=get_selected_background_color(),mouse_x=mouse_x,mouse_y=mouse_y)

def apply_player_card_backgrounds(selections):
  for char in state.combat:
    cid=getattr(char,"combat_id",None)
    if cid in selections: char.card_background=selections[cid]
  refresh_display()

def clear_combat_and_reset():
  should_clear = messagebox.askyesno(
    "Clear Combat",
    "Clear all characters from combat and reset the round/turn counts?",
    parent=root
  )

  if not should_clear:
    return

  audio_theme_player.stop()
  state.combat.clear()
  state.curr = 0
  state.turns = 0
  state.round = 1
  refresh_display()


def show_hotkey_help():
  hotkey_text = (
    "Ctrl + E       - Config\n"
    "Ctrl + H       - Show Hotkeys\n"
    "Ctrl + L       - Load Combat\n"
    "Ctrl + M       - Audio Themes\n"
    "Ctrl + P       - Player Card Backgrounds\n"
    "Ctrl + Q       - Quit Program\n"
    "Ctrl + R       - Refresh Display\n"
    "Ctrl + S       - Save Combat\n"
    "Ctrl + V       - Server Status\n"
    "Ctrl + W       - Open Player Website\n"
    "\n"
    "Ctrl + 0       - Return to Original Sort\n"
    "Ctrl + 1       - Add Characters\n"
    "Ctrl + 2       - Add Statuses\n"
    "Ctrl + 8       - Save Players\n"
    "Ctrl + 9       - Load Players\n"
    "\n"
    "Ctrl + -       - Lower System Volume Gradually\n"
    "Ctrl + Shift + + - Raise System Volume Gradually\n"
    "Ctrl + Delete  - Clear Combat & Reset\n"
    "Ctrl + Enter   - Next Character\n"
    "Ctrl + Space   - Start Combat"
  )

  messagebox.showinfo(
    "Combat Tracker Hotkeys",
    hotkey_text
  )


def ask_show_buttons():
  return messagebox.askyesno(
    "Combat Tracker Controls",
    "Would you like to display the control buttons?\n\n"
    "Yes: Show buttons and use hotkeys.\n"
    "No: Hide buttons and use hotkeys only.\n\n"
    "Press Ctrl+H at any time to view the hotkey list."
  )


def bind_hotkey(sequence, command):
  root.bind(
    sequence,
    lambda event: command()
  )


root = tk.Tk(screenName="Combat Tracker", baseName="Tracker", className="Combat Round Tracker", useTk=1)
root.title(
  f"Combat Round Tracker - {get_campaign_name()}"
)
audio_theme_player.attach_root(root)
system_volume_controller = SystemVolumeController(root, app_config, save_config)
root.configure(bg="black")
root.withdraw()

selected_background_color = tk.StringVar(value="Black")
selected_font_family = tk.StringVar(
  value=app_config.get("font", "Georgia")
)

show_buttons = ask_show_buttons()

root.deiconify()
root.attributes("-fullscreen", True)

button_area = tk.Frame(root, bg="black")

if show_buttons:
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

config_button = tk.Button(
  button_frame,
  text="Config",
  width=18,
  command=open_config_window
)
config_button.pack(side=tk.LEFT, padx=3)

save_load_frame = tk.Frame(button_area, bg="black")
save_load_frame.pack(anchor=tk.CENTER, pady=(5, 0))

tk.Button(save_load_frame, text="Save Combat", width=18, command=save_combat).pack(side=tk.LEFT, padx=3)
tk.Button(save_load_frame, text="Load Combat", width=18, command=load_combat).pack(side=tk.LEFT, padx=3)
tk.Button(save_load_frame, text="Refresh Display", width=18, command=refresh_display).pack(side=tk.LEFT, padx=3)

player_storage_frame = tk.Frame(button_area, bg="black")
player_storage_frame.pack(anchor=tk.CENTER, pady=(5, 0))

tk.Button(player_storage_frame, text="Save Players", width=18, command=save_player_characters).pack(side=tk.LEFT, padx=3)
tk.Button(player_storage_frame, text="Load Players", width=18, command=load_player_characters).pack(side=tk.LEFT, padx=3)
tk.Button(player_storage_frame, text="Audio Themes", width=18, command=open_audio_themes).pack(side=tk.LEFT, padx=3)

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

bind_hotkey("<Control-e>", open_config_window)
bind_hotkey("<Control-h>", show_hotkey_help)
bind_hotkey("<Control-l>", load_combat)
bind_hotkey("<Control-m>", open_audio_themes)
bind_hotkey("<Control-p>", open_player_card_backgrounds)
bind_hotkey("<Control-q>", confirm_quit)
bind_hotkey("<Control-r>", refresh_display)
bind_hotkey("<Control-s>", save_combat)
bind_hotkey("<Control-v>", show_server_status)
bind_hotkey("<Control-w>", open_player_website)

bind_hotkey("<Control-Key-0>", return_to_original_sort)
bind_hotkey("<Control-Key-1>", open_add_characters_window)
bind_hotkey("<Control-Key-2>", open_status_window)
bind_hotkey("<Control-Key-8>", save_player_characters)
bind_hotkey("<Control-Key-9>", load_player_characters)

def change_master_volume(direction):
  try:
    system_volume_controller.transition(direction)
  except RuntimeError as error:
    messagebox.showerror("System Volume", str(error), parent=root)


bind_hotkey("<Control-minus>", lambda: change_master_volume("down"))
# Plus is Shift+Equals on most US keyboards; support keypad plus as well.
bind_hotkey("<Control-Shift-equal>", lambda: change_master_volume("up"))
bind_hotkey("<Control-plus>", lambda: change_master_volume("up"))
bind_hotkey("<Control-KP_Add>", lambda: change_master_volume("up"))
bind_hotkey("<Control-Delete>", clear_combat_and_reset)
bind_hotkey("<Control-Return>", next_character)
bind_hotkey("<Control-space>", start_combat)

sync_player_web_server()
apply_main_background()
refresh_display()

root.after(
  500,
  show_player_web_link
)

root.mainloop()
