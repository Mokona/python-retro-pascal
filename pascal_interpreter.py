import io
import sys
from math import sin, cos, exp, log, sqrt, atan, trunc

import streams
import string_buffer
from streams import InputStream

# INPUT is stdin
# OUTPUT is stdout
# PRD is input file
# PRR is output file

# The interpreter reads the program from PRD

# The compiler reads from stdin/INPUT
# The compiler writes the result to file/PRR
# The compiler outputs information to stdout/OUTPUT

prd_filename = "hello.p2"
prr_filename = "hello.out"

# Constants

# PCMAX: int = 13470  # (* SIZE OF STORE *)
PCMAX: int = 14000  # (* SIZE OF STORE *)
MAXSTK: int = 13650  # (* SIZE OF VARIABLE STORE *)
OVERI: int = MAXSTK + 5  # (* SIZE OF INTEGER CONSTANT TABLE = 5 *)
OVERR: int = OVERI + 5  # (* SIZE OF REAL CONSTANT TABLE = 5 *)
OVERS: int = OVERR + 70  # (* SIZE OF SET CONSTANT TABLE = 70 *)
OVERB: int = OVERS + 4  # (* SIZE OF BOUNDARY CONSTANT TABLE = 4 *)
OVERM: int = OVERB + 1300  # (* SIZE OF MULTIPLE CONSTANT TABLE = 1300 *)
MAXSTR = OVERM + 1  #
LARGEINT = 524288  # (* = 2**19 *)
BEGINCODE = 3  #
INPUTADR = 4  # (* ABSOLUTE ADDRESS *)
OUTPUTADR = 5  #
PRDADR = 6  #
PRRADR = 7  #

MAXLABEL = 1550

# Instructions
instructions = ['LOD', 'LDO', 'STR', 'SRO', 'LDA', 'LAO', 'STO', 'LDC', '...', 'IND',
                'INC', 'MST', 'CUP', 'ENT', 'RET', 'CSP', 'IXA', 'EQU', 'NEQ', 'GEQ',
                'GRT', 'LEQ', 'LES', 'UJP', 'FJP', 'XJP', 'CHK', 'EOF', 'ADI', 'ADR',
                'SBI', 'SBR', 'SGS', 'FLT', 'FLO', 'TRC', 'NGI', 'NGR', 'SQI', 'SQR',
                'ABI', 'ABR', 'NOT', 'AND', 'IOR', 'DIF', 'INT', 'UNI', 'INN', 'MOD',
                'ODD', 'MPI', 'MPR', 'DVI', 'DVR', 'MOV', 'LCA', 'DEC', 'STP']

# Standard functions are procedures
sptable = ['GET', 'PUT', 'RST', 'RLN', 'NEW',
           'WLN', 'WRS', 'ELN', 'WRI', 'WRR',
           'WRC', 'RDI', 'RDR', 'RDC', 'SIN',
           'COS', 'EXP', 'LOG', 'SQT', 'ATN',
           'SAV']


# Global variables

class Code:
    def __init__(self):
        self.op = 0
        self.p = 0
        self.q = 0


code = [Code() for _ in range(PCMAX)]
store: list[tuple] = [('UNDEF', None) for _ in range(OVERM)]  # Tuples of (Type, Value)


# Types are : INT (VI), REEL (VR), BOOL (VB), SETT (VS), ADR (VA), MARK (VM), UNDEF

class Pointers:
    def __init__(self):
        self.icp: int = MAXSTK + 1
        self.rcp: int = OVERI + 1
        self.scp: int = OVERR + 1
        self.bcp: int = OVERS + 2
        self.mcp: int = OVERB + 1


