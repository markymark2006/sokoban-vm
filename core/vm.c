#include "vm.h"
#include <string.h>

void vm_init(VM *vm, const uint8_t *program, uint16_t size) {
    memset(vm, 0, sizeof(VM));
    if (size > MEM_SIZE) size = MEM_SIZE;
    memcpy(vm->memory, program, size);
}

static bool push(VM *vm, int16_t val) {
    if (vm->sp >= STACK_SIZE) { vm->halted = true; return false; }
    vm->stack[vm->sp++] = val;
    return true;
}

static bool pop(VM *vm, int16_t *val) {
    if (vm->sp == 0) { vm->halted = true; return false; }
    *val = vm->stack[--vm->sp];
    return true;
}

static uint16_t read_u16(VM *vm) {
    if (vm->pc + 1 >= MEM_SIZE) { vm->halted = true; return 0; }
    uint16_t hi = vm->memory[vm->pc++];
    uint16_t lo = vm->memory[vm->pc++];
    return (hi << 8) | lo;
}

void vm_step_frame(VM *vm, uint8_t key) {
    vm->current_key = key;
    vm->pc = 0;
    vm->sp = 0;
    vm->halted = false;
    uint32_t cycles = 0;

    while (!vm->halted && vm->pc < MEM_SIZE && cycles++ < 50000) {
        uint8_t op = vm->memory[vm->pc++];
        int16_t a, b, c;
        switch (op) {
            case OP_HALT:  vm->halted = true; break;
            case OP_PUSH:  push(vm, (int16_t)read_u16(vm)); break;
            case OP_POP:   pop(vm, &a); break;
            case OP_ADD:   if (pop(vm, &b) && pop(vm, &a)) push(vm, a + b); break;
            case OP_SUB:   if (pop(vm, &b) && pop(vm, &a)) push(vm, a - b); break;
            case OP_MUL:   if (pop(vm, &b) && pop(vm, &a)) push(vm, a * b); break;
            case OP_LOAD:  if (pop(vm, &a)) push(vm, vm->memory[(uint16_t)a % MEM_SIZE]); break;
            case OP_STORE:
                if (pop(vm, &b) && pop(vm, &a)) {
                    uint16_t addr = (uint16_t)a;
                    if (addr >= 1500 && addr < MEM_SIZE) vm->memory[addr] = (uint8_t)b;
                }
                break;
            case OP_JMP:   vm->pc = read_u16(vm); break;
            case OP_JZ: {
                uint16_t target = read_u16(vm);
                if (pop(vm, &a) && a == 0) vm->pc = target;
                break;
            }
            case OP_EQ:    if (pop(vm, &b) && pop(vm, &a)) push(vm, (a == b) ? 1 : 0); break;
            case OP_LT:    if (pop(vm, &b) && pop(vm, &a)) push(vm, (a < b) ? 1 : 0); break;
            case OP_KEY:   push(vm, vm->current_key); break;
            case OP_DRAW:
                if (pop(vm, &c) && pop(vm, &b) && pop(vm, &a)) {
                    if (a >= 0 && a < SCREEN_W && b >= 0 && b < SCREEN_H) vm->screen[b][a] = (uint8_t)c;
                }
                break;
            case OP_DUP:   if (pop(vm, &a)) { push(vm, a); push(vm, a); } break;
            default:       vm->halted = true; break;
        }
    }
}
