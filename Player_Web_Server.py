import copy
import json
import mimetypes
import socket
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote

from Graphics_Options import resolve_image_path


PLAYER_PAGE = r"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>D&D Combat Tracker</title>
  <style>
    :root {
      color-scheme: dark;
      font-family: Georgia, serif;
    }

    * {
      box-sizing: border-box;
    }

    html,
    body {
      min-height: 100%;
      margin: 0;
    }

    body {
      background: #000;
      background-position: center;
      background-repeat: no-repeat;
      background-size: cover;
      color: #fff;
    }

    .shade {
      min-height: 100vh;
      padding: 24px;
      background: rgba(0, 0, 0, 0.28);
    }

    header {
      max-width: 1500px;
      margin: 0 auto 18px;
      padding: 12px 16px;
      border-radius: 14px;
      background: rgba(0, 0, 0, 0.58);
      backdrop-filter: blur(5px);
      text-align: center;
    }

    h1 {
      margin: 0 0 6px;
      font-size: clamp(1.8rem, 4vw, 3rem);
    }

    #round {
      margin: 0;
      font-size: 1.15rem;
    }

    #status {
      min-height: 1.2em;
      margin-top: 6px;
      color: #ddd;
      font-family: Arial, sans-serif;
      font-size: 0.9rem;
    }

    #cards {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      gap: 18px;
      max-width: 1500px;
      margin: 0 auto;
    }

    .card {
      position: relative;
      min-height: 300px;
      overflow: hidden;
      border: 4px solid transparent;
      border-radius: 16px;
      background: #2b2b2b center / 100% 100% no-repeat;
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.45);
      transition: border-color 180ms ease;
    }

    .card.active {
      border-color: #32ff66;
      animation: activePulse 1s infinite;
    }

    .card.bloodied:not(.active) {
      border-color: #ff3030;
      animation: bloodiedPulse 1.8s infinite;
    }

    .card-content {
      min-height: 300px;
      padding: 28px 26px;
      background: linear-gradient(
        180deg,
        rgba(0, 0, 0, 0.52),
        rgba(0, 0, 0, 0.30) 45%,
        rgba(0, 0, 0, 0.56)
      );
      text-shadow: 0 2px 4px #000, 0 0 8px #000;
    }

    .turn-marker {
      min-height: 1.4em;
      color: #4dff76;
      font-size: 1.25rem;
      font-weight: bold;
    }

    .name {
      margin: 2px 0 8px;
      font-size: clamp(1.35rem, 2.5vw, 2rem);
      text-align: center;
    }

    .info {
      margin: 4px 0;
      text-align: center;
      font-family: Arial, sans-serif;
      font-weight: 700;
    }

    .health {
      margin: 12px 0;
      text-align: center;
      font-family: Arial, sans-serif;
      font-size: 1.05rem;
      font-weight: 800;
    }

    .health.bloodied-text {
      color: #ff7777;
    }

    .section-title {
      margin: 18px 0 8px;
      padding-top: 12px;
      border-top: 1px solid rgba(255, 255, 255, 0.45);
      text-align: center;
      font-family: Arial, sans-serif;
      font-size: 0.9rem;
      font-weight: 800;
    }

    .statuses {
      display: flex;
      flex-wrap: wrap;
      justify-content: center;
      gap: 6px;
    }

    .status-badge {
      padding: 5px 9px;
      border: 1px solid rgba(255, 255, 255, 0.45);
      border-radius: 999px;
      background: rgba(0, 0, 0, 0.50);
      font-family: Arial, sans-serif;
      font-size: 0.84rem;
    }

    .none {
      opacity: 0.8;
      font-family: Arial, sans-serif;
      font-size: 0.9rem;
    }

    @keyframes activePulse {
      0%, 100% {
        box-shadow: 0 0 8px rgba(50, 255, 102, 0.40), 0 8px 24px rgba(0, 0, 0, 0.45);
      }
      50% {
        box-shadow: 0 0 26px rgba(50, 255, 102, 0.95), 0 8px 24px rgba(0, 0, 0, 0.45);
      }
    }

    @keyframes bloodiedPulse {
      0%, 100% {
        box-shadow: 0 0 6px rgba(255, 48, 48, 0.35), 0 8px 24px rgba(0, 0, 0, 0.45);
      }
      50% {
        box-shadow: 0 0 24px rgba(255, 48, 48, 0.90), 0 8px 24px rgba(0, 0, 0, 0.45);
      }
    }

    @media (max-width: 650px) {
      .shade {
        padding: 12px;
      }

      #cards {
        grid-template-columns: 1fr;
      }
    }
  </style>
