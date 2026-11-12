OP = {
    'HALT': 0x00, 'PUSH': 0x01, 'POP': 0x02, 'ADD': 0x03,
    'SUB':  0x04, 'MUL':  0x05, 'LOAD': 0x06, 'STORE': 0x07,
    'JMP':  0x08, 'JZ':   0x09, 'EQ':   0x0A, 'LT': 0x0B,
    'KEY':  0x0C, 'DRAW': 0x0D, 'DUP':  0x0E
}

VAR_INIT, VAR_PX, VAR_PY, VAR_DX, VAR_DY = 1500, 1501, 1502, 1503, 1504
VAR_NX, VAR_NY, VAR_NNX, VAR_NNY = 1505, 1506, 1507, 1508
VAR_X, VAR_Y, VAR_WIN, VAR_IDX = 1509, 1510, 1511, 1512
MAP_BASE  = 1600  # Рабочая карта (120 байт)
GOAL_BASE = 1800  # Слой целей (120 байт)
ORIG_BASE = 2000  # Эталонная карта для рестарта по R (120 байт)

LEVEL = [
    "############",
    "#          #",
    "#  $   .   #",
    "#   ###    #",
    "# @  $  .  #",
    "#    #     #",
    "#  $    .  #",
    "#          #",
    "#          #",
    "############"
]

class Asm:
    def __init__(self):
        self.code = bytearray()
        self.labels = {}
        self.fixups = []

    def emit(self, op, arg=None):
        self.code.append(OP[op])
        if arg is not None:
            if isinstance(arg, str):
                self.fixups.append((len(self.code), arg))
                self.code.extend(bytes(2))
            else:
                self.code.append((arg >> 8) & 0xFF)
                self.code.append(arg & 0xFF)

    def label(self, name):
        self.labels[name] = len(self.code)

    def build(self):
        for pos, name in self.fixups:
            addr = self.labels[name]
            self.code[pos] = (addr >> 8) & 0xFF
            self.code[pos + 1] = addr & 0xFF
        return self.code

a = Asm()

# 1. Инициализация или рестарт (клавиша 5 = R)
a.emit('PUSH', VAR_INIT); a.emit('LOAD'); a.emit('JZ', 'do_init')
a.emit('KEY'); a.emit('PUSH', 5); a.emit('EQ'); a.emit('JZ', 'main_loop')

a.label('do_init')
# Копируем 120 байт из ORIG_BASE в MAP_BASE циклом
a.emit('PUSH', VAR_IDX); a.emit('PUSH', 0); a.emit('STORE')
a.label('copy_loop')
a.emit('PUSH', VAR_IDX); a.emit('LOAD'); a.emit('PUSH', 120); a.emit('LT'); a.emit('JZ', 'init_player')
a.emit('PUSH', MAP_BASE); a.emit('PUSH', VAR_IDX); a.emit('LOAD'); a.emit('ADD')
a.emit('PUSH', ORIG_BASE); a.emit('PUSH', VAR_IDX); a.emit('LOAD'); a.emit('ADD'); a.emit('LOAD')
a.emit('STORE')
a.emit('PUSH', VAR_IDX); a.emit('PUSH', VAR_IDX); a.emit('LOAD'); a.emit('PUSH', 1); a.emit('ADD'); a.emit('STORE')
a.emit('JMP', 'copy_loop')

a.label('init_player')
a.emit('PUSH', VAR_PX); a.emit('PUSH', 2); a.emit('STORE')
a.emit('PUSH', VAR_PY); a.emit('PUSH', 4); a.emit('STORE')
a.emit('PUSH', VAR_INIT); a.emit('PUSH', 1); a.emit('STORE')

# 2. Обработка кнопок (dx, dy храним со сдвигом +10)
a.label('main_loop')
a.emit('PUSH', VAR_DX); a.emit('PUSH', 10); a.emit('STORE')
a.emit('PUSH', VAR_DY); a.emit('PUSH', 10); a.emit('STORE')

for key_code, dx, dy, lbl in [(1, 10, 9, 'k2'), (2, 10, 11, 'k3'), (3, 9, 10, 'k4'), (4, 11, 10, 'k_end')]:
    a.emit('KEY'); a.emit('PUSH', key_code); a.emit('EQ'); a.emit('JZ', lbl)
    a.emit('PUSH', VAR_DX); a.emit('PUSH', dx); a.emit('STORE')
    a.emit('PUSH', VAR_DY); a.emit('PUSH', dy); a.emit('STORE')
    a.label(lbl)

