def normalize_statuses(char, combat=None):
  if not hasattr(char, "status"):
    char.status = []

  if not char.status:
    return char.status

  if isinstance(char.status[0], dict):
    return char.status

  legacy = list(char.status)
  converted = []

  for index in range(0, len(legacy), 3):
    if index + 2 >= len(legacy):
      break

    effect = legacy[index]

    try:
      duration = int(legacy[index + 1])
    except (TypeError, ValueError):
      duration = 1

    old_trigger_index = legacy[index + 2]
    trigger_character_id = None
    trigger_character_name = "Unknown"

    if (
      combat is not None
      and isinstance(old_trigger_index, int)
      and 0 <= old_trigger_index < len(combat)
    ):
      trigger_char = combat[old_trigger_index]
      trigger_character_id = getattr(
        trigger_char,
        "combat_id",
        None
      )
      trigger_character_name = trigger_char.name

    converted.append({
      "name": effect,
      "remaining_triggers": max(1, duration),
      "trigger_character_id": trigger_character_id,
      "trigger_character_name": trigger_character_name,
      "trigger_phase": "end_turn"
    })

  char.status = converted
  return char.status


def add_status(
  combat,
  target_character_id,
  effect,
  duration,
  trigger_character_id,
  trigger_phase="end_turn",
  status_effect="none",
  amount=0
):
  target = None
  trigger_name = "Unknown"

  for char in combat:
    if getattr(char, "combat_id", None) == target_character_id:
      target = char

    if getattr(char, "combat_id", None) == trigger_character_id:
      trigger_name = char.name

  if target is None:
    return False

  normalize_statuses(target, combat)

  try:
    duration = int(duration)
  except (TypeError, ValueError):
    duration = 1

  target.status.append({
    "name": effect,
    "remaining_triggers": max(1, duration),
    "trigger_character_id": trigger_character_id,
    "trigger_character_name": trigger_name,
    "trigger_phase": (
      trigger_phase
      if trigger_phase in ["start_turn", "end_turn"]
      else "end_turn"
    ),
    "effect": status_effect,
    "amount": amount
  })

  return True


def remove_status(combat, character_index, status_index):
  if character_index < 0 or character_index >= len(combat):
    return False

  char = combat[character_index]
  normalize_statuses(char, combat)

  if status_index < 0 or status_index >= len(char.status):
    return False

  del char.status[status_index]
  return True


def apply_status_effect(char, effect, amount):
  try:
    amount = int(amount or 0)
  except (TypeError, ValueError):
    amount = 0

  if amount <= 0:
    return

  effect_key = str(effect or "none").strip().lower().replace("_", " ")

  if effect_key == "none":
    return

  if getattr(char, "chType", "") == "LA":
    return

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

  if effect_key == "heal":
    if max_hp > 0:
      char.current_hp = min(
        max_hp,
        current_hp + amount
      )

  elif effect_key == "damage":
    absorbed = min(
      temp_hp,
      amount
    )
    char.temp_hp = temp_hp - absorbed
    remaining_damage = amount - absorbed

    if remaining_damage > 0:
      char.current_hp = max(
        0,
        current_hp - remaining_damage
      )

  elif effect_key == "temp hp":
    char.temp_hp = max(
      temp_hp,
      amount
    )


def tick_statuses_for_trigger(combat, trigger_character, trigger_phase):
  if trigger_character is None:
    return

  trigger_character_id = getattr(
    trigger_character,
    "combat_id",
    None
  )

  if trigger_character_id is None:
    return

  for char in combat:
    statuses = normalize_statuses(char, combat)
    kept_statuses = []

    for status in statuses:
      matches_trigger = (
        status.get("trigger_character_id") == trigger_character_id
        and status.get("trigger_phase", "end_turn") == trigger_phase
      )

      if matches_trigger:
        apply_status_effect(
          char,
          status.get("effect", "none"),
          status.get("amount", 0)
        )

        try:
          remaining = int(
            status.get("remaining_triggers", 1)
          )
        except (TypeError, ValueError):
          remaining = 1

        status["remaining_triggers"] = remaining - 1

      if int(status.get("remaining_triggers", 0)) > 0:
        kept_statuses.append(status)

    char.status = kept_statuses


def get_status_text(char, combat=None):
  statuses = normalize_statuses(char, combat)
  result = []

  for status in statuses:
    try:
      remaining = int(
        status.get("remaining_triggers", 1)
      )
    except (TypeError, ValueError):
      remaining = 1

    result.append(
      f"{status.get('name', '')}: {remaining} round"
      f"{'' if remaining == 1 else 's'}"
    )

  return result


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

    apply_status_effect(
      char,
      status.get("effect", "none"),
      status.get("amount", 0)
    )

  return messages

