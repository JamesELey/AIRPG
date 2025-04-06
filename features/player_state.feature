# features/player_state.feature

Feature: Player State Rules

  Scenario: Player cannot move when HP is 0 or less
    Given the player's current position is [0, 3, 3]
    And the player's current HP is 0
    When the player attempts to move "up" (command 'w')
    Then the player's position should remain [0, 3, 3]
    And the game should indicate the move failed due to player death (e.g., log message or status)

    # Optional: Repeat for other directions if necessary
    # When the player attempts to move "down" (command 's')
    # Then the player's position should remain [0, 3, 3]
    # ... etc for 'a' and 'd' 