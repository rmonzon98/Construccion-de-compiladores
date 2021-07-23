import sys
from antlr4 import *
from DecafLexer import DecafLexer
from DecafParser import DecafParser


def main(argv):
    input = FileStream(argv[1])
    lexer = DecafLexer(input)
    stream = CommonTokenStream(lexer)
    parser = DecafParser(stream)
    tree = parser.program()
    print(tree.toStringTree(recog=parser))

if __name__ == '__main__':
    main(sys.argv)