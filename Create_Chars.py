import math as m
import uuid

t = "\t"


class character:
  def __init__(
    self,
    name,
    chType,
    bonus,
    initiative,
    max_hp="",
    current_hp="",
    permanent_statuses=None,
    combat_id=None,
    card_background="",
    temp_hp=0,
    theme_audio=""
  ):
    self.name = name
    self.chType = chType
    self.bonus = bonus
    self.status = []
    self.max_hp = max_hp
    self.current_hp = current_hp
    self.death_successes = 0
    self.death_fails = 0
    self.dead = False
    self.permanent_statuses = list(permanent_statuses or [])
    self.combat_id = combat_id or str(uuid.uuid4())
    self.card_background = card_background or ""
    self.theme_audio = theme_audio or ""

    try:
      self.temp_hp = max(0, int(temp_hp or 0))
    except (TypeError, ValueError):
      self.temp_hp = 0

    if chType == "LA":
      self.temp_hp = 0
      initiative = 20

    self.initiative = initiative + bonus if initiative + bonus > 0 else 0

  def __str__(self):
    return f"{self.name}{t}{t}{t}|| Ch.Type: {self.chType} ||{t}|| CI: {m.floor(self.initiative)}"


def createChar(
  name="",
  chType="",
  bonus=0,
  initiative=0,
  max_hp="",
  current_hp="",
  permanent_statuses=None,
  combat_id=None,
  card_background="",
  temp_hp=0,
  theme_audio=""
):
  return character(
    name,
    chType,
    bonus,
    initiative,
    max_hp,
    current_hp,
    permanent_statuses,
    combat_id,
    card_background,
    temp_hp,
    theme_audio
  )
