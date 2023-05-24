import unittest

from reinterpreted.asm_labels import Labels
from reinterpreted.code import Code
from reinterpreted.store import Store
from translation import string_buffer

BEGINCODE = 3  #
MAX_LABELS = 1550

# Taken from P2, not really fitting the Python environment on a current PC
LARGEINT = 524288  # (* = 2**19 *)

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


def get_name(line):
    line = line.lstrip()
    word = line[:2]
    line = line[2:]

    if len(line):
        word += line[0]
        line = line[1:]

    return word, line


def get_label_id(line):
    l_index = line.index('L')
    line = line[l_index + 1:]
    x, _ = string_buffer.parse_integer(line)

    return x


def assemble(line, pc, store, labels: Labels):
    """TRANSLATE SYMBOLIC CODE INTO MACHINE CODE AND context.store"""
    name, line = get_name(line)

    op = instructions.index(name)
    p = 0
    q = 0

    if op in (17, 18, 19, 20, 21, 22):  # (*EQU,NEQ,GEQ,GRT,LEQ,LES*)
        p = [0, 1, 2, 3, 4, 5]['AIRBSM'.index(line[0])]
        if p == 5:
            q, _ = string_buffer.parse_integer(line[1:])
    elif op in (0, 2, 4):  # (*LOD,STR,LDA*)
        p, line = string_buffer.parse_integer(line)
        q, _ = string_buffer.parse_integer(line)
    elif op == 12:  # (*CUP*)
        p, line = string_buffer.parse_integer(line)
        label_id = get_label_id(line)
        q = labels.add_reference(label_id, pc)
    elif op == 11:  # (*MST*)
        p, _ = string_buffer.parse_integer(line)
    elif op == 14:  # (*RET*)
        p = [0, 1, 2, 3, 4, 5]['PIRCBA'.index(line[0])]
    elif op in (1, 3, 5, 9, 10, 16, 55, 57):  # (*LDO,SRO,LAO,IND,INC,IXA,MOV,DEC*)
        q, _ = string_buffer.parse_integer(line)
    elif op in (13, 23, 24, 25):  # (*ENT,UJP,FJP,XJP*)
        label_id = get_label_id(line)
        q = labels.add_reference(label_id, pc)
    elif op == 15:  # (*CSP*)
        name, _ = get_name(line)
        while sptable[q] != name:
            q += 1
    elif op == 7:  # (*LDC*)
        type_ch = line[0]
        line = line[1:]
        if type_ch == 'I':
            p = 1
            i, _ = string_buffer.parse_integer(line)
            if abs(i) > LARGEINT:
                op = 8  # Change to LCI
                q = store.add_int_constant(i)
            else:
                q = i
            pass
        elif type_ch == 'R':
            op = 8  # Change to LCI
            p = 2
            r, _ = string_buffer.parse_real(line)
            q = store.add_real_constant(r)
            pass
        elif type_ch == 'N':
            pass
        elif type_ch == 'B':
            p = 3
            q, _ = string_buffer.parse_integer(line)
        elif type_ch == '(':
            op = 8  # Change to LCI
            p = 4
            s = set()

            while type_ch != ')':
                s1, line = string_buffer.parse_integer(line)
                type_ch = line.strip()[0]

                s.add(s1)

            q = store.add_set_constant(s)
    elif op == 26:  # (*CHK*)
        lb, line = string_buffer.parse_integer(line[1:])
        ub, _ = string_buffer.parse_integer(line)

        store.add_boundary_constant((lb, ub))
    elif op == 56:  # (*LCA*)
        line = line[1:]
        data = [ord(ch) for ch in line[:line.index("'")]]
        q = store.add_multiple_constant(data)

    return op, p, q


def generate(prd, pc, store: Store, labels: Labels, code: list[Code]):
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
                labels.declare(x, label_value, code)
            elif ch == ' ':
                op, p, q = assemble(line, pc, store, labels)
                code[pc].op = op
                code[pc].p = p
                code[pc].q = q

                pc += 1

        else:
            break


def load(prd, store: Store, code):
    labels = Labels(MAX_LABELS)

    # There are two generate calls. The first is the general source code to assemble
    # starting from the BEGINCODE address. This part is ended by a blank line.
    # It is followed by another generation of the startup code to be assembled at address 0.
    generate(prd, BEGINCODE, store, labels, code)
    generate(prd, 0, store, labels, code)


class TestAssembler(unittest.TestCase):
    def test_one(self):
        pass