a.emit('PUSH', VAR_DX); a.emit('LOAD'); a.emit('PUSH', 10); a.emit('EQ'); a.emit('JZ', 'do_move')
a.emit('PUSH', VAR_DY); a.emit('LOAD'); a.emit('PUSH', 10); a.emit('EQ'); a.emit('JZ', 'do_move')
a.emit('JMP', 'render')

# 3. Движение и толкание ящиков
a.label('do_move')
a.emit('PUSH', VAR_NX); a.emit('PUSH', VAR_PX); a.emit('LOAD'); a.emit('PUSH', VAR_DX); a.emit('LOAD'); a.emit('ADD'); a.emit('PUSH', 10); a.emit('SUB'); a.emit('STORE')
a.emit('PUSH', VAR_NY); a.emit('PUSH', VAR_PY); a.emit('LOAD'); a.emit('PUSH', VAR_DY); a.emit('LOAD'); a.emit('ADD'); a.emit('PUSH', 10); a.emit('SUB'); a.emit('STORE')

a.emit('PUSH', MAP_BASE); a.emit('PUSH', VAR_NY); a.emit('LOAD'); a.emit('PUSH', 12); a.emit('MUL'); a.emit('ADD')
a.emit('PUSH', VAR_NX); a.emit('LOAD'); a.emit('ADD'); a.emit('LOAD')

a.emit('DUP'); a.emit('PUSH', ord('#')); a.emit('EQ'); a.emit('JZ', 'not_wall')
a.emit('POP'); a.emit('JMP', 'render')

a.label('not_wall')
a.emit('PUSH', ord('$')); a.emit('EQ'); a.emit('JZ', 'move_player')

a.emit('PUSH', VAR_NNX); a.emit('PUSH', VAR_NX); a.emit('LOAD'); a.emit('PUSH', VAR_DX); a.emit('LOAD'); a.emit('ADD'); a.emit('PUSH', 10); a.emit('SUB'); a.emit('STORE')
a.emit('PUSH', VAR_NNY); a.emit('PUSH', VAR_NY); a.emit('LOAD'); a.emit('PUSH', VAR_DY); a.emit('LOAD'); a.emit('ADD'); a.emit('PUSH', 10); a.emit('SUB'); a.emit('STORE')

a.emit('PUSH', MAP_BASE); a.emit('PUSH', VAR_NNY); a.emit('LOAD'); a.emit('PUSH', 12); a.emit('MUL'); a.emit('ADD')
a.emit('PUSH', VAR_NNX); a.emit('LOAD'); a.emit('ADD'); a.emit('LOAD')
a.emit('PUSH', ord(' ')); a.emit('EQ'); a.emit('JZ', 'render')

a.emit('PUSH', MAP_BASE); a.emit('PUSH', VAR_NNY); a.emit('LOAD'); a.emit('PUSH', 12); a.emit('MUL'); a.emit('ADD')
a.emit('PUSH', VAR_NNX); a.emit('LOAD'); a.emit('ADD'); a.emit('PUSH', ord('$')); a.emit('STORE')

a.emit('PUSH', MAP_BASE); a.emit('PUSH', VAR_NY); a.emit('LOAD'); a.emit('PUSH', 12); a.emit('MUL'); a.emit('ADD')
a.emit('PUSH', VAR_NX); a.emit('LOAD'); a.emit('ADD'); a.emit('PUSH', ord(' ')); a.emit('STORE')

a.label('move_player')
a.emit('PUSH', VAR_PX); a.emit('PUSH', VAR_NX); a.emit('LOAD'); a.emit('STORE')
a.emit('PUSH', VAR_PY); a.emit('PUSH', VAR_NY); a.emit('LOAD'); a.emit('STORE')

# 4. Отрисовка
a.label('render')
a.emit('PUSH', VAR_WIN); a.emit('PUSH', 1); a.emit('STORE')
a.emit('PUSH', VAR_Y); a.emit('PUSH', 0); a.emit('STORE')

a.label('loop_y')
a.emit('PUSH', VAR_Y); a.emit('LOAD'); a.emit('PUSH', 10); a.emit('LT'); a.emit('JZ', 'draw_player')
a.emit('PUSH', VAR_X); a.emit('PUSH', 0); a.emit('STORE')