def load(prd):
    labeltab = []
    pointers = Pointers()

    def init():
        nonlocal pointers

        for i in range(pointers.icp, OVERI + 1):
            store[i] = ('INT', 0)
        for i in range(pointers.rcp, OVERR + 1):
            store[i] = ('REEL', 0.0)
        for i in range(pointers.scp, OVERS + 1):
            store[i] = ('SETT', set())
        for i in range(pointers.bcp - 1, OVERB):
            store[i] = ('INT', 0)
        for i in range(pointers.mcp, OVERM):
            store[i] = ('INT', 0)

        nonlocal labeltab
        labeltab = [(-1, 'ENTERED') for _ in range(MAXLABEL + 1)]

    def get_name(ch, line):
        word = ch
        w1, line = string_buffer.parse_char(line)
        w2, line = string_buffer.parse_char(line)
        word += w1
        word += w2

        if len(line):
            ch, line = string_buffer.parse_char(line)

        return word, line, ch

    def lookup(pc, label_id):
        value, status = labeltab[label_id]

        vq = -1

        if status == 'ENTERED':
            if value == -1:
                labeltab[label_id] = (pc, status)
                vq = -1
            else:
                vq = value
                labeltab[label_id] = (pc, status)
        elif status == 'DEFINED':
            vq = value

        return vq

    def label_search(pc, line):
        l_index = line.index('L')
        line = line[l_index + 1:]
        x, line = string_buffer.parse_integer(line)

        return '', line, lookup(pc, x)

    def assemble(ch, line, pc):
        """TRANSLATE SYMBOLIC CODE INTO MACHINE CODE AND STORE"""
        nonlocal pointers

        name, line, ch = get_name(ch, line)

        op = instructions.index(name)
        p = 0
        q = 0

        if op in (17, 18, 19, 20, 21, 22):  # (*EQU,NEQ,GEQ,GRT,LEQ,LES*)
            p = [0, 1, 2, 3, 4, 5]['AIRBSM'.index(ch)]
            if p == 5:
                q, line = string_buffer.parse_integer(ch + line)
        elif op in (0, 2, 4):  # (*LOD,STR,LDA*)
            p, line = string_buffer.parse_integer(ch + line)
            q, line = string_buffer.parse_integer(line)
        elif op == 12:  # (*CUP*)
            p, line = string_buffer.parse_integer(ch + line)
            ch, line, q = label_search(pc, line)
        elif op == 11:  # (*MST*)
            p, line = string_buffer.parse_integer(ch + line)
        elif op == 14:  # (*RET*)
            p = [0, 1, 2, 3, 4, 5]['PIRCBA'.index(ch)]
        elif op in (1, 3, 5, 9, 10, 16, 55, 57):  # (*LDO,SRO,LAO,IND,INC,IXA,MOV,DEC*)
            q, line = string_buffer.parse_integer(ch + line)
        elif op in (13, 23, 24, 25):  # (*ENT,UJP,FJP,XJP*)
            ch, line, q = label_search(pc, ch + line)
        elif op == 15:  # (*CSP*)
            name, line, ch = get_name(ch, line)
            while sptable[q] != name:
                q += 1
        elif op == 7:  # (*LDC*)
            if ch == 'I':
                p = 1
                i, line = string_buffer.parse_integer(line)
                if abs(i) > LARGEINT:
                    op = 8
                    store[pointers.icp] = ('INT', i)
                    q = MAXSTK
                    while store[q][1] != i:
                        q += 1
                    if q == pointers.icp:
                        pointers.icp += 1
                        if pointers.icp == OVERI:
                            raise RuntimeError("Integer table overflow")
                else:
                    q = i
                pass
            elif ch == 'R':
                op = 8
                p = 2
                r, line = string_buffer.parse_integer(line)
                store[pointers.rcp] = ('REEL', r)
                q = OVERI
                while store[q][1] != r:
                    q += 1
                if q == pointers.rcp:
                    pointers.rcp += 1
                    if pointers.rcp == OVERM:
                        raise RuntimeError("Real table overflow")
                pass
            elif ch == 'N':
                pass
            elif ch == 'B':
                p = 3
                q, line = string_buffer.parse_integer(line)
            elif ch == '(':
                op = 8
                p = 4
                s = set()

                while ch != ')':
                    s1, line = string_buffer.parse_integer(line)
                    ch = line.strip()[0]

                    s.add(s1)

                store[pointers.scp] = ('SET', s)
                q = OVERR
                while store[q][1] != s:
                    q += 1
                if q == pointers.scp:
                    pointers.scp += 1
                    if pointers.scp == OVERS:
                        raise RuntimeError("Set table overflow")
        elif op == 26:  # (*CHK*)
            lb, line = string_buffer.parse_integer(line)
            ub, line = string_buffer.parse_integer(line)

            store[pointers.bcp - 1] = ('INT', lb)
            store[pointers.bcp] = ('INT', ub)
            q = OVERS
            while store[q - 1][1] != lb or store[q][1] != ub:
                q += 2
            if q == pointers.bcp:
                pointers.bcp += 2
                if pointers.bcp == OVERB:
                    raise RuntimeError("Boundary table overflow")
        elif op == 56:  # (*LCA*)
            ch, line = string_buffer.parse_char(line)
            q = pointers.mcp
            while ch != "'":
                store[pointers.mcp] = ('INT', ord(ch))
                pointers.mcp += 1
                ch = line[0]
                line = line[1:]

        code[pc].op = op
        code[pc].p = p
        code[pc].q = q

        pc += 1

        return pc

    def update(label_id, label_value):
        nonlocal labeltab

        value, status = labeltab[label_id]
        if status == 'DEFINED':
            print("Duplicated label")
        else:
            if value != -1:  # Forward reference
                current, _ = labeltab[label_id]
                end_list = False
                while not end_list:
                    c = code[current]
                    successor = c.q
                    c.q = label_value
                    if successor == -1:
                        end_list = True
                    else:
                        current = successor

            labeltab[label_id] = (label_value, 'DEFINED')

    def generate(pc):
        nonlocal prd
        while line := prd.readline():
            if len(line.strip()) > 0:
                ch = line[0]
                line = line[1:]
                if ch == 'I':
                    pass  # Ignored
                elif ch == 'L':
                    x, line = string_buffer.parse_integer(line)
                    if line:
                        ch, line = string_buffer.parse_char(line)
                    if ch == '=':
                        label_value, line = string_buffer.parse_integer(line)
                    else:
                        label_value = pc
                    update(x, label_value)
                elif ch == ' ':
                    ch, line = string_buffer.parse_char(line)
                    pc = assemble(ch, line, pc)
            else:
                break

    init()
    generate(BEGINCODE)
    generate(0)  # Inserting start of code (which is at the end of assembly code, after a blank line)


