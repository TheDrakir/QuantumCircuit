from math import sqrt
from pygame.font import Font
from pygame.surface import Surface
from MyMath import my_complex_to_str
from time import time
import pyperclip


from Storage import *
import pygame
pygame.init()


# set window size
pygame.display.set_caption("Quantum Circuit Builder")
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
SCREEN_WIDTH, SCREEN_HEIGHT = pygame.display.get_surface().get_size()

# load standard font (can take up to a few seconds)

FONT = pygame.font.SysFont("arial", 40)



class CustomGateEditor:
    def __init__(self, rect: pygame.Rect):
        self.surf = pygame.Surface(rect.size)
        self.rect = rect
        self.title = TextView((0,0), "EDIT GATE", FONT, DARK)
        self.name_input = TextInput(
            pygame.Rect(0, 80, 500, 50), hint="Gate name")
        self.letter_prompt = TextView((0, 180), "Letter:", FONT, DARK)
        self.letter_input = TextInput(pygame.Rect(140, 180, 40, 50), maxlen=1)
        self.matrix_editor = MatrixEditor((2, 2), pygame.Rect(0, 280, 500, 500))
        self._matrix_updated()
        self.button_save = Button(pygame.Rect(0, 680, 150, 60), "Save", color=GREEN)
        self.button_delete = Button(pygame.Rect(180, 680, 150, 60), "Delete", color=RED)
        self.button_cancel = Button(pygame.Rect(360, 680, 150, 60), "Cancel", color=ORANGE)
        self.draw()
    
    def _matrix_updated(self):
        self.matrix = LinearTransformation(self.matrix_editor.values)
        if not self.matrix._is_unitary():
            self.warning = TextView((0, 580), "Transformation ist nicht unitär.", FONT, RED)
        elif self.letter_input.text == "":
            self.warning = TextView((0, 580), "Kein Buchstabe eingegeben.", FONT, RED)
        elif self.name_input.text == "":
            self.warning = TextView((0, 580), "Kein Name eingegeben.", FONT, RED)
        else:
            self.warning = TextView((0, 580), "Sieht gut aus!", FONT, GREEN)

    def update(self, pos):
        pos = adjust_pos(pos, self.rect)
        self.matrix_editor.update(pos)
        self.button_save.update(pos)
        self.button_delete.update(pos)
        self.button_cancel.update(pos)

    def draw(self):
        self.letter_input.draw()
        self.name_input.draw()
        self.matrix_editor.draw()
        self.button_save.draw()
        self.button_delete.draw()
        self.button_cancel.draw()
        self.surf.fill(WHITE)
        self.surf.blit(self.name_input.surf, self.name_input.rect)
        self.surf.blit(self.letter_input.surf, self.letter_input.rect)
        self.surf.blit(self.letter_prompt.surf, self.letter_prompt.pos)
        self.surf.blit(self.matrix_editor.surf, self.matrix_editor.rect)
        self.surf.blit(self.button_save.surf, self.button_save.rect)
        self.surf.blit(self.button_delete.surf, self.button_delete.rect)
        self.surf.blit(self.button_cancel.surf, self.button_cancel.rect)
        self.surf.blit(self.warning.surf, self.warning.pos)
        self.surf.blit(self.title.surf, self.title.pos)

    def mouse_down(self, pos):
        pos = adjust_pos(pos, self.rect)
        self.letter_input.mouse_down(pos)
        self.name_input.mouse_down(pos)
        self.matrix_editor.mouse_down(pos)
        self._matrix_updated()

    def key_down(self, event):
        self.letter_input.key_down(event)
        self.name_input.key_down(event)
        self.matrix_editor.key_down(event)
        self._matrix_updated()


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

    def __init__(self, rect: pygame.Rect, text: str = "", hint: str = "", maxlen: int = 20, editable: bool = True):
        self.surf = pygame.Surface(rect.size)
        self.font = FONT
        self.rect = rect
        self.text = text
        self.hint = hint
        self.active = False
        self.start_time = 0
        self._update_text_surf()
        self.animation = Animation(0, self.rect.w, 1000)
        self.maxlen = maxlen
        self.anim_line_color = TEAL
        self.base_line_color = GREY
        self.editable = editable
        

    def _update_text_surf(self):
        if self.text:
            self.text_surf = self.font.render(self.text, True, DARK)
        else:
            if not self.active:
                self.text_surf = self.font.render(self.hint, True, GREY)
            else:
                self.text_surf = self.font.render("", True, GREY)

    def draw(self):
        self.surf.fill(WHITE)
        pygame.draw.rect(self.surf, self.base_line_color, (0, self.rect.h-4, self.rect.w, 4))
        pygame.draw.rect(self.surf, self.anim_line_color, (0, self.rect.h -
                         4, self.animation.get_value(), 4))
        self.surf.blit(self.text_surf, (0, 0))
        if self.active and (time() - self.start_time) % 1 < 0.5:
            w = self.text_surf.get_width()
            pygame.draw.rect(self.surf, TextInput.TEXT_COLOR,
                             (w, 0, 2, self.rect.h-8))
    
    def point_in(self, pos):
        return self.rect.collidepoint(pos)

    def mouse_down(self, pos):
        if not self.editable:
            return
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
        if not self.editable:
            return
        if self.active:
            if event.key == pygame.K_BACKSPACE:
                if self.text:
                    self.text = self.text[:-1]
            elif len(self.text) < self.maxlen:
                self.text += event.unicode
            self._update_text_surf()
            self.draw()


