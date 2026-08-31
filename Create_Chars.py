import math as m

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
    permanent_statuses=None
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

    if chType == "LA":
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
  permanent_statuses=None
):
  return character(
    name,
    chType,
    bonus,
    initiative,
    max_hp,
    current_hp,
    permanent_statuses
  )
