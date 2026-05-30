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
      "initiative",
      "statuses"
    ])

    writer.writerow([
      META_ROW,
      state.round,
      state.curr,
      state.turns,
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
        char.initiative,
        json.dumps(char.status)
      ])


def load_combat_from_csv(filepath):
  combat = []
  loaded_round = 1
  loaded_curr = 0
  loaded_turns = 0

  with open(filepath, "r", newline="") as file:
    reader = csv.DictReader(file)

    for row in reader:
      if row["row_type"] == META_ROW:
        loaded_round = int(row["round"])
        loaded_curr = int(row["current_turn_index"])
        loaded_turns = int(row["total_turns"])

      elif row["row_type"] == CHAR_ROW:
        name = row["name"]
        chType = row["character_type"]
        initiative = float(row["initiative"])
        statuses = json.loads(row["statuses"]) if row["statuses"] else []

        char = createChar(name, chType, 0, initiative)
        char.initiative = initiative
        char.status = statuses

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