class Button:
    def __init__(self, rect: pygame.Rect, text: str, color=BLUE):
        self.rect = rect
        self.surf = pygame.Surface(rect.size)
        self.surf = pygame.Surface(rect.size, pygame.SRCALPHA)
        self.text = text
        self.text_surf = FONT.render(self.text, True, WHITE)
        self.w, self.h = self.text_surf.get_width(), self.text_surf.get_height()
        self.hover = False
        self.animation = Animation(0, self.w, 700)
        self.color = color

    def draw(self):
        self.surf.fill(WHITE)
        pygame.draw.rect(self.surf, self.color, (0, 0, self.rect.w,
                         self.rect.h), border_radius=20)
        if (v := self.animation.get_value()) > 1.:
            pygame.draw.line(self.surf, WHITE,
                            (self.rect.w/2-self.w/2, self.rect.h/2+self.h/2-3),
                            (self.rect.w/2-self.w/2+v, self.rect.h/2+self.h/2-3),
                            width=4)
        self.surf.blit(self.text_surf, (self.rect.w/2 -
                       self.w/2, self.rect.h/2-self.h/2-2))

    def update(self, pos):
        if self.point_in(pos):
            if not self.hover:
                self.hover = True
                self.animation.run()
                
        else:
            if self.hover:
                self.hover = False
                self.animation.reverse()
    
    def point_in(self, pos):
        #pos = adjust_pos(pos, self.rect)
        return self.rect.collidepoint(pos)


