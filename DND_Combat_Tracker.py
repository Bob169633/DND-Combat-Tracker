import tkinter as tk
from tkinter import filedialog
from tkinter import simpledialog
import random
import os
import math as m

nl = '\n'
t = '\t'
combat = []
curr = 0
turns = 0
Round = 1
priority = 0
currChar = f"***"
maxNameLength = 0

# Character objects for combat
class character:
  def __init__(self, name, chType, bonus, initiative):
    global priority
    self.name = name
    self.chType = chType
    self.status = []
    if chType == "LA":
      initiative = 20
      priority = .3
    elif chType == "PC":
      priority = .2
    elif chType == "EN":
      priority = .1
    elif chType == "NP":
      priority = 0
    self.initiative = initiative+bonus+priority if initiative+bonus+priority > 0 else 0+priority
    
  def __str__(self):
    return f"{self.name}{t}{t}{t}|| Ch.Type: {self.chType} ||{t}|| CI: {m.floor(self.initiative)}"



# Calls Character init function and allows Character object to be named from name variable
def createChar(name="", chType="", bonus=0, initiative=0 ):
  globals()[name] = character(name, chType, bonus, initiative)
  combat.append(globals()[name])
  

# Displays all characters currently in combat
def displayCombat():
  global name_width, type_width, initiative_width
  overview = f">> Round #{Round} <<        >> Turn #{curr+1} <<       >> Total Turn #{turns+1} <<"
  listbox.delete(0,tk.END)
  listbox.insert(tk.END, overview)
  listbox.insert(tk.END, "-" * (name_width + type_width + initiative_width))  # Separator line
  row_form = "{:<" + str(name_width) + "} {:<" + str(type_width) + "} {:<" + str(initiative_width) + "}"
  header = row_form.format("Name", "Ch. Type", "Initiative")
  listbox.insert(tk.END, header)
  listbox.insert(tk.END, "-" * (name_width + type_width + initiative_width))  # Separator line
  for i in range(len(combat)):
    form = row_form.format(combat[i].name, combat[i].chType, m.floor(combat[i].initiative))
    if curr == i:
      listbox.insert(tk.END, currChar)
      listbox.insert(tk.END, form)
      if len(combat[i].status) != 0:
        for n in range(m.floor(len(combat[i].status)/3)):
          statuses = combat[i].status[3*n] + " " + str(combat[i].status[3*n+1])
          listbox.insert(tk.END, statuses)
      listbox.insert(tk.END, currChar)
    else:
      listbox.insert(tk.END, form)
      if len(combat[i].status) != 0:
        for n in range(m.floor(len(combat[i].status)/3)):
          statuses = "----" + combat[i].status[3*n] + " " + str(combat[i].status[3*n+1])
          listbox.insert(tk.END, statuses)
      listbox.insert(tk.END, "")


# Sorts all characters in combat by decreasing initiative
def sortCombat():
  swapped = True
  if len(combat) == 1:
    swapped = False
  
  while swapped:
    swapped = False
    for i in range (len(combat)-1):
      if combat[i].initiative < combat[i+1].initiative:
        temp = combat[i]
        combat[i] = combat[i+1]
        combat[i+1] = temp
        swapped = True
  displayCombat()


# Moves combat to next character's turn
def nextChar():
  global curr
  global Round
  global turns
  turns += 1
  if curr == len(combat)-1:
    curr = 0
    Round += 1
  else:
    curr += 1
  for i in range(len(combat)):
    if len(combat[i].status) != 0:
      for n in range(m.floor(len(combat[i].status)/3)):
        if combat[i].status[3*n+2] == curr:
          combat[i].status[3*n+1] -= 1
          if combat[i].status[3*n+1] == 0:
            combat[i].status.remove(combat[i].status[3*n])
            combat[i].status.remove(combat[i].status[3*n])
            combat[i].status.remove(combat[i].status[3*n])
          n -= 3
  displayCombat()


