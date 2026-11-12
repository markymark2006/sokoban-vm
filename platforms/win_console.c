#include <stdio.h>
#include <stdlib.h>
#include <windows.h>
#include <conio.h>
#include "../core/vm.h"
#include "../game/rom_data.h"

static uint8_t read_input(void) {
    if (!_kbhit()) return KEY_NONE;
    int ch = _getch();
    if (ch == 0 || ch == 224) {
        ch = _getch();
        if (ch == 72) return KEY_UP;
        if (ch == 80) return KEY_DOWN;
        if (ch == 75) return KEY_LEFT;
        if (ch == 77) return KEY_RIGHT;
    }
    if (ch == 'w' || ch == 'W') return KEY_UP;
    if (ch == 's' || ch == 'S') return KEY_DOWN;
    if (ch == 'a' || ch == 'A') return KEY_LEFT;
    if (ch == 'd' || ch == 'D') return KEY_RIGHT;
    if (ch == 'r' || ch == 'R') return KEY_RESET;
    if (ch == 27) exit(0);
    return KEY_NONE;
}

static void render_console(const VM *vm) {
    COORD pos = {0, 0};
    SetConsoleCursorPosition(GetStdHandle(STD_OUTPUT_HANDLE), pos);
    printf("=== SOKOBAN VM (Windows) ===\n\n");
    for (int y = 0; y < SCREEN_H; y++) {
        for (int x = 0; x < SCREEN_W; x++) {
            char tile = vm->screen[y][x];
            putchar(tile ? tile : ' ');
            putchar(' ');
        }
        putchar('\n');
    }
    if (*(vm->memory + 1511) == 1) {
        printf("\nYOU WIN! Press R to restart or ESC to quit.   \n");
    } else {
        printf("\nArrows/WASD: Move | R: Reset | ESC: Quit       \n");
    }
}

int main(void) {
    VM vm;
    vm_init(&vm, sokoban_rom, sizeof(sokoban_rom));
    CONSOLE_CURSOR_INFO info = {100, FALSE};
    SetConsoleCursorInfo(GetStdHandle(STD_OUTPUT_HANDLE), &info);
    system("cls");

    while (1) {
        uint8_t key = read_input();
        vm_step_frame(&vm, key);
        render_console(&vm);
        Sleep(30);
    }
    return 0;
}
