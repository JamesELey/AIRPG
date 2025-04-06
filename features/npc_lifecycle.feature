# features/npc_lifecycle.feature

Feature: NPC Lifecycle - Death and Respawn

  Scenario: NPC dies and is removed from the grid when HP drops below 1
    Given an NPC "Test Dummy" exists on level 0 at position [0, 5, 5] with 10 HP
    And the player is adjacent to the NPC
    When the player attacks the NPC dealing 15 damage
    Then the NPC "Test Dummy" should have 0 or less HP
    And the grid cell at [0, 5, 5] should not contain the NPC "Test Dummy" symbol 'E'

  Scenario: NPC respawns correctly after death
    Given an NPC "Respawn Candidate" exists on level 0 at position [0, 6, 6]
    And the NPC "Respawn Candidate" has max_hp 100, attack 10, defense 10, agility 10
    When the player defeats the NPC "Respawn Candidate"
    Then a respawned NPC instance derived from "Respawn Candidate" should exist
    And the respawned NPC should have max_hp 110
    And the respawned NPC should have current HP equal to its max_hp
    And the respawned NPC should have at least one stat (attack, defense, or agility) greater than 10
    And the respawned NPC should be located on level 0 at a position different from [0, 6, 6]
    And the respawned NPC should not be located at the player's current position 