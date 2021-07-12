from matplotlib.colors import TwoSlopeNorm
import pygame
import json
import seaborn as sns

from MyMath import my_round
from Storage import *
from Circuit import *



pygame.init()

# set file name, which input data will be written to
INPUT_FILE_NAME = "to_back.json"

# set window size
SCREEN_WIDTH = 1500
SCREEN_HEIGHT = 1000
CIRCUIT_WIDTH = 1000

pygame.display.set_caption("Quantum Circuit Builder")
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# load standard font (can take up to a few seconds)
FONT = pygame.font.SysFont('Arial', 70)
TEXT_FONT = pygame.font.SysFont('Arial', 20)



class Control:
    def __init__(self):
        self.midpoint = (0, 0)
        self.radius = 15

    def point_in(self, pos):
        x, y = pos
        midx, midy = self.midpoint
        return (x-midx)**2 + (y-midy)**2 <= self.radius**2

class Node:
    def __init__(self, gate, offset, main = True):
        self.gate = gate
        self.offset = offset
        self.main = main


class Gate:
    """Stores a graphical instance of a gate."""

    SIZE = 75

    HOVER = 0
    CLICKED = 1
    FIXED = 2
    PLACED = 3
    GRABBED = 4

    def __init__(self, circuit_builder, gate_type: GateType, pos: tuple[int, int] = (0, 0)):
        self.circuit_builder = circuit_builder
        self.nodes = [Node(self, 0)]
        self.gate_type = gate_type
        self.surf = pygame.Surface((Gate.SIZE, Gate.SIZE))
        self.rect = self.surf.get_rect()
        self.rect.topleft = pos
        self.gatey = 0
        self.control = None
        self.state = Gate.FIXED
        self.inactive_count = 0
        self.redraw()
        self.grabx, self.graby = None, None

    def set_control(self, control, offset, ystep):
        if control is not None:
            self.control = control
        self.nodes = self.nodes[:1] + [Node(self, offset, False)]
        self.offset = offset
        self.ystep = ystep
        self.surf = pygame.Surface((Gate.SIZE, Gate.SIZE+ystep*abs(offset)), pygame.SRCALPHA)
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
            pygame.draw.circle(self.surf, self.gate_type.color, self.control.midpoint, self.control.radius)
            pygame.draw.line(self.surf, self.gate_type.color, self.control.midpoint, (Gate.SIZE/2, self.gatey+Gate.SIZE/2), width=5)

        img = FONT.render(self.gate_type.name, True, WHITE)
        width, height = img.get_size()

        if self.gate_type is CNOT:
            pygame.draw.circle(self.surf, self.gate_type.color, (Gate.SIZE/2, self.gatey+Gate.SIZE/2), Gate.SIZE/2)
        else:
            pygame.draw.rect(self.surf, self.gate_type.color, (0, self.gatey, Gate.SIZE, Gate.SIZE))
        pos = ((Gate.SIZE-width)*0.5, self.gatey+(Gate.SIZE-height)*0.5)
        self.surf.blit(img, pos)

        if self.state == Gate.GRABBED:
            self.surf.set_alpha(150)
        elif self.inactive_count > 0:
            self.surf.set_alpha(80)
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

    def place(self, pos):
        (slot, num), (x, y) = pos
        self.state = Gate.PLACED
        self.rect.topleft = x, y
        self.circuit_builder._set_overlap(self, num, slot, BLOCKED)
        self.inactive_count = 0
        for node in self.nodes:
            qubit = self.circuit_builder.qubits[num + node.offset]
            if qubit.state == Qubit.INACTIVE:
                self.inactive_count += 1
        self.redraw()

    def update(self, pos):
        x, y = pos
        self.rect.x, self.rect.y = x - self.grabx, y - self.graby

    def activate(self):
        self.inactive_count -= 1
        self.redraw()

    def deactivate(self):
        self.inactive_count += 1
        self.redraw()



