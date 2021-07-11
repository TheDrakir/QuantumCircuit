import pygame


pygame.init()

# set window size
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 1000
pygame.display.set_caption("Quantum Circuit Builder")
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# load standard font (can take up to a few seconds)
FONT = pygame.font.SysFont('Arial', 70)

# define colors
WHITE = (255, 255, 255)
GREY = (200, 200, 200)
RED = (219, 42, 42)
ORANGE = (219, 163, 42)
GREEN = (151, 219, 42)
TEAL = (42, 219, 160)
CYAN = (42, 219, 219)
BLUE = (42, 89, 219)
PURPLE = (148, 42, 219)
PINK = (219, 42, 154)


class GateType:
    """Stores a type of gate."""

    def __init__(self, name, color, control=False):
        self.name = name
        self.color = color
        self.control = control


H = GateType('H', RED)
X = GateType('X', ORANGE)
Y = GateType('Y', GREEN)
Z = GateType('Z', TEAL)
CNOT = GateType('+', CYAN, control=True)
CZ = GateType('Z', PINK, control=True)


class Control:
    def __init__(self):
        self.midpoint = (0, 0)
        self.radius = 15

    def point_in(self, pos):
        x, y = pos
        midx, midy = self.midpoint
        return (x-midx)**2 + (y-midy)**2 <= self.radius**2


class Gate:
    """Stores a graphical instance of a gate."""

    SIZE = 75

    HOVER = 0
    CLICKED = 1
    FIXED = 2
    PLACED = 3
    GRABBED = 4

    def __init__(self, gate_type: GateType, pos: tuple[int, int] = (0, 0)):
        self.gate_type = gate_type
        self.surf = pygame.Surface((Gate.SIZE, Gate.SIZE))
        self.rect = self.surf.get_rect()
        self.rect.topleft = pos
        self.gatey = 0
        self.control = None
        self.state = Gate.FIXED
        self.redraw()
        self.grabx, self.graby = None, None

    def set_control(self, control, offset, ystep):
        if control is not None:
            self.control = control
        self.offset = offset
        self.ystep = ystep
        self.surf = pygame.Surface(
            (Gate.SIZE, Gate.SIZE+ystep*abs(offset)), pygame.SRCALPHA)
        self.rect.h = Gate.SIZE+ystep*abs(offset)
        if offset < 0:
            self.rect.y -= ystep * abs(offset)
            self.control.midpoint = (Gate.SIZE/2, Gate.SIZE/2)
            self.gatey = ystep*abs(offset)
        else:
            self.gatey = 0
            self.control.midpoint = (Gate.SIZE/2, ystep*offset+Gate.SIZE/2)
        self.redraw()

    def update_offset(self, new_offset):
        if new_offset != self.offset:
            self.rect.y += self.gatey
            self.set_control(None, new_offset, self.ystep)

    def redraw(self):
        if self.control is not None:
            pygame.draw.circle(
                self.surf, self.gate_type.color, self.control.midpoint,
                self.control.radius)
            pygame.draw.line(self.surf, self.gate_type.color,
                             self.control.midpoint,
                             (Gate.SIZE/2, self.gatey+Gate.SIZE/2), width=5)

        img = FONT.render(self.gate_type.name, True, WHITE)
        width, height = img.get_size()

        if self.gate_type is CNOT:
            pygame.draw.circle(self.surf, self.gate_type.color,
                               (Gate.SIZE/2, self.gatey+Gate.SIZE/2), Gate.SIZE/2)
        else:
            pygame.draw.rect(self.surf, self.gate_type.color,
                             (0, self.gatey, Gate.SIZE, Gate.SIZE))
        pos = ((Gate.SIZE-width)*0.5, self.gatey+(Gate.SIZE-height)*0.5)
        self.surf.blit(img, pos)

        if self.state == Gate.GRABBED:
            self.surf.set_alpha(150)
        else:
            self.surf.set_alpha(255)

    def point_in(self, pos: tuple[int, int]) -> bool:
        return self.rect.collidepoint(pos)

    def point_in_control(self, pos):
        x, y = pos
        pos = x - self.rect.x, y - self.rect.y
        return self.control.point_in(pos)

    def grab(self, grab_pos: tuple[int, int]):
        self.state = Gate.GRABBED
        x, y = grab_pos
        self.grabx, self.graby = x - self.rect.x, y - self.rect.y
        self.redraw()

    def place(self, pos: tuple[int, int]):
        self.state = Gate.PLACED
        self.rect.topleft = pos
        self.redraw()

    def update(self, pos):
        x, y = pos
        self.rect.x, self.rect.y = x - self.grabx, y - self.graby


class Qubit:

    def __init__(self, rect: pygame.Rect):
        self.surf = pygame.Surface(rect.size)
        self.surf.fill(GREY)
        self.rect = rect


class Blocked:
    pass


BLOCKED = Blocked()


