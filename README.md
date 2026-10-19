# DND Combat Tracker

A Python/Tkinter combat tracker for running tabletop RPG encounters. It manages initiative, character cards, hit points, temporary and permanent status effects, death saves, saved player profiles, and a read-only player website. The tracker also supports character theme music, custom sound playback, and gradual Windows system-volume adjustments.

## Requirements and setup

- **Python 3** on Windows (the Windows master-volume features specifically require Windows).
- **Pillow** for image backgrounds and previews.
- **pygame** for theme and custom audio playback.
- **pycaw** and **comtypes** for Windows master-volume control.
- **qrcode** (with Pillow) for the player-website QR code.

Install the main optional/third-party dependencies using the Python interpreter that runs the tracker:

```powershell
python -m pip install pillow pygame pycaw comtypes "qrcode[pil]"
```

`tkinter`, `csv`, and the built-in HTTP server are provided with standard Python distributions that include Tk support. For packaged executables, the required libraries must be included when building the application.

Start the application with:

```powershell
python DND_Combat_Tracker.py
```

The application opens fullscreen and allows a choice between visible control buttons and hotkey-oriented operation.

## Combat and initiative

- Add multiple combatants, including duplicate enemies in a single operation.
- Roll initiative automatically when an initiative-roll field is left blank; initiative bonuses are supported.
- Sort combatants by initiative; manually drag cards to reorganize the order and restore the original initiative sort when needed.
- Track rounds, current turns, and total turns, with the active character visually highlighted.
- Clear the encounter and reset round/turn counts together with **Ctrl+Delete**, after confirmation.
- **Lair Actions (LA)** use initiative **20**; LA stands for *Lair Action*, not Legendary Action.

### Character types

| Type | Meaning | HP behavior |
| --- | --- | --- |
| `PC` | Player Character | Retains death-save controls at 0 HP |
| `SPC` | Special Player Character | Retains death-save controls at 0 HP |
| `NPC` | Non-Player Character | Removed when reduced to 0 HP |
| `EN` | Enemy | Removed when reduced to 0 HP |
| `LA` | Lair Action | No HP or Temp HP |

### Adding characters

The Add Characters popup supports name, character type, initiative bonus, initiative roll, count, HP or HP formula, current HP, and **Temp HP**. PCs/SPCs use direct HP values, while NPCs/enemies can use a numeric value or dice formula. Multiple copies receive numbered names. Empty Temp HP fields default to **0**.

Example HP entries:

```text
12
d6+1
1d8+2
2d8+6
4d10+20
```

## Hit points and death saves

- Track **maximum HP**, **current HP**, and **temporary HP** for every non-Lair character.
- Click the HP area of a card to open the damage/healing popup or adjust Temp HP.
- **Damage removes Temp HP first**, and any remaining damage reduces current HP.
- Healing restores current HP, capped at maximum HP; it does not replenish Temp HP.
- The bloodied indicator depends on **current HP at or below half of maximum HP**, not on Temp HP.
- PC/SPC characters at 0 HP show controls for **Stabilize**, **Critical Success**, **Success**, **Failure**, and **Critical Failure**.
- Three successes, a critical success, or stabilization restore a PC/SPC to 1 HP in this tracker; three failures remove the character, and a critical failure adds two failures.

## Status effects

Statuses can be applied to a selected target and linked to a selected **caster/trigger character**. The Add Statuses popup includes:

`Caster | Status | Duration | Target | Effect Trigger | Permanent | Amount | Effect`

- **Temporary statuses** count down on the selected character's **start** or **end** of turn, rather than relying on initiative positions. This remains consistent after manual initiative reordering.
- The end of the caster's current turn can count as the first end-of-turn trigger.
- **Permanent statuses** continue until removed and can be retained with player profiles.
- Both temporary and permanent statuses can perform an automatic effect at their specified trigger: **None**, **Heal**, **Damage**, or **Temp HP**.
- Damage effects consume Temp HP before actual HP; healing respects maximum HP.
- Temp HP granted by status effects retains the higher of the existing amount and the new amount rather than adding the two amounts.
- Status badges appear on combat cards; hover for expiration/trigger information or remove statuses manually.
- Temporary durations are shown in **rounds**, even though their internal countdown follows the configured character's turn events.

