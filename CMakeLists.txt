cmake_minimum_required(VERSION 3.10)
project(sokoban_vm C)

set(CMAKE_C_STANDARD 99)
set(CMAKE_C_STANDARD_REQUIRED ON)

add_library(vm_core STATIC core/vm.c)
target_include_directories(vm_core PUBLIC core)

if(WIN32)
    add_executable(sokoban platforms/win_console.c)
    target_link_libraries(sokoban PRIVATE vm_core)
endif()

enable_testing()
add_executable(test_vm tests/test_vm.c)
target_link_libraries(test_vm PRIVATE vm_core)
add_test(NAME vm_unit_and_fuzz_tests COMMAND test_vm)
