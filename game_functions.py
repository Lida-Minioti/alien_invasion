import sys
from time import sleep

import pygame
from bullet import Bullet
from alien import Alien


def check_keydown_events(event, ship, ai_settings, screen, bullets):
    if event.key == pygame.K_RIGHT:
        ship.moving_right = True
    elif event.key == pygame.K_LEFT:
        ship.moving_left = True
    elif event.key == pygame.K_SPACE:
        # Create a new bullet and add it to the bullets group
        fire_bullet(ai_settings, screen, ship, bullets)
    elif event.key == pygame.K_q:
        sys.exit()


def fire_bullet(ai_settings, screen, ship, bullets):
    if len(bullets) < ai_settings.bullets_allowed:
        new_bullet = Bullet(ai_settings, screen, ship)
        bullets.add(new_bullet)


def check_keyup_events(event, ship):
    if event.key == pygame.K_RIGHT:
        ship.moving_right = False
    elif event.key == pygame.K_LEFT:
        ship.moving_left = False


def check_events(ship, aliens, ai_settings, screen, sb,  bullets, stats, play_button):
    """Respond to keyboard and mouse events."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            check_keydown_events(event, ship, ai_settings, screen, bullets)
        elif event.type == pygame.KEYUP:
            check_keyup_events(event, ship)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            check_play_buttons(stats, ai_settings, screen, sb, ship, bullets, aliens, play_button, mouse_x, mouse_y)


def check_play_buttons(stats, ai_settings, screen, sb, ship, bullets, aliens, play_button, mouse_x, mouse_y):
    """Start a new game when the player hits play."""
    if play_button.rect.collidepoint(mouse_x, mouse_y) and not stats.game_active:
        # Reset the game's dynamic settings
        ai_settings.initialise_dynamic_settings()
        # Hide the mouse cursor
        pygame.mouse.set_visible(False)

        #Reset the game statistics
        stats.reset_stats()

        stats.game_active = True

        # The below line is so that the scoreboard writes 0 every time the user hits the play button
        sb.prep_score()
        sb.prep_high_score()
        sb.prep_level()
        sb.prep_ships()
        #print(stats.score)

        # Empty the list of aliens and bullets
        bullets.empty()
        aliens.empty()

        # Create new fleet and center the ship
        create_fleet(ai_settings, screen, ship, aliens)
        ship.center_ship()


def update_screen(ai_settings, screen, stats, sb, ship, aliens, bullets, play_button):
    """Update the images on the screen and flip to the new screen"""
    screen.fill(ai_settings.bg_colour)
    # Redraw all bullets behind ship
    for bullet in bullets.sprites():
        bullet.draw_bullet()

    ship.blitme()
    aliens.draw(screen)

    # Draw the score information
    sb.show_score()

    if not stats.game_active:
        play_button.draw_button()

    # Make the most recently drawn screen visible.
    pygame.display.flip()


def update_bullets(aliens, bullets, ai_settings, screen, stats, sb, ship):
    """Update the position of the bullets and get rid of the old ones.
    Also calls a function that creates new fleet and empties the bullets if the alien fleet is empty"""
    # Update bullet position
    bullets.update()

    # Get rid of bullets that have disappeared from the screen
    for bullet in bullets.copy():
        if bullet.rect.bottom <= 0:
            bullets.remove(bullet)
    check_bullet_alien_collision(ai_settings, screen, stats, sb, ship, aliens, bullets)


def check_bullet_alien_collision(ai_settings, screen, stats, sb,  ship, aliens, bullets):
    """Respond to bullet-alien collision"""
    # Remove any bullet and alien that have collided
    collisions = pygame.sprite.groupcollide(aliens, bullets, True, False)
    if collisions:
        for aliens in collisions.values():
            stats.score += ai_settings.alien_points*len(aliens)
        sb.prep_score()
        check_high_score(stats, sb)

    if len(aliens) == 0:
        # Start a new level: Destroy existing bullets, create new fleet and speed up game
        bullets.empty()
        ai_settings.increase_speed()

        # Increase level
        stats.level += 1
        sb.prep_level()


        create_fleet(ai_settings, screen, ship, aliens)


def get_number_aliens_x(ai_settings, alien_width):
    """Determine the number of aliens that fit in a row"""
    available_space_x = ai_settings.screen_width - 2 * alien_width
    number_aliens_x = int(available_space_x / (2 * alien_width))
    return number_aliens_x


def get_number_rows(ai_settings, alien_height, ship_height):
    available_space_y = (ai_settings.screen_height -
                         (3 * alien_height) - ship_height)
    number_rows = int(available_space_y / (2 * alien_height))
    return number_rows


def create_alien(ai_settings, screen, aliens, alien_number, row_number):
    """Create one alien and place it in a row"""
    alien = Alien(ai_settings, screen)
    alien_width = alien.rect.width
    alien.x = alien_width + 2 * alien_width * alien_number
    alien.rect.x = alien.x
    alien.rect.y = alien.rect.height + 2 * alien.rect.height * row_number
    aliens.add(alien)


def create_fleet(ai_settings, screen, ship, aliens):
    """Create a full fleet of aliens"""
    # Create an alien and use it to define the number of aliens in a row
    # Spacing between 2 aliens is equal to the width of an alien
    alien = Alien(ai_settings, screen)
    number_aliens_x = get_number_aliens_x(ai_settings, alien.rect.width)
    number_rows = get_number_rows(ai_settings, alien.rect.height, ship.rect.height)

    # Create the first row of aliens
    for row_number in range(number_rows):
        for alien_number in range(number_aliens_x):
            create_alien(ai_settings, screen, aliens, alien_number, row_number)


def check_fleet_edges(ai_settings, aliens):
    """ Check if any alien has reached the end and if so, call the function that moves the fleet
    and changes direction"""
    for alien in aliens.sprites():
        if alien.check_edges():
            change_fleet_direction(ai_settings, aliens)
            break


def change_fleet_direction(ai_settings, aliens):
    """Drop the entire fleet and change fleet direction"""
    for alien in aliens.sprites():
        alien.rect.y += ai_settings.fleet_drop_speed
    ai_settings.fleet_direction *= -1


def ship_hit(ai_settings, stats, sb, screen, ship, aliens, bullets):
    """Respond to ship being hit by alien"""
    if stats.ships_left > 0:
        # Decrement ships left
        stats.ships_left -= 1

        # Update the scoreboard
        sb.prep_ships()

        # Empty the list of aliens and bullets
        aliens.empty()
        bullets.empty()

        # Create a new fleet and center the ship
        create_fleet(ai_settings, screen, ship, aliens)
        ship.center_ship()

        # Pause
        sleep(0.5)
    else:
        stats.game_active = False
        pygame.mouse.set_visible(True)


def update_aliens(ai_settings, stats, sb,  screen, ship, aliens, bullets):
    """Check if the fleet has reached one of the 2 edges and update the position of ALL aliens in the
    fleet by x and if needed by y"""
    check_fleet_edges(ai_settings, aliens)
    aliens.update()

    # Look for alien - ship collision
    if pygame.sprite.spritecollideany(ship, aliens):
        # print("ship hit!!!")
        ship_hit(ai_settings, stats, sb, screen, ship, aliens, bullets)

    # Look for alien reaching the bottom of the screen
    check_aliens_bottom(ai_settings, stats, sb, screen, ship, aliens, bullets)


def check_aliens_bottom(ai_settings, stats, sb, screen, ship, aliens, bullets):
    """Check if any aliens have reached the bottom of the screen"""
    screen_rect = screen.get_rect()
    for alien in aliens.sprites():
        if alien.rect.bottom >= screen_rect.bottom:
            # Treat this the same as if the ship is hit
            ship_hit(ai_settings, stats, sb, screen, ship, aliens, bullets)
            break

def check_high_score(stats, sb):
    """Check if there is a new high score"""
    if stats.score > stats.high_score:
        stats.high_score = stats.score
        sb.prep_high_score()