# Reflexa

Reflexa is a rythm based gesture game inspired by the viral tiktok trend (Woah Challenge) built using **Pygame**, **OpenCV**, and **MediaPipe**
It reimagines teh beat-drop reaction concept into and interactive compiter vision game where the players respond to music driven cues using real-time hand tracking

When the beat drops the player must move their hand in either UP, DOWN, RIGHT or LEFT direction and at the same time an arrow will appear on the screen.
If the player moves their hand in the same direction as the arrow, They Lose.
if they move their hand in a different direction than the arrow, They Score.

----

## Features

- Beat-synced random arrow spawning
- Real time hand tracking using MediaPipa
- Opposite direction gameplay logic
- Forgiving hit window
- Start, Countdown and Restart System
- Stable beat scheduling

---

## Tech Stack

- **Python**
- **Pygame** - UI & Game Loop
- **OpenCV** - Camera Feed
- **MediaPipe** - Hand Tracking
- **Numpy**

---

## How to Run

1. Clone the repository
2. Create a virtual environment (python -m venv venv -> venv/Scripts/activate)
3. Install depedencies (pip install pygame opencv-pthon mediapipe)
4. Run the game (main.py)

## Future Improvements

- Polished and refined UI
- Difficulty modes
- Leaderboard System
- Visual themes and customization
- Package as a standalone executable (.exe) for full game application release

---

## License

This project is for educational and personal use. It is intended as a learning and experimentation project demonstrating computer vision and interactive game development concepts.

---

## Author

Developed by Pranshu Rawat