class Qubit:
    ACTIVE = 0
    INACTIVE = 1

    def __init__(self, circuit_builder, index, rect: pygame.Rect):
        self.circuit_builder = circuit_builder
        self.index = index
        self.surf = pygame.Surface(rect.size)
        self.surf.fill(GREY)
        self.rect = rect
        self.state = Qubit.ACTIVE

    def redraw(self):
        if self.state == Qubit.INACTIVE:
            self.surf.set_alpha(100)
        else:
            self.surf.set_alpha(255)

    def activate(self):
        self.state = Qubit.ACTIVE
        self.circuit_builder.active_qubits += 1
        for node in self.circuit_builder.circuitNodes[self.index]:
            if node != None and node != BLOCKED:
                gate = node.gate
                gate.activate()
        self.redraw()

    def deactivate(self):
        self.state = Qubit.INACTIVE
        self.circuit_builder.active_qubits -= 1
        for node in self.circuit_builder.circuitNodes[self.index]:
            if node != None and node != BLOCKED:
                gate = node.gate
                gate.deactivate()
        self.redraw()

    def toggle(self):
        if self.state == Qubit.ACTIVE:
            self.deactivate()
        else:
            self.activate()



class Blocked:
    pass


BLOCKED = Blocked()


class CircuitBuilder:

    def __init__(self, input_file_name):
        self.input_file_name = input_file_name
        self.ytop = 50
        self.xleft = 50
        self.width = SCREEN_WIDTH - 2 * self.xleft
        self.height = SCREEN_HEIGHT - 2 * self.ytop
        self.ytop_circuit = 400
        self.circuit_width = CIRCUIT_WIDTH
        self.ystep = 100
        self.xstep = 100
        self.num_slots = self.circuit_width // self.xstep

        self.gate_types = [H, X, Y, Z, CNOT, CZ]

        # create the gate object for all gate types
        self.build_gates = []
        for i, g in enumerate(self.gate_types):
            self.build_gates.append(Gate(self, g, pos=(100*i, 100)))
            if g.control:
                self.build_gates[i].set_control(Control(), -1, self.ystep)

        self.num_qubits = 5
        self.qubits = []
        self.active_qubits = self.num_qubits
        for i in range(self.num_qubits):
            rect = pygame.Rect(0, self.ytop_circuit+self.ystep*(i+0.5)-5/2, self.circuit_width, 5)
            self.qubits.append(Qubit(self, i, rect))
        self.pretty_matrices = []
        self.pretty_matrices.append(PrettyMatrix(self, 300, [700, self.ytop]))
        self.surf = pygame.Surface((self.width, self.height))
        self.rect = self.surf.get_rect()
        self.rect.topleft = [self.xleft, self.ytop]

        self.circuitNodes = [[None] * self.num_slots for _ in range(self.num_qubits)]

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
        for pretty_matrix in self.pretty_matrices:
            self.surf.blit(pretty_matrix.surf, pretty_matrix.rect)
        for row in self.circuitNodes:
            for node in row:
                if node is not None and node is not BLOCKED and node.main:
                    gate = node.gate
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
            num = int((gate.rect.y+gate.gatey-self.ytop_circuit+self.ystep/2)/self.ystep)
            x = slot*self.xstep
            y = num*self.ystep + self.ytop_circuit + self.ystep/2 - gate.SIZE/2-gate.gatey
            if 0 <= slot < self.num_slots and 0 <= num < self.num_qubits:
                if not self._valid_position(num, slot):
                    return None
                return (slot, num), (x, y)
            return None
        return None

    def _valid_position(self, num, slot):
        if self.grabbed_gate.control is None:
            return self.circuitNodes[num][slot] is None
        else:
            if self.grabbed_gate.offset < 0:
                if num < abs(self.grabbed_gate.offset):
                    return False
                for n in range(num - abs(self.grabbed_gate.offset), num+1):
                    if self.circuitNodes[n][slot] is not None:
                        return False
            elif self.grabbed_gate.offset > 0:
                if num + self.grabbed_gate.offset >= self.num_qubits:
                    return False
                for n in range(num, num+self.grabbed_gate.offset+1):
                    if self.circuitNodes[n][slot] is not None:
                        return False
            else:
                return False
            return True

    def _set_overlap(self, gate, num, slot, value):
        if gate.control is not None:
            if gate.offset < 0:
                for n in range(num - abs(gate.offset) + 1, num):
                    self.circuitNodes[n][slot] = value
            elif gate.offset > 0:
                for n in range(num+1, num+gate.offset):
                    self.circuitNodes[n][slot] = value
        for node in gate.nodes:
            if value == BLOCKED:
                self.circuitNodes[num + node.offset][slot] = node
            else:
                self.circuitNodes[num + node.offset][slot] = value

    def mouse_up(self):
        if (pos := self._get_position()) is not None:
            self.grabbed_gate.place(pos)
            self.control_grabbed = False
            self.control_j = None
            self.control_offset_start = None
            self.gate_i = None
            builder.run_circuit()
        self.grabbed_gate = None

    def update(self, pos):
        x, y = pos
        pos = x - self.rect.x, y - self.rect.y
        x, y = pos
        if self.grabbed_gate is not None:
            if not self.control_grabbed:
                self.grabbed_gate.update(pos)
            else:
                newi = int((y - self.ytop_circuit)/self.ystep)
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
                self.grabbed_gate = Gate(self, gate.gate_type, pos=(gate.rect.x, gate.rect.y + gate.gatey))
                if gate.control is not None:
                    self.grabbed_gate.set_control(Control(), gate.offset, self.ystep)
                self.grabbed_gate.grab(pos)
                return
        for i, row in enumerate(self.circuitNodes):
            for j, node in enumerate(row):
                if node is not None and node is not BLOCKED and node.main:
                    gate = node.gate
                    if gate.control is not None and gate.point_in_control(pos):
                        self.grabbed_gate = gate
                        self.grabbed_gate.grab(pos)
                        self._set_overlap(self.grabbed_gate, i, j, None)
                        self.control_grabbed = True
                        self.control_j = j
                        self.control_offset_start = gate.offset
                        self.gate_i = i
                        return
                    elif gate.point_in(pos):
                        self.grabbed_gate = gate
                        self.grabbed_gate.grab(pos)
                        self._set_overlap(self.grabbed_gate, i, j, None)
                        return

    def serialize_gates(self):
        content = {"qubits": [], "gates": {}}
        for qubit in self.qubits:
            if qubit.state == Qubit.ACTIVE:
                content["qubits"] += [1]
            else:
                content["qubits"] += [0]
        for gate_type in GATE_TYPES:
            content["gates"][gate_type.name] = []
        for qubit, row in enumerate(self.circuitNodes):
            for slot, node in enumerate(row):
                if node is not None and node is not BLOCKED and node.main:
                    gate = node.gate
                    content["gates"][gate.gate_type.name] += [[[qubit + node.offset for node in gate.nodes][::-1], slot, gate.inactive_count]]
        with open(self.input_file_name, 'w', encoding='utf-8') as f:
            json.dump(content, f, ensure_ascii=False, indent=4)

    def deserialize_gates(self):
        with open(self.input_file_name, "r") as f:
            content = json.load(f)
        for qubit, active in enumerate(content["qubits"]):
            if active == 0:
                self.qubits[qubit].deactivate()
        for gate_type_string, coords in content["gates"].items():
            gate_type = strg[gate_type_string]
            for coord in coords:
                saved_gate = Gate(self, gate_type)
                slot = coord[1]
                num = coord[0][0]
                if saved_gate.gate_type.control:
                    saved_gate.set_control(Control(), -1, self.ystep)
                    saved_gate.update_offset(coord[0][1] - coord[0][0])
                x = slot*self.xstep
                y = num*self.ystep + self.ytop_circuit + self.ystep/2 - saved_gate.SIZE/2-saved_gate.gatey
                pos = (slot, num), (x, y)
                saved_gate.place(pos)

    def run_circuit(self):
        print(self.active_qubits)
        if self.active_qubits != 0:
            self.serialize_gates()
            current_circuit = Circuit.deserialize_gates()
            linear_transformation = current_circuit.gate()
            self.pretty_matrices[0].set_matrix(linear_transformation.array)
        else:
            self.pretty_matrices[0].set_matrix([[0]])

    def toggle_qubit(self, index):
        self.qubits[index].toggle()
        self.run_circuit()


