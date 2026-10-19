import sys
import time
import subprocess
import json
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox


AUDIO_FILETYPES = [
  ("Audio Files", "*.mp3 *.wav *.ogg"),
  ("MP3 Files", "*.mp3"),
  ("WAV Files", "*.wav"),
  ("OGG Files", "*.ogg"),
  ("All Files", "*.*")
]

SUPPORTED_AUDIO_SUFFIXES = {
  ".mp3",
  ".wav",
  ".ogg"
}


def app_folder():
  if getattr(
    sys,
    "frozen",
    False
  ):
    return Path(
      sys.executable
    ).resolve().parent

  return Path(
    __file__
  ).resolve().parent


def get_audio_folder():
  folder = app_folder() / "audio"
  folder.mkdir(
    parents=True,
    exist_ok=True
  )
  return folder


class AudioThemePlayer:
  def __init__(self):
    self._pygame = None
    self.volume = 1.0
    self.current_path = ""
    self.root = None
    self._fade_after = None
    self._fade_start = None
    self._fade_end = None
    self._duration = None

  def attach_root(self, root):
    self.root = root

  def cancel_fade(self):
    if self.root is not None and self._fade_after is not None:
      try:
        self.root.after_cancel(self._fade_after)
      except Exception:
        pass
    self._fade_after = None
    self._fade_start = None
    self._fade_end = None

  def _get_length(self, path):
    try:
      return float(self._pygame.mixer.Sound(str(path)).get_length())
    except Exception:
      try:
        from mutagen import File
        info = File(str(path))
        return float(info.info.length)
      except Exception:
        try:
          result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", str(path)],
            capture_output=True, text=True, timeout=5, check=True
          )
          return float(json.loads(result.stdout)["format"]["duration"])
        except Exception:
          return None

  def _fade_tick(self):
    self._fade_after = None
    if self._pygame is None or not self._pygame.mixer.music.get_busy():
      self._fade_start = None
      return
    elapsed = time.monotonic() - self._play_started
    if self._duration is not None:
      remaining = self._duration - elapsed
      if remaining <= 0:
        self._pygame.mixer.music.set_volume(0)
        return
      fraction = min(1.0, max(0.0, remaining / min(3.0, self._duration)))
      self._pygame.mixer.music.set_volume(self.volume * fraction)
    self._fade_after = self.root.after(80, self._fade_tick)

  def ensure_ready(self):
    if self._pygame is not None:
      return

    try:
      import pygame
    except ImportError as error:
      raise RuntimeError(
        "Audio playback requires pygame.\n\n"
        "Install it with:\n"
        "py -m pip install pygame"
      ) from error

    try:
      pygame.mixer.init()
    except Exception as error:
      raise RuntimeError(
        "The audio mixer could not be initialized.\n\n"
        f"{error}"
      ) from error

    self._pygame = pygame
    self.set_volume(
      self.volume
    )

  def play(self, filepath, loop=False):
    path = Path(
      filepath
    ).expanduser()

    if not path.is_file():
      raise RuntimeError(
        "The assigned theme file could not be found:\n"
        f"{path}"
      )

    self.cancel_fade()
    self.ensure_ready()
    self._pygame.mixer.music.stop()
    self._pygame.mixer.music.load(
      str(path)
    )
    self._pygame.mixer.music.set_volume(
      self.volume
    )
    self._pygame.mixer.music.play(
      -1 if loop else 0
    )
    self.current_path = str(path)
    self._duration = None if loop else self._get_length(path)
    self._play_started = time.monotonic()
    if not loop and self.root is not None:
      self._fade_after = self.root.after(80, self._fade_tick)

  def stop(self):
    self.cancel_fade()
    if self._pygame is not None:
      self._pygame.mixer.music.stop()

    self.current_path = ""

  def set_volume(self, volume):
    try:
      volume = float(volume)
    except (TypeError, ValueError):
      volume = 0.7

    self.volume = max(
      0.0,
      min(
        1.0,
        volume
      )
    )

    if self._pygame is not None:
      fraction = 1.0
      if self._fade_after is not None and self._duration is not None:
        remaining = self._duration - (time.monotonic() - self._play_started)
        fraction = min(1.0, max(0.0, remaining / min(3.0, self._duration)))
      self._pygame.mixer.music.set_volume(self.volume * fraction)

  def shutdown(self):
    self.cancel_fade()
    if self._pygame is None:
      return

    try:
      self._pygame.mixer.music.stop()
      self._pygame.mixer.quit()
    except Exception:
      pass

    self._pygame = None
    self.current_path = ""