class CircuitBuilder:

    def __init__(self):
        self.width = SCREEN_WIDTH - 200
        self.ytop = 250
        self.ystep = 100
        self.xstep = 100
        self.num_slots = self.width // self.xstep

        self.gate_types = [H, X, Y, Z, CNOT, CZ]

        # create the gate object for all gate types
        self.build_gates = []
        for i, g in enumerate(self.gate_types):
            self.build_gates.append(Gate(g, pos=(100*i, 100)))
            if g.control:
                self.build_gates[i].set_control(Control(), -1, self.ystep)

        self.num_qubits = 5
        self.qubits = []
        for i in range(self.num_qubits):
            rect = pygame.Rect(0,
                               self.ytop+self.ystep*(i+0.5)-5/2,
                               self.width,
                               5)
            self.qubits.append(Qubit(rect))

        self.surf = pygame.Surface((self.width,
                                   self.ytop + self.ystep*self.num_qubits))
        self.rect = self.surf.get_rect()

        self.gates = [[None] * self.num_slots for _ in range(self.num_qubits)]

        self.grabbed_gate = None
        self.control_grabbed = False
        self.control_j = None
        self.gate_i = None
        self.control_offset_start = None

    def draw(self):
        self.surf.fill(WHITE)
        for qubit in self.qubits:
            self.surf.blit(qubit.surf, qubit.rect)
        for gate in self.build_gates:
            self.surf.blit(gate.surf, gate.rect)
        for row in self.gates:
            for gate in row:
                if gate is not None and gate is not BLOCKED:
                    self.surf.blit(gate.surf, gate.rect)
        if self.grabbed_gate is not None:
            if (pos := self._get_position()) is not None:
                gate = self.grabbed_gate
                (_, _), (x, y) = pos
                rect = pygame.Rect(x, y, gate.rect.w, gate.rect.h)
                pygame.draw.rect(self.surf, WHITE, rect)
                pygame.draw.rect(self.surf, GREY, rect, width=3)
            self.surf.blit(self.grabbed_gate.surf, self.grabbed_gate.rect)

    def _get_position(self):
        if (gate := self.grabbed_gate) is not None:
            slot = int((gate.rect.x+self.xstep/2)/self.xstep)
            num = int((gate.rect.y+gate.gatey-self.ytop+self.ystep/2)/self.ystep)
            x = slot*self.xstep
            y = num*self.ystep + self.ytop + self.ystep/2 - gate.SIZE/2-gate.gatey
            if 0 <= slot < self.num_slots and 0 <= num < self.num_qubits:
                if not self._valid_position(num, slot):
                    return None
                return (slot, num), (x, y)
            return None
        return None

    def _valid_position(self, num, slot):
        if self.grabbed_gate.control is None:
            return self.gates[num][slot] is None
        else:
            if self.grabbed_gate.offset < 0:
                if num < abs(self.grabbed_gate.offset):
                    return False
                for n in range(num - abs(self.grabbed_gate.offset), num+1):
                    if self.gates[n][slot] is not None:
                        return False
            elif self.grabbed_gate.offset > 0:
                if num + self.grabbed_gate.offset >= self.num_qubits:
                    return False
                for n in range(num, num+self.grabbed_gate.offset+1):
                    if self.gates[n][slot] is not None:
                        return False
            else:
                return False
            return True

    def _set_overlap(self, num, slot, value):
        if self.grabbed_gate.control is not None:
            if self.grabbed_gate.offset < 0:
                for n in range(num - abs(self.grabbed_gate.offset), num):
                    self.gates[n][slot] = value
            elif self.grabbed_gate.offset > 0:
                for n in range(num+1, num+self.grabbed_gate.offset+1):
                    self.gates[n][slot] = value

    def mouse_up(self):
        if (pos := self._get_position()) is not None:
            (slot, num), (x, y) = pos
            self.grabbed_gate.place((x, y))
            self.gates[num][slot] = self.grabbed_gate
            self._set_overlap(num, slot, BLOCKED)
            self.grabbed_gate = None
            self.control_grabbed = False
            self.control_j = None
            self.control_offset_start = None
            self.gate_i = None
        else:
            self.grabbed_gate = None

    def update(self, pos):
        x, y = pos
        pos = x - self.rect.x, y - self.rect.y
        x, y = pos
        if self.grabbed_gate is not None:
            if not self.control_grabbed:
                self.grabbed_gate.update(pos)
            else:
                newi = int((y - self.ytop)/self.ystep)
                offset = newi - self.gate_i
                old_offset = self.grabbed_gate.offset
                self.grabbed_gate.update_offset(offset)
                if not self._valid_position(self.gate_i, self.control_j):
                    self.grabbed_gate.update_offset(old_offset)

    def mouse_down(self, pos):
        x, y = pos
        pos = x - self.rect.x, y - self.rect.y
        if self.grabbed_gate is not None:
            return
        for gate in self.build_gates:
            if gate.point_in(pos):
                self.grabbed_gate = Gate(gate.gate_type, pos=(
                    gate.rect.x, gate.rect.y + gate.gatey))
                if gate.control is not None:
                    self.grabbed_gate.set_control(
                        Control(), gate.offset, self.ystep)
                self.grabbed_gate.grab(pos)
                return
        for i, row in enumerate(self.gates):
            for j, gate in enumerate(row):
                if gate is not None and gate is not BLOCKED:
                    if gate.control is not None and gate.point_in_control(pos):
                        self.grabbed_gate = gate
                        self.grabbed_gate.grab(pos)
                        self.gates[i][j] = None
                        self._set_overlap(i, j, None)
                        self.control_grabbed = True
                        self.control_j = j
                        self.control_offset_start = gate.offset
                        self.gate_i = i
                        return
                    elif gate.point_in(pos):
                        self.grabbed_gate = gate
                        self.grabbed_gate.grab(pos)
                        self.gates[i][j] = None
                        self._set_overlap(i, j, None)
                        return


builder = CircuitBuilder()
builder.rect.topleft = (100, 100)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            builder.mouse_down(event.pos)
        elif event.type == pygame.MOUSEBUTTONUP:
            builder.mouse_up()

    screen.fill((255, 255, 255))
    builder.update(pygame.mouse.get_pos())
    builder.draw()
    screen.blit(builder.surf, builder.rect)

    pygame.display.flip()

pygame.quit()
