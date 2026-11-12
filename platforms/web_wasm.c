#include "../core/vm.h"
#include "../game/rom_data.h"

static VM web_vm;

void web_init(void) {
    vm_init(&web_vm, sokoban_rom, sizeof(sokoban_rom));
}

void web_tick(uint8_t key) {
    vm_step_frame(&web_vm, key);
}

uint8_t web_get_tile(int x, int y) {
    if (x < 0 || x >= SCREEN_W || y < 0 || y >= SCREEN_H) return ' ';
    return *(*(web_vm.screen + y) + x);
}

uint8_t web_is_win(void) {
    return *(web_vm.memory + 1511);
}
