# DND-Combat-Tracker
A Python based DND Combat Initiative Tracker for DMs


## Summary
The tracker is based off of an array of custom objects called Characters and uses Tkinter GUI windows to display the combat order.

## Section 1: The Characters
I structured each Character object to have 4 different attributes: Name, Character Type (CHTYPE), Bonus, and Initiative.

* The NAME is self explanatory, just the character's name.

* The CHTYPE is one of 4 options; Player Character (PC), Non-Player Character (NPC), Enemy (EN), or Lair (LA). Use these abbreviations when writing down each character's type.

* The BONUS is just the bonus added to a character's initiative. When entered into a character file or the GUI window, you can enter the bonus as an integer and include the sign. Sign is not necessary for positive bonuses and no bonus is entered as a 0.

* The INITIATIVE is just the character's initiative, and mainly applies to the player.txt file, which is covered later. However, there is an order to what character types go first if there are multiple characters sharing the same initiative. I use priority which is added to the initiative and is dependent on what character type they are. Lairs have the highest priority, thus get +.3. Players go before other characters, and get a +.2. Enemies go next, with a +.1. NPCs go last, with +0. 


## Section 2: Combat
I originally tried to design this as a linked list because I thought it would be cool, however a linked list, for me, was a lot harder to implement than using an array.

* Create Char: The function that I use to create each of the characters. It uses the character's name to create a character object with the name as both the object name and the character's name attribute. It then appends the new character to the combat array.

* Sort Combat: The sort combat function uses a decreasing bubble sort algorithm and sorts the characters based off of initiative. The priority described above helps sort the players into the correct initiative order. It then refreshes the Tkinter GUI window with the updated combat order.

* Next Char: The function that I use to go to the next character. (README WIP)
