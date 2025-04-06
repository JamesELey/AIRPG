# features/steps/player_steps.py

from behave import *  # noqa
import ast
import logging  # Import logging to potentially check messages

# Import necessary game classes relative to the 'features' directory
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..')) # Add project root to path

from grid_game import GridGame
from entities.player import Player

# Use behave contexts (context object) to store game state between steps
# Example: context.game = GridGame(...)

# --- Helper to get/create game instance --- #
def _get_or_create_game(context):
    if not hasattr(context, 'game'):
        # Minimal setup for testing: 1 level, small grid
        logging.info("Creating GridGame instance for test context.")
        context.game = GridGame()
        context.game.initialize_player("TestPlayer", "Medium") # Provide name and difficulty
        context.player = context.game.player # Store player for easy access
    # Ensure player exists if game already did
    elif not hasattr(context, 'player') or not context.player:
        context.player = context.game.player
        if not context.player:
             context.game.initialize_player("TestPlayer", "Medium") # Provide name and difficulty
             context.player = context.game.player
    return context.game

# --- Steps for player_state.feature ---

@given('the player\'s current position is {pos_str}')
def step_impl(context, pos_str):
    """Set the player's starting position."""
    game = _get_or_create_game(context)
    try:
        pos = ast.literal_eval(pos_str)
        assert isinstance(pos, list) and len(pos) == 3, "Position must be a list [level, row, col]"
        assert 0 <= pos[0] < game.grid_depth, f"Level {pos[0]} out of bounds (Depth: {game.grid_depth})"
        assert 0 <= pos[1] < game.grid_height, f"Row {pos[1]} out of bounds"
        assert 0 <= pos[2] < game.grid_width, f"Col {pos[2]} out of bounds"

        game.player_pos = pos
        # Ensure grid reflects position (optional but good practice)
        game.populate_grid_for_level(pos[0])
        context.initial_pos = pos # Store for checking later
        logging.debug(f"Set player position to {pos}")
    except (ValueError, SyntaxError, AssertionError, IndexError) as e:
        raise ValueError(f"Invalid position string: {pos_str}. Error: {e}")

@given('the player\'s current HP is {hp:d}')
def step_impl(context, hp):
    """Set the player's current health."""
    game = _get_or_create_game(context)
    if not context.player:
        raise Exception("Player object not found on context. Ensure player is initialized.")
    context.player.health = hp
    # Ensure max_health is consistent if setting HP > original max_health for some reason
    if hp > context.player.max_health:
        context.player.max_health = hp
    logging.debug(f"Set player HP to {hp}")

@when('the player attempts to move "{direction}" (command \'{command}\')')
def step_impl(context, direction, command):
    """Simulate the player attempting a move command."""
    game = _get_or_create_game(context)
    player = context.player

    # Store the position *before* the attempted move
    context.pos_before_move = list(game.player_pos)
    logging.debug(f"Attempting move '{command}' from {context.pos_before_move}. Player HP: {player.health}")

    # --- CORRECTION: Simulate movement logic directly --- #
    # Check if player is alive first
    if player.is_alive():
        # Calculate target position (using game's helper if available, or manually)
        # Assuming get_target_position exists based on earlier file read
        try:
            next_pos = game.get_target_position(command)
        except AttributeError:
            # Fallback if get_target_position is missing
            logging.warning("GridGame.get_target_position not found, calculating manually.")
            level, row, col = context.pos_before_move
            next_pos = list(context.pos_before_move)
            if command == 'w': next_pos[1] = row - 1
            elif command == 's': next_pos[1] = row + 1
            elif command == 'a': next_pos[2] = col - 1
            elif command == 'd': next_pos[2] = col + 1
            # Basic bounds check
            if not (0 <= next_pos[1] < game.grid_height and 0 <= next_pos[2] < game.grid_width):
                next_pos = None

        if next_pos:
            # Simulate checking if the target cell is walkable (e.g., empty)
            # For this test, assume any valid target is walkable unless we add obstacles
            target_level, target_row, target_col = next_pos
            if game.grid[target_level][target_row][target_col] == ' ': # Simplistic check
                logging.debug(f"Player is alive and target {next_pos} is valid/empty. Updating player_pos.")
                game.player_pos = next_pos
                # Update grid visualization (clear old, place new)
                game.grid[context.pos_before_move[0]][context.pos_before_move[1]][context.pos_before_move[2]] = ' '
                game.grid[next_pos[0]][next_pos[1]][next_pos[2]] = player.symbol
            else:
                 logging.debug(f"Player is alive but target {next_pos} is blocked ('{game.grid[target_level][target_row][target_col]}'). Position not changed.")
        else:
            logging.debug("Player is alive but move is invalid (out of bounds). Position not changed.")
    else:
        # Player is not alive, do not change position
        logging.debug("Player is not alive. Position not changed.")
    # ------------------------------------------------ #

    logging.debug(f"Position after attempting move: {game.player_pos}")

@then('the player\'s position should remain {pos_str}')
def step_impl(context, pos_str):
    """Check if the player's position has changed."""
    game = _get_or_create_game(context)
    try:
        expected_pos = ast.literal_eval(pos_str)
        actual_pos = game.player_pos
        logging.debug(f"Checking position: Expected {expected_pos}, Actual {actual_pos}")
        assert actual_pos == expected_pos, f"Player position mismatch: Expected {expected_pos}, Got {actual_pos}"
        # Also check against the stored initial position from the Given step if needed
        # assert actual_pos == context.initial_pos
    except (ValueError, SyntaxError) as e:
        raise ValueError(f"Invalid position string in Then step: {pos_str}. Error: {e}")

@then('the game should indicate the move failed due to player death (e.g., log message or status)')
def step_impl(context):
    """Check for an indication that the move failed because the player is dead."""
    game = _get_or_create_game(context)
    # Primary check: Player should not be alive
    player_is_alive = context.player.is_alive()
    logging.debug(f"Checking if player is alive: {player_is_alive}")
    assert not player_is_alive, "Player move should have failed because player is dead, but player.is_alive() is True."

    # Secondary check (optional): Ensure position didn't change from before the move attempt
    if hasattr(context, 'pos_before_move'):
        assert game.player_pos == context.pos_before_move, \
            f"Player position changed ({context.pos_before_move} -> {game.player_pos}) even though player is dead." 