# Grid Game - Game Guide

This guide provides details on various elements within the Grid Game.

## NPCs (Non-Player Characters)

NPCs are encountered randomly as you explore the grid. They will initiate combat if you move onto their tile.

### Generation
*   NPCs are randomly generated with stats (Health, Attack, Defense, Agility) appropriate for the current level.
*   Stats increase by approximately 15% per level compared to base values.
*   Names are randomly generated (e.g., "Level 3 Fierce Warrior", "Boss 5 Cunning Knight").
*   NPCs have a chance to be designated as a "Boss", which doubles their stats and rewards.
*   They carry a random amount of credits based on their level.
*   *(Future feature: NPCs may carry weapons or have specific item drops).* 

### Combat
*   When encountered, you can choose to fight (`Y`) or decline (`N`).
*   Combat is turn-based (details TBD).
*   Defeating an NPC grants experience points and credits.
    *   XP is calculated based on the NPC's stats and level.
    *   Credits scale with level (base 10 * level, doubled for bosses).

### Respawning
*   After being defeated, NPCs will respawn at a random empty location on the current level.
*   Respawned NPCs have full health and +1 to a random stat (attack, defense, or agility).

## Items

### Crops
Crops can be planted on empty tiles and harvested for credits.

*   **Planting:** Use the `F` key on an empty tile.
*   **Harvesting:** Use the `R` key on a mature crop (`🌾`).
*   **Checking Status:** Use `F` or `T` on a planted crop tile.

**Growth:**
*   Crops grow over time based on in-game hours.
*   Game time advances by 1 hour for each player move.
*   Growth Stages:
    *   `🌱`: Seedling (Just planted)
    *   `🌿`: Growing (>= 50% grown)
    *   `🌾`: Ready to Harvest (>= 100% grown)

**Available Crop Types:**

| Name   | Growth Time (Hours) | Value (Credits) | Description                                           |
| :----- | :------------------ | :-------------- | :---------------------------------------------------- |
| Tomato | 24                  | 50              | A juicy red tomato. Grows best in sunny weather.      |
| Wheat  | 48                  | 30              | Basic but reliable crop. Moderate weather resistance. |
| Corn   | 72                  | 75              | High-value crop that takes longer to grow.            |
| Potato | 36                  | 40              | Hardy crop that can grow in most weather conditions.  |
| Rice   | 60                  | 60              | Grows exceptionally well in rainy weather.            |

*(Note: Weather effects mentioned in descriptions are not yet implemented).*

### Other Items
*(Potions, Weapons, Equipment - To Be Added)* 