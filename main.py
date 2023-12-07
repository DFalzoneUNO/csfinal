#!/usr/bin/env python3
from argparse import ArgumentParser
from interpreter import Interpreter


gpl3_notice = """\
Copyright (C) 2023  Dante Falzone

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>."""


def main():
    argparser = ArgumentParser(
        prog="narrate",
        description="Interpreter for the Narrate programming language",
        epilog=gpl3_notice
    )
    argparser.add_argument("filename", help="path to the file to start in")
    argparser.add_argument(
        "-e", "--entry",
        required=False,
        help='scoped scene id to start execution in; defaults to "main"'
    )
    args = argparser.parse_args()
    interpreter = None
    try:
        interpreter = Interpreter(args.filename, args.entry or "main")
        interpreter.main_loop()
    except BaseException as e:
        filename = args.filename if interpreter is None else interpreter.src_filename
        print(f"Error in file {filename}")
        print(str(e))


if __name__ == "__main__":
    main()