class SystemVolumeController:
  def __init__(self, root, config, save_callback):
    self.root = root
    self.config = config
    self.save_callback = save_callback
    self._pending = None

  def _endpoint(self):
    try:
      from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
      from comtypes import CLSCTX_ALL
      device = AudioUtilities.GetSpeakers()
      endpoint = getattr(device, "EndpointVolume", None)
      if endpoint is not None:
        return endpoint
      return device.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None).QueryInterface(IAudioEndpointVolume)
    except Exception as error:
      raise RuntimeError(
        "Windows master-volume control requires pycaw and comtypes.\n"
        "Install with: py -m pip install pycaw comtypes\n\n"
        f"{error}"
      ) from error

  def transition(self, direction):
    self.cancel()
    endpoint = self._endpoint()
    settings = self.config.setdefault("audio_volume", {})
    target = float(settings.get("decrease_target" if direction == "down" else "increase_target", 20 if direction == "down" else 100)) / 100
    seconds = max(0.1, float(settings.get("duration", 5)))
    starting = endpoint.GetMasterVolumeLevelScalar()
    if (direction == "down" and starting <= target) or (direction == "up" and starting >= target):
      return
    begun = time.monotonic()

    def step():
      self._pending = None
      progress = min(1.0, (time.monotonic() - begun) / seconds)
      value = starting + (target - starting) * progress
      try:
        endpoint.SetMasterVolumeLevelScalar(max(0, min(1, value)), None)
      except Exception:
        return
      if progress < 1:
        self._pending = self.root.after(10, step)

    step()

  def cancel(self):
    if self._pending is not None:
      self.root.after_cancel(self._pending)
      self._pending = None

  def update_settings(self, decrease, increase, duration):
    try:
      down = float(decrease)
      up = float(increase)
      seconds = float(duration)
    except (TypeError, ValueError):
      raise ValueError("Enter numeric volume targets and transition duration.")
    if not (0 <= down <= 100 and 0 <= up <= 100 and 0 < seconds <= 3600):
      raise ValueError("Targets must be 0–100%, and time must be greater than 0 and at most 3600 seconds.")
    self.config["audio_volume"] = {
      "decrease_target": int(down),
      "increase_target": int(up),
      "duration": seconds
    }
    self.save_callback(self.config)