def base(registers, ld):
    ad = registers.mp
    while ld > 0:
        _, mark_value = store[ad + 1]
        ad = mark_value
        ld -= 1
    return ad


def push(registers):
    registers.sp += 1
    if registers.sp > registers.np:
        raise RuntimeError("Store Overflow")


def get_stream(registers, stream_id) -> streams.InputStream | io.IOBase:
    return registers.files[stream_id - INPUTADR]


def getfile(registers):
    _, file_id = store[registers.sp]
    _, position = store[file_id]

    value = get_stream(registers, file_id).read()
    store[file_id] = ('INT', value)
    registers.sp -= 1


def putfile(registers):
    _, file_id = store[registers.sp]
    _, value = store[file_id]
    get_stream(registers, file_id).write(str([value]))
    store[file_id] = ('UNDEF', 0)
    registers.sp -= 1


def readline(registers):
    _, file_id = store[registers.sp]
    stream = get_stream(registers, file_id)
    stream.read_line()
    value = stream.read()
    store[INPUTADR] = ('INT', value)
    registers.sp -= 1


def writeline(registers):
    _, file_id = store[registers.sp]
    stream = get_stream(registers, file_id)
    stream.writelines(["\n"])
    registers.sp -= 1


def eoln(registers):
    _, file_id = store[registers.sp]
    stream = get_stream(registers, file_id)
    result = stream.eol()
    store[registers.sp] = ('BOOL', result)


def writestr(registers: "Registers"):
    _, file_id = store[registers.sp]
    stream = get_stream(registers, file_id)

    _, ad = store[registers.sp - 3]
    _, k = store[registers.sp - 1]
    _, j = store[registers.sp - 2]

    if k > j:
        for i in range(k - j):
            stream.write(' ')
    else:
        j = k

    for i in range(j):
        _, v = store[ad + i]
        stream.write(chr(v))

    registers.sp -= 4


def write_to_file(registers, q):
    _, file_id = store[registers.sp]
    t, v1 = store[registers.sp - 2]
    _, v2 = store[registers.sp - 1]

    stream = get_stream(registers, file_id)
    if q == 10 and t != 'CHAR':
        v1 = chr(v1)
    stream.write(f"{v1:>{v2}}")

    registers.sp -= 3


