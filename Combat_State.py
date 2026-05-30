class CombatState:
  def __init__(self):
    self.combat = []
    self.curr = 0
    self.turns = 0
    self.round = 1

  def add_character(self, char):
    self.combat.append(char)
    self.sort_combat()

  def add_characters(self, chars):
    for char in chars:
      self.combat.append(char)

    self.sort_combat()

  def sort_combat(self):
    self.combat.sort(key=lambda char: char.initiative, reverse=True)

    if self.combat and self.curr >= len(self.combat):
      self.curr = 0

  def move_character(self, old_index, new_index):
    if old_index == new_index:
      return

    if old_index < 0 or old_index >= len(self.combat):
      return

    if new_index < 0 or new_index >= len(self.combat):
      return

    current_char = self.combat[self.curr] if self.combat else None

    char = self.combat.pop(old_index)
    self.combat.insert(new_index, char)

    if current_char in self.combat:
      self.curr = self.combat.index(current_char)
    else:
      self.curr = 0

  def load_state(self, combat, round_number, current_turn_index, total_turns):
    self.combat = combat
    self.round = round_number
    self.curr = current_turn_index
    self.turns = total_turns

    if self.combat and self.curr >= len(self.combat):
      self.curr = 0

    if not self.combat:
      self.curr = 0

  def current_character(self):
    if not self.combat:
      return None

    return self.combat[self.curr]

  def next_character(self):
    if not self.combat:
      return

    self.turns += 1

    if self.curr == len(self.combat) - 1:
      self.curr = 0
      self.round += 1
    else:
      self.curr += 1
