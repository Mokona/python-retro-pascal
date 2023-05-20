# Direct python translation of `pasint.pas`

In this folder can be found a direct translation (well, as direct as I could) of
`pasint.pas` from the P2 Pascal Interpreter, into Python.

This is not pythonic Python at all. The mixture is weird. But it's working.

## Usage

Usage is crude and there's no bell nor whistles.

To use the compiler, from this folder, run
`python3 pascal_interpreter.py ../compiler/pcomp-adjusted.p2 < ../examples/hello.pas`.

It will produce a `pcomp-adjusted.out` file with the P2 result in the compiler folder.
, you can run the result with:
`python3 pascal_interpreter.py ../compiler/pcomp-adjusted.out < /dev/null`.

The interpreted expects something in the standard input to run. That's was the original
interpreted is doing too. You can use `/dev/null`, or just press `ENTER` after the
interpreter has started.

You should see a nice `HELLO, WORLD` on the standard output. 

At the beginning of the source file, you can modify three options for the compiler.
They are written in the directive format, with a letter denoting the option followed
by a plus ('+') to enable it, or a minus ('-') to disable it.

Example to activate everything: `(*$T+,L+,C+*)`

  * `T` lists the compilation tables,
  * `L` produces the listing (and will show the errors),
  * `C` produces the code output.