def read_byte(registers, q):
    _, file_id = store[registers.sp]
    _, store_addr = store[registers.sp - 1]

    stream = get_stream(registers, file_id)

    t = ['INT', 'REEL', 'INT'][q - 11]  # 11 is RDI opcode number / RDC reads byte as INTs
    value = stream.read()
    if q == 13 and value != 0:
        value = ord(value)
    store[store_addr] = (t, value)

    registers.sp -= 2


def file_eof(registers):
    _, file_id = store[registers.sp]
    stream = get_stream(registers, file_id)
    store[registers.sp] = ('BOOL', stream.eof())


def call_sp(q, registers: "Registers"):
    if q == 0:  # (*GET*)
        getfile(registers)
    elif q == 1:  # (*PUT*)
        putfile(registers)
    elif q == 2:  # (*RST*)
        _, value = store[registers.sp]
        registers.np = value
        registers.sp -= 1
    elif q == 3:  # (*RLN*)
        readline(registers)
    elif q == 4:  # (*NEW*)
        _, adr = store[registers.sp]
        ad = registers.np - adr
        if ad <= registers.sp:
            raise RuntimeError("Store Overflow")
        for i in range(registers.np - 1, ad, -1):
            store[i] = ('UNDEF', 0)
        registers.np = ad
        _, ad = store[registers.sp - 1]
        store[ad] = ('ADR', registers.np)
        registers.sp -= 2
    elif q == 5:  # (*WLN*)
        writeline(registers)
    elif q == 6:  # (*WRS*)
        writestr(registers)
        registers.sp -= 1
    elif q == 7:  # (*ELN*)
        eoln(registers)
    elif q in (8, 9, 10):  # (*WRI*) (*WRR*) (*WRC*)
        write_to_file(registers, q)
    elif q in (11, 12, 13):  # (*RDI*) (*RDR*) (*RDC*)
        read_byte(registers, q)
    elif q == 14:  # (*SIN*)
        _, v = store[registers.sp]
        store[registers.sp] = ('REEL', sin(v))
    elif q == 15:  # (*COS*)
        _, v = store[registers.sp]
        store[registers.sp] = ('REEL', cos(v))
    elif q == 16:  # (*EXP*)
        _, v = store[registers.sp]
        store[registers.sp] = ('REEL', exp(v))
    elif q == 17:  # (*LOG*)
        _, v = store[registers.sp]
        store[registers.sp] = ('REEL', log(v))
    elif q == 18:  # (*SQT*)
        _, v = store[registers.sp]
        store[registers.sp] = ('REEL', sqrt(v))
    elif q == 19:  # (*ATN*)
        _, v = store[registers.sp]
        store[registers.sp] = ('REEL', atan(v))
    elif q == 20:  # (*SAV*)
        _, addr = store[registers.sp]
        store[addr] = ('ADR', registers.np)
        registers.sp -= 1