# Add character to combat after combat has started
def addChar():
  title = "Add Char"
  t2 = "Add Init"
  p2 = "Init"
  prompt = "Name,Type,Bonus"
  newChar = simpledialog.askstring(title, prompt)
  NAME, CHTYPE, BONUS = newChar.split(',')
  if CHTYPE != 'PC':
    if CHTYPE == 'LA':
      INIT = 20
    else:
      INIT = random.randint(1,20)
  else:
    INIT = simpledialog.askinteger(t2, p2)
  try:
    BONUS = int(BONUS)
  except ValueError:
    pass
  createChar(NAME, CHTYPE, BONUS, INIT)
  sortCombat()


# Allows special statuses that are applied to characters be shown in combat display
def specialStatus():
  global combat
  t1 = "Select Character"
  p1 = "Enter Character Name"
  t2 = "Effect and Duration"
  p2 = "Effect,Duration"
  char = simpledialog.askstring(t1,p1)
  special = simpledialog.askstring(t2,p2)
  EFF, DUR = special.split(',')
  APP = curr
  try:
    DUR = int(DUR)
  except ValueError:
    pass
  for ch in combat:
    if ch.name == char:
      ch.status.append(EFF)
      ch.status.append(DUR)
      ch.status.append(APP)
      break
  sortCombat()
  


# Open the file for any .txt file with character data
def open_file(f):
  fpath = filedialog.askdirectory()
  filepath = os.path.join(fpath, f)
  try:
    with open(filepath, 'r') as file:
      for line in file:
        try:
          NAME, CHTYPE, BONUS, INIT = line.strip().split(',')
        except ValueError:
          NAME, CHTYPE, BONUS = line.strip().split(',')
        if CHTYPE != 'PC':
          if CHTYPE == 'LA':
            INIT = 20
          else:
            INIT = random.randint(1,20)
        try:
          INIT = int(INIT)
          BONUS = int(BONUS)
        except ValueError:
          pass
        createChar(NAME, CHTYPE, BONUS, INIT)
  except Exception as e:
    print(e)


# Specify files to be added into combat
# Player files should follow the NAME,CHTYPE,BONUS,INIT format
# Non-player files should follow the NAME,CHTYPE,BONUS format
# The CHTYPE should be 1 of 4 options; PC, NPC, EN, or LA
player = "players.txt"
enemy = ["bandits.txt"]




# Tkinter GUI window creation
root = tk.Tk(screenName="Combat Tracker", baseName="Tracker", className="Combat Round Tracker", useTk=1)

# Call open_file as many times as needed for each file
for item in enemy:
  open_file(item)
open_file(player)
maxNameLength = max(len(char.name) for char in combat)

# Start Combat Button
start_button = tk.Button(root, text="Start Combat", width=50, command=sortCombat)
start_button.pack()

# Add Character Button
add_character = tk.Button(root, text="Add Character", width=50, command=addChar)
add_character.pack()

# Next Character Button
next_character = tk.Button(root, text="Next Character", width=50, command=nextChar)
next_character.pack()

# Special Status Button
status_button = tk.Button(root, text="Special Stats", width=50, command = specialStatus)
status_button.pack()

# Refresh Display
refresh_button = tk.Button(root, text="Refresh Display", width=50, command=sortCombat)
refresh_button.pack()

# Define column widths
name_width = maxNameLength + 2  # Extra padding
type_width = 12
initiative_width = 12

# Frame to hold Listbox and Scrollbar
frame = tk.Frame(root)
frame.pack(padx=10, pady=10)

# Create a Listbox inside the frame
listbox = tk.Listbox(frame, width=100, height=30, yscrollcommand=lambda *args: scrollbar.set(*args))
listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Add Scrollbar
scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL, command=listbox.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Link Listbox to Scrollbar
listbox.config(yscrollcommand=scrollbar.set)

# Quit Button
button = tk.Button(root, text="Quit", width=50, command=root.destroy)
button.pack()

root.mainloop()