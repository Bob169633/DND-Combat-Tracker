import math as m


def add_status(combat, character_name, effect, duration, applied_turn):
  for char in combat:
    if char.name == character_name:
      char.status.append(effect)
      char.status.append(duration)
      char.status.append(applied_turn)
      return True

  return False


def remove_status(combat, character_index, status_index):
  if character_index < 0 or character_index >= len(combat):
    return False

  char = combat[character_index]
  real_index = status_index * 3

  if real_index < 0 or real_index + 2 >= len(char.status):
    return False

  del char.status[real_index:real_index + 3]
  return True


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


def ensure_permanent_statuses(char):
  if not hasattr(char, "permanent_statuses"):
    char.permanent_statuses = []

  return char.permanent_statuses


def add_permanent_status(combat, character_name, name, trigger="none", effect="none", amount=0):
  for char in combat:
    if char.name == character_name:
      ensure_permanent_statuses(char)
      char.permanent_statuses.append({
        "name": name,
        "trigger": trigger,
        "effect": effect,
        "amount": amount
      })
      return True

  return False


def remove_permanent_status(combat, character_index, status_index):
  if character_index < 0 or character_index >= len(combat):
    return False

  char = combat[character_index]
  permanent_statuses = ensure_permanent_statuses(char)

  if status_index < 0 or status_index >= len(permanent_statuses):
    return False

  del permanent_statuses[status_index]
  return True


def apply_permanent_statuses_for_turn(char, trigger):
  permanent_statuses = ensure_permanent_statuses(char)
  messages = []

  for status in permanent_statuses:
    if status.get("trigger", "none") != trigger:
      continue

    effect = status.get("effect", "none")

    try:
      amount = int(status.get("amount", 0) or 0)
    except ValueError:
      amount = 0

    if effect == "none" or amount <= 0:
      continue

    try:
      current_hp = int(getattr(char, "current_hp", 0) or 0)
    except ValueError:
      current_hp = 0

    try:
      max_hp = int(getattr(char, "max_hp", 0) or 0)
    except ValueError:
      max_hp = 0

    if effect == "heal":
      if max_hp <= 0:
        continue

      char.current_hp = min(max_hp, current_hp + amount)

    elif effect == "damage":
      char.current_hp = max(0, current_hp - amount)

  return messages
