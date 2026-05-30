import math as m


def add_status(combat, character_name, effect, duration, applied_turn):
  for char in combat:
    if char.name == character_name:
      char.status.append(effect)
      char.status.append(duration)
      char.status.append(applied_turn)
      return True

  return False


def tick_statuses_for_turn(combat, current_turn_index):
  for char in combat:
    if len(char.status) == 0:
      continue

    status_index = 0

    while status_index < len(char.status):
      effect_index = status_index
      duration_index = status_index + 1
      applied_turn_index = status_index + 2

      if applied_turn_index >= len(char.status):
        break

      if char.status[applied_turn_index] == current_turn_index:
        char.status[duration_index] -= 1

        if char.status[duration_index] <= 0:
          del char.status[effect_index:effect_index + 3]
          continue

      status_index += 3


def get_status_text(char):
  statuses = []

  for index in range(m.floor(len(char.status) / 3)):
    effect = char.status[3 * index]
    duration = char.status[3 * index + 1]
    statuses.append(f"{effect}: {duration} rounds")

  return statuses
