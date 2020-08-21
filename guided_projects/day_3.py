import sys

PRINT_BEEJ = 1
HALT = 2
SAVE_REG = 3
PRINT_REG = 4
PUSH = 5
POP = 6
CALL = 7
RET = 8

memory = [0] * 256   # think of as a big array of bytes, 8-bits per byte

registers = [0] * 8

SP = 7

registers[SP] = 0xf4  # Stack pointer

# Load the program file
address = 0

if len(sys.argv) != 2:
    print("usage: comp.py progname")
    sys.exit(1)

try:
    with open(sys.argv[1]) as f:
        for line in f:
            line = line.strip()
            temp = line.split()

            if len(temp) == 0:
                continue

            if temp[0][0] == '#':
                continue

            try:
                memory[address] = int(temp[0])

            except ValueError:
                print(f"Invalid number: {temp[0]}")
                sys.exit(1)

            address += 1

except FileNotFoundError:
    print(f"Couldn't open {sys.argv[1]}")
    sys.exit(2)

if address == 0:
    print("Program was empty!")
    sys.exit(3)

# print(memory[:10])
# sys.exit(0)


running = True

pc = 0   # Program Counter, the index into memory of the currently-executing instruction

while running:
    ir = memory[pc]  # Instruction Register

    if ir == PRINT_BEEJ:
        print("Beej!")
        pc += 1

    elif ir == HALT:
        running = False
        pc += 1

    elif ir == SAVE_REG:
        reg_num = memory[pc + 1]
        value = memory[pc + 2]
        registers[reg_num] = value

        pc += 3

    elif ir == PRINT_REG:
        reg_num = memory[pc + 1]
        print(registers[reg_num])

        pc += 2

    elif ir == PUSH:
        # Decrement SP
        registers[SP] -= 1

        # Get value from register
        reg_num = memory[pc + 1]
        value = registers[reg_num]  # We want to push this value

        # Store it on the stack
        top_of_stack_addr = registers[SP]
        memory[top_of_stack_addr] = value

        pc += 2

    elif ir == POP:
        # Get value from the top of the stack
        top_of_stack_addr = registers[SP]
        value = memory[top_of_stack_addr]

        # Get the register number and store the value there
        reg_num = memory[pc + 1]
        registers[reg_num] = value

        # Increment the SP
        registers[SP] += 1

        pc += 2

    elif ir == CALL:
        # Push return address
        ret_addr = pc + 2
        registers[SP] -= 1
        memory[registers[SP]] = ret_addr

        # Call the subroutine
        reg_num = memory[pc + 1]
        pc = registers[reg_num]

    elif ir == RET:
        # Pop the return addr off the stack
        ret_addr = memory[registers[SP]]
        registers[SP] += 1

        # Set the PC to it
        pc = ret_addr

    else:
        print(f"Invalid instruction {ir} at address {pc}")
        sys.exit(1)

    # This if tests to see if the instruction set the PC to some
    # arbitrary place or not (like CALL and RET do).
    # if ir & 0b00010000 == 0:
        #pc += (ir >> 6) + 1
