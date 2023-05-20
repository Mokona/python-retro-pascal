# Source P2 compiler

This is the source code of the P2 compiler adjusted to run on the Python Interpreter.
This is a mixture a needed fixes taken from [Scott A. Moore](https://github.com/samiam95124)'s
adaptation for ISO 7185 conversion and a couple of fixes upon.

I didn't take the ISO 7185 adaptations that were not fixing bugs per se, but abiding
to the standard only.

The Python interpreter is not yet capable of running the compiler to compile itself.
The bootstrap is done with P2 code generation from the
[code provided by Scott A. Moore](https://github.com/samiam95124/Pascal-P2). The
resulting P2 code is provided here for ease of use.