</head>
<body>
  <div class="shade">
    <header>
      <h1 id="campaign">D&D Combat</h1>
      <p id="round">Round 1</p>
      <div id="status">Connecting...</div>
    </header>
    <main id="cards"></main>
  </div>

  <script>
    let lastRevision = null;

    function addStatusBadges(container, statuses) {
      if (!statuses || statuses.length === 0) {
        const none = document.createElement("span");
        none.className = "none";
        none.textContent = "None";
        container.appendChild(none);
        return;
      }

      for (const status of statuses) {
        const badge = document.createElement("span");
        badge.className = "status-badge";
        badge.textContent = status;
        container.appendChild(badge);
      }
    }

    function buildCard(character, revision) {
      const card = document.createElement("article");
      card.className = "card";

      if (character.active) {
        card.classList.add("active");
      }

      if (character.bloodied === true) {
        card.classList.add("bloodied");
      }

      if (character.has_card_image) {
        card.style.backgroundImage =
          `url("/media/character/${encodeURIComponent(character.id)}?v=${revision}")`;
      }

      const content = document.createElement("div");
      content.className = "card-content";

      const marker = document.createElement("div");
      marker.className = "turn-marker";
      marker.textContent = character.active ? "▶ CURRENT TURN" : "";
      content.appendChild(marker);

      const name = document.createElement("h2");
      name.className = "name";
      name.textContent = character.name;
      content.appendChild(name);

      const initiative = document.createElement("div");
      initiative.className = "info";
      initiative.textContent = `Initiative: ${character.initiative}`;
      content.appendChild(initiative);

      const type = document.createElement("div");
      type.className = "info";
      type.textContent = `Type: ${character.type}`;
      content.appendChild(type);

      if (character.health_text) {
        const health = document.createElement("div");
        health.className = "health";

        if (character.bloodied === true) {
          health.classList.add("bloodied-text");
        }

        health.textContent = character.health_text;
        content.appendChild(health);
      }

      const statusTitle = document.createElement("div");
      statusTitle.className = "section-title";
      statusTitle.textContent = "Statuses";
      content.appendChild(statusTitle);

      const statuses = document.createElement("div");
      statuses.className = "statuses";
      addStatusBadges(statuses, character.statuses);
      content.appendChild(statuses);

      card.appendChild(content);
      return card;
    }

    function render(state) {
      document.title = `${state.campaign_name} - Combat`;
      document.getElementById("campaign").textContent = state.campaign_name;
      document.getElementById("round").textContent =
        `Round ${state.round} • Turn ${state.turn_number}`;

      document.body.style.fontFamily = state.font || "Georgia";

      if (state.background.type === "image" && state.background.has_image) {
        document.body.style.backgroundImage =
          `url("/media/background?v=${state.revision}")`;
        document.body.style.backgroundColor = "#000";
      } else {
        document.body.style.backgroundImage = "none";
        document.body.style.backgroundColor =
          state.background.value || "#000";
      }

      const cards = document.getElementById("cards");
      cards.replaceChildren();

      for (const character of state.characters) {
        cards.appendChild(buildCard(character, state.revision));
      }

      if (state.characters.length === 0) {
        const empty = document.createElement("div");
        empty.className = "card";
        empty.innerHTML =
          '<div class="card-content"><h2 class="name">No characters loaded.</h2></div>';
        cards.appendChild(empty);
      }
    }

    async function update() {
      try {
        const response = await fetch("/api/state", {
          cache: "no-store"
        });

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }

        const state = await response.json();

        if (state.revision !== lastRevision) {
          lastRevision = state.revision;
          render(state);
        }

        document.getElementById("status").textContent = "";
      } catch (error) {
        document.getElementById("status").textContent =
          "Waiting for the combat tracker...";
      }
    }

    update();
    setInterval(update, 1000);
  </script>
</body>
</html>
"""


def get_local_ip_address():
  sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

  try:
    sock.connect(("8.8.8.8", 80))
    return sock.getsockname()[0]
  except OSError:
    return "127.0.0.1"
  finally:
    sock.close()


def get_player_view_url(port):
  return f"http://{get_local_ip_address()}:{int(port)}"


class PlayerWebServer:
  def __init__(self):
    self.httpd = None
    self.thread = None
    self.port = None
    self.lock = threading.Lock()
    self.snapshot = {
      "revision": 0,
      "campaign_name": "D&D Campaign",
      "round": 1,
      "turn_number": 0,
      "font": "Georgia",
      "background": {
        "type": "color",
        "value": "black",
        "has_image": False
      },
      "characters": []
    }
    self.media_paths = {}

  def is_running(self):
    return self.httpd is not None

  def start(self, port):
    port = int(port)

    if self.is_running() and self.port == port:
      return

    self.stop()

    server_owner = self

    class Handler(BaseHTTPRequestHandler):
      def do_GET(self):
        path = unquote(self.path.split("?", 1)[0])

        if path == "/":
          self.send_html(PLAYER_PAGE)
          return

        if path == "/api/state":
          with server_owner.lock:
            payload = copy.deepcopy(server_owner.snapshot)

          self.send_json(payload)
          return

        if path == "/media/background":
          self.send_media("background")
          return

        if path.startswith("/media/card/"):
          character_type = path[len("/media/card/"):]
          self.send_media(f"card:{character_type}")
          return

        if path.startswith("/media/character/"):
          character_id = path[len("/media/character/"):]
          self.send_media(f"character:{character_id}")
          return

        self.send_error(404, "Not Found")

      def send_html(self, html):
        body = html.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

      def send_json(self, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

      def send_media(self, media_key):
        with server_owner.lock:
          stored_path = server_owner.media_paths.get(media_key)

        full_path = resolve_image_path(stored_path)

        if (
          full_path is None
          or not Path(full_path).is_file()
        ):
          self.send_error(404, "Image not found")
          return

        try:
          data = Path(full_path).read_bytes()
        except OSError:
          self.send_error(404, "Image not found")
          return

        content_type, _ = mimetypes.guess_type(str(full_path))

        if content_type is None:
          content_type = "application/octet-stream"

        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

      def log_message(self, format, *args):
        return

    self.httpd = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    self.httpd.daemon_threads = True
    self.port = port

    self.thread = threading.Thread(
      target=self.httpd.serve_forever,
      daemon=True
    )
    self.thread.start()

  def stop(self):
    if self.httpd is None:
      return

    httpd = self.httpd
    thread = self.thread

    self.httpd = None
    self.thread = None
    self.port = None

    httpd.shutdown()
    httpd.server_close()

    if thread is not None and thread.is_alive():
      thread.join(timeout=1.0)

  def update(self, snapshot, media_paths):
    with self.lock:
      self.snapshot = copy.deepcopy(snapshot)
      self.media_paths = dict(media_paths)
