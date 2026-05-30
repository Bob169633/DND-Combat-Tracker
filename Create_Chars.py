import math as m

t = "\t"


class character:
  def __init__(self, name, chType, bonus, initiative):
    self.name = name
    self.chType = chType
    self.status = []

    if chType == "LA":
      initiative = 20

    self.initiative = initiative + bonus if initiative + bonus > 0 else 0

  def __str__(self):
    return f"{self.name}{t}{t}{t}|| Ch.Type: {self.chType} ||{t}|| CI: {m.floor(self.initiative)}"


def createChar(name="", chType="", bonus=0, initiative=0):
  return character(name, chType, bonus, initiative)
