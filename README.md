# A Python Pascal Retro Interpreter experience

The experience is about taking the P-Code of P2 Pascal compiler and run it
through a P-Code interpreter, so it can compile Pascal source code into P-Code.

This was a personal experience to be is sort of similar situation of the time
people would bootstrap a Pascal environment on a new computer.

This was inspired and made possible by the work of [Scott A. Moore](https://github.com/samiam95124)
who [documented these early version of Pascal](https://www.standardpascaline.org/PascalP.html), provided the source files adapted to Pascal ISO 7185,
and provided a project that makes the bootstrap possible by producing the compiler P2 code.

I also consulter the original untouched sources files of both the interpreter and compiler
that [can be found here](http://pascal.hansotten.com/niklaus-wirth/px-compilers/p2-pascal-compiler/).

## Direct translation

The first experience was to translate in a rather *raw* form the Pascal Interpreter from
Pascal to Python. This is what is found in the `translation/` folder.

This gives a very not pythonic source code, but somehow faithful to the original Pascal
source code. This is now how you would write a Pascal interpreter in Python from scratch.
The experience was to port the code as is.

