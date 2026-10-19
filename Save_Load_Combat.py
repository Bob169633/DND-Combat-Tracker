import csv
import json

from Create_Chars import createChar


META_ROW = "META"
CHAR_ROW = "CHAR"

FIELDNAMES = [
  "row_type",
  "round",
  "current_turn_index",
  "total_turns",
  "name",
  "character_type",
  "initiative_bonus",
  "initiative",
  "max_hp",
  "current_hp",
  "temp_hp",
  "death_successes",
  "death_fails",
  "dead",
  "combat_id",
  "statuses",
  "permanent_statuses",
  "card_background",
  "theme_audio"
]


def save_combat_to_csv(filepath, state):
  with open(
    filepath,
    "w",
    newline="",
    encoding="utf-8"
  ) as file:
    writer = csv.DictWriter(
      file,
      fieldnames=FIELDNAMES
    )
    writer.writeheader()

    writer.writerow({
      "row_type": META_ROW,
      "round": state.round,
      "current_turn_index": state.curr,
      "total_turns": state.turns
    })

    for char in state.combat:
      writer.writerow({
        "row_type": CHAR_ROW,
        "name": char.name,
        "character_type": char.chType,
        "initiative_bonus": getattr(char, "bonus", 0),
        "initiative": char.initiative,
        "max_hp": getattr(char, "max_hp", ""),
        "current_hp": getattr(char, "current_hp", ""),
        "temp_hp": getattr(char, "temp_hp", 0),
        "death_successes": getattr(char, "death_successes", 0),
        "death_fails": getattr(char, "death_fails", 0),
        "dead": getattr(char, "dead", False),
        "combat_id": getattr(char, "combat_id", ""),
        "statuses": json.dumps(getattr(char, "status", [])),
        "permanent_statuses": json.dumps(
          getattr(char, "permanent_statuses", [])
        ),
        "card_background": getattr(char, "card_background", ""),
        "theme_audio": getattr(char, "theme_audio", "")
      })


def load_combat_from_csv(filepath):
  combat = []
  loaded_round = 1
  loaded_curr = 0
  loaded_turns = 0

  with open(
    filepath,
    "r",
    newline="",
    encoding="utf-8"
  ) as file:
    reader = csv.DictReader(file)

    for row in reader:
      if row.get("row_type") == META_ROW:
        try:
          loaded_round = int(row.get("round", 1) or 1)
          loaded_curr = int(row.get("current_turn_index", 0) or 0)
          loaded_turns = int(row.get("total_turns", 0) or 0)
        except ValueError:
          loaded_round = 1
          loaded_curr = 0
          loaded_turns = 0
        continue

      if row.get("row_type") != CHAR_ROW:
        continue

      try:
        bonus = int(row.get("initiative_bonus", 0) or 0)
      except ValueError:
        bonus = 0

      try:
        initiative = float(row.get("initiative", 0) or 0)
      except ValueError:
        initiative = 0

      try:
        statuses = json.loads(row.get("statuses", "[]") or "[]")
      except json.JSONDecodeError:
        statuses = []

      try:
        permanent_statuses = json.loads(
          row.get("permanent_statuses", "[]") or "[]"
        )
      except json.JSONDecodeError:
        permanent_statuses = []

      char = createChar(
        name=row.get("name", ""),
        chType=row.get("character_type", ""),
        bonus=bonus,
        initiative=initiative,
        max_hp=row.get("max_hp", ""),
        current_hp=row.get("current_hp", ""),
        permanent_statuses=permanent_statuses,
        combat_id=row.get("combat_id") or None,
        card_background=row.get("card_background", ""),
        temp_hp=row.get("temp_hp", 0) or 0,
        theme_audio=row.get("theme_audio", "")
      )

      char.initiative = initiative
      char.status = statuses

      try:
        char.death_successes = int(
          row.get("death_successes", 0) or 0
        )
      except ValueError:
        char.death_successes = 0

      try:
        char.death_fails = int(
          row.get("death_fails", 0) or 0
        )
      except ValueError:
        char.death_fails = 0

      char.dead = (
        str(row.get("dead", "False")).lower()
        == "true"
      )

      combat.append(char)

  if combat and loaded_curr >= len(combat):
    loaded_curr = 0

  if not combat:
    loaded_curr = 0

  return {
    "combat": combat,
    "round": loaded_round,
    "curr": loaded_curr,
    "turns": loaded_turns
  }
