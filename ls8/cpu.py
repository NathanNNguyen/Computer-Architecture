"""CPU functionality."""

import sys

LDI = 0b10000010
PRN = 0b01000111
HLT = 0b00000001
ADD = 0b10100000
MUL = 0b10100010
POP = 0b01000110
PUSH = 0b01000101
CALL = 0b01010000
RET = 0b00010001
CMP = 0b10100111
JMP = 0b01010100
JEQ = 0b01010101
JNE = 0b01010110


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        # Program Counter, address of the currently executing instruction
        self.pc = 0
        self.running = False
        self.reg[7] = 0xf4
        self.fl = 0b00000000

        self.branchtable = {
            LDI: self.LDI,
            PRN: self.PRN,
            MUL: self.MUL,
            ADD: self.ADD,
            PUSH: self.PUSH,
            POP: self.POP,
            HLT: self.HLT,
            CALL: self.CALL,
            RET: self.RET,
            CMP: self.CMP,
            JMP: self.JMP,
            JEQ: self.JEQ,
            JNE: self.JNE
        }

    # Memory Address Register (MAR) and the Memory Data Register (MDR):
    # The MAR contains the address that is being read or written to.
    # The MDR contains the data that was read or the data to write.
    def ram_read(self, MAR):
        return self.ram[MAR]

    def ram_write(self, MAR, MDR):
        self.ram[MAR] = MDR

    def load(self):
        """Load a program into memory."""

        address = 0

        if len(sys.argv) != 2:
            print('Please use one of the text in examples!')
            sys.exit(1)
        try:
            with open(sys.argv[1]) as f:
                for line in f:
                    line = line.strip()
                    temp = line.split()

                    if len(temp) == 0:
                        continue

                    elif temp[0][0] == '#':
                        continue
                    try:
                        self.ram[address] = int(temp[0], 2)
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

        # For now, we've just hardcoded a program:
        # program = [
        #     # From print8.ls8
        #     LDI,  # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     PRN,  # PRN R0
        #     0b00000000,
        #     HLT,  # HLT
        # ]

        # for instruction in program:
        #     self.ram[address] = instruction
        #     address += 1

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
            self.pc += 3
        # elif op == "SUB": etc
        elif op == 'MUL':
            self.reg[reg_a] *= self.reg[reg_b]
            self.pc += 3
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def LDI(self):
        num = self.ram_read(self.pc + 1)
        val = self.ram_read(self.pc + 2)
        self.reg[num] = val
        self.pc += 3

    def PRN(self):
        num = self.ram_read(self.pc + 1)
        print(self.reg[num])
        self.pc += 2

    def HLT(self):
        self.running = False

    def MUL(self):
        a = self.ram_read(self.pc + 1)
        b = self.ram_read(self.pc + 2)
        self.reg[a] *= self.reg[b]
        self.pc += 3
        # print(a, 'a')
        # print(b, 'b')
        # self.alu('MUL', a, b)

    def ADD(self):
        a = self.ram_read(self.pc + 1)
        b = self.ram_read(self.pc + 2)
        self.reg[a] += self.reg[b]
        self.pc += 3

    def PUSH(self):
        # Decrement stack pointer
        # print(self.reg, 'REG BEFORE')
        self.reg[7] -= 1

        # Get register value
        num = self.ram_read(self.pc + 1)
        value = self.reg[num]

        # Store it on the stack
        address = self.reg[7]
        self.ram[address] = value
        # print(self.reg, 'REG AFTER')

        self.pc += 2

    def POP(self):
        # Get value from the top of the stack
        # print(self.reg, 'POP ****** BEFORE')
        address_to_pop_from = self.reg[7]
        value = self.ram[address_to_pop_from]

        # Get the register number and store the value there
        num = self.ram_read(self.pc + 1)
        self.reg[num] = value

        # Increment the SP
        self.reg[7] += 1
        # print(self.reg, 'POP ****** AFTER')
        self.pc += 2

    def CALL(self):
        # Where RET will return to
        # we are going to add to the stack so decrement the stack pointer
        address = self.pc + 2
        self.reg[7] -= 1
        self.ram[self.reg[7]] = address
        # get address to call
        reg_num = self.ram[self.pc + 1]
        # assign the value in the register to the program counter
        self.pc = self.reg[reg_num]

    def RET(self):
        # get the return address
        address = self.ram[self.reg[7]]
        # increment the stack pointer since a value was "popped"
        self.reg[7] += 1
        # # set pc to return address
        self.pc = address

    def run(self):
        """Run the CPU."""
        self.running = True
        while self.running:
            ir = self.ram_read(self.pc)
            if ir in self.branchtable:
                # print(ir, 'ir')
                self.branchtable[ir]()