class PrettyMatrix:
    GRID_MARGIN = 3
    

    def __init__(self, circuit_builder, size, pos = [0, 0]):
        self.circuit_builder = circuit_builder
        self.size = size
        self.matrix = [[0]]
        self.palette = sns.color_palette("rocket", as_cmap=True)
        self.ytop = 30
        self.xright = 0
        self.surf = pygame.Surface((self.size + self.xright, self.size + self.ytop))
        self.surf.fill(WHITE)
        self.rect = self.surf.get_rect()
        self.rect.topleft = pos
        self.len_to_round = {1:5, 2:4, 4:3, 8:1}
        self.redraw()
        
    def __len__(self):
        return len(self.matrix)


    def set_matrix(self, matrix):
        self.matrix = matrix
        self.redraw()

    def redraw(self):
        self.grid_size = self.size // len(self)
        self.surf.fill(WHITE)
        for i in range(len(self)):
            for j in range(len(self)):
                left = j * self.grid_size + PrettyMatrix.GRID_MARGIN // 2
                top = i * self.grid_size + PrettyMatrix.GRID_MARGIN // 2 + self.ytop
                width = self.grid_size - PrettyMatrix.GRID_MARGIN
                height = self.grid_size - PrettyMatrix.GRID_MARGIN
                pygame.draw.rect(self.surf, self.grid_color(i, j), (left, top, width, height))
                if len(self) <= 8:
                    grid_text = TEXT_FONT.render(str(my_round(abs(self.matrix[i][j]), self.len_to_round[len(self)])), True, BLACK)
                    t_width, t_height = grid_text.get_size()
                    self.surf.blit(grid_text, (left + (width - t_width) // 2, top + (height - t_height) // 2))
        title = TEXT_FONT.render("circuit matrix in std base", True, BLACK)
        width, height = title.get_size()
        self.surf.blit(title, ((self.size - width) // 2, 0))

    def draw_palette(self):
        return

    def grid_color(self, i, j):
        x = abs(self.matrix[i][j]) - 0.01
        c = [255 * value for value in self.palette(x)]
        return tuple(c[:3])

                


builder = CircuitBuilder(INPUT_FILE_NAME)

running = True
builder.deserialize_gates()
builder.run_circuit()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            builder.mouse_down(event.pos)
        elif event.type == pygame.MOUSEBUTTONUP:
            builder.mouse_up()
        elif event.type == pygame.KEYDOWN:
            # if pygame.key.get_mods() & pygame.KMOD_CTRL:
            #     if event.key == pygame.K_s:
            #         builder.serialize_gates()
            #     elif event.key == pygame.K_p:
            #         builder.run_circuit()
            if event.key == pygame.K_1:
                builder.toggle_qubit(0)
            if event.key == pygame.K_2:
                builder.toggle_qubit(1)
            if event.key == pygame.K_3:
                builder.toggle_qubit(2)
            if event.key == pygame.K_4:
                builder.toggle_qubit(3)
            if event.key == pygame.K_5:
                builder.toggle_qubit(4)

    screen.fill((255, 255, 255))
    builder.update(pygame.mouse.get_pos())
    builder.draw()
    screen.blit(builder.surf, builder.rect)

    pygame.display.flip()

pygame.quit()
