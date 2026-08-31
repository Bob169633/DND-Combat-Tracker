import random
import re


HP_DICE_PATTERN = re.compile(r"^\s*(?:(\d*)d(\d+))\s*([+-]\s*\d+)?\s*$", re.IGNORECASE)
HP_NUMBER_PATTERN = re.compile(r"^\s*(\d+)\s*$")


def roll_hp_formula(formula):
  formula = formula.strip()

  if not formula:
    return ""

  number_match = HP_NUMBER_PATTERN.match(formula)

  if number_match:
    return max(1, int(number_match.group(1)))

  dice_match = HP_DICE_PATTERN.match(formula)

  if not dice_match:
    raise ValueError("HP must be a number or dice format, such as 1, d6+1, or 2d8+6.")

  dice_count_text = dice_match.group(1)
  die_size = int(dice_match.group(2))
  modifier_text = dice_match.group(3)

  dice_count = int(dice_count_text) if dice_count_text else 1
  modifier = 0

  if modifier_text:
    modifier = int(modifier_text.replace(" ", ""))

  if dice_count < 1:
    raise ValueError("HP dice count must be at least 1.")

  if die_size < 2:
    raise ValueError("HP die size must be at least 2.")

  rolls = [random.randint(1, die_size) for _ in range(dice_count)]
  total = sum(rolls) + modifier

  return max(1, total)
