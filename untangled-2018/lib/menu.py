import pygame, pygame.locals
import time
from string import printable

from enum import Enum

from lib.config import HOSTNAME


class MenuStates(Enum):
    """Where we can be in the menu system."""
    PLAY = 0,
    MAIN_MENU = 1,
    CHAR_SETUP = 2,
    GAME_LOBBY = 3,
    HELP = 4,
    QUIT = 5


class MenuState:
    def __init__(self, framework):
        self.framework = framework
        self.screen = framework.screen
        self.net = framework.net
        self.current_state = MenuStates.MAIN_MENU
        self.font_path = 'assets/fonts/alterebro-pixel-font.ttf'

        self.fonts = {
            'small': pygame.font.Font(self.font_path, 45),
            'normal': pygame.font.Font(self.font_path, 55),
            'large': pygame.font.Font(self.font_path, 75),
            'heading': pygame.font.Font(self.font_path, 95),
        }

        self.structure = {
            MenuStates.MAIN_MENU: MenuItem(self, {
                "Play": MenuStates.CHAR_SETUP,
                "Help": MenuStates.HELP,
                "Quit": MenuStates.QUIT
            }),
            MenuStates.CHAR_SETUP: CharSetupMenuItem(self, {
                "Name": None,
                "Gender": None,
                "Colour": None,
                "Find Game": MenuStates.GAME_LOBBY,
                "Back": MenuStates.MAIN_MENU,
            }),
            MenuStates.GAME_LOBBY: LobbyMenuItem(self, {
                "Host": None,
                "Back": MenuStates.CHAR_SETUP,
            }),
            MenuStates.HELP: HelpMenuItem(self, {
                "Back": MenuStates.MAIN_MENU
            }),
            MenuStates.PLAY: None,
            MenuStates.QUIT: None,
        }

    def get_current(self):
        return self.structure[self.current_state]

    def get_screen_data(self, state: MenuStates):
        return self.structure[state]

    def update(self, dt: float, events: list):

        if self.current_state == MenuStates.PLAY:
            char_data = self.get_screen_data(MenuStates.CHAR_SETUP)
            self.framework.enter_game(char_data.char_name, char_data.gender_options[char_data.gender_choice],char_data.hexToRGB(char_data.hex))
            return
        elif self.current_state == MenuStates.QUIT:
            pygame.event.post(pygame.event.Event(pygame.QUIT, {}))

        if self.get_current():
            self.get_current().render()
            self.get_current().update(dt, events)

class MenuItem:
    def __init__(self, menu_state: MenuState, options={}):
        self.menu_state = menu_state
        self.screen = menu_state.screen

        self.options = options
        self.options_shift = (55, 55)
        self.selected_option = 0

        self.font = self.menu_state.fonts['large']
        self.info_font = self.menu_state.fonts['small']
        self.header_font = self.menu_state.fonts['heading']

    def update(self, dt, events) -> None:
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.locals.K_UP:
                    self.selected_option -= 1
                    self.selected_option %= len(self.options)
                elif event.key == pygame.locals.K_DOWN:
                    self.selected_option += 1
                    self.selected_option %= len(self.options)
                elif event.key == pygame.locals.K_RETURN:
                    option_values = list(self.options.values())
                    self.menu_state.current_state = option_values[self.selected_option] or MenuStates.MAIN_MENU

    def get_screen_centre(self):
        return pygame.Vector2(
            self.menu_state.framework.dimensions[0] / 2,
            self.menu_state.framework.dimensions[1] / 2
        )

    def render(self) -> None:
        self.render_options(self.font, (
            self.get_screen_centre()[0] - self.options_shift[0],
            self.get_screen_centre()[1] - self.options_shift[1]
        ))

    def render_text(self, font, text, pos=(0, 0), colour=(255, 255, 255)):
        rendered_text_surface = font.render(text, False, colour)
        self.screen.blit(rendered_text_surface, pos)

    def render_options(self, font, offset=(0, 0)):
        for index, value in enumerate(self.options.keys()):
            text = value
            if index == self.selected_option:
                text = ">{0}".format(text)

            self.render_text(font, text, (index + offset[0], index * 55 + offset[1]))


