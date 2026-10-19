import csv
import json

from Create_Chars import createChar


FIELDNAMES = [
  "name",
  "character_type",
  "initiative_bonus",
  "max_hp",
  "current_hp",
  "temp_hp",
  "permanent_statuses",
  "card_background",
  "theme_audio"
]


def save_players_to_csv(filepath, combat):
  players = [
    char
    for char in combat
    if char.chType in ["PC", "SPC"]
  ]

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

    for char in players:
      writer.writerow({
        "name": char.name,
        "character_type": char.chType,
        "initiative_bonus": getattr(
          char,
          "bonus",
          0
        ),
        "max_hp": getattr(
          char,
          "max_hp",
          ""
        ),
        "current_hp": getattr(
          char,
          "current_hp",
          ""
        ),
        "temp_hp": getattr(
          char,
          "temp_hp",
          0
        ),
        "permanent_statuses": json.dumps(
          getattr(
            char,
            "permanent_statuses",
            []
          )
        ),
        "card_background": getattr(
          char,
          "card_background",
          ""
        ),
        "theme_audio": getattr(
          char,
          "theme_audio",
          ""
        )
      })


def load_players_from_csv(filepath, reset_hp=False):
  players = []

  with open(
    filepath,
    "r",
    newline="",
    encoding="utf-8"
  ) as file:
    for row in csv.DictReader(file):
      try:
        bonus = int(
          row.get(
            "initiative_bonus",
            0
          ) or 0
        )
      except (TypeError, ValueError):
        bonus = 0

      max_hp = row.get(
        "max_hp",
        ""
      )
      current_hp = row.get(
        "current_hp",
        ""
      )

      if reset_hp or current_hp == "":
        current_hp = max_hp

      try:
        permanent_statuses = json.loads(
          row.get(
            "permanent_statuses",
            "[]"
          ) or "[]"
        )
      except json.JSONDecodeError:
        permanent_statuses = []

      players.append(
        createChar(
          name=row.get(
            "name",
            ""
          ),
          chType=row.get(
            "character_type",
            "PC"
          ),
          bonus=bonus,
          initiative=0,
          max_hp=max_hp,
          current_hp=current_hp,
          permanent_statuses=permanent_statuses,
          card_background=row.get(
            "card_background",
            ""
          ),
          temp_hp=row.get(
            "temp_hp",
            0
          ) or 0,
          theme_audio=row.get(
            "theme_audio",
            ""
          )
        )
      )

  return players
