from pygame.surface import Surface
from MyMath import my_complex_to_str
from time import time


from Storage import *
import pygame
pygame.init()


# set window size
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 1000
pygame.display.set_caption("Quantum Circuit Builder")
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# load standard font (can take up to a few seconds)
FONT = pygame.font.SysFont('Arial', 40)


class CustomGateEditor:
    def __init__(self, rect: pygame.Rect):
        self.surf = pygame.Surface(rect.size)
        self.rect = rect
        self.name_input = TextInput(
            pygame.Rect(0, 0, 500, 50), hint="Gate name")
        self.letter_prompt = TextView((0, 100), "Letter:", FONT, DARK)
        self.letter_input = TextInput(pygame.Rect(250, 100, 50, 50), maxlen=1)
        self.matrix_editor = MatrixEditor((2, 2), (50, 200))
        self.draw()
    
    def update(self, pos):
        pos = adjust_pos(pos, self.rect)
        self.matrix_editor.update(pos)

    def draw(self):
        self.letter_input.draw()
        self.name_input.draw()
        self.matrix_editor.draw()
        self.surf.fill(WHITE)
        self.surf.blit(self.name_input.surf, self.name_input.rect)
        self.surf.blit(self.letter_input.surf, self.letter_input.rect)
        self.surf.blit(self.letter_prompt.surf, self.letter_prompt.pos)
        self.surf.blit(self.matrix_editor.surf, self.matrix_editor.rect)

    def mouse_down(self, pos):
        pos = adjust_pos(pos, self.rect)
        self.letter_input.mouse_down(pos)
        self.name_input.mouse_down(pos)

    def key_down(self, event):
        self.letter_input.key_down(event)
        self.name_input.key_down(event)


class Animation:
    def __init__(self, start, end, speed):
        self.start = start
        self.end = end
        self.speed = speed
        self.start_time = 0
        self.value = start
        self.running = False
        self.forward = True

    def run(self):
        self.value = self.get_value()
        self.start_time = time()
        self.running = True
        self.forward = True

    def reverse(self):
        self.value = self.get_value()
        self.start_time = time()
        self.running = True
        self.forward = False

    def get_value(self):
        if self.running and self.forward:
            value = self.value + self.speed * (time() - self.start_time)
            if value >= self.end:
                self.running = False
                self.value = self.end
        elif self.running and not self.forward:
            value = self.value - self.speed * (time() - self.start_time)
            if value <= self.start:
                self.running = False
                self.value = self.start
        else:
            return self.value
        return value


class TextView:
    def __init__(self, pos: tuple[int, int], text: str, font: pygame.font.Font,
                 color: tuple[int, int, int]):
        self.pos = pos
        self.text = text
        self.surf = font.render(self.text, True, color)


class TextInput:
    TEXT_COLOR = (0, 0, 0)
    HINT_COLOR = (200, 200, 200)

    def __init__(self, rect: pygame.Rect, text: str = "", hint: str = "", maxlen: int = 20):
        self.surf = pygame.Surface(rect.size)
        self.rect = rect
        self.text = text
        self.hint = hint
        self.active = False
        self.start_time = 0
        self._update_text_surf()
        self.animation = Animation(0, self.rect.w, 1500)
        self.maxlen = maxlen

    def _update_text_surf(self):
        if self.text:
            self.text_surf = FONT.render(self.text, True, DARK)
        else:
            if not self.active:
                self.text_surf = FONT.render(self.hint, True, GREY)
            else:
                self.text_surf = FONT.render("", True, GREY)

    def draw(self):
        self.surf.fill(WHITE)
        pygame.draw.rect(self.surf, GREY, (0, self.rect.h-4, self.rect.w, 4))
        pygame.draw.rect(self.surf, TEAL, (0, self.rect.h -
                         3, self.animation.get_value(), 3))
        self.surf.blit(self.text_surf, (0, 0))
        if self.active and (time() - self.start_time) % 1 < 0.5:
            w = self.text_surf.get_width()
            pygame.draw.rect(self.surf, TextInput.TEXT_COLOR,
                             (w, 0, 2, self.rect.h-8))

    def mouse_down(self, pos):
        if self.rect.collidepoint(pos):
            if not self.active:
                self.animation.run()
            self.active = True
        else:
            self.active = False
            if not self.active:
                self.animation.reverse()
        self._update_text_surf()
        self.draw()

    def key_down(self, event):
        if self.active:
            if event.key == pygame.K_BACKSPACE:
                if self.text:
                    self.text = self.text[:-1]
            elif len(self.text) < self.maxlen:
                self.text += event.unicode
            self._update_text_surf()
            self.draw()


