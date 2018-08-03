import pygame, pygame.locals

from enum import Enum

class MenuStates(Enum):
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
        # self.net = framework.net
        self.current_state = MenuStates.MAIN_MENU
        self.font_path = 'assets/fonts/alterebro-pixel-font.ttf'

        self.fonts = {
            'small': pygame.font.Font(self.font_path, 45),
            'normal': pygame.font.Font(self.font_path, 55),
            'large': pygame.font.Font(self.font_path, 75),
            'heading': pygame.font.Font(self.font_path, 95),
        }

        self.structure = {
            MenuStates.MAIN_MENU: HomepageMenuItem(self, {
                "Play": MenuStates.CHAR_SETUP,
                "Help": MenuStates.HELP,
                "Quit": MenuStates.QUIT
            }),
            MenuStates.CHAR_SETUP: CharSetupMenuItem(self, {
                "Find Game": MenuStates.GAME_LOBBY,
                "Back": MenuStates.MAIN_MENU,
            }),
            MenuStates.GAME_LOBBY: LobbyMenuItem(self, {
                "Play": MenuStates.PLAY,
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

    def render(self) -> None:
        if self.get_current():
            self.get_current().render()

    def update(self, dt: float) -> MenuStates:
        if self.get_current():
            self.get_current().update()
        return self.current_state


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

    def update(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.menu_state.framework.running = False
            elif event.type == pygame.KEYDOWN:
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
            )
        )

    def render_text(self, font, text, pos=(0, 0), colour=(255, 255, 255)):
        rendered_text_surface = font.render(text, False, colour)
        self.screen.blit(rendered_text_surface, pos)

    def render_options(self, font, offset=(0,0)):
        for index, value in enumerate(self.options.keys()):
            text = value
            if index == self.selected_option:
                text = ">{0}".format(text)

            self.render_text(font, text, (index + offset[0], index * 55 + offset[1]))


class HomepageMenuItem(MenuItem):
    def __init__(self, menu_state, options):
        super().__init__(menu_state, options)

    def update(self) -> None:
        super().update()

    def render(self) -> None:
        super().render()


class CharSetupMenuItem(MenuItem):
    def __init__(self, menu_state, options={}):
        super().__init__(menu_state, options)
        self.options_shift = (100, -200)
        self.char_name = ""
        self.ticker = 0
        self.char_name_max = 15
        self.gender_options = ("Boy", "Girl")
        self.gender_choice = 0

    def update(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.menu_state.framework.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.locals.K_UP:
                    self.selected_option -= 1
                    self.selected_option %= len(self.options) + 2
                elif event.key == pygame.locals.K_DOWN:
                    self.selected_option += 1
                    self.selected_option %= len(self.options) + 2
                elif event.key == pygame.locals.K_RETURN:
                    option_values = list(self.options.values())
                    self.menu_state.current_state = option_values[self.selected_option] or MenuStates.MAIN_MENU
                elif self.selected_option == 0: # name
                    if event.key == pygame.locals.K_BACKSPACE:
                        self.char_name = self.char_name[:-1]
                    elif event.key < 123 and event.key != 13 and len(self.char_name) < self.char_name_max:
                        if pygame.key.get_mods() & pygame.KMOD_LSHIFT:
                            self.char_name += chr(event.key).upper()
                        else:
                            self.char_name += chr(event.key)
                elif self.selected_option == 1: # gender
                    if event.key == pygame.locals.K_RIGHT:
                        self.gender_choice += 1
                    elif event.key == pygame.locals.K_LEFT:
                        self.gender_choice -= 1
            self.gender_choice %= 2

        self.ticker += 2
        self.ticker %= 100

    def render(self) -> None:
        font = self.font
        offset = self.get_screen_centre()

        name_string = '>Name: ' if self.selected_option == 0 else 'Name: '
        self.render_text(self.font, name_string, self.get_screen_centre() - (150, 0))
        if self.ticker > 50:
            self.render_text(self.font, self.char_name + "_", self.get_screen_centre() - (10, 0))
        else:
            self.render_text(self.font, self.char_name, self.get_screen_centre() - (10, 0))

        gender_string = '>' if self.selected_option == 1 else ''
        self.render_text(self.font, 'Are you a:', self.get_screen_centre() - (150, -50))
        self.render_text(self.font, gender_string, self.get_screen_centre() - (150, -90))
        self.render_text(self.font, self.gender_options[self.gender_choice], self.get_screen_centre() - (130, -100))

        for index, value in enumerate(self.options.keys()):
            text = value
            if index + 2 == self.selected_option:
                text = ">{0}".format(text)

            self.render_text(font, text, (index + offset[0], index * 55 + offset[1]))


class LobbyMenuItem(MenuItem):
    def __init__(self, menu_state, options={}):
        super().__init__(menu_state, options)

    def update(self) -> None:
        super().update()


    def render(self) -> None:
        super().render()

class HelpMenuItem(MenuItem):
    def __init__(self, menu_state, options={}):
        super().__init__(menu_state, options)

    def update(self) -> None:
        super().update()


    def render(self) -> None:
        super().render()
