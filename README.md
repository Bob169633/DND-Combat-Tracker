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
I originally tried to design this as a linked list because I thought it would be cool. However a linked list, for me, was a lot harder to implement than using an array.

* Create Char: The function that I use to create each of the characters. It uses the character's name to create a character object with the name as both the object name and the character's name attribute. It then appends the new character to the combat array.

* Display Combat: The function I use to display the combat order and all that information in the Tkinter GUI window. I have an overview line that displays the current round number, the current turn number, and the total amount of turns so far. I then display each character's NAME, CHTYPE, and INITIATIVE in the listbox, along with any special statuses they have. The current character's turn is "highlighted" by a row of asterisks above and below any relevant information to that character. Additionally, if the current character has any special effects, the effects are NOT indented by dashes as they would be if it wasn't the current character's turn. 

* Sort Combat: The sort combat function uses a decreasing bubble sort algorithm and sorts the characters based off of initiative. The priority described above helps sort the players into the correct initiative order. It then refreshes the Tkinter GUI window with the updated combat order.

* Next Char: The function that I use to go to the next character. This function keeps track of the total number of rounds the combat has progressed, as well as the total number of turns and what the current turn count in the round is. This function also keeps track of any statuses that may be applied to any character and decreases the duration of that effect if the current turn is the same turn as when it was applied. (Ex. There are 4 turns in a round and on turn 1 Player A blinds Enemy A for 1 round, ending on Player A's next turn. When it gets back to Player A's turn, the condition applied to Enemy A is removed.) It then refreshes the Tkinter GUI window with the updated current player "highlighted"

* Add Char: The function used to add any characters that enter combat after combat has already started. Because I don't have the DM enter in the initiative role for enemies and NPCs, the first simpledialog pop up asks for the character's NAME, CHTYPE, and BONUS. Then depending on CHTYPE, it assigns a random roll if EN or NPC, 20 if LA, or if PC another simpledialog pop up asks for the initiative roll. Then it calls the createChar and sortCombat functions.

* Special Status: The function that I implemented to track any special statuses or effects that could be applied to any character, ex. a barbarian's rage, blinded, frightened, etc. The first pop up asks for the character's name, then the second pop up asks for the Effect and Duration in Effect,Duration format. It also records the round that the condition is applied and creates a fifth attribute array called Status on whatever character the effect was applied to. Then, like the other functions, it refreshes the Tkinter GUI window with the updated effects under the character's name.

## Section 3: The Files
My dad had told me about a tcl program he made back in the day when he was first DM-ing and how he created special files called .combat files to enter character information, and I thought that was a cool idea so I decided to make it my own.

* Open File: The function I use to open any character file. It asks you to select the folder that you have the character files in and then strips each line for NAME, CHTYPE, BONUS, and INIT or NAME, CHTYPE, BONUS if there aren't enough values (ex. the file is an enemy file)

* Character Files: I recommend using these files if these characters are all starting combat together. I have the player file as "players.txt", but ultimately you can name the players file whatever you'd like, you just need to change it in the code. For the enemies file(s), I have it structured as an array where you can enter multiple .txt files and it will open all of them for you.

## Seciton 3B: Formatting Character Files
When I was coding the open_file function, I had to think of a way for the same format to be used in both the players.txt as well as any enemy.txt file you'd specify so that way there would only be 1 open_file function.

* Players.txt: The players.txt file should be structured where each line is a separate character. Each line should follow the NAME, CHTYPE, BONUS, and INITIATIVE format that I've been using above, entered as NAME,CHTYPE,BONNUS,INITIATIVE with no spaces. This file should also be for player characters only, as an ease of use for you, that way when you're initiating combat and entering each player's rolls into the file you don't have to look through each line for what type the character is.

* Enemies.txt: Any enemy.txt file you write should follow the same guide lines as the players.txt file, EXCEPT you don't enter any INITIATIVE roll. You can also enter in as many of these files as you'd like into the enemy array, following standard string array formatting. You can also have any CHTYPE in these files, however it is not recommended that you write and PC characters into these files.

One more thing to note, you don't have to use the enemy array if you want to enter in the enemies manually, but that takes more time.

## Section 4: Tkinter GUI
I first started this whole project off displaying the combat order into the Visual Studio Code terminal window, but then I was like "wait, that's just annoying to have VS Code open and look at that while also having other windows open", so I came up with using a Tkinter GUI to display everything!

* Start Combat Button: calls the start combat function.

* Add Character Button: calls the add character function.

* Next Character Button: calls the next character function.

* Status Button: calls the special status function.

* Refresh Button: calls the display combat function.

I use a listbox to display the combat order because I discovered it was the easiest way to write and rewrite the data to the Tkinter window. I also implemented a scroll bar so you can scroll down if there are too many characters.

## Section 5: Conclusion
That's all I have for now! If there's anything else you'd want to see in this program or any recommendations you have for me, feel free to let me know! Right now, here are some future changes I plan on implementing:

* A delete character button/function to remove a character from combat if they die or leave combat.

* A remove status effect button/function to remove a status from a character if the status ends earlier than expected, think losing concentration on a spell.

# Thank you for taking the time to look at this README file and looking at my project! - PerkelzThePretzel
