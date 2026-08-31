# DND Combat Tracker

A Python/Tkinter combat tracker designed for running tabletop RPG combat with initiative ordering, character cards, HP tracking, status effects, death saves, player character saving/loading, and permanent equipment-based effects.

---

## Features

### Combat Initiative Tracking
- Add player characters, special player characters, NPCs, enemies, and lair actions to combat.
- Automatically sorts combatants by initiative.
- Tracks the current round, current turn, and total turn count.
- Highlights the active character on the combat display.
- Move to the next character with one button.
- Return the combat list to initiative order after manual rearranging.

---

### Supported Character Types
- **PC**: Player Character
- **SPC**: Special Player Character
- **NPC**: Non-Player Character
- **EN**: Enemy
- **LA**: Lair Action

Lair actions automatically use initiative 20.

---

### Manual Character Entry
- Add one or multiple characters at once.
- Enter a character name, type, initiative bonus, initiative roll, count, HP/formula, and current HP.
- Leave initiative blank to automatically roll initiative.
- Use count to quickly add multiple copies of the same enemy.
- Multiple enemies are automatically numbered when count is greater than 1.

---

### HP Tracking
- Tracks current HP and maximum HP.
- Click a character’s HP on their card to open the HP adjustment window.
- Apply damage or healing from the HP popup.
- HP cannot exceed maximum HP.
- HP cannot go below 0.

---

### Enemy and NPC Removal
- NPCs and enemies are automatically removed from combat when reduced to 0 HP.
- Player characters and special player characters remain in combat at 0 HP for death save tracking.

---

### Death Save Tracking
- Player characters and special player characters at 0 HP display death save controls.
- Supports:
  - Stabilize
  - Critical Success
  - Success
  - Failure
  - Critical Failure
- Three successes restore the character to 1 HP.
- Three failures remove the character from combat.
- Critical success restores the character to 1 HP.
- Stabilize restores the character to 1 HP.
- Critical failure adds two failed death saves.

---

### Temporary Status Effects
- Add temporary status effects to any character in combat.
- Set the number of rounds each status lasts.
- Temporary statuses automatically tick down based on the turn they were applied on.
- Temporary statuses are removed when their duration reaches 0.
- Temporary statuses display directly on the character’s combat card.
- Hover over a status to see when it ends.
- Remove temporary statuses manually from the character card.

---

### Permanent Status Effects
- Add permanent statuses to characters for long-term equipment, passive effects, or persistent abilities.
- Permanent statuses are stored on the character instead of only the current combat.
- Permanent statuses can be saved with player characters and loaded into future combats.
- Permanent statuses can have automatic start-turn or end-turn effects.
- Supported permanent effect triggers:
  - None
  - Start of turn
  - End of turn
- Supported permanent effect types:
  - None
  - Heal
  - Damage
- Example permanent effect:
  - Ring of Regeneration
  - Trigger: Start of turn
  - Effect: Heal
  - Amount: 1
- Permanent statuses display separately from temporary statuses on character cards.
- Permanent statuses can be removed manually from the character card.

---

### Automatic Permanent Effects
- Permanent statuses can automatically apply healing or damage.
- Start-turn effects trigger when the character becomes the active turn.
- End-turn effects trigger before moving away from the current character.
- Healing effects respect the character’s maximum HP.
- Damage effects cannot reduce HP below 0.
- Automatic damage can trigger the normal 0 HP behavior.

---

### Player Character Saving
- Save all PC and SPC characters to a CSV file.
- Saved player characters include:
  - Name
  - Character type
  - Initiative bonus
  - Maximum HP
  - Current HP
  - Permanent statuses
- Temporary combat statuses are not saved as part of player character profiles.

---

### Player Character Loading
- Load saved player characters from a CSV file.
- Loaded players open in a review window before being added to combat.
- Initiative bonuses are automatically loaded.
- Current HP can be edited before adding the characters to combat.
- Initiative rolls can be entered before adding the characters to combat.
- Leaving initiative blank automatically rolls initiative.
- Permanent statuses load with the character.

