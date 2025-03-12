# Brainfuck Interpreter in Python

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Brainfuck Interpreter in Python is a fully featured Brainfuck interpreter written in Python. This interpreter is a port and improvement over the original C version by Fabian Mastenbroek. It supports interactive mode, executing code from files, or running raw Brainfuck code passed as command-line arguments.

## Features

- **Interactive Console:** Launch an interactive session to enter Brainfuck code.
- **File Mode:** Execute Brainfuck code stored in `.bf` files.
- **Raw Code Execution:** Provide raw Brainfuck code directly on the command line.
- **Piped Input:** Execute Brainfuck code provided via standard input.
- **Error Handling:** Clear error messages for parse errors and runtime errors (e.g. tape overruns/underruns).
- **Modular Codebase:** Clean, well-documented code split into modular functions for parsing, execution, and CLI handling.

## Installation

### Requirements

- Python 3.6 or later

### Clone the Repository

```bash
git clone https://github.com/BaseMax/brainfuck-interpreter-python.git
cd brainfuck-interpreter-python
```

There is no additional installation step required; the interpreter is contained within a single Python script.

## Usage

You can run the interpreter in several ways:

### Interactive Mode

If you run the interpreter without any arguments, it will start in interactive mode:

```bash
python3 brainfuck-interpreter.py
```

Then, enter Brainfuck code at the prompt (>> ). Use Ctrl-D (or Ctrl-Z on Windows) to exit.

### Running a File

If an argument ends with .bf, the interpreter treats it as a file containing Brainfuck code:

```bash
python3 brainfuck-interpreter.py program.bf
```

### Running Raw Code

If an argument does not end with .bf, it is treated as raw Brainfuck code:

```bash
python3 brainfuck-interpreter.py "++++++++[>++++++++<-]>+.[-]<"
```

### Piped Input

You can also pipe Brainfuck code into the interpreter:

```bash
echo "+++++[>+++++<-]>." | python3 brainfuck-interpreter.py
```

## Command Line Options
- `-h, --help`

Show the help message.

- `-v, --version`

Show version information.

The interpreter automatically distinguishes between file paths (ending with .bf) and raw Brainfuck code provided as arguments.

## Contributing

Contributions are welcome! If you have ideas for improvements or bug fixes, please fork the repository and open a pull request. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Author

© 2025 Max Base (Seyyed Ali Mohammadiyeh)