def ex0(op, p, q, registers):
    if op == 0:  # (*LOD*)
        ad = base(registers, p) + q
        t, v = store[ad]
        if t == 'UNDEF':
            raise RuntimeError("Value Undefined")
        push(registers)
        store[registers.sp] = store[ad]
    elif op == 1:  # (*LDO*)
        t, v = store[q]
        if t == 'UNDEF':
            raise RuntimeError("Value Undefined")
        push(registers)
        store[registers.sp] = t, v
    elif op == 2:  # (*STR*)
        t, v = store[registers.sp]
        store[base(registers, p) + q] = t, v
        registers.sp -= 1
    elif op == 3:  # (*SRO*)
        t, v = store[registers.sp]
        store[q] = t, v
        registers.sp -= 1
    elif op == 4:  # (*LDA*)
        push(registers)
        store[registers.sp] = ('ADR', base(registers, p) + q)
    elif op == 5:  # (*LAO*)
        push(registers)
        store[registers.sp] = ('ADR', q)
    elif op == 6:  # (*STO*)
        _, adr = store[registers.sp - 1]
        store[adr] = store[registers.sp]
        registers.sp -= 2
    elif op == 7:  # (*LDC*)
        push(registers)
        if p == 1:
            store[registers.sp] = ('INT', q)
        elif p == 3:
            store[registers.sp] = ('BOOL', q == 1)
        else:
            store[registers.sp] = ('ADR', MAXSTR)
    elif op == 8:  # (*LCI*)
        push(registers)
        store[registers.sp] = store[q]
    elif op == 9:  # (*IND*)
        _, adr = store[registers.sp]
        adr += q
        t, value = store[adr]
        if t == 'UNDEF':
            raise RuntimeError("Value Undefined")
        store[registers.sp] = (t, value)
    elif op == 10:  # (*INC*)
        t, v = store[registers.sp]
        store[registers.sp] = (t, v + q)
    elif op == 11:  # (*MST*)
        # (*P=LEVEL OF CALLING PROCEDURE MINUS LEVEL OF CALLED PROCEDURE + 1;  SET DL AND SL, INCREMENT SP*)
        store[registers.sp + 1] = ('UNDEF', 0)
        store[registers.sp + 2] = ('MARK', base(registers, p))
        store[registers.sp + 3] = ('MARK', registers.mp)
        store[registers.sp + 4] = ('UNDEF', 0)
        registers.sp += 4
    elif op == 12:  # (*CUP*)
        # (*P=NO OF LOCATIONS FOR PARAMETERS, Q=ENTRY POINT*)
        registers.mp = registers.sp - (p + 3)
        store[registers.mp + 3] = ('MARK', registers.pc)
        registers.pc = q
    elif op == 13:  # (*ENT*)
        j = registers.mp + q
        if j > registers.np:
            raise RuntimeError("Store overflow")
        if registers.sp < INPUTADR:
            registers.sp = PRDADR
        for i in range(registers.sp + 1, j + 1):
            store[i] = ('UNDEF', 0)
        registers.sp = j
    elif op == 14:  # (*RET*)
        if p == 0:
            registers.sp = registers.mp - 1
        else:
            registers.sp = registers.mp
        _, pc = store[registers.mp + 3]
        _, mp = store[registers.mp + 2]
        registers.pc = pc
        registers.mp = mp
    elif op == 15:  # (*CSP*)
        call_sp(q, registers)

    return True


def compare(registers, q):
    _, adr1 = store[registers.sp + 1]
    _, adr2 = store[registers.sp]
    i = 0
    b = True
    while b and i != q:
        _, v1 = store[adr1 + i]
        _, v2 = store[adr2 + i]
        if v1 == v2:
            i += 1
        else:
            b = False
    return b, (adr1 + i, adr2 + i)


