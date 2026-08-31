import csv
import json

from Create_Chars import createChar


META_ROW = "META"
CHAR_ROW = "CHAR"


def save_combat_to_csv(filepath, state):
  with open(filepath, "w", newline="") as file:
    writer = csv.writer(file)

    writer.writerow([
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
      "death_successes",
      "death_fails",
      "dead",
      "statuses",
      "permanent_statuses"
    ])

    writer.writerow([
      META_ROW,
      state.round,
      state.curr,
      state.turns,
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      ""
    ])

    for char in state.combat:
      writer.writerow([
        CHAR_ROW,
        "",
        "",
        "",
        char.name,
        char.chType,
        getattr(char, "bonus", 0),
        char.initiative,
        getattr(char, "max_hp", ""),
        getattr(char, "current_hp", ""),
        getattr(char, "death_successes", 0),
        getattr(char, "death_fails", 0),
        getattr(char, "dead", False),
        json.dumps(getattr(char, "status", [])),
        json.dumps(getattr(char, "permanent_statuses", []))
      ])


def load_combat_from_csv(filepath):
  combat = []
  loaded_round = 1
  loaded_curr = 0
  loaded_turns = 0

  with open(filepath, "r", newline="") as file:
    reader = csv.DictReader(file)

    for row in reader:
      if row.get("row_type") == META_ROW:
        loaded_round = int(row.get("round", 1) or 1)
        loaded_curr = int(row.get("current_turn_index", 0) or 0)
        loaded_turns = int(row.get("total_turns", 0) or 0)

      elif row.get("row_type") == CHAR_ROW:
        name = row.get("name", "")
        chType = row.get("character_type", "")

        try:
          bonus = int(row.get("initiative_bonus", 0))
        except ValueError:
          bonus = 0

        try:
          initiative = float(row.get("initiative", 0) or 0)
        except ValueError:
          initiative = 0

        max_hp = row.get("max_hp", "")
        current_hp = row.get("current_hp", "")

        try:
          statuses = json.loads(row.get("statuses", "[]") or "[]")
        except json.JSONDecodeError:
          statuses = []

        try:
          permanent_statuses = json.loads(row.get("permanent_statuses", "[]") or "[]")
        except json.JSONDecodeError:
          permanent_statuses = []

        char = createChar(
          name=name,
          chType=chType,
          bonus=bonus,
          initiative=initiative,
          max_hp=max_hp,
          current_hp=current_hp,
          permanent_statuses=permanent_statuses
        )
        char.initiative = initiative
        char.status = statuses
        char.death_successes = int(row.get("death_successes", 0) or 0)
        char.death_fails = int(row.get("death_fails", 0) or 0)
        char.dead = row.get("dead", "False") == "True"

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
