from os.path import splitext

from reinterpreted.assembler import load
from reinterpreted.code import Code
from reinterpreted.interpreter import interpret
from reinterpreted.store import Store, StoreConfiguration
from translation import streams

"""This is a P-Code Interpreter at P2 level.

The intent is to have a Pythonic version of PasInt.
"""

PCMAX: int = 15000  # (* SIZE OF context.store. *)


def main():
    import sys
    prd_filename = sys.argv[1]
    base_filename, _ = splitext(prd_filename)
    prr_filename = base_filename + ".out"

    store = Store(StoreConfiguration())
    code = [Code() for _ in range(PCMAX)]

    with open(prd_filename) as prd:
        load(prd, store, code)
        with open(prr_filename, "w") as prr:
            input_stream = streams.InputStream(4, sys.stdin)
            interpret(input_stream, sys.stdout, prd, prr, code, store)


if __name__ == '__main__':
    main()