def ex1(op, p, q, registers):
    if op == 16:  # (*IXA*)
        registers.sp -= 1
        _, adr1 = store[registers.sp + 1]
        _, adr2 = store[registers.sp]
        store[registers.sp] = ('ADR', q * adr1 + adr2)
    if op == 17:  # (*EQU*)
        registers.sp -= 1
        if p in (0, 1, 2, 3, 4):
            _, v1 = store[registers.sp]
            _, v2 = store[registers.sp + 1]
            store[registers.sp] = ('BOOL', v1 == v2)
        elif p == 5:
            b, _ = compare(registers, q)
            store[registers.sp] = ('BOOL', b)
    if op == 18:  # (*NEQ*)
        registers.sp -= 1
        if p in (0, 1, 2, 3, 4):
            _, v1 = store[registers.sp]
            _, v2 = store[registers.sp + 1]
            store[registers.sp] = ('BOOL', v1 != v2)
        elif p == 5:
            b, _ = compare(registers, q)
            store[registers.sp] = ('BOOL', not b)
    if op == 19:  # (*GEQ*)
        registers.sp -= 1
        if p in (0, 1, 2, 3, 4):
            _, v1 = store[registers.sp]
            _, v2 = store[registers.sp + 1]
            store[registers.sp] = ('BOOL', v1 >= v2)
        elif p == 5:
            b, (i1, i2) = compare(registers, q)
            _, v1 = store[i1]
            _, v2 = store[i2]
            store[registers.sp] = ('BOOL', v1 >= v2 or b)
    if op == 20:  # (*GRT*)
        registers.sp -= 1
        if p in (0, 1, 2, 3, 4):
            _, v1 = store[registers.sp]
            _, v2 = store[registers.sp + 1]
            store[registers.sp] = ('BOOL', v1 > v2)
        elif p == 5:
            b, (i1, i2) = compare(registers, q)
            _, v1 = store[i1]
            _, v2 = store[i2]
            store[registers.sp] = ('BOOL', v1 > v2 and not b)
    if op == 21:  # (*LEQ*)
        registers.sp -= 1
        if p in (0, 1, 2, 3, 4):
            _, v1 = store[registers.sp]
            _, v2 = store[registers.sp + 1]
            store[registers.sp] = ('BOOL', v1 <= v2)
        elif p == 5:
            b, (i1, i2) = compare(registers, q)
            _, v1 = store[i1]
            _, v2 = store[i2]
            store[registers.sp] = ('BOOL', v1 <= v2 or b)
    if op == 22:  # (*LES*)
        registers.sp -= 1
        if p in (0, 1, 2, 3, 4):
            _, v1 = store[registers.sp]
            _, v2 = store[registers.sp + 1]
            store[registers.sp] = ('BOOL', v1 < v2)
        elif p == 5:
            b, (i1, i2) = compare(registers, q)
            _, v1 = store[i1]
            _, v2 = store[i2]
            store[registers.sp] = ('BOOL', v1 < v2 and not b)
    if op == 23:  # (*UJP*)
        registers.pc = q
    if op == 24:  # (*FJP*)
        _, b = store[registers.sp]
        if not b:
            registers.pc = q
        registers.sp -= 1
    if op == 25:  # (*XJP*)
        _, v = store[registers.sp]
        registers.pc = v + q
        registers.sp -= 1
    if op == 26:  # (*CHK*)
        _, v1 = store[registers.sp]
        _, v2 = store[q - 1]
        _, v3 = store[q]
        if v1 < v2 or v1 > v3:
            raise RuntimeError("Value out of range")
    if op == 27:  # (*EOF*)
        file_eof(registers)
    if op == 28:  # (*ADI*)
        registers.sp -= 1
        _, v1 = store[registers.sp]
        _, v2 = store[registers.sp + 1]
        store[registers.sp] = ('INT', v1 + v2)
    if op == 29:  # (*ADR*)
        registers.sp -= 1
        _, v1 = store[registers.sp]
        _, v2 = store[registers.sp + 1]
        store[registers.sp] = ('REEL', v1 + v2)
    if op == 30:  # (*SBI*)
        registers.sp -= 1
        _, v1 = store[registers.sp]
        _, v2 = store[registers.sp + 1]
        store[registers.sp] = ('INT', v1 - v2)
    if op == 31:  # (*SBR*)
        registers.sp -= 1
        _, v1 = store[registers.sp]
        _, v2 = store[registers.sp + 1]
        store[registers.sp] = ('REEL', v1 - v2)

    return True


def ex2(op, p, q, registers):
    if op == 32:  # (*SGS*)
        _, v = store[registers.sp]
        store[registers.sp] = ('SETT', v)
    if op == 33:  # (*FLT*)
        _, v = store[registers.sp]
        store[registers.sp] = ('REEL', v)
    if op == 34:  # (*FLO*)
        _, v = store[registers.sp - 1]
        store[registers.sp - 1] = ('REEL', v)
    if op == 35:  # (*TRC*)
        _, v = store[registers.sp]
        store[registers.sp] = ('INT', int(trunc(v)))
    if op == 36:  # (*NGI*)
        _, v = store[registers.sp]
        store[registers.sp] = ('INT', -v)
    if op == 37:  # (*NGR*)
        _, v = store[registers.sp]
        store[registers.sp] = ('REEL', -v)
    if op == 38:  # (*SQI*)
        _, v = store[registers.sp]
        store[registers.sp] = ('INT', v * v)
    if op == 39:  # (*SQR*)
        _, v = store[registers.sp]
        store[registers.sp] = ('REEL', v * v)
    if op == 40:  # (*ABI*)
        _, v = store[registers.sp]
        store[registers.sp] = ('INT', abs(v))
    if op == 41:  # (*ABR*)
        _, v = store[registers.sp]
        store[registers.sp] = ('REEL', abs(v))
    if op == 42:  # (*NOT*)
        _, v = store[registers.sp]
        store[registers.sp] = ('BOOL', not v)
    if op == 43:  # (*AND*)
        registers.sp -= 1
        _, v1 = store[registers.sp]
        _, v2 = store[registers.sp + 1]
        store[registers.sp] = ('BOOL', v1 and v2)
    if op == 44:  # (*IOR*)
        registers.sp -= 1
        _, v1 = store[registers.sp]
        _, v2 = store[registers.sp + 1]
        store[registers.sp] = ('BOOL', v1 or v2)
    if op == 45:  # (*DIF*)
        registers.sp -= 1
        _, v1 = store[registers.sp]
        _, v2 = store[registers.sp + 1]
        store[registers.sp] = ('SETT', v1.difference(v2))
    if op == 46:  # (*INT*)
        registers.sp -= 1
        _, v1 = store[registers.sp]
        _, v2 = store[registers.sp + 1]
        store[registers.sp] = ('BOOL', v1.intersection(v2))
    if op == 47:  # (*UNI*)
        registers.sp -= 1
        _, v1 = store[registers.sp]
        _, v2 = store[registers.sp + 1]
        store[registers.sp] = ('BOOL', v1.union(v2))

    return True


