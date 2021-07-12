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
    def __init__(self):
        self.surf = pygame.Surface(500, 1000)
        self.rect = self.surf.get_rect()

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
            self.text_surf = FONT.render(self.text, True, TextInput.TEXT_COLOR)
        else:
            if not self.active:
                self.text_surf = FONT.render(self.hint, True, TextInput.HINT_COLOR)
            else:
                self.text_surf = FONT.render("", True, TextInput.HINT_COLOR)
    
    def draw(self):
        self.surf.fill(WHITE)
        #pygame.draw.rect(self.surf, GREY, (0, self.rect.h-4, self.rect.w, 4))
        pygame.draw.rect(self.surf, TEAL, (0, self.rect.h-3, self.animation.get_value(), 3))
        self.surf.blit(self.text_surf, (0, 0))
        if self.active and (time() - self.start_time) % 1 < 0.5:
            w = self.text_surf.get_width()
            pygame.draw.rect(self.surf, TextInput.TEXT_COLOR, (w, 0, 2, self.rect.h-15))
    
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
    
    def key_down(self, key):
        if key == pygame.K_BACKSPACE:
            if self.text:
                self.text = self.text[:-1]
        elif len(self.text) < self.maxlen: 
            self.text += event.unicode
        self._update_text_surf()
        self.draw()

    

text_input = TextInput(pygame.Rect(100, 100, 500, 60), hint="Gate name")

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            text_input.mouse_down(event.pos)
        elif event.type == pygame.MOUSEBUTTONUP:
            pass
        elif event.type == pygame.KEYDOWN:
            text_input.key_down(event.key)

    screen.fill(WHITE)
    text_input.draw()
    screen.blit(text_input.surf, text_input.rect)

    pygame.display.flip()

pygame.quit()