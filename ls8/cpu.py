"""CPU functionality."""

import sys

LDI = 0b10000010
PRN = 0b01000111
HLT = 0b00000001


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        # Program Counter, address of the currently executing instruction
        self.pc = 0
        self.running = False

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

        # For now, we've just hardcoded a program:

        program = [
            # From print8.ls8
            LDI,  # LDI R0,8
            0b00000000,
            0b00001000,
            PRN,  # PRN R0
            0b00000000,
            HLT,  # HLT
        ]

        for instruction in program:
            self.ram[address] = instruction
            address += 1

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        # elif op == "SUB": etc
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

    def HLT(self):
        self.running = False

    def run(self):
        """Run the CPU."""
        self.running = True
        while self.running:
            for ir in self.ram:
                if ir == LDI:
                    self.LDI()
                elif ir == PRN:
                    self.PRN()
                elif ir == HLT:
                    self.HLT()
