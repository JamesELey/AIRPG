# Grid Game

A simple grid-based exploration and farming game built with Python and Tkinter.

## How to Run

### Prerequisites
*   Python 3.x installed on your system.

### Installation
This game uses Python's built-in Tkinter library for the GUI, so no external package installation is usually required.

### Running the Game
1.  Open a terminal or command prompt.
2.  Navigate to the project directory (`runnable_game`).
3.  Run the game using the command:
    ```bash
    python main.py
    ```

## How to Play

### Objective
Explore different levels, plant and harvest crops, manage your energy, and battle NPCs you encounter. The goal is currently open-ended - survive and thrive!

### Controls

**Movement:**
*   **W**: Move Up
*   **S**: Move Down
*   **A**: Move Left
*   **D**: Move Right
*   **1 / 2**: Move Down / Up Levels (when on a Portal `@`)

**Farming:**
*   **F**: Plant Crop (on empty tile) / Check Status (on existing crop)
*   **R**: Harvest Crop (when ready `🌾`)
*   **T**: Check Crop Status (detailed info)

**Game Actions:**
*   **E**: Open Inventory (*Currently non-functional*)
*   **H**: View Battle History (*Functionality TBD*)
*   **G**: View Game Statistics (*Functionality TBD*)
*   **V**: Toggle Survival Mode (*Functionality TBD*)
*   **Q**: Quit Game

**Combat:**
*   **Y**: Accept Battle (when prompted)
*   **N**: Decline Battle (when prompted)
*   **I**: Use Item in Battle (*Functionality TBD*)

**Portal Travel:**
*   **K + number**: Quick Travel to Level (e.g., `K5` for level 5) (*Functionality TBD*)


### Saving and Loading
The game automatically attempts to load the most recent save file (`savegame_*.json`) when you select "Continue Game". Saving happens periodically or possibly on quit (exact triggers TBD).

### Symbols
*   `><`: Player
*   `@`: Portal
*   `$`: Store
*   `🌱`: Seedling Crop
*   `🌿`: Growing Crop
*   `🌾`: Harvestable Crop
*   `K`: NPC (Knight)
*   `G`: NPC (Goblin)
*   (Space): Empty Ground 