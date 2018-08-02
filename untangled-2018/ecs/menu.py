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
        self.options_shift = 55
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
                elif event.key == pygame.locals.K_RETURN or event.key == pygame.locals.K_SPACE:
                    option_values = list(self.options.values())
                    self.menu_state.current_state = option_values[self.selected_option] or MenuStates.MAIN_MENU

    def render(self) -> None:
        self.render_options(self.font, (
                self.menu_state.framework.dimensions[0]/2 - self.options_shift,
                self.menu_state.framework.dimensions[1]/2 - self.options_shift
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

            self.render_text(font, text, (index + offset[0], index * self.options_shift + offset[1]))


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

    def update(self) -> None:
        super().update()

    def render(self) -> None:
        super().render()

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