class MatrixEditor:

    def __init__(self, size: tuple[int, int], rect: pygame.Rect, editable=True, values=None, vector = False, equals = False, arrow = False):
        self.eq_width = 50
        self.eq_dist = 20

        self.width, self.height = size
        self.strings = [["0"] * self.width for _ in range(self.height)]
        self.values = [[0] * self.width for _ in range(self.height)]
        self.rect = rect
        self.set_values(values)

        self.vector = vector
        if not self.vector:
            self._set_font(rect.width - 70)
        else:
            if len(values) <= 4:
                self._set_font(rect.width - 70)
            elif len(values) == 8:
                self._set_font(rect.width - 100)
            elif len(values) == 16:
                self._set_font(rect.width - 115)
            elif len(values) == 32:
                self._set_font(rect.width - 145)



        
        self.surf = Surface(self.rect.size)


        self.equals = equals
        self.arrow = arrow
        

        self.value_surfs = [[None] * self.width for _ in range(self.height)]
        self.value_rects = [[None] * self.width for _ in range(self.height)]

        self.hover = None
        self.selection = None

        self.input_rect = pygame.Rect(0, 0, 650, 50)
        self.editable = editable

        self.text_input = None

        for i, row in enumerate(self.values):
            for j, value in enumerate(row):
                self.value_surfs[i][j] = self.font.render(
                    my_complex_to_str(value), True, DARK)
        self.draw()

    def set_values(self, values):
        if values is not None:
            for i in range(self.height):
                for j in  range(self.width):
                    self.values[i][j] = values[i][j]
                    self.strings[i][j] = str(values[i][j])
        self._set_font(self.rect.width-70)
    
    def _set_font(self, desired_width):
        self._set_spaces(50)
        w1 = self.matrix_rect.width
        self._set_spaces(100)
        w2 = self.matrix_rect.width
        # calculating font size based on the assumption that width is
        # linear to it
        font_size = min(int(map_value(desired_width, w1, w2, 50, 100)), 50)
        self._set_spaces(font_size)
    
    def _set_spaces(self, fontsize):
        self.font_size = fontsize
        self.font = pygame.font.SysFont("arial", self.font_size)
        self.HGAP = 10 + self.font_size * 4/7
        self.VSPACE = self.font_size + 5
        self.SIDE = 20

        self.value_surfs = [[None] * self.width for _ in range(self.height)]

        for i, row in enumerate(self.values):
            for j, value in enumerate(row):
                self.value_surfs[i][j] = self.font.render(
                    my_complex_to_str(value), True, DARK)
        
        self._compute_matrix_rect()
        
    def _compute_matrix_rect(self):
        self._compute_width()
        visualw = sum(self.col_widths) + self.HGAP * \
            (self.width-1) + 2*self.SIDE
        visualh = self.VSPACE * self.height
        self.matrix_rect = pygame.Rect(self.eq_width, 100, visualw, visualh)
        self.eq_rect = pygame.Rect(0, 100, self.eq_width, visualh)

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
        if self.text_input is not None and self.text_input.point_in(pos):
            pass
        elif (click := self._pos_in_matrix(pos)) is not None:
            if click != self.selection:
                if self.selection is not None:
                    previ, prevj = self.selection
                    self.value_surfs[previ][prevj] = self.font.render(
                        my_complex_to_str(self.values[previ][prevj]), True, DARK)
                i, j = click
                self.selection = click
                self.value_surfs[i][j] = self.font.render(
                    my_complex_to_str(self.values[i][j]), True, BLUE)
                self.text_input = TextInput(self.input_rect, text=self.strings[i][j], maxlen=50)
                
                if self.editable:
                    self.text_input.active = True
                    self.text_input.animation.run()
        else:
            if self.selection is not None:
                previ, prevj = self.selection
                self.value_surfs[previ][prevj] = self.font.render(
                    my_complex_to_str(self.values[previ][prevj]), True, DARK)
                self.selection = None
                self.text_input = None
    
    def key_down(self, event):
        if not self.editable:
            return
        if self.text_input is not None:
            if event.key == pygame.K_RETURN:
                i, j = self.selection
                good = False
                try:
                    self.values[i][j] = eval(self.text_input.text, {'sqrt': sqrt}, {})
                    if self.text_input.anim_line_color == RED:
                        self.text_input.base_line_color = RED
                        self.text_input.anim_line_color = TEAL
                        self.text_input.animation.value = 0
                        self.text_input.animation.run()
                    good = True
                except:
                    if self.text_input.anim_line_color == TEAL:
                        self.text_input.base_line_color = TEAL
                        self.text_input.anim_line_color = RED
                        self.text_input.animation.value = 0
                        self.text_input.animation.run()

                if good:
                    self.strings[i][j] = self.text_input.text
                    self._set_font(self.rect.width - 20)
                    self.value_surfs[i][j] = self.font.render(
                    my_complex_to_str(self.values[i][j]), True, RED)
                    self._compute_matrix_rect()
            else:
                self.text_input.key_down(event)
        

    def draw(self):
        self.surf.fill(WHITE)
        cap = 20
        thick = int(max(self.font_size * 0.15, 3))
        x_eq, y_eq = self.eq_rect.topleft
        r_eq, b_eq = self.eq_rect.bottomright
        if self.equals:
            pygame.draw.rect(self.surf, DARK, (x_eq, (y_eq+b_eq-thick + self.eq_dist)/2, 0.8*self.eq_width, thick))
            pygame.draw.rect(self.surf, DARK, (x_eq, (y_eq+b_eq-thick - self.eq_dist)/2, 0.8*self.eq_width, thick))
        elif self.arrow:
            pygame.draw.rect(self.surf, DARK, (x_eq, (y_eq+b_eq-thick)/2, 0.8*self.eq_width, thick))

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
        if self.text_input is not None:
            self.text_input.draw()
            self.surf.blit(self.text_input.surf, self.text_input.rect)

    def update(self, pos):
        pos = adjust_pos(pos, self.rect)
        if (current_hover := self._pos_in_matrix(pos)) is not None:
            if current_hover != self.hover and current_hover != self.selection:
                i, j = current_hover
                self.value_surfs[i][j] = self.font.render(
                    my_complex_to_str(self.values[i][j]), True, CYAN)
                if self.hover is not None and self.hover != self.selection:
                    previ, prevj = self.hover
                    self.value_surfs[previ][prevj] = self.font.render(
                        my_complex_to_str(self.values[previ][prevj]), True, DARK)
                self.hover = current_hover
        elif self.hover is not None and self.hover != self.selection:
            previ, prevj = self.hover
            self.value_surfs[previ][prevj] = self.font.render(
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

def map_value(value, istart, istop, ostart, ostop):
    return ostart + (ostop - ostart) * ((value - istart) / (istop - istart))

if __name__ == '__main__':
    g = CustomGateEditor(pygame.Rect(100, 100, 1000, 780))

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


class CopyBox:

    def __init__(self, circuit_builder, message, pretty_matrix):
        self.circuit_builder = circuit_builder
        self.message = message
        self.surf = pygame.Surface((pretty_matrix.width + pretty_matrix.xright, pretty_matrix.height + pretty_matrix.ytop))
        self.rect = self.surf.get_rect()
        self.rect.topleft = pretty_matrix.rect.topleft
        self.string = ""

    def set_string(self, string):
        self.string = string

    def copy(self):
        pyperclip.copy(self.string)
        self.circuit_builder.message = Message(self.circuit_builder, self.message, 1)


    def point_in(self, pos: tuple[int, int]) -> bool:
        return self.rect.collidepoint(pos)



class Message:
    SIZE = 100
    def __init__(self, circuit_builder, string, runtime):
        self.start = time()
        self.font = pygame.font.SysFont('Arial', Message.SIZE)
        self.circuit_builder = circuit_builder
        self.string = string
        self.runtime = runtime
        self.surf = pygame.Surface((SCREEN_WIDTH, Message.SIZE))
        self.rect = self.surf.get_rect()
        self.rect.topleft = [0, (SCREEN_HEIGHT-Message.SIZE) / 2-100]

        self.surf.fill(WHITE)
        text = self.font.render(self.string, True, DARK)
        t_width, _ = text.get_size()
        self.surf.blit(text, ((SCREEN_WIDTH - t_width) / 2, 0))


    def redraw(self):
        self.surf.set_alpha(255-255*(time() - self.start) / self.runtime)
        if self.runtime <= time() - self.start:
            self.circuit_builder.message = None
            del self