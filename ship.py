import pygame
from pygame.sprite import Sprite

class Ship (Sprite):
    def __init__(self, ai_settings, screen):
        """Initialise the ship and its starting position"""
        super().__init__()
        self.screen = screen
        self.ai_settings = ai_settings

        # Load the ship image and get its rect.
        self.image = pygame.image.load("images/ship.bmp")
        self.rect = self.image.get_rect()
        self.screen_rect = self.screen.get_rect()

        # Start each new ship at the bottom centre of the screen
        self.rect.centerx = self.screen_rect.centerx
        self.rect.bottom = self.screen_rect.bottom

        # Store a decimal value for the ship's centre
        self.center = float(self.rect.centerx)

        # Movement flag
        self.moving_right = False
        self.moving_left = False

    def update(self):
        """Update the ship's position bsed on the movement flag"""
        if self.moving_right and self.rect.right < self.screen_rect.right:
            self.center += self.ai_settings.ship_speed_factor
        if self.moving_left and self.rect.left > 0:
            self.center -= self.ai_settings.ship_speed_factor
        # Update the rect object from self.center
        self.rect.centerx = self.center

    def center_ship(self):
        """Center the ship on the screen"""
        self.center = self.screen_rect.centerx

    def blitme(self):
        """Draw the ship at its current position"""
        self.screen.blit(self.image, self.rect)
