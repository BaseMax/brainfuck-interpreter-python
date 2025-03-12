#!/usr/bin/env python3
"""
#
# Name: Brainfuck Interpreter in Python
# Date: 03/12/2025
# Repository: https://github.com/BaseMax/brainfuck-interpreter-python
#
"""

import sys
import os
import argparse
from typing import List, Tuple, Optional

# -----------------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------------
VERSION_MAJOR = 1
VERSION_MINOR = 0
VERSION_PATCH = 0
TAPE_SIZE = 30000

TOKEN_PLUS      = '+'
TOKEN_MINUS     = '-'
TOKEN_NEXT      = '>'
TOKEN_PREVIOUS  = '<'
TOKEN_OUTPUT    = '.'
TOKEN_INPUT     = ','
TOKEN_LOOP_START= '['
TOKEN_LOOP_END  = ']'
TOKEN_BREAK     = '#'

# -----------------------------------------------------------------------------
# Custom Exceptions
# -----------------------------------------------------------------------------
class BrainfuckRuntimeError(Exception):
    """Exception for runtime errors in the Brainfuck interpreter."""
    pass

# -----------------------------------------------------------------------------
# Data Classes
# -----------------------------------------------------------------------------
class BrainfuckInstruction:
    """
    Represents a single Brainfuck instruction.
    For loop instructions, `loop` holds a list of instructions inside the loop.
    """
    def __init__(self, token: str, difference: int = 1,
                 loop: Optional[List['BrainfuckInstruction']] = None) -> None:
        self.token = token
        self.difference = difference
        self.loop = loop

    def __repr__(self) -> str:
        if self.token == TOKEN_LOOP_START:
            return f"Instr({self.token}, diff={self.difference}, loop={self.loop})"
        return f"Instr({self.token}, diff={self.difference})"


class BrainfuckExecutionContext:
    """
    Holds the execution context for the Brainfuck program.
    """
    def __init__(self, tape_size: int) -> None:
        self.tape = [0] * tape_size
        self.tape_index = 0
        self.tape_size = tape_size
        self.should_stop = False
        # Handlers for output and input.
        self.output_handler = lambda x: sys.stdout.write(chr(x))
        self.input_handler = brainfuck_getchar

# -----------------------------------------------------------------------------
# I/O Utility
# -----------------------------------------------------------------------------
def brainfuck_getchar() -> str:
    """
    Reads exactly one character from stdin and clears the rest of the line.
    """
    ch = sys.stdin.read(1)
    # Discard remaining characters until newline.
    while True:
        t = sys.stdin.read(1)
        if t == '\n' or t == '':
            break
    return ch

# -----------------------------------------------------------------------------
# Parsing Functions
# -----------------------------------------------------------------------------
def parse_brainfuck(code: str, index: int = 0,
                    end: Optional[int] = None) -> Tuple[List[BrainfuckInstruction], int]:
    """
    Recursively parses Brainfuck code into a list of instructions.
    Consecutive tokens (like +, -, >, <, ., or ,) are combined with a "difference" value.
    For loops, the function recurses until a matching ']' is found.
    
    Returns:
        A tuple: (list_of_instructions, new_index)
    """
    if end is None:
        end = len(code)
    instructions: List[BrainfuckInstruction] = []
    while index < end:
        c = code[index]
        index += 1
        if c not in (TOKEN_PLUS, TOKEN_MINUS, TOKEN_NEXT, TOKEN_PREVIOUS,
                     TOKEN_OUTPUT, TOKEN_INPUT, TOKEN_LOOP_START, TOKEN_LOOP_END, TOKEN_BREAK):
            continue  # Skip non-token characters
        if c == TOKEN_LOOP_START:
            loop_instructions, index = parse_brainfuck(code, index, end)
            instructions.append(BrainfuckInstruction(TOKEN_LOOP_START, 1, loop_instructions))
        elif c == TOKEN_LOOP_END:
            return instructions, index
        elif c in (TOKEN_PLUS, TOKEN_MINUS):
            diff = 1
            while index < end and code[index] in (TOKEN_PLUS, TOKEN_MINUS):
                diff = diff + 1 if code[index] == c else diff - 1
                index += 1
            instructions.append(BrainfuckInstruction(c, diff))
        elif c in (TOKEN_NEXT, TOKEN_PREVIOUS):
            diff = 1
            while index < end and code[index] in (TOKEN_NEXT, TOKEN_PREVIOUS):
                diff = diff + 1 if code[index] == c else diff - 1
                index += 1
            instructions.append(BrainfuckInstruction(c, diff))
        elif c in (TOKEN_OUTPUT, TOKEN_INPUT):
            diff = 1
            while index < end and code[index] == c:
                diff += 1
                index += 1
            instructions.append(BrainfuckInstruction(c, diff))
        elif c == TOKEN_BREAK:
            instructions.append(BrainfuckInstruction(c, 1))
    return instructions, index

def parse_string(code: str) -> List[BrainfuckInstruction]:
    """
    Parses an entire Brainfuck code string into a list of instructions.
    """
    instructions, _ = parse_brainfuck(code)
    return instructions