class AudioThemesWindow:
  def __init__(
    self,
    root,
    characters,
    player,
    on_theme_changed=None,
    system_volume=None,
    background_color="black",
    mouse_x=None,
    mouse_y=None
  ):
    self.root = root
    self.characters = sorted(
      (char for char in characters if getattr(char, "chType", "") != "LA"),
      key=lambda char: char.name.casefold()
    )
    self.player = player
    self.on_theme_changed = on_theme_changed
    self.system_volume = system_volume
    self.background_color = background_color
    self.rows = []

    self.window = tk.Toplevel(
      root
    )
    self.window.title(
      "Audio Themes"
    )
    self.window.geometry(
      "1040x620"
    )
    self.window.configure(
      bg=self.background_color
    )
    self.window.grab_set()

    self.volume_var = tk.DoubleVar(
      value=self.player.volume * 100
    )
    self.loop_var = tk.BooleanVar(
      value=False
    )
    self.custom_audio_var = tk.StringVar(value="")

    self.build_window()
    self.place_window_at_mouse(
      mouse_x,
      mouse_y
    )
    self.grab_window_attention()

  def place_window_at_mouse(
    self,
    mouse_x=None,
    mouse_y=None
  ):
    if mouse_x is None or mouse_y is None:
      return

    self.window.update_idletasks()
    width = self.window.winfo_reqwidth()
    height = self.window.winfo_reqheight()
    vroot_x = self.window.winfo_vrootx()
    vroot_y = self.window.winfo_vrooty()
    vroot_width = self.window.winfo_vrootwidth()
    vroot_height = self.window.winfo_vrootheight()

    x = max(
      vroot_x,
      min(
        mouse_x + 20,
        vroot_x + vroot_width - width
      )
    )
    y = max(
      vroot_y,
      min(
        mouse_y + 20,
        vroot_y + vroot_height - height
      )
    )

    self.window.geometry(
      f"+{x}+{y}"
    )

  def grab_window_attention(self):
    self.window.lift()
    self.window.focus_force()
    self.window.attributes(
      "-topmost",
      True
    )
    self.window.after(
      250,
      lambda: self.window.attributes(
        "-topmost",
        False
      )
    )

  def build_window(self):
    top = tk.Frame(
      self.window,
      bg=self.background_color
    )
    top.pack(
      fill=tk.X,
      padx=12,
      pady=12
    )

    tk.Label(
      top,
      text="Volume",
      bg=self.background_color,
      fg="white"
    ).pack(
      side=tk.LEFT,
      padx=(0, 6)
    )

    tk.Scale(
      top,
      from_=0,
      to=100,
      orient=tk.HORIZONTAL,
      variable=self.volume_var,
      command=self.change_volume,
      length=220,
      bg=self.background_color,
      fg="white",
      highlightthickness=0
    ).pack(
      side=tk.LEFT
    )

    tk.Checkbutton(
      top,
      text="Loop",
      variable=self.loop_var,
      bg=self.background_color,
      fg="white",
      selectcolor="black",
      activebackground=self.background_color,
      activeforeground="white"
    ).pack(
      side=tk.LEFT,
      padx=16
    )

    tk.Button(
      top,
      text="Stop All Audio",
      command=self.player.stop
    ).pack(
      side=tk.RIGHT,
      padx=5
    )

    tk.Button(
      top,
      text="Open Audio Folder",
      command=self.open_audio_folder
    ).pack(
      side=tk.RIGHT,
      padx=5
    )

    if self.system_volume is not None:
      volume_settings = self.system_volume.config.get("audio_volume", {})
      setting_frame = tk.Frame(self.window, bg=self.background_color, height=48)
      setting_frame.pack(fill=tk.X, padx=12, pady=(0, 8))
      setting_frame.pack_propagate(False)
      self.down_var = tk.StringVar(value=str(volume_settings.get("decrease_target", 20)))
      self.up_var = tk.StringVar(value=str(volume_settings.get("increase_target", 100)))
      self.seconds_var = tk.StringVar(value=str(volume_settings.get("duration", 5)))
      for label, var, width in [
        ("Lower target %", self.down_var, 6),
        ("Raise target %", self.up_var, 6),
        ("Duration (s)", self.seconds_var, 7)
      ]:
        tk.Label(setting_frame, text=label, bg=self.background_color, fg="white").pack(side=tk.LEFT, padx=(6, 3))
        tk.Entry(setting_frame, textvariable=var, width=width).pack(side=tk.LEFT, fill=tk.Y, pady=5)
      tk.Button(setting_frame, text="Save Volume Settings", command=self.save_volume_settings).pack(side=tk.LEFT, padx=12, fill=tk.Y, pady=5)
      tk.Button(setting_frame, text="Stop Volume Transition", command=self.system_volume.cancel).pack(side=tk.LEFT, padx=6, fill=tk.Y, pady=5)

    custom_frame = tk.Frame(
      self.window,
      bg=self.background_color,
      height=84
    )
    custom_frame.pack(fill=tk.X, padx=12, pady=(0, 10))
    custom_frame.pack_propagate(False)

    tk.Label(
      custom_frame,
      text="Custom Audio (not assigned to a character)",
      bg=self.background_color,
      fg="white",
      anchor="w"
    ).pack(fill=tk.X, pady=(0, 5))

    custom_row = tk.Frame(custom_frame, bg=self.background_color, height=36)
    custom_row.pack(fill=tk.X)
    custom_row.pack_propagate(False)

    tk.Entry(
      custom_row,
      textvariable=self.custom_audio_var
    ).pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 6))

    for label, callback in [
      ("Play", self.play_custom_audio),
      ("Stop", self.player.stop),
      ("Choose", self.choose_custom_audio),
      ("Clear", lambda: self.custom_audio_var.set(""))
    ]:
      tk.Button(
        custom_row,
        text=label,
        width=8,
        command=callback
      ).pack(side=tk.LEFT, fill=tk.Y, padx=2)

    outer = tk.Frame(
      self.window,
      bg=self.background_color
    )
    outer.pack(
      fill=tk.BOTH,
      expand=True,
      padx=12,
      pady=(0, 12)
    )

    canvas = tk.Canvas(
      outer,
      bg=self.background_color,
      highlightthickness=0
    )
    scrollbar = tk.Scrollbar(
      outer,
      orient=tk.VERTICAL,
      command=canvas.yview
    )
    rows_frame = tk.Frame(
      canvas,
      bg=self.background_color
    )

    rows_frame.bind(
      "<Configure>",
      lambda event: canvas.configure(
        scrollregion=canvas.bbox(
          "all"
        )
      )
    )

    canvas_window = canvas.create_window(
      (0, 0),
      window=rows_frame,
      anchor="nw"
    )
    canvas.configure(
      yscrollcommand=scrollbar.set
    )
    canvas.pack(
      side=tk.LEFT,
      fill=tk.BOTH,
      expand=True
    )
    scrollbar.pack(
      side=tk.RIGHT,
      fill=tk.Y
    )
    canvas.bind(
      "<Configure>",
      lambda event: canvas.itemconfig(
        canvas_window,
        width=event.width
      )
    )

    header = tk.Frame(
      rows_frame,
      bg=self.background_color,
      height=34
    )
    header.pack(
      fill=tk.X,
      pady=(0, 4)
    )
    header.pack_propagate(
      False
    )

    tk.Label(
      header,
      text="Character",
      width=22,
      bg=self.background_color,
      fg="white"
    ).pack(
      side=tk.LEFT,
      fill=tk.Y
    )

    tk.Label(
      header,
      text="Theme",
      bg=self.background_color,
      fg="white"
    ).pack(
      side=tk.LEFT,
      fill=tk.BOTH,
      expand=True
    )

    tk.Label(
      header,
      text="Controls",
      width=34,
      bg=self.background_color,
      fg="white"
    ).pack(
      side=tk.RIGHT,
      fill=tk.Y
    )

    if not self.characters:
      tk.Label(
        rows_frame,
        text=(
          "There are no non-Lair "
          "characters in combat."
        ),
        bg=self.background_color,
        fg="white"
      ).pack(
        pady=25
      )

    for char in self.characters:
      self.add_character_row(
        rows_frame,
        char
      )

  def add_character_row(
    self,
    parent,
    char
  ):
    row = tk.Frame(
      parent,
      bg=self.background_color,
      height=42
    )
    row.pack(
      fill=tk.X,
      pady=2
    )
    row.pack_propagate(
      False
    )

    tk.Label(
      row,
      text=char.name,
      anchor="w",
      width=22,
      bg=self.background_color,
      fg="white"
    ).pack(
      side=tk.LEFT,
      fill=tk.Y
    )

    theme_var = tk.StringVar(
      value=getattr(
        char,
        "theme_audio",
        ""
      )
    )

    theme_entry = tk.Entry(
      row,
      textvariable=theme_var
    )
    theme_entry.pack(
      side=tk.LEFT,
      fill=tk.BOTH,
      expand=True,
      padx=(4, 8)
    )

    def commit_theme():
      char.theme_audio = (
        theme_var.get().strip()
      )

      if self.on_theme_changed is not None:
        self.on_theme_changed(
          char
        )

    def choose_theme():
      initial_dir = get_audio_folder()
      current = theme_var.get().strip()

      if current:
        current_path = Path(
          current
        )

        if current_path.exists():
          initial_dir = (
            current_path.parent
          )

      filepath = filedialog.askopenfilename(
        title=(
          f"Choose Theme - "
          f"{char.name}"
        ),
        initialdir=str(
          initial_dir
        ),
        filetypes=AUDIO_FILETYPES,
        parent=self.window
      )

      if not filepath:
        return

      theme_var.set(
        filepath
      )
      commit_theme()

    def clear_theme():
      theme_var.set("")
      commit_theme()

    def play_theme():
      commit_theme()
      filepath = (
        theme_var.get().strip()
      )

      if not filepath:
        messagebox.showinfo(
          "Audio Themes",
          (
            f"{char.name} does not "
            "have a theme assigned."
          ),
          parent=self.window
        )
        return

      try:
        self.player.play(
          filepath,
          loop=self.loop_var.get()
        )
      except RuntimeError as error:
        messagebox.showerror(
          "Audio Playback",
          str(error),
          parent=self.window
        )

    tk.Button(
      row,
      text="Play",
      width=7,
      command=play_theme
    ).pack(
      side=tk.LEFT,
      fill=tk.Y,
      padx=2
    )

    tk.Button(
      row,
      text="Stop",
      width=7,
      command=self.player.stop
    ).pack(
      side=tk.LEFT,
      fill=tk.Y,
      padx=2
    )

    tk.Button(
      row,
      text="Choose",
      width=8,
      command=choose_theme
    ).pack(
      side=tk.LEFT,
      fill=tk.Y,
      padx=2
    )

    tk.Button(
      row,
      text="Clear",
      width=7,
      command=clear_theme
    ).pack(
      side=tk.LEFT,
      fill=tk.Y,
      padx=2
    )

    theme_entry.bind(
      "<FocusOut>",
      lambda event: commit_theme()
    )

    theme_entry.bind(
      "<Return>",
      lambda event: commit_theme()
    )

    self.rows.append({
      "character": char,
      "theme": theme_var
    })

  def choose_custom_audio(self):
    initial_dir = get_audio_folder()
    current = self.custom_audio_var.get().strip()
    if current:
      path = Path(current).expanduser()
      if path.is_file():
        initial_dir = path.parent

    filepath = filedialog.askopenfilename(
      title="Choose Custom Audio",
      initialdir=str(initial_dir),
      filetypes=AUDIO_FILETYPES,
      parent=self.window
    )
    if filepath:
      self.custom_audio_var.set(filepath)

  def play_custom_audio(self):
    filepath = self.custom_audio_var.get().strip()
    if not filepath:
      messagebox.showinfo(
        "Custom Audio",
        "Choose an audio file before playing.",
        parent=self.window
      )
      return

    try:
      self.player.play(filepath, loop=self.loop_var.get())
    except RuntimeError as error:
      messagebox.showerror(
        "Audio Playback",
        str(error),
        parent=self.window
      )

  def save_volume_settings(self):
    try:
      self.system_volume.update_settings(
        self.down_var.get(), self.up_var.get(), self.seconds_var.get()
      )
    except ValueError as error:
      messagebox.showerror("Volume Settings", str(error), parent=self.window)

  def change_volume(
    self,
    value
  ):
    try:
      volume = float(value) / 100.0
    except (TypeError, ValueError):
      volume = 0.7

    self.player.set_volume(
      volume
    )

  def open_audio_folder(self):
    folder = get_audio_folder()

    try:
      import os
      os.startfile(
        str(folder)
      )
    except Exception as error:
      messagebox.showerror(
        "Audio Folder",
        (
          "The audio folder could "
          "not be opened.\n\n"
          f"{folder}\n\n{error}"
        ),
        parent=self.window
      )
