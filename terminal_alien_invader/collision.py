"""Checking every projectile against what it flew into."""
import time

from terminal_alien_invader.config import (
    ENEMY_BOSS_BARRIER_CHARACTERS,
    ENEMY_BOSS_CHARACTERS,
    ENEMY_CHARACTERS,
    ENEMY_EXPLOSIONS,
    ENEMY_KILL_SCORES,
    ENEMY_LESSER_BOSSES,
    EXPLOSION_DURATION,
    PLAYER_PROJECTILE,
    PLAYER_PROJECTILE_DAMAGE,
)
from terminal_alien_invader.effects import show_player_projectile_explosion_effect
from terminal_alien_invader.enemies.bosses import boss_hit_at
from terminal_alien_invader.player import destroy_player, hits_player
from terminal_alien_invader.state import state


def collision_detection():
    """Detect collisions between the projectiles and the ships they fly into.

    If a player projectile hits an enemy ship, the shot bursts in the cell in
    front of it and is spent taking its damage out of what that ship has left of its health. 
    
    A ship with health to spare survives the hit and keeps its cell. 
    One whose last is gone explodes, is removed from the world, and is scored. 
    The ranks are a single shot's worth of health apiece and so go down to the first that reaches them, 
    while a boss stands through a good many. 

    A projectile that flies into a boss's barrier instead explodes in front of it
    in the same way and is spent on it, and the barrier is left standing, so
    the boss behind it is not reached. 
    
    An enemy projectile that reaches the player's ship is spent taking a bite out of its health, 
    and the ship itself explodes once the last of that health is gone.

    Called after the projectiles have moved and before any of them is drawn, 
    so the cell a projectile now occupies still shows what it flew into. 
    Every projectile that hits nothing is drawn here, in the cell it just entered.
    """
    now = time.monotonic()
    updated_projectiles = []
    for projectile in state.player_projectiles:
        projectile_x, projectile_y = projectile
        enemy = state.world[projectile_x][projectile_y]

        # The ship the shot strikes, which is the one in the cell it flew into,
        # or, with nothing there to stop it, a boss whose hitbox reaches that cell from one to the side.
        target_x, target_y = projectile_x, projectile_y
        if (
            enemy not in ENEMY_EXPLOSIONS
            and enemy not in ENEMY_BOSS_BARRIER_CHARACTERS.values()
        ):
            boss = boss_hit_at(projectile_x, projectile_y)
            if boss is not None:
                target_x, target_y = boss
                enemy = state.world[target_x][target_y]

        if enemy in ENEMY_EXPLOSIONS:
            # Collision detected: the projectile is spent, and takes its damage
            # out of what the ship it flew into has left of its health. 
            # It bursts against the ship whether or not this is the hit that destroys it.
            show_player_projectile_explosion_effect(target_x, target_y, now)

            health = state.enemy_health.get((target_x, target_y), 0)
            remaining = health - PLAYER_PROJECTILE_DAMAGE
            if remaining > 0:
                # The ship has taken the hit and is still standing, so it keeps its cell and nothing is drawn over it.
                state.enemy_health[(target_x, target_y)] = remaining
                continue

            # The last of its health is gone, so the ship is destroyed and the
            # explosion that kind of ship leaves is put in its cell for a moment.
            explosion = ENEMY_EXPLOSIONS[enemy]
            state.world[target_x][target_y] = explosion
            state.explosions.append(
                [target_x, target_y, now + EXPLOSION_DURATION, explosion]
            )
            state.score += ENEMY_KILL_SCORES[enemy]

            # The ship is gone, and so are its countdown and its health, which
            # would otherwise be left in the cell for whichever ship marched into it next.
            state.enemy_next_attack.pop((target_x, target_y), None)
            state.enemy_health.pop((target_x, target_y), None)

            # One fewer ship holding the lesser bosses' barriers up, or, once
            # those are down and the bosses can be reached at all, one fewer
            # boss standing between the player and the end of the round. 
            # A lesser boss is counted off twice over. It is also one fewer of the
            # two holding the last boss's own barrier up.
            if enemy in ENEMY_BOSS_CHARACTERS:
                state.boss_count -= 1
                if enemy in ENEMY_LESSER_BOSSES:
                    state.lesser_boss_count -= 1
            else:
                state.non_boss_enemy_count -= 1
        elif enemy in ENEMY_BOSS_BARRIER_CHARACTERS.values():
            # The barrier takes the shot and keeps its cell, so nothing is drawn
            # over it and the spent projectile is dropped here. 
            # The shot bursts against it all the same, in the cell in front of it.
            show_player_projectile_explosion_effect(projectile_x, projectile_y, now)
            continue
        else:
            state.world[projectile_x][projectile_y] = PLAYER_PROJECTILE
            updated_projectiles.append(projectile)
    state.player_projectiles.clear()
    state.player_projectiles.extend(updated_projectiles)

    updated_projectiles = []
    for projectile in state.enemy_projectiles:
        projectile_x, projectile_y, projectile_character, damage = projectile
        if hits_player(projectile_x, projectile_y):
            # The shot is spent on the ship, whether it came down on the cell
            # the ship is drawn in or on one of the cells either side of it that
            # count as part of it. With health to spare the ship survives the
            # hit and keeps its cell, so nothing is drawn over it. 
            # With the last of it gone the ship explodes where it stands.
            state.player_health = max(0, state.player_health - damage)
            if state.player_health <= 0:
                destroy_player()
        elif state.world[projectile_x][projectile_y] in ENEMY_CHARACTERS:
            # A ship of the army has marched across a shot from its own side.
            # The ship keeps its cell and the shot is spent on it: drawn over
            # it instead, the projectile would rub it out of the world.
            continue
        else:
            state.world[projectile_x][projectile_y] = projectile_character
            updated_projectiles.append(projectile)
    state.enemy_projectiles.clear()
    state.enemy_projectiles.extend(updated_projectiles)
