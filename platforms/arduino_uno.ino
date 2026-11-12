#include "../core/vm.h"
#include "../core/vm.c"
#include "../game/rom_data.h"

VM avr_vm;

void setup() {
    Serial.begin(115200);
    vm_init(&avr_vm, sokoban_rom, sizeof(sokoban_rom));
}

void loop() {
    uint8_t key = KEY_NONE;
    if (Serial.available()) {
        char c = Serial.read();
        if (c == 'w') key = KEY_UP;
        else if (c == 's') key = KEY_DOWN;
        else if (c == 'a') key = KEY_LEFT;
        else if (c == 'd') key = KEY_RIGHT;
        else if (c == 'r') key = KEY_RESET;
    }

    vm_step_frame(&avr_vm, key);

    Serial.write(27); Serial.print("[H");
    for (int y = 0; y < SCREEN_H; y++) {
        for (int x = 0; x < SCREEN_W; x++) {
            char t = *(*(avr_vm.screen + y) + x);
            Serial.print(t ? t : ' ');
            Serial.print(' ');
        }
        Serial.println();
    }
    delay(50);
}