def ex3(op, p, q, registers):
    if op == 48:  # (*INN*)
        registers.sp -= 1
        _, int_value = store[registers.sp]
        _, set_value = store[registers.sp + 1]
        store[registers.sp] = ('BOOL', int_value in set_value)
    elif op == 49:  # (*MOD*)
        registers.sp -= 1
        _, a_value = store[registers.sp]
        _, b_value = store[registers.sp + 1]
        store[registers.sp] = ('INT', a_value % b_value)
    elif op == 50:  # (*ODD*)
        _, a_value = store[registers.sp]
        store[registers.sp] = ('BOOL', (a_value % 2) > 0)
    elif op == 51:  # (*MPI*)
        registers.sp -= 1
        _, a_value = store[registers.sp]
        _, b_value = store[registers.sp + 1]
        store[registers.sp] = ('INT', a_value * b_value)
    elif op == 52:  # (*MPR*)
        registers.sp -= 1
        _, a_value = store[registers.sp]
        _, b_value = store[registers.sp + 1]
        store[registers.sp] = ('REEL', a_value * b_value)
    elif op == 53:  # (*DVI*)
        registers.sp -= 1
        _, a_value = store[registers.sp]
        _, b_value = store[registers.sp + 1]
        store[registers.sp] = ('INT', a_value // b_value)
    elif op == 54:  # (*DVR*)
        registers.sp -= 1
        _, a_value = store[registers.sp]
        _, b_value = store[registers.sp + 1]
        store[registers.sp] = ('REEL', a_value / b_value)
    elif op == 55:  # (*MOV*)
        _, i1_value = store[registers.sp - 1]
        _, i2_value = store[registers.sp]
        registers.sp -= 2
        for i in range(q):
            store[i1_value + i] = store[i2_value + i]
    elif op == 56:  # (*LCA*)
        registers.sp += 1
        if registers.sp >= registers.np:
            raise RuntimeError("Store overflow")
        store[registers.sp] = ('ADR', q)
    elif op == 57:  # (*DEC*)
        _, value = store[registers.sp]
        store[registers.sp] = ('INT', value - q)
    if op == 58:  # (*STP*)
        return False

    return True


class Registers:
    def __init__(self, input_stream, output_stream, input_file, output_file):
        self.pc = 0
        self.mp = 0  # Beginning of Data segment
        self.sp = -1  # Top of Stack
        self.np = MAXSTK + 1  # Dynamically allocated Area

        self.files = [input_stream, output_stream, input_file, output_file]


def interpret(input_stream, output_stream, input_file, output_file):
    registers = Registers(input_stream, output_stream, input_file, output_file)

    store[INPUTADR] = ('INT', 0)
    store[PRDADR] = ('INT', 0)
    store[OUTPUTADR] = ('UNDEF', 0)
    store[PRRADR] = ('UNDEF', 0)

    interpreting = True
    while interpreting:
        c = code[registers.pc]
        op = c.op
        p = c.p
        q = c.q

        registers.pc += 1

        split_op = op // 16

        if split_op == 0:
            interpreting = ex0(op, p, q, registers)
        elif split_op == 1:
            interpreting = ex1(op, p, q, registers)
        elif split_op == 2:
            interpreting = ex2(op, p, q, registers)
        else:
            interpreting = ex3(op, p, q, registers)


def main():
    with open(prd_filename) as prd:
        load(prd)
        with open(prr_filename, "w") as prr:
            input_stream = InputStream(4, sys.stdin)
            interpret(input_stream, sys.stdout, prd, prr)


if __name__ == '__main__':
    main()
