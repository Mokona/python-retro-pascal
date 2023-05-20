# Direct python translation of `pasint.pas`

In this folder can be found a direct translation (well, as direct as I could) of
`pasint.pas` from the P2 Pascal Interpreter, into Python.

This is not pythonic Python at all. The mixture is weird. But it's working.

## Usage

Usage is crude and there's no bell nor whistles.

To use the compiler: `python pascal_interpreter.py pcomp-adjusted.p2 < hello.pas`, where
`pcomp-adjusted.p2` is the P2 code for the compiler (found in the `compiler` folder)
and `hello.pas` a source file written in early Pascal. You can find it into the
`examples` folder.

It will produce a `pcomp-adjusted.out` file with the P2 result, that you then
run. Rename it to `hello.p2`, then: `python pascal_interpreter.py test.p2 < /dev/null`.

The interpreted expects something in the standard input to run. That's was the original
interpreted is doing too. You can use `/dev/null`, or just press `ENTER` after the
interpreter has started.