a.label('loop_x')
a.emit('PUSH', VAR_X); a.emit('LOAD'); a.emit('PUSH', 12); a.emit('LT'); a.emit('JZ', 'next_y')
a.emit('PUSH', VAR_IDX); a.emit('PUSH', VAR_Y); a.emit('LOAD'); a.emit('PUSH', 12); a.emit('MUL'); a.emit('PUSH', VAR_X); a.emit('LOAD'); a.emit('ADD'); a.emit('STORE')

a.emit('PUSH', GOAL_BASE); a.emit('PUSH', VAR_IDX); a.emit('LOAD'); a.emit('ADD'); a.emit('LOAD')
a.emit('JZ', 'choose_tile')
a.emit('PUSH', MAP_BASE); a.emit('PUSH', VAR_IDX); a.emit('LOAD'); a.emit('ADD'); a.emit('LOAD')
a.emit('PUSH', ord('$')); a.emit('EQ'); a.emit('JZ', 'not_won')
a.emit('JMP', 'choose_tile')
a.label('not_won')
a.emit('PUSH', VAR_WIN); a.emit('PUSH', 0); a.emit('STORE')

a.label('choose_tile')
a.emit('PUSH', VAR_X); a.emit('LOAD')
a.emit('PUSH', VAR_Y); a.emit('LOAD')
a.emit('PUSH', MAP_BASE); a.emit('PUSH', VAR_IDX); a.emit('LOAD'); a.emit('ADD'); a.emit('LOAD')
a.emit('DUP'); a.emit('PUSH', ord(' ')); a.emit('EQ'); a.emit('JZ', 'chk_box')
a.emit('POP')
a.emit('PUSH', GOAL_BASE); a.emit('PUSH', VAR_IDX); a.emit('LOAD'); a.emit('ADD'); a.emit('LOAD')
a.emit('JZ', 't_space')
a.emit('PUSH', ord('.')); a.emit('JMP', 'do_draw')
a.label('t_space')
a.emit('PUSH', ord(' ')); a.emit('JMP', 'do_draw')

a.label('chk_box')
a.emit('DUP'); a.emit('PUSH', ord('$')); a.emit('EQ'); a.emit('JZ', 'do_draw')
a.emit('POP')
a.emit('PUSH', GOAL_BASE); a.emit('PUSH', VAR_IDX); a.emit('LOAD'); a.emit('ADD'); a.emit('LOAD')
a.emit('JZ', 't_box')
a.emit('PUSH', ord('*')); a.emit('JMP', 'do_draw')
a.label('t_box')
a.emit('PUSH', ord('$'))

a.label('do_draw')
a.emit('DRAW')
a.emit('PUSH', VAR_X); a.emit('PUSH', VAR_X); a.emit('LOAD'); a.emit('PUSH', 1); a.emit('ADD'); a.emit('STORE')
a.emit('JMP', 'loop_x')

a.label('next_y')
a.emit('PUSH', VAR_Y); a.emit('PUSH', VAR_Y); a.emit('LOAD'); a.emit('PUSH', 1); a.emit('ADD'); a.emit('STORE')
a.emit('JMP', 'loop_y')

a.label('draw_player')
a.emit('PUSH', VAR_PX); a.emit('LOAD')
a.emit('PUSH', VAR_PY); a.emit('LOAD')
a.emit('PUSH', ord('@'))
a.emit('DRAW')
a.emit('HALT')

# Формируем образ памяти ROM на 2200 байт (код + данные карты)
rom = bytearray(2200)
code = a.build()
rom[:len(code)] = code

for y, row in enumerate(LEVEL):
    for x, ch in enumerate(row):
        idx = y * 12 + x
        rom[GOAL_BASE + idx] = 1 if ch == '.' else 0
        rom[ORIG_BASE + idx] = ord('#') if ch == '#' else (ord('$') if ch == '$' else ord(' '))

with open("game/rom_data.h", "w") as f:
    f.write("#ifndef ROM_DATA_H\n#define ROM_DATA_H\n#include <stdint.h>\n")
    f.write(f"static const uint8_t sokoban_rom[{len(rom)}] = {{\n    ")
    f.write(", ".join(f"0x{b:02X}" for b in rom))
    f.write("\n};\n#endif\n")
print(f"Code size: {len(code)} bytes, Total ROM: {len(rom)} bytes")
