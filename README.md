# Yeardle

**Yeardle** is a Wordle-inspired game developed in Python. This project demonstrates programming, database management, and game logic skills, along with a clear explanation of the design and implementation process.

## Video Demonstration

Watch a short video showing **how to play Yeardle**:

[![How to Play Yeardle](https://img.youtube.com/vi/iEXfgVlUQPI/0.jpg)](https://www.youtube.com/watch?v=iEXfgVlUQPI)

---

## Project Files

- **Yeardle.py** – Main Python script for the game.  
- **Yeardle.db** – SQLite database used to store game data and statistics.  
- **Yeardle Report.docx** – Detailed report explaining the project’s design, functionality, and technical approach.  

---

## Project Overview

Yeardle challenges players to guess a series of historical years associated with events within a limited number of attempts. The game provides visual feedback for correct and incorrect guesses, tracks progress through levels, and maintains a leaderboard of top scores. The game combines interactive GUI design with a dynamic scoring system to create an engaging experience.

---

## Design and Approach

**Yeardle** is designed using a modular, object-oriented approach to separate concerns and promote maintainable code. The architecture includes multiple classes to handle the user interface, game logic, scoring, and database operations.

### Key Features:

- **GUI with Tkinter:** Interactive and visually appealing interface with drag-and-drop functionality for guessing years.  
- **Database Integration:** SQLite stores user data and leaderboards for persistent tracking of high scores.  
- **Dynamic Question Generation:** Randomly selects events and generates decoy years to challenge the player.  
- **Progressive Difficulty:** Increasing levels, reduced time limits, and bonus challenges encourage skill development.  
- **Scoring System:** Points awarded for correct guesses and bonus interactions, with real-time leaderboard updates.  
- **Interactive Bonus Balls:** Animated elements provide extra points and add a dynamic visual component.  
- **Leaderboard:** Ranks users by score and level, promoting replayability.  

### Technical Highlights:

- **Object-Oriented Programming:** Classes encapsulate game elements and logic, supporting modularity and code readability.  
- **Event Handling:** Mouse interactions (click, drag, release) and timers manage gameplay mechanics.  
- **Database Operations:** SQL queries handle user verification, score updates, and leaderboard retrieval.  
- **Graphics and Animation:** Bonus balls and draggable year widgets demonstrate basic physics calculations and interactive GUI design.  

### Learning Outcomes:

- Built a complete, interactive Python application using Tkinter.  
- Integrated a database into a real-time game application.  
- Developed modular, maintainable, and user-friendly code.  
- Gained experience translating a concept into a functional and engaging project.  

---

## Installation and Running the Game

1. Clone the repository:  
   ```bash
   git clone https://github.com/KatieDowle/Yeardle.git
   cd Yeardle