class Button:
    def __init__(self, rect: pygame.Rect, text: str):
        self.rect = rect
        self.surf = pygame.Surface(rect.size)
        self.text = text

    def draw(self):
        self.surf.fill(ORANGE)
        self.text_surf = FONT.render(self.text, True, WHITE)

    def point_in(self, pos):
        return self.rect.collidepoint(pos)


class MatrixEditor:
    HGAP = 50
    VSPACE = 50
    SIDE = 30

    def __init__(self, size: tuple[int, int], pos=tuple[int, int]):
        self.width, self.height = size
        self.strings = [["0"] * self.width for _ in range(self.height)]
        self.values = [[0] * self.width for _ in range(self.height)]

        self.value_surfs = [[None] * self.width for _ in range(self.height)]

        for i, row in enumerate(self.values):
            for j, value in enumerate(row):
                self.value_surfs[i][j] = FONT.render(
                    my_complex_to_str(value), True, DARK)
        self._compute_width()

        visualw = sum(self.col_widths) + self.HGAP * \
            (self.width-1) + 2*self.SIDE
        visualh = self.VSPACE * self.height
        self.matrix_rect = pygame.Rect(50, 100, visualw, visualh)
        self.rect = pygame.Rect(pos[0], pos[1], visualw+100, visualh+150)
        self.surf = Surface(self.rect.size)

        self.value_surfs = [[None] * self.width for _ in range(self.height)]
        self.value_rects = [[None] * self.width for _ in range(self.height)]

        self.hover = None
        self.selection = None

        self.text_input = None

        for i, row in enumerate(self.values):
            for j, value in enumerate(row):
                self.value_surfs[i][j] = FONT.render(
                    my_complex_to_str(value), True, DARK)
        self.draw()

    def _compute_width(self):
        self.col_widths = [0] * self.width
        for j in range(self.width):
            self.col_widths[j] = max(
                self.value_surfs[i][j].get_width() for i in range(self.height))
        self.xcoords = [0] * self.width
        self.xcoords[0] = self.SIDE
        for j in range(1, self.width):
            self.xcoords[j] = self.xcoords[j-1] + \
                self.col_widths[j-1] + self.HGAP
    
    def mouse_down(self, pos):
        pos = adjust_pos(pos, self.rect)
        pass


    def draw(self):
        self.surf.fill(WHITE)
        cap = 20
        thick = 6
        x, y = self.matrix_rect.topleft
        r, b = self.matrix_rect.bottomright
        h = self.matrix_rect.height
        pygame.draw.rect(self.surf, DARK, (x, y, cap, thick))
        pygame.draw.rect(self.surf, DARK, (x, y, thick, h))
        pygame.draw.rect(self.surf, DARK, (x, b-thick, cap, thick))
        pygame.draw.rect(self.surf, DARK, (r-cap, y, cap, thick))
        pygame.draw.rect(self.surf, DARK, (r, y, thick, h))
        pygame.draw.rect(self.surf, DARK, (r-cap, b-thick, cap, thick))

        for i, row in enumerate(self.values):
            for j in range(len(row)):
                self.value_rects[i][j] = self.surf.blit(self.value_surfs[i][j],
                                                        (x+self.xcoords[j],
                                                         y+self.VSPACE*i))

    def update(self, pos):
        pos = adjust_pos(pos, self.rect)
        if (current_hover := self._pos_in_matrix(pos)) is not None:
            if current_hover != self.hover:
                i, j = current_hover
                self.value_surfs[i][j] = FONT.render(
                    my_complex_to_str(self.values[i][j]), True, ORANGE)
                if self.hover is not None:
                    previ, prevj = self.hover
                    self.value_surfs[previ][prevj] = FONT.render(
                        my_complex_to_str(self.values[previ][prevj]), True, DARK)
                self.hover = current_hover
        elif self.hover is not None:
            previ, prevj = self.hover
            self.value_surfs[previ][prevj] = FONT.render(
                my_complex_to_str(self.values[previ][prevj]), True, DARK)
            self.hover = None

    def _pos_in_matrix(self, pos):
        for i, row in enumerate(self.values):
            for j in range(len(row)):
                if self.value_rects[i][j].collidepoint(pos):
                    return i, j
        return None

def adjust_pos(pos, rect):
    x, y = pos
    return (x - rect.x, y - rect.y)

g = CustomGateEditor(pygame.Rect(100, 100, 500, 500))

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            g.mouse_down(event.pos)
        elif event.type == pygame.MOUSEBUTTONUP:
            pass
        elif event.type == pygame.KEYDOWN:
            g.key_down(event)

    screen.fill(WHITE)
    g.update(pygame.mouse.get_pos())
    g.draw()
    screen.blit(g.surf, g.rect)

    pygame.display.flip()

pygame.quit()