For example, a temporary Burning status could cause 5 damage at the end of a specified character's turn for 3 triggers; a permanent Ring of Regeneration could heal 1 HP at the start of each turn.

## Saving and loading

### Saved player profiles (PC/SPC)

Save selected player-character information to CSV for reuse in later combats. Supported saved information includes name, character type, initiative bonus, max/current/Temp HP, permanent statuses, individual card background, and character theme audio path. **Temporary combat statuses do not become permanent player-profile data.**

When loading players, the review window allows edits to:

- Name and initiative bonus.
- Maximum HP, current HP, and Temp HP (defaulting to 0 when not provided).
- Initiative roll (blank rolls automatically).
- Character theme/audio assignment.

The **Reset Current HP to Max HP** button copies each player's displayed Max HP into their Current HP field before adding them to combat.

### Combat saves

Save and reload an encounter as CSV, including combatants and initiative, current round/turn counters, HP and Temp HP, death-save progress, temporary and permanent statuses, card-background assignments, and theme-audio assignments. Older saves without newly added fields generally default missing optional values; keep a backup before relying on compatibility with very old save formats.

## Combat display and appearance

- Large, scrollable, draggable combatant cards, wrapping to fit the window.
- Active-turn indicator and flashing **bloodied** border at half HP or less.
- Character information, status badges, and death-save controls displayed on cards as applicable.
- Fullscreen background color or image, selectable fonts, and separate card-background images by character type.
- **Individual PC/SPC card backgrounds** configured from the Player Card Backgrounds popup (**Ctrl+P**), with the normal PC/SPC image as fallback.
- Image options from the local **`graphics/`** directory, as well as selected external image files; supported formats include `.png`, `.jpg`, `.jpeg`, and `.webp`.
- Background previews in the relevant configuration dialogs, using the enlarged preview design.
- Configuration includes campaign name and player-website settings, saved in `config.json` beside the application.

## Player website (local network)

The tracker can host a **read-only player view** using a local HTTP server. The server displays combat order, current turn/round, status effects, the configured background, and character-card images; it refreshes automatically as the DM changes combat.

- Players can join from a browser on the same reachable network using the link or **QR code** provided by the tracker.
- **PC/SPC exact HP and Temp HP** can be shown.
- **NPC/enemy exact HP and Temp HP are hidden**; a flashing red border indicates bloodied status without displaying numerical HP.
- The website is view-only: player devices do not edit combat state.
- **Ctrl+W** opens the player website; **Ctrl+V** opens server/network status.
- Port and enabled/disabled state are configurable (default port **8080**).

Network access depends on routing, firewalls, and whether the Wi-Fi/hotspot isolates connected devices. A Windows Mobile Hotspot hosted on the tracker computer may be useful when the venue's network blocks device-to-device connections.

## Audio Themes

Open **Audio Themes** using **Ctrl+M** or its application button. This window supports:

- A case-insensitive, alphabetically ordered list of current non-Lair characters.
- A character-specific theme path and **Play**, **Stop**, **Choose**, and **Clear** controls.
- Audio assignments saved with player profiles and combat saves.
- A **Custom Audio** section to choose and play a sound without associating it with a character, useful for monster cries, environmental effects, and boss music.
- Master **theme-playback** volume slider, a **Loop** option, **Stop All Audio**, and **Open Audio Folder**.
- Playing a new track stops the currently playing track; only one track uses the theme playback channel at a time.
- Non-looping playback fades during approximately the **last 3 seconds** when track duration is available; looping tracks do not fade between repeats.
- Common files include `.mp3`, `.wav`, and `.ogg`.

Place audio files in the project's **`audio/`** folder, which the program can create automatically. Files can also be selected from elsewhere on disk. Moving a referenced file may require assigning it again.

