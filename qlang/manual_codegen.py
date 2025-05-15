#!/usr/bin/env python3
"""
Manual ARM64 assembly code generator for QLang AST.
"""
import sys

from parser import Parser
from ast import Program, Number, BinOp, Print

class ManualCodegen:
    def __init__(self):
        self.output = []
        self.reg_count = 1

    def emit(self, line):
        self.output.append(line)

    def new_reg(self):
        reg = self.reg_count
        self.reg_count += 1
        return reg

    def generate(self, program: Program):
        self.emit('.section __TEXT,__text')
        self.emit('.align 2')
        self.emit('.global _main')
        self.emit('_main:')
        # Prologue: save frame pointer (FP) and link register (LR)
        self.emit('    stp x29, x30, [sp, #-16]!')
        self.emit('    mov x29, sp')
        # Generate code for each statement
        for stmt in program.statements:
            self.codegen(stmt)
        # Epilogue: return 0 (if no Print statement returned earlier)
        self.emit('    mov x0, #0')
        self.emit('    ldp x29, x30, [sp], #16')
        self.emit('    ret')
        return '\n'.join(self.output)

    def codegen(self, node):
        if isinstance(node, Number):
            reg = self.new_reg()
            self.emit(f'    mov x{reg}, #{node.value}')
            return reg
        elif isinstance(node, BinOp):
            left = self.codegen(node.left)
            right = self.codegen(node.right)
            target = self.new_reg()
            op_map = {'+': 'add', '-': 'sub', '*': 'mul', '/': 'udiv'}
            instr = op_map.get(node.op)
            if instr is None:
                raise ValueError(f'Unsupported operator {node.op}')
            self.emit(f'    {instr} x{target}, x{left}, x{right}')
            return target
        elif isinstance(node, Print):
            # Compute the value, move into return register, and return
            val_reg = self.codegen(node.expr)
            self.emit(f'    mov x0, x{val_reg}')
            # Restore frame pointer and link register, then return
            self.emit('    ldp x29, x30, [sp], #16')
            self.emit('    ret')
        else:
            raise ValueError(f'Unknown node type: {type(node)}')

def main():
    if len(sys.argv) != 2:
        print(f'Usage: {sys.argv[0]} <input.ql>', file=sys.stderr)
        sys.exit(1)
    path = sys.argv[1]
    with open(path) as f:
        src = f.read()
    parser = Parser(src)
    program = parser.parse()
    cg = ManualCodegen()
    asm = cg.generate(program)
    print(asm)

if __name__ == '__main__':
    main()