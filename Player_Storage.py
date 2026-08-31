import csv
import json

from Create_Chars import createChar


FIELDNAMES = [
  "name",
  "character_type",
  "initiative_bonus",
  "max_hp",
  "current_hp",
  "permanent_statuses"
]


def save_players_to_csv(filepath, characters):
  with open(filepath, "w", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
    writer.writeheader()

    for char in characters:
      if char.chType not in ["PC", "SPC"]:
        continue

      writer.writerow({
        "name": char.name,
        "character_type": char.chType,
        "initiative_bonus": getattr(char, "bonus", 0),
        "max_hp": getattr(char, "max_hp", ""),
        "current_hp": getattr(char, "current_hp", ""),
        "permanent_statuses": json.dumps(getattr(char, "permanent_statuses", []))
      })


def load_players_from_csv(filepath, reset_hp=False):
  players = []

  with open(filepath, "r", newline="") as file:
    reader = csv.DictReader(file)

    for row in reader:
      name = row.get("name", "").strip()

      if not name:
        continue

      chType = row.get("character_type", "PC").strip() or "PC"

      if chType not in ["PC", "SPC"]:
        chType = "PC"

      try:
        bonus = int(row.get("initiative_bonus", 0))
      except ValueError:
        bonus = 0

      max_hp = row.get("max_hp", "").strip()
      saved_current_hp = row.get("current_hp", "").strip()

      if reset_hp:
        current_hp = max_hp
      elif saved_current_hp == "":
        current_hp = max_hp
      else:
        current_hp = saved_current_hp

      try:
        permanent_statuses = json.loads(row.get("permanent_statuses", "[]") or "[]")
      except json.JSONDecodeError:
        permanent_statuses = []

      players.append(
        createChar(
          name=name,
          chType=chType,
          bonus=bonus,
          initiative=0,
          max_hp=max_hp,
          current_hp=current_hp,
          permanent_statuses=permanent_statuses
        )
      )

  return players