### Windows system-volume automation

The Audio Themes popup also has settings for independently adjusting the **Windows master volume** (not just the theme player's volume):

- **Lower target %**, **Raise target %**, and **Duration (seconds)**.
- **Save Volume Settings** to retain the automation settings.
- **Ctrl+-** gradually moves the master volume down toward the lower target.
- **Ctrl+Shift++** gradually moves the master volume up toward the raise target.
- An active transition can be reversed by invoking the opposite direction; each stops on reaching the specified target.
- Smooth changes use frequent, time-based volume updates, subject to the sound device's available resolution.

- **Stop Volume Transition** immediately cancels any active master-volume change while leaving the current Windows volume unchanged and continuing audio playback.
- The Audio Themes playback-volume slider defaults to **100%** when the tracker starts.

## Hotkeys

### Alphabetic

| Hotkey | Action |
| --- | --- |
| Ctrl+E | Configuration |
| Ctrl+H | Show hotkey help |
| Ctrl+L | Load combat |
| Ctrl+M | Audio Themes |
| Ctrl+P | Player Card Backgrounds |
| Ctrl+Q | Quit (confirmation) |
| Ctrl+R | Refresh display |
| Ctrl+S | Save combat |
| Ctrl+V | Server Status |
| Ctrl+W | Open player website |

### Numeric

| Hotkey | Action |
| --- | --- |
| Ctrl+0 | Return to original initiative sort |
| Ctrl+1 | Add Characters |
| Ctrl+2 | Add Statuses |
| Ctrl+8 | Save Players |
| Ctrl+9 | Load Players |

### Special

| Hotkey | Action |
| --- | --- |
| Ctrl+- | Decrease Windows volume gradually |
| Ctrl+Shift++ | Increase Windows volume gradually |
| Ctrl+Delete | Clear combat and reset round/turn counts |
| Ctrl+Enter | Next character |
| Ctrl+Space | Start combat |

Keyboard behavior for `+` depends on the keyboard layout; the application also includes alternative key bindings for the increase command.

## Project files

| File | Purpose |
| --- | --- |
| `DND_Combat_Tracker.py` | Main application, window layout, callbacks, hotkeys, player-web state |
| `Combat_State.py` | Combatant list, initiative ordering, round and turn state |
| `Create_Chars.py` | Character objects and their saved properties |
| `Add_Characters_Window.py` | Manual character entry |
| `Load_Players_Window.py` | Review/edit saved PC/SPC profiles before combat |
| `Player_Storage.py` | Player CSV persistence |
| `Save_Load_Combat.py` | Combat CSV persistence |
| `Display_Combat.py` | Cards, status badges, HP/death-save interactions, dragging and scrolling |
| `HP_Window.py` | HP and Temp HP adjustments |
| `Roll_HP.py` | Numeric and dice-formula HP rolling |
| `Status_Window.py` | Temporary/permanent status entry |
| `Status_Effects.py` | Status durations, trigger tracking, and automatic effects |
| `Config_Window.py` | Application configuration popup |
| `Config_Storage.py` | Persistent configuration values |
| `Graphics_Options.py` | Background and image selection helpers |
| `Player_Card_Backgrounds_Window.py` | Individual PC/SPC background selection |
| `Player_Web_Server.py` | Local read-only browser view |
| `Audio_Themes_Window.py` | Character themes, custom audio, playback and volume automation |
| `graphics/` | Optional images for backgrounds and cards |
| `audio/` | Optional character themes and custom sounds |
| `config.json` | Generated/saved application settings |

Other supporting modules may be present in a particular project version. Do not remove a module from an existing working installation solely because it is not listed above.

## Notes

- The program runs locally; player-browser access is intended for a trusted local network, not public internet exposure.
- Audio processing scripts for extracting or altering elk/monster recordings (librosa, SciPy, noisereduce, FFmpeg) are separate utilities; they are **not required to run the combat tracker**.
- Dependencies used to *create* audio are distinct from those needed for *playing* it in the tracker.
