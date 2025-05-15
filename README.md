# qlang
A minimal educational toy language: QLang → ARM64 assembly → native binary (Apple M1)

## Organization

```
.
├── qlang/
│   ├── __init__.py
│   ├── ast.py           # AST node definitions
│   ├── parser.py        # Recursive-descent parser
│   └── manual_codegen.py# ARM64 assembly code generator
└── examples/
    └── hello.ql         # Sample QLang program
```

## Requirements

- Apple Silicon (M1/M2)
- as (Apple assembler)
- clang (linker)
- Python 3.6+

## Usage

1. Generate ARM64 assembly:
   ```bash
   python3 qlang/manual_codegen.py examples/hello.ql > out.s
   ```

2. Assemble and link:
   ```bash
   as out.s -o out.o
   clang out.o -o out
   ```

3. Run the binary and check its exit code:
   ```bash
   ./out
   echo $?  # exit code = 5
   ```
