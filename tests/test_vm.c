#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include "../core/vm.h"
#include "../game/rom_data.h"

static void test_arithmetic_and_stack(void) {
    uint8_t prog[] = {
        OP_PUSH, 0, 10,
        OP_PUSH, 0, 25,
        OP_ADD,
        OP_PUSH, 0, 5,
        OP_SUB,
        OP_PUSH, 0, 2,
        OP_MUL,
        OP_HALT
    };
    VM vm;
    vm_init(&vm, prog, sizeof(prog));
    vm_step_frame(&vm, KEY_NONE);

    assert(vm.halted == true);
    assert(vm.sp == 1);
    assert(*(vm.stack + 0) == 60);
    printf("[PASS] Unit test: arithmetic and stack\n");
}

static void test_memory_and_endianness(void) {
    uint8_t prog[] = {
        OP_PUSH, 0x07, 0xD0,
        OP_PUSH, 0x00, 0x2A,
        OP_STORE,
        OP_PUSH, 0x07, 0xD0,
        OP_LOAD,
        OP_HALT
    };
    VM vm;
    vm_init(&vm, prog, sizeof(prog));
    vm_step_frame(&vm, KEY_NONE);

    assert(vm.sp == 1);
    assert(*(vm.stack + 0) == 42);
    assert(*(vm.memory + 2000) == 42);
    printf("[PASS] Unit test: memory and Big-Endian decoding\n");
}

static void test_fuzzing(void) {
    srand(42);
    VM vm;

    vm_init(&vm, sokoban_rom, sizeof(sokoban_rom));
    for (int i = 0; i < 5000; i++) {
        uint8_t random_key = (uint8_t)(rand() % 6);
        vm_step_frame(&vm, random_key);
        assert(vm.sp <= STACK_SIZE);
        assert(vm.halted == true);
    }

    uint8_t junk_rom[MEM_SIZE];
    for (int run = 0; run < 5000; run++) {
        for (int b = 0; b < MEM_SIZE; b++) {
            *(junk_rom + b) = (uint8_t)(rand() % 256);
        }
        vm_init(&vm, junk_rom, MEM_SIZE);
        vm_step_frame(&vm, (uint8_t)(rand() % 6));
        assert(vm.sp <= STACK_SIZE);
    }
    printf("[PASS] Fuzzing test: 10,000 random inputs & bytecode mutations\n");
}

int main(void) {
    test_arithmetic_and_stack();
    test_memory_and_endianness();
    test_fuzzing();
    printf("\nAll tests passed successfully!\n");
    return 0;
}
