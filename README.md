# Persona

**A quieter way to remember.**

Persona is an offline desktop companion for everyday tasks. A pixel-art character lives on your desktop, moves and reacts to interaction, and presents scheduled reminders as small floating notes. Tasks are stored locally in SQLite.

This repository also contains a responsive, static portfolio website that introduces the project. Its browser demo is illustrative only; it does not connect to the desktop application or create tasks.

>**Live**: https://vallchagas.github.io/projeto-postit/

## Features

- Autonomous idle, walking, sitting, emote, and fall animations.
- A task agenda with recent, upcoming, all, and completed filters.
- Create, edit, complete, and delete scheduled tasks.
- Floating reminder notes with an action to mark a task complete.
- Local SQLite storage; no account or backend required.
- A static portfolio site suitable for GitHub Pages.

## Tech stack

| Component | Technologies |
| --- | --- |
| Desktop application | Python, PyQt5, SQLite |
| Portfolio website | HTML, CSS, vanilla JavaScript |
| Website fonts | Google Fonts (EB Garamond, Lora, and JetBrains Mono) |
| Optional Windows executable | PyInstaller |

## Getting started

### Desktop application

**Requirements:** Python 3.8 or newer and `pip`.

1. Clone the repository and open its directory:

   ```bash
   git clone https://github.com/VallChagas/projeto-postit.git
   cd projeto-postit
   ```

2. (Recommended) Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   ```

   Windows PowerShell:

   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

   Windows Command Prompt:

   ```bat
   .venv\Scripts\activate.bat
   ```

3. Install PyQt5 and start the application:

   ```bash
   python -m pip install PyQt5
   python main.py
   ```

On first launch, Persona creates `tarefas.db` in the project directory. The reminder checker runs while the application is open.

### Portfolio website

The website is plain static HTML, CSS, and JavaScript. No build step or package installation is needed. To preview it locally, start a web server from the repository root:

```bash
python -m http.server 8000
```

Then open <http://localhost:8000> in a browser. The interactive demo animates a sample reminder locally; it does not read from or write to `tarefas.db`.

### Publish with GitHub Pages

The website uses relative paths and can be published from the repository root:

1. Push the repository to GitHub.
2. Open **Settings → Pages** for the repository.
3. Under **Build and deployment**, select **Deploy from a branch**, then choose the desired branch and the `/ (root)` folder.
4. Save and open the URL shown in the Pages settings.

Google Fonts is the only external website dependency. The desktop application itself runs locally and does not require the website.

## Using the desktop app

- **Left-click** the character to trigger an emote.
- **Right-click** to open the menu, launch the agenda, choose an animation, or exit.
- **Drag and release** the character in the upper half of the screen to trigger a fall and recovery animation.
- In the agenda, create a task with a title and reminder date/time. Tasks can also be edited, completed, or deleted.
- When a scheduled reminder is due, a floating note appears near the character. Choose **Complete** to mark the task done, or close the note to dismiss it.

The agenda provides filters for recent, upcoming, all, and completed tasks.

### Add a task from Python

The agenda is the recommended way to manage tasks. For scripts, `db.py` provides a small API:

```python
from datetime import datetime, timedelta

import db

db.criar_tabela()
reminder_time = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M")

db.adicionar_tarefa(
    titulo="Take a short break",
    descricao="Stretch and rest your eyes.",
    horario_lembrete=reminder_time,
)
```

The reminder time must use the `YYYY-MM-DD HH:MM` format. To inspect the database helper directly, run `python db.py`; this also inserts an immediate sample reminder.

## Build a Windows executable

Install PyInstaller:

```bash
python -m pip install pyinstaller
```

From the repository root in Windows, package the application and its sprites:

```bat
pyinstaller --noconsole --onefile --name "PersonaPet" --add-data "imagens;imagens" main.py
```

The executable is written to `dist/PersonaPet.exe`. When running the packaged app, the SQLite database is stored beside the executable. The generated `build/` and `dist/` directories are build outputs, not source files.

## Project structure

```text
.
├── assets/
│   ├── main.js
│   └── style.css
├── imagens/
│   └── persona/          # Character animation sprites
├── agenda.py             # Task agenda and dialogs
├── animacao.py           # Sprite loading and animation frames
├── avatar.py             # Desktop character and reminder windows
├── config.py             # Paths and animation settings
├── db.py                 # SQLite task operations
├── index.html            # Static portfolio website
├── main.py               # Desktop application entry point
└── verificador.py        # Scheduled reminder checker
```

`tarefas.db` is created at runtime and contains local task data. Back it up separately if you want to preserve tasks; do not publish a database containing personal reminders.

## Credits and licensing

The Persona sprites were assembled with the [Universal LPC Spritesheet Character Generator](https://liberatedpixelcup.github.io/Universal-LPC-Spritesheet-Character-Generator/). The generated artwork may include contributions under OGA-BY 3.0, CC-BY-SA 3.0, CC-BY 3.0, GPL 3.0, and CC0. Applicable terms depend on the individual assets; preserve the required attribution and share-alike notices when redistributing or adapting sprites.

Contributors identified for the generated sprites include bluecarrot16, Evert, TheraHedwig, Benjamin K. Smith (BenCreating), MuffinElZangano, Durrani, Pierre Vigier (pvigier), Eliza Wyatt (ElizaWy), Matthew Krohn (makrohn), Johannes Sjölund (wulax), Stephen Challener (Redshrike), JaidynReiman, Thane Brimhall (pennomi), laetissima, and Ahmad3366.

The repository does not currently include a project-wide `LICENSE` file. The licenses for the generated sprites do not automatically define the license for the rest of the project.
