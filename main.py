#!/usr/bin/env python3
import sys
from interpreter import Interpreter


def main():
    if len(sys.argv) < 2:
        print("Error: No file given to execute. Please pass a file name for the first command-line argument.")
        sys.exit(1)
    interpreter = Interpreter(sys.argv[1])
    interpreter.main_loop()


if __name__ == "__main__":
    main()
