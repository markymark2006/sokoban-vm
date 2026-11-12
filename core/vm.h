#ifndef VM_H
#define VM_H

#include <stdint.h>
#include <stdbool.h>

#define MEM_SIZE 4096
#define STACK_SIZE 64
#define SCREEN_W 12
#define SCREEN_H 10

enum { KEY_NONE = 0, KEY_UP = 1, KEY_DOWN = 2, KEY_LEFT = 3, KEY_RIGHT = 4, KEY_RESET = 5 };

enum {
    OP_HALT  = 0x00, OP_PUSH  = 0x01, OP_POP   = 0x02, OP_ADD   = 0x03,
    OP_SUB   = 0x04, OP_MUL   = 0x05, OP_LOAD  = 0x06, OP_STORE = 0x07,
    OP_JMP   = 0x08, OP_JZ    = 0x09, OP_EQ    = 0x0A, OP_LT    = 0x0B,
    OP_KEY   = 0x0C, OP_DRAW  = 0x0D, OP_DUP   = 0x0E
};

typedef struct {
    uint8_t memory[MEM_SIZE];
    int16_t stack[STACK_SIZE];
    uint8_t screen[SCREEN_H][SCREEN_W];
    uint16_t pc;
    uint8_t sp;
    uint8_t current_key;
    bool halted;
} VM;

void vm_init(VM *vm, const uint8_t *program, uint16_t size);
void vm_step_frame(VM *vm, uint8_t key);

#endif