---

### Combat Saving and Loading
- Save the full current combat to a CSV file.
- Load a previously saved combat.
- Saved combat includes:
  - Round number
  - Current turn index
  - Total turn count
  - Character list
  - Initiative values
  - HP values
  - Death save progress
  - Temporary statuses
  - Permanent statuses

---

### Drag-and-Drop Reordering
- Manually reorder character cards by dragging them.
- Dragging uses a short hold delay to prevent accidental movement.
- Reordering preserves the current active character.
- The combat list can be restored to initiative order at any time.

---

### Card-Based Combat Display
- Each combatant is shown as a large card.
- Cards display:
  - Character name
  - Initiative
  - Character type
  - Current HP and maximum HP
  - Death saves when applicable
  - Temporary statuses
  - Permanent statuses
- The active character is marked on their card.
- Cards automatically wrap based on available window width.

---

### Custom Background Colors
- Change the tracker background color from a dropdown.
- Background color applies to the main window.
- Popup windows use the selected background color.

---

### Custom Fonts
- Change the card name/title font from a dropdown.
- Font changes apply to combat cards immediately.

---

### Popup Windows
- Add Characters, Add Statuses, Load Players, and HP adjustment open in separate popup windows.
- Popup windows use the current selected background color.
- Popup windows are designed to open near the mouse position.

---

### Scrollable Combat View
- Combat cards are displayed in a scrollable area.
- The display prevents scrolling past the top or bottom of the combat area.
- The combat view resets to the top after refreshing.

---

### Optional Border Image
- The combat cards can use a custom border image.
- Supported border filenames:
  - `border.jpg`
  - `border.jpeg`
  - `border.png`
- The border image should be placed in the same folder as `DND_Combat_Tracker.py`.

---

## File Overview

### Main Program
- `DND_Combat_Tracker.py`
  - Main application file.
  - Builds the main window.
  - Connects all buttons, windows, combat state, saving/loading, HP, statuses, and display refreshes.

### Character Creation
- `Create_Chars.py`
  - Defines the character object.
  - Stores name, type, initiative bonus, initiative, HP, death saves, temporary statuses, and permanent statuses.

### Combat State
- `Combat_State.py`
  - Stores the active combat list.
  - Handles sorting, turn order, round tracking, and manual reordering.

### Combat Display
- `Display_Combat.py`
  - Draws the combat cards.
  - Handles scrolling, drag-and-drop reordering, status display, HP clicking, death save buttons, and card layout.

### Add Characters Window
- `Add_Characters_Window.py`
  - Popup for manually adding characters to combat.
  - Supports multiple entries, initiative rolls, HP, formulas, and enemy counts.

### Load Players Window
- `Load_Players_Window.py`
  - Popup for reviewing saved player characters before adding them to combat.
  - Allows current HP and initiative rolls to be entered before combat begins.

### HP Window
- `HP_Window.py`
  - Popup for applying damage or healing to a character.

### Status Window
- `Status_Window.py`
  - Popup for adding temporary and permanent statuses.
  - Supports permanent status triggers and automatic effects.

### Status Effects
- `Status_Effects.py`
  - Handles temporary status tracking.
  - Handles permanent status storage, removal, display text, and automatic healing/damage effects.

### Combat Save/Load
- `Save_Load_Combat.py`
  - Saves and loads full combat state.

### Player Save/Load
- `Player_Storage.py`
  - Saves and loads PC/SPC character profiles.

### HP Rolling
- `Roll_HP.py`
  - Rolls HP formulas for enemies and NPCs.
  - Supports direct HP numbers and dice formulas.

---

## HP Formula Examples

Enemy and NPC HP can be entered as a number or dice formula.

Examples:

```text
12
d6+1
1d8+2
2d8+6
4d10+20