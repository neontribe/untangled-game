import pygame
import time

from enum import Enum

import client

class Screen():
    def __init__(self, pygame_screen):
        self.pygame_screen = pygame_screen
        self.font_path = client.font
        self.fonts = {
            'small': pygame.font.Font(client.font, 45),
            'normal': pygame.font.Font(client.font, 55),
            'large': pygame.font.Font(client.font, 75),
            'heading': pygame.font.Font(client.font, 95),
        }


    def render(self):
        return

    def update(self, event):
        return

class MenuState(Enum):
    CHOICE = 0
    CHAR_SETUP = 1
    RESUME = 2

class MainMenu(Screen):
    def __init__(self, pygame_screen, player_manager):
        super().__init__(pygame_screen)

        self.selected = 0
        self.state = MenuState.CHOICE
        self.player_manager = player_manager
        self.ticker = 0.0
        self.char_name = player_manager.me.name
        self.info_message = ''

        self.main_options = {
            'Play': {
                'pos': 0,
            },
            'Load': {
                'pos': 1,
            },
            'Help': {
                'pos': 2,
            },
            'Mute': {
                'pos': 3,
            },
            'Quit': {
                'pos': 4,
            }
        }
        self.resume_options = {
            'Continue': {
                'pos': 0,
            },
            'Save': {
                'pos': 1,
            },
            'Mute': {
                'pos': 2,
            },
            'Quit': {
                'pos': 3,
            }
        }

        self.options_length = len(self.main_options)

    def render_text(self, font, text, pos = (0, 0), colour = (0, 0, 0)):
        rendered_text_surface = font.render(text, False, colour)
        self.pygame_screen.blit(rendered_text_surface, pos)

    def render(self, offset = (0, 0)):
        font = self.fonts['large']
        info_font = self.fonts['small']
        header_font = self.fonts['heading']
        logo = pygame.image.load('assets/images/logo.jpg')
        logo = pygame.transform.scale(logo, (700, 200))

        self.ticker += 2
        self.ticker %= 100
        
        self.pygame_screen.blit(logo,(offset[0] - 320, 220))
        self.render_text(info_font, self.info_message, (offset[0] - 50, 375), (255, 100,100))

        if(self.state == MenuState.CHOICE):
            self.options_length = len(self.main_options)
            self.render_options(self.main_options, font, offset)

        elif(self.state == MenuState.CHAR_SETUP):
            self.render_text(font, 'Name: ', (offset[0] - 125, offset[1]))
            if(self.ticker > 50):
                self.render_text(font, self.char_name + '_', (offset[0], offset[1]))
            else:
                self.render_text(font, self.char_name, (offset[0], offset[1]))

        elif(self.state == MenuState.RESUME):
            self.options_length = len(self.resume_options)
            self.render_options(self.resume_options, font, offset)

    def render_options(self, options, font, offset):
        for key, value in options.items():
                if(value['pos'] == self.selected):
                    key = ">{0}".format(key)

                self.render_text(font, key, (value['pos'] + offset[0], value['pos'] * 55 + offset[1]))

    def set_state(self, state):
        self.selected = 0
        self.state = state

    def setup_player(self):
        self.player_manager.me.set_name(self.char_name, True)

    def update(self, event):
        # Update menu state based off of key press or joystick
        from client import GameState
            
        if event.type == pygame.locals.JOYAXISMOTION:
            # up/down
            if event.axis == 1:
                if int(event.value) < 0:
                    self.selected -= 1
                    self.selected %= self.options_length
                if int(event.value) > 0:
                    self.selected += 1
                    self.selected %= self.options_length
        elif event.type == pygame.locals.KEYDOWN:
            if event.key == pygame.locals.K_UP:
                self.selected -= 1
                self.selected %= self.options_length
            elif event.key == pygame.locals.K_DOWN:
                self.selected += 1
                self.selected %= self.options_length
 
        if(self.state == MenuState.CHOICE):
            if event.type == pygame.locals.KEYDOWN:
                if event.key == pygame.locals.K_SPACE:
                    self.info_message = ''

                    if(self.selected == 0):
                        #PLAY GAME
                        self.set_state(MenuState.CHAR_SETUP)
                        return GameState.MENU
                    elif(self.selected == 1):
                        #LOAD SAVE
                        load_state = self.player_manager.me.load_from_config()
                        if load_state:
                            self.set_state(MenuState.RESUME)
                            return GameState.PLAY
                        else:
                            self.info_message = 'No Saved Player :-('
                            return GameState.MENU
                    elif(self.selected == 2):
                        #HELP
                        return GameState.HELP
                    elif(self.selected == 3):
                        #MUTE
                        return GameState.MUTE
                    elif(self.selected == 4):
                        #QUIT
                        return GameState.QUIT
            if event.type == pygame.locals.JOYAXISMOTION:
                if event.axis == 0:
                    self.info_message = ''

                    if(self.selected == 0):
                        #PLAY GAME
                        self.set_state(MenuState.CHAR_SETUP)
                        return GameState.MENU
                    elif(self.selected == 1):
                        #LOAD SAVE
                        load_state = self.player_manager.me.load_from_config()
                        if load_state:
                            self.set_state(MenuState.RESUME)
                            return GameState.PLAY
                        else:
                            self.info_message = 'No Saved Player :-('
                            return GameState.MENU
                    elif(self.selected == 2):
                        #HELP
                        return GameState.HELP
                    elif(self.selected == 3):
                        #MUTE
                        return GameState.MUTE
                    elif(self.selected == 4):
                        #QUIT
                        return GameState.QUIT
                
        elif(self.state == MenuState.RESUME):
            if event.type == pygame.locals.KEYDOWN:
                if event.key == pygame.locals.K_SPACE:
                    self.info_message = ''

                    if(self.selected == 0):
                        #CONTINUE GAME
                        return GameState.PLAY
                    elif(self.selected == 1):
                        #SAVE CHAR
                        load_state = self.player_manager.me.save_to_config()
                        self.info_message = 'Successfully Saved! :-)'
                        return GameState.MENU
                    elif(self.selected == 2):
                        #QUIT
                        return GameState.MUTE
                    elif(self.selected == 3):
                        #QUIT
                        return GameState.QUIT
            if event.type == pygame.locals.JOYAXISMOTION:
                if event.axis == 0:
                    self.info_message = ''

                    if(self.selected == 0):
                        #CONTINUE GAME
                        return GameState.PLAY
                    elif(self.selected == 1):
                        #SAVE CHAR
                        load_state = self.player_manager.me.save_to_config()
                        self.info_message = 'Successfully Saved! :-)'
                        return GameState.MENU
                    elif(self.selected == 2):
                        #QUIT
                        return GameState.MUTE
                    elif(self.selected == 3):
                        #QUIT
                        return GameState.QUIT
        elif(self.state == MenuState.CHAR_SETUP):
            # Limit name to 15 characters.
            if(event.type == pygame.locals.KEYDOWN):
                if(event.key == pygame.locals.K_BACKSPACE):
                    self.char_name = self.char_name[:-1]
                elif event.key == pygame.locals.K_ESCAPE:
                    if self.state == MenuState.CHAR_SETUP:
                        self.set_state(MenuState.CHOICE)
                elif(event.key < 123 and event.key != 13 and len(self.char_name)<10):
                    self.char_name += chr(event.key)
            if event.key == pygame.locals.K_RETURN:
                if self.state == MenuState.CHAR_SETUP:
                    self.setup_player()
                    self.set_state(MenuState.RESUME)
                    self.selected = 0
                    return GameState.PLAY
            if(event.type == pygame.locals.JOYAXISMOTION):
                if event.axis == 1:
                    self.setup_player()
                    self.set_state(MenuState.RESUME)
                    self.selected = 0
                    return GameState.PLAY
        return
