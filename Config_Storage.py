import json
from pathlib import Path


DEFAULT_CONFIG = {
  "campaign_name": "D&D Campaign",
  "audio_volume": {"decrease_target": 20, "increase_target": 100, "duration": 5.0},
  "player_web": {
    "enabled": True,
    "port": 8080
  },
  "background": {
    "type": "color",
    "value": "black"
  },
  "font": "Georgia",
  "borders": {
    "PC": "graphics/border.jpg",
    "SPC": "graphics/border.jpg",
    "NPC": "graphics/border.jpg",
    "EN": "graphics/border.jpg",
    "LA": "graphics/border.jpg"
  }
}


def get_config_path():
  return Path(__file__).resolve().parent / "config.json"


def copy_default_config():
  return {
    "campaign_name": DEFAULT_CONFIG["campaign_name"],
    "audio_volume": DEFAULT_CONFIG["audio_volume"].copy(),
    "player_web": DEFAULT_CONFIG["player_web"].copy(),
    "background": DEFAULT_CONFIG["background"].copy(),
    "font": DEFAULT_CONFIG["font"],
    "borders": DEFAULT_CONFIG["borders"].copy()
  }


def load_config():
  config_path = get_config_path()

  if not config_path.exists():
    return copy_default_config()

  try:
    with open(config_path, "r", encoding="utf-8") as file:
      loaded = json.load(file)
  except (json.JSONDecodeError, OSError):
    return copy_default_config()

  config = copy_default_config()

  campaign_name = loaded.get("campaign_name")

  if isinstance(campaign_name, str) and campaign_name.strip():
    config["campaign_name"] = campaign_name.strip()

  loaded_player_web = loaded.get("player_web", {})

  if isinstance(loaded_player_web, dict):
    enabled = loaded_player_web.get(
      "enabled",
      DEFAULT_CONFIG["player_web"]["enabled"]
    )
    port = loaded_player_web.get(
      "port",
      DEFAULT_CONFIG["player_web"]["port"]
    )

    config["player_web"]["enabled"] = bool(enabled)

    try:
      port = int(port)
    except (TypeError, ValueError):
      port = DEFAULT_CONFIG["player_web"]["port"]

    if 1 <= port <= 65535:
      config["player_web"]["port"] = port

  loaded_background = loaded.get("background")

  if isinstance(loaded_background, dict):
    background_type = loaded_background.get("type", "color")
    background_value = loaded_background.get("value", "black")

    if background_type in ["color", "image"]:
      config["background"] = {
        "type": background_type,
        "value": background_value
      }

  elif isinstance(loaded_background, str):
    config["background"] = {
      "type": "color",
      "value": loaded_background
    }

  loaded_font = loaded.get("font")

  if isinstance(loaded_font, str) and loaded_font:
    config["font"] = loaded_font

  loaded_borders = loaded.get("borders", {})

  if isinstance(loaded_borders, dict):
    for character_type in config["borders"]:
      value = loaded_borders.get(character_type)

      if isinstance(value, str) and value:
        config["borders"][character_type] = value

  audio = loaded.get("audio_volume", {})
  if isinstance(audio, dict):
    for key in ("decrease_target", "increase_target"):
      try:
        val = float(audio.get(key, config["audio_volume"][key]))
        if 0 <= val <= 100:
          config["audio_volume"][key] = int(val)
      except (ValueError, TypeError):
        pass
    try:
      duration = float(audio.get("duration", config["audio_volume"]["duration"]))
      if 0 < duration <= 3600:
        config["audio_volume"]["duration"] = duration
    except (ValueError, TypeError):
      pass

  return config


def save_config(config):
  config_path = get_config_path()

  with open(config_path, "w", encoding="utf-8") as file:
    json.dump(config, file, indent=2)