# -----------------------------------------------------------------------------
# Execution Functions
# -----------------------------------------------------------------------------
def execute_instruction(instr: BrainfuckInstruction,
                        context: BrainfuckExecutionContext) -> None:
    """
    Executes a single Brainfuck instruction using the given context.
    May recursively execute loops.
    """
    token = instr.token
    diff = instr.difference

    if token == TOKEN_PLUS:
        context.tape[context.tape_index] = (context.tape[context.tape_index] + diff) % 256

    elif token == TOKEN_MINUS:
        context.tape[context.tape_index] = (context.tape[context.tape_index] - diff) % 256

    elif token == TOKEN_NEXT:
        new_index = context.tape_index + diff
        if new_index >= context.tape_size:
            raise BrainfuckRuntimeError(f"Tape overrun: attempted index {new_index}, tape size is {context.tape_size}")
        context.tape_index = new_index

    elif token == TOKEN_PREVIOUS:
        new_index = context.tape_index - diff
        if new_index < 0:
            raise BrainfuckRuntimeError("Tape underrun: negative tape index")
        context.tape_index = new_index

    elif token == TOKEN_OUTPUT:
        for _ in range(diff):
            context.output_handler(context.tape[context.tape_index])
        sys.stdout.flush()

    elif token == TOKEN_INPUT:
        for _ in range(diff):
            ch = context.input_handler()
            context.tape[context.tape_index] = 0 if ch == '' else ord(ch)

    elif token == TOKEN_LOOP_START:
        while context.tape[context.tape_index] != 0:
            brainfuck_execute(instr.loop, context)

    elif token == TOKEN_BREAK:
        low = max(0, context.tape_index - 10)
        high = min(context.tape_size, low + 21)
        indices = "\t".join(str(i) for i in range(low, high))
        values = "\t".join(str(context.tape[i]) for i in range(low, high))
        pointer_line = "\t".join("^" if i == context.tape_index else " " for i in range(low, high))
        print(indices)
        print(values)
        print(pointer_line)
    else:
        pass

def brainfuck_execute(instructions: List[BrainfuckInstruction],
                      context: BrainfuckExecutionContext) -> None:
    """
    Executes a list of Brainfuck instructions using the given context.
    Each instruction is processed by execute_instruction.
    """
    for instr in instructions:
        if context.should_stop:
            break
        execute_instruction(instr, context)

# -----------------------------------------------------------------------------
# Run Modes
# -----------------------------------------------------------------------------
def run_file(filename: str) -> bool:
    """
    Reads Brainfuck code from a file and executes it.
    Returns True on success; False otherwise.
    """
    try:
        with open(filename, 'r') as f:
            code = f.read()
    except Exception as e:
        sys.stderr.write(f"error: failed to read file {filename}: {e}\n")
        return False

    try:
        instructions = parse_string(code)
    except Exception as e:
        sys.stderr.write(f"error: failed to parse code in file {filename}: {e}\n")
        return False

    context = BrainfuckExecutionContext(TAPE_SIZE)
    try:
        brainfuck_execute(instructions, context)
    except BrainfuckRuntimeError as e:
        sys.stderr.write(f"Runtime error in file {filename}: {e}\n")
        return False

    return True

def run_code(code: str) -> bool:
    """
    Runs Brainfuck code provided as a raw string.
    Returns True on success; False otherwise.
    """
    try:
        instructions = parse_string(code)
    except Exception as e:
        sys.stderr.write(f"error: failed to parse code: {e}\n")
        return False

    context = BrainfuckExecutionContext(TAPE_SIZE)
    try:
        brainfuck_execute(instructions, context)
    except BrainfuckRuntimeError as e:
        sys.stderr.write(f"Runtime error: {e}\n")
        return False

    return True

def run_interactive_console() -> None:
    """
    Runs an interactive Brainfuck console.
    """
    print(f"Brainfuck Interpreter v{VERSION_MAJOR}.{VERSION_MINOR}.{VERSION_PATCH} (Python)")
    print("Enter Brainfuck code (Ctrl-D to exit)")
    context = BrainfuckExecutionContext(TAPE_SIZE)
    while True:
        try:
            line = input(">> ")
        except EOFError:
            break
        if not line.strip():
            continue
        try:
            instructions = parse_string(line)
            brainfuck_execute(instructions, context)
        except Exception as e:
            sys.stderr.write(f"error: {e}\n")
        print()

# -----------------------------------------------------------------------------
# CLI and Main Entry Point
# -----------------------------------------------------------------------------
def print_usage(progname: str) -> None:
    sys.stderr.write(f"usage: {progname} [options] [code or file ...]\n")
    sys.stderr.write("\n")
    sys.stderr.write("If an argument ends with .bf, it is read as a file; otherwise, it is\n")
    sys.stderr.write("treated as raw Brainfuck code.\n")
    sys.stderr.write("\n")
    sys.stderr.write("Options:\n")
    sys.stderr.write("  -v, --version    show version information\n")
    sys.stderr.write("  -h, --help       show this help message\n")

def print_version() -> None:
    sys.stderr.write(f"Brainfuck Interpreter v{VERSION_MAJOR}.{VERSION_MINOR}.{VERSION_PATCH} (Python)\n")
    sys.stderr.write("Copyright (c) 2025 Max Base.\n")
    sys.stderr.write("Distributed under the MIT License.\n")

def main() -> None:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("args", nargs="*", help="Brainfuck code or file(s) to run")
    parser.add_argument("-v", "--version", action="store_true", help="show version information")
    parser.add_argument("-h", "--help", action="store_true", help="show help message")
    parsed = parser.parse_args()

    if parsed.help:
        print_usage(os.path.basename(sys.argv[0]))
        sys.exit(0)
    if parsed.version:
        print_version()
        sys.exit(0)

    if parsed.args:
        success = True
        for arg in parsed.args:
            if arg.lower().endswith(".bf"):
                if not run_file(arg):
                    sys.stderr.write(f"error: failed to run file {arg}\n")
                    success = False
            else:
                if not run_code(arg):
                    sys.stderr.write("error: failed to run code input\n")
                    success = False
        sys.exit(0 if success else 1)
    else:
        if not sys.stdin.isatty():
            code = sys.stdin.read()
            if not run_code(code):
                sys.stderr.write("error: failed to run piped code\n")
                sys.exit(1)
        else:
            run_interactive_console()

if __name__ == '__main__':
    main()