class CharSetupMenuItem(MenuItem):
    def __init__(self, menu_state, options={}):
        super().__init__(menu_state, options)
        self.options_shift = (100, -200)
        self.char_name = ""
        self.ticker = 0
        self.char_name_max = 15
        self.gender_options = ("Boy", "Girl")
        self.gender_choice = 0
        self.hex = "00FF19"

    def update(self, dt, events) -> None:
        """Update values for the character setup menu page"""
        option_values = list(self.options.values())
        option_keys = list(self.options.keys())
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.locals.K_UP:
                    self.selected_option -= 1
                    self.selected_option %= len(self.options)
                elif event.key == pygame.locals.K_DOWN:
                    self.selected_option += 1
                    self.selected_option %= len(self.options)
                elif event.key == pygame.locals.K_RETURN:
                    if option_values[self.selected_option] is not None:
                        self.menu_state.current_state = option_values[self.selected_option] or MenuStates.MAIN_MENU
                elif option_keys[self.selected_option] == "Name":
                    if event.key == pygame.locals.K_BACKSPACE:
                        self.char_name = self.char_name[:-1]
                    elif event.key < 123 and event.key != 13 and len(self.char_name) < self.char_name_max:
                        char_new = chr(event.key)
                        if char_new in printable:
                            if pygame.key.get_mods() & pygame.KMOD_LSHIFT:
                                self.char_name += char_new.upper()
                            else:
                                self.char_name += char_new
                elif option_keys[self.selected_option] == "Gender":
                    if event.key == pygame.locals.K_RIGHT:
                        self.gender_choice += 1
                    elif event.key == pygame.locals.K_LEFT:
                        self.gender_choice -= 1
                elif option_keys[self.selected_option] == "Colour":
                    if event.key == pygame.locals.K_BACKSPACE:
                        self.hex = self.hex[:-1]
                    elif event.key < 123 and event.key != 13 and len(self.hex) < 6:
                        char_new = chr(event.key)
                        if char_new in "0123456789abcdefABCDEF-":
                            self.hex += char_new.lower()
            self.gender_choice %= len(self.gender_options)

        self.ticker += 2
        self.ticker %= 100

    def render(self) -> None:
        font = self.font
        offset = self.get_screen_centre() + (-150, 100)

        name_string = '>Name: ' if self.selected_option == 0 else 'Name: '
        self.render_text(self.font, name_string, self.get_screen_centre() - (150, 50))
        if self.ticker > 50 and self.selected_option == 0:
            self.render_text(self.font, self.char_name + "_", self.get_screen_centre() - (10, 50))
        else:
            self.render_text(self.font, self.char_name, self.get_screen_centre() - (10, 50))

        gender_string = '>' if self.selected_option == 1 else ''
        self.render_text(self.font, 'Are you a:', self.get_screen_centre() - (150, 10))
        self.render_text(self.font, gender_string, self.get_screen_centre() - (150, -40))
        self.render_text(self.font, self.gender_options[self.gender_choice], self.get_screen_centre() - (130, -40))

        hex_string = ('>' if self.selected_option == 2 else '') + 'Colour: (Hexadecimal)'
        hex_colour = [255,255,255]
        temp_hex_colour = self.hexToRGB(self.hex)
        if temp_hex_colour is not None:
            for i, v in enumerate(temp_hex_colour):
                if v not in range(0,256):
                    hex_colour[i] = 0
                else:
                    hex_colour[i] = v
        self.render_text(self.font, hex_string, self.get_screen_centre() - (150, -90))
        self.render_text(self.font, '#' + self.hex, self.get_screen_centre() - (150, -130), hex_colour)

        for index, value in enumerate(self.options.keys()):
            if self.options[value] is None:
                continue

            text = value
            if index == self.selected_option:
                text = ">{0}".format(text)

            self.render_text(font, text, (index + offset[0], index * 55 + offset[1]))

    def hexToRGB(self,hexa):
        if len(hexa) == 6:
            if hexa[1] != "-" and hexa[3] != "-" and hexa[5] != "-":
                return tuple(int(hexa[i:i+2], 16) for i in (0, 2 ,4))
        return None


class LobbyMenuItem(MenuItem):
    def __init__(self, menu_state, options={}):
        super().__init__(menu_state, options)
        self.last_checked = 0
        self.hosts = []

    def update(self, dt, events) -> None:
        if time.time() - self.last_checked > 1:
            self.hosts = self.menu_state.net.get_all_groups()
            self.menu_state.net.close()
            self.menu_state.net.open()
            self.last_checked = time.time()

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.locals.K_UP:
                    self.selected_option -= 1
                elif event.key == pygame.locals.K_DOWN:
                    self.selected_option += 1
                elif event.key == pygame.locals.K_RETURN:
                    if self.selected_option < len(self.hosts):
                        self.menu_state.net.join_group(self.hosts[self.selected_option])
                        self.menu_state.current_state = MenuStates.PLAY
                    elif self.selected_option == (len(self.hosts)):
                        if HOSTNAME not in self.menu_state.net.get_all_groups():
                            self.menu_state.net.host_group(HOSTNAME)
                            self.menu_state.current_state = MenuStates.PLAY
                    else:
                        option_values = list(self.options.values())
                        self.menu_state.current_state = option_values[self.selected_option - len(
                            self.hosts)] or MenuStates.MAIN_MENU

        self.selected_option %= len(self.options) + len(self.hosts)

    def render(self) -> None:
        font = self.font
        offset = self.get_screen_centre() - self.options_shift

        for index, host in enumerate(self.hosts):
            text = host
            if index == self.selected_option:
                text = ">{0}".format(host)

            self.render_text(font, text, (index + offset[0], index * 55 + offset[1]))

        for index, value in enumerate(self.options.keys()):
            text = value
            if index + len(self.hosts) == self.selected_option:
                text = ">{0}".format(text)

            self.render_text(font, text, (index + offset[0], (index + len(self.hosts)) * 55 + offset[1]))


class HelpMenuItem(MenuItem):
    def __init__(self, menu_state, options={}):
        super().__init__(menu_state, options)

    def update(self, dt, events) -> None:
        super().update(dt, events)

    def render(self) -> None:
        super().render()
