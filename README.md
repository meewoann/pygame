# UEH Journey (Pygame)

A simple platformer-style game built with **Pygame**.

## ▶️ How to Run

1. Make sure you have Python 3.11+ and `pygame` installed:

```bash
python -m pip install pygame
```

2. From the project root, run:

```bash
python platfomer.py
```

## 🎮 Controls

- **Move left/right:** Arrow keys (← / →)
- **Jump / Double jump:** Right mouse button
- **Shoot:** Left mouse button (once per cooldown)

## 🖼️ Demo Screenshot

A sample game background is included in `assets/Background/`.

![Game Demo](assets/Background/_9d8b7719-9392-4635-8ff5-79c9e12f3207.jpg)

## 📂 Project Structure

- `platfomer.py` – main game script
- `assets/` – game sprites, backgrounds, and sound
  - `Background/` – background images
  - `MainCharacters/` – character spritesheets
  - `Terrain/` – terrain tiles
  - `Traps/` – hazard sprites

## 🧩 Notes

- The game uses relative paths, so it can be launched from any working directory.
- If you want to add your own background or sprites, put them under the appropriate folder in `assets/` and update `platfomer.py` accordingly.
