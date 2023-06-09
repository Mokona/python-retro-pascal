import io
from math import sin, cos, exp, log, sqrt, atan, trunc

from reinterpreted.int_context import Context
from translation import streams

INPUTADR = 4  # (* ABSOLUTE ADDRESS *)
OUTPUTADR = 5  #
PRDADR = 6  #
PRRADR = 7  #


def base(context, ld):
    ad = context.mp
    while ld > 0:
        ad = context.store.get_value(ad + 1)  # Read static link
        ld -= 1
    return ad


def get_stream(context, stream_id) -> streams.InputStream | io.IOBase:
    return context.files[stream_id - INPUTADR]


def file_get(context):
    _, file_id = context.pop()
    if file_id in (OUTPUTADR, PRRADR):
        raise RuntimeError("Get on Output. Error")

    value = get_stream(context, file_id).read()
    context.store[file_id] = ('INT', value)


def file_put(context):
    _, file_id = context.pop()
    if file_id in (INPUTADR, PRDADR):
        raise RuntimeError("Put on Input. Error")

    value = context.store.get_value(file_id)
    get_stream(context, file_id).write(str([value]))
    context.store[file_id] = ('UNDEF', 0)


def read_line(context):
    _, file_id = context.pop()
    stream = get_stream(context, file_id)
    stream.read_line()
    value = stream.read()
    context.store[INPUTADR] = ('INT', value)


def write_line(context):
    _, file_id = context.pop()
    stream = get_stream(context, file_id)
    stream.writelines(["\n"])


def eoln(context):
    file_id = context.store.get_value(context.sp)
    stream = get_stream(context, file_id)
    result = stream.eol()
    context.store[context.sp] = ('BOOL', result)


def write_string(context: Context):
    file_id = context.store.get_value(context.sp)
    stream = get_stream(context, file_id)

    address = context.store.get_value(context.sp - 3)
    k = context.store.get_value(context.sp - 1)
    j = context.store.get_value(context.sp - 2)

    k, j = j, k  # I'm not sure why these two values seem inverted compared to original
    # If not inverted, this makes no sense. Or is it because another bug?

    if k > j:
        for i in range(k - j):
            stream.write(' ')
    else:
        j = k

    for i in range(j):
        v = context.store.get_value(address + i)
        stream.write(chr(v))

    context.sp -= 4


def write_to_file(context, q):
    file_id = context.store.get_value(context.sp)
    t, v1 = context.store[context.sp - 2]
    v2 = context.store.get_value(context.sp - 1)

    stream = get_stream(context, file_id)
    if q == 10 and t != 'CHAR':  # Is this really a valid type?
        v1 = chr(v1)
    stream.write(f"{v1:>{v2}}")

    context.sp -= 3


def read_byte(context, q):
    file_id = context.store.get_value(context.sp)
    store_addr = context.store.get_value(context.sp - 1)

    stream = get_stream(context, file_id)

    t = ['INT', 'REEL', 'INT'][q - 11]  # 11 is RDI opcode number / RDC reads byte as INTs
    value = stream.read()
    if q == 13 and value != 0:
        value = ord(value)
    if value == 10:
        value = 13
    context.store[store_addr] = (t, value)

    context.sp -= 2


def file_eof(context):
    file_id = context.store.get_value(context.sp)
    stream = get_stream(context, file_id)
    context.store[context.sp] = ('BOOL', stream.eof())


def call_sp(q, context: Context):
    if q == 0:  # (*GET*)
        file_get(context)
    elif q == 1:  # (*PUT*)
        file_put(context)
    elif q == 2:  # (*RST*)
        _, value = context.pop()
        context.np = value
    elif q == 3:  # (*RLN*)
        read_line(context)
    elif q == 4:  # (*NEW*)
        adr = context.store.get_value(context.sp)
        ad = context.np - adr
        if ad <= context.sp:
            raise RuntimeError("Store Overflow")
        for i in range(context.np - 1, ad, -1):
            context.store[i] = ('UNDEF', 0)
        context.np = ad
        ad = context.store.get_value(context.sp - 1)
        context.store[ad] = ('ADR', context.np)
        context.sp -= 2
    elif q == 5:  # (*WLN*)
        write_line(context)
    elif q == 6:  # (*WRS*)
        write_string(context)
    elif q == 7:  # (*ELN*)
        eoln(context)
    elif q in (8, 9, 10):  # (*WRI*) (*WRR*) (*WRC*)
        write_to_file(context, q)
    elif q in (11, 12, 13):  # (*RDI*) (*RDR*) (*RDC*)
        read_byte(context, q)
    elif q == 14:  # (*SIN*)
        v = context.store.get_value(context.sp)
        context.store[context.sp] = ('REEL', sin(v))
    elif q == 15:  # (*COS*)
        v = context.store.get_value(context.sp)
        context.store[context.sp] = ('REEL', cos(v))
    elif q == 16:  # (*EXP*)
        v = context.store.get_value(context.sp)
        context.store[context.sp] = ('REEL', exp(v))
    elif q == 17:  # (*LOG*)
        v = context.store.get_value(context.sp)
        context.store[context.sp] = ('REEL', log(v))
    elif q == 18:  # (*SQT*)
        v = context.store.get_value(context.sp)
        context.store[context.sp] = ('REEL', sqrt(v))
    elif q == 19:  # (*ATN*)
        v = context.store.get_value(context.sp)
        context.store[context.sp] = ('REEL', atan(v))
    elif q == 20:  # (*SAV*)
        t, addr = context.pop()
        assert (t == 'ADR')
        context.store[addr] = ('ADR', context.np)


def ex0(op, p, q, context):
    if op == 0:  # (*LOD*)
        ad = base(context, p) + q
        t, v = context.store[ad]
        if t == 'UNDEF':
            raise RuntimeError("Value Undefined")
        context.push((t, v))
    elif op == 1:  # (*LDO*)
        t, v = context.store[q]
        if t == 'UNDEF':
            raise RuntimeError("Value Undefined")
        context.push((t, v))
    elif op == 2:  # (*STR*)
        context.store[base(context, p) + q] = context.pop()
    elif op == 3:  # (*SRO*)
        context.store[q] = context.pop()
    elif op == 4:  # (*LDA*)
        context.push(('ADR', base(context, p) + q))
    elif op == 5:  # (*LAO*)
        context.push(('ADR', q))
    elif op == 6:  # (*STO*)
        t, adr = context.store[context.sp - 1]
        assert (t == 'ADR')
        context.store[adr] = context.store[context.sp]
        context.sp -= 2
    elif op == 7:  # (*LDC*)
        if p == 1:
            typed_value = ('INT', q)
        elif p == 3:
            typed_value = ('BOOL', q == 1)
        else:
            typed_value = ('ADR', context.store.highest_address)
        context.push(typed_value)
    elif op == 8:  # (*LCI*)
        context.push(context.store[q])
    elif op == 9:  # (*IND*)
        adr = context.store.get_value(context.sp)
        adr += q
        t, value = context.store[adr]
        if t == 'UNDEF':
            raise RuntimeError("Value Undefined")
        context.store[context.sp] = (t, value)
    elif op == 10:  # (*INC*)
        t, v = context.store[context.sp]
        context.store[context.sp] = (t, v + q)
    elif op == 11:  # (*MST*)
        # (*P=LEVEL OF CALLING PROCEDURE MINUS LEVEL OF CALLED PROCEDURE + 1;  SET DL AND SL, INCREMENT SP*)
        context.store[context.sp + 1] = ('UNDEF', 0)  # For return value
        context.store[context.sp + 2] = ('MARK', base(context, p))  # For static link
        context.store[context.sp + 3] = ('MARK', context.mp)  # For dynamic link
        context.store[context.sp + 4] = ('UNDEF', 0)  # For previous EP
        context.sp += 4
    elif op == 12:  # (*CUP*)
        # (*P=NO OF LOCATIONS FOR PARAMETERS, Q=ENTRY POINT*)
        context.mp = context.sp - (p + 3)
        context.store[context.mp + 3] = ('MARK', context.pc)  # Return address
        context.pc = q
    elif op == 13:  # (*ENT*)
        j = context.mp + q
        if j > context.np:
            raise RuntimeError("Store overflow")
        if context.sp < INPUTADR:
            context.sp = PRDADR
        for i in range(context.sp + 1, j + 1):
            context.store[i] = ('UNDEF', 0)
        context.sp = j
    elif op == 14:  # (*RET*)
        if p == 0:
            context.sp = context.mp - 1
        else:
            context.sp = context.mp
        pc = context.store.get_value(context.mp + 3)
        mp = context.store.get_value(context.mp + 2)
        context.pc = pc
        context.mp = mp
    elif op == 15:  # (*CSP*)
        call_sp(q, context)


def compare(context, q):
    adr1 = context.store.get_value(context.sp)
    adr2 = context.store.get_value(context.sp + 1)
    i = 0
    b = True
    while b and i != q:
        v1 = context.store.get_value(adr1 + i)
        v2 = context.store.get_value(adr2 + i)
        if v1 == v2:
            i += 1
        else:
            b = False
    return b, (adr1 + i, adr2 + i)


def ex1(op, p, q, context):
    if op == 16:  # (*IXA*)
        context.sp -= 1
        adr1 = context.store.get_value(context.sp + 1)
        adr2 = context.store.get_value(context.sp)
        context.store[context.sp] = ('ADR', q * adr1 + adr2)
    if op == 17:  # (*EQU*)
        context.sp -= 1
        if p in (0, 1, 2, 3, 4):
            v1 = context.store.get_value(context.sp)
            v2 = context.store.get_value(context.sp + 1)
            context.store[context.sp] = ('BOOL', v1 == v2)
        elif p == 5:
            b, _ = compare(context, q)
            context.store[context.sp] = ('BOOL', b)
    if op == 18:  # (*NEQ*)
        context.sp -= 1
        if p in (0, 1, 2, 3, 4):
            v1 = context.store.get_value(context.sp)
            v2 = context.store.get_value(context.sp + 1)
            context.store[context.sp] = ('BOOL', v1 != v2)
        elif p == 5:
            b, _ = compare(context, q)
            context.store[context.sp] = ('BOOL', not b)
    if op == 19:  # (*GEQ*)
        context.sp -= 1
        if p in (0, 1, 2, 3, 4):
            v1 = context.store.get_value(context.sp)
            v2 = context.store.get_value(context.sp + 1)
            context.store[context.sp] = ('BOOL', v1 >= v2)
        elif p == 5:
            b, (i1, i2) = compare(context, q)
            v1 = context.store.get_value(i1)
            v2 = context.store.get_value(i2)
            context.store[context.sp] = ('BOOL', v1 >= v2 or b)
    if op == 20:  # (*GRT*)
        context.sp -= 1
        if p in (0, 1, 2, 3, 4):
            v1 = context.store.get_value(context.sp)
            v2 = context.store.get_value(context.sp + 1)
            context.store[context.sp] = ('BOOL', v1 > v2)
        elif p == 5:
            b, (i1, i2) = compare(context, q)
            v1 = context.store.get_value(i1)
            v2 = context.store.get_value(i2)
            context.store[context.sp] = ('BOOL', v1 > v2 and not b)
    if op == 21:  # (*LEQ*)
        context.sp -= 1
        if p in (0, 1, 2, 3, 4):
            v1 = context.store.get_value(context.sp)
            v2 = context.store.get_value(context.sp + 1)
            context.store[context.sp] = ('BOOL', v1 <= v2)
        elif p == 5:
            b, (i1, i2) = compare(context, q)
            v1 = context.store.get_value(i1)
            v2 = context.store.get_value(i2)
            context.store[context.sp] = ('BOOL', v1 <= v2 or b)
    if op == 22:  # (*LES*)
        context.sp -= 1
        if p in (0, 1, 2, 3, 4):
            v1 = context.store.get_value(context.sp)
            v2 = context.store.get_value(context.sp + 1)
            context.store[context.sp] = ('BOOL', v1 < v2)
        elif p == 5:
            b, (i1, i2) = compare(context, q)
            v1 = context.store.get_value(i1)
            v2 = context.store.get_value(i2)
            context.store[context.sp] = ('BOOL', v1 < v2 and not b)
    if op == 23:  # (*UJP*)
        context.pc = q
    if op == 24:  # (*FJP*)
        _, b = context.pop()
        if not b:
            context.pc = q
    if op == 25:  # (*XJP*)
        _, v = context.pop()
        context.pc = v + q
    if op == 26:  # (*CHK*)
        v1 = context.store.get_value(context.sp)
        lower_bound = context.store.get_value(q - 1)
        upper_bound = context.store.get_value(q)
        if v1 < lower_bound or v1 > upper_bound:
            raise RuntimeError("Value out of range")
    if op == 27:  # (*EOF*)
        file_eof(context)
    if op == 28:  # (*ADI*)
        context.sp -= 1
        v1 = context.store.get_value(context.sp)
        v2 = context.store.get_value(context.sp + 1)
        context.store[context.sp] = ('INT', v1 + v2)
    if op == 29:  # (*ADR*)
        context.sp -= 1
        v1 = context.store.get_value(context.sp)
        v2 = context.store.get_value(context.sp + 1)
        context.store[context.sp] = ('REEL', v1 + v2)
    if op == 30:  # (*SBI*)
        context.sp -= 1
        v1 = context.store.get_value(context.sp)
        v2 = context.store.get_value(context.sp + 1)
        context.store[context.sp] = ('INT', v1 - v2)
    if op == 31:  # (*SBR*)
        context.sp -= 1
        v1 = context.store.get_value(context.sp)
        v2 = context.store.get_value(context.sp + 1)
        context.store[context.sp] = ('REEL', v1 - v2)


def ex2(op, p, q, context):
    if op == 32:  # (*SGS*)
        v = context.store.get_value(context.sp)
        context.store[context.sp] = ('SETT', {v})
    if op == 33:  # (*FLT*)
        v = context.store.get_value(context.sp)
        context.store[context.sp] = ('REEL', v)
    if op == 34:  # (*FLO*)
        v = context.store.get_value(context.sp - 1)
        context.store[context.sp - 1] = ('REEL', v)
    if op == 35:  # (*TRC*)
        v = context.store.get_value(context.sp)
        context.store[context.sp] = ('INT', int(trunc(v)))
    if op == 36:  # (*NGI*)
        v = context.store.get_value(context.sp)
        context.store[context.sp] = ('INT', -v)
    if op == 37:  # (*NGR*)
        v = context.store.get_value(context.sp)
        context.store[context.sp] = ('REEL', -v)
    if op == 38:  # (*SQI*)
        v = context.store.get_value(context.sp)
        context.store[context.sp] = ('INT', v * v)
    if op == 39:  # (*SQR*)
        v = context.store.get_value(context.sp)
        context.store[context.sp] = ('REEL', v * v)
    if op == 40:  # (*ABI*)
        v = context.store.get_value(context.sp)
        context.store[context.sp] = ('INT', abs(v))
    if op == 41:  # (*ABR*)
        v = context.store.get_value(context.sp)
        context.store[context.sp] = ('REEL', abs(v))
    if op == 42:  # (*NOT*)
        v = context.store.get_value(context.sp)
        context.store[context.sp] = ('BOOL', not v)
    if op == 43:  # (*AND*)
        context.sp -= 1
        v1 = context.store.get_value(context.sp)
        v2 = context.store.get_value(context.sp + 1)
        context.store[context.sp] = ('BOOL', v1 and v2)
    if op == 44:  # (*IOR*)
        context.sp -= 1
        v1 = context.store.get_value(context.sp)
        v2 = context.store.get_value(context.sp + 1)
        context.store[context.sp] = ('BOOL', v1 or v2)
    if op == 45:  # (*DIF*)
        context.sp -= 1
        v1 = context.store.get_value(context.sp)
        v2 = context.store.get_value(context.sp + 1)
        context.store[context.sp] = ('SETT', v1.difference(v2))
    if op == 46:  # (*INT*)
        context.sp -= 1
        v1 = context.store.get_value(context.sp)
        v2 = context.store.get_value(context.sp + 1)
        context.store[context.sp] = ('SETT', v1.intersection(v2))
    if op == 47:  # (*UNI*)
        context.sp -= 1
        v1 = context.store.get_value(context.sp)
        v2 = context.store.get_value(context.sp + 1)
        context.store[context.sp] = ('SETT', v1.union(v2))


def ex3(op, p, q, context):
    if op == 48:  # (*INN*)
        context.sp -= 1
        int_value = context.store.get_value(context.sp)
        set_value = context.store.get_value(context.sp + 1)
        context.store[context.sp] = ('BOOL', int_value in set_value)
    elif op == 49:  # (*MOD*)
        context.sp -= 1
        a_value = context.store.get_value(context.sp)
        b_value = context.store.get_value(context.sp + 1)
        context.store[context.sp] = ('INT', a_value % b_value)
    elif op == 50:  # (*ODD*)
        a_value = context.store.get_value(context.sp)
        context.store[context.sp] = ('BOOL', (a_value % 2) > 0)
    elif op == 51:  # (*MPI*)
        context.sp -= 1
        a_value = context.store.get_value(context.sp)
        b_value = context.store.get_value(context.sp + 1)
        context.store[context.sp] = ('INT', a_value * b_value)
    elif op == 52:  # (*MPR*)
        context.sp -= 1
        a_value = context.store.get_value(context.sp)
        b_value = context.store.get_value(context.sp + 1)
        context.store[context.sp] = ('REEL', a_value * b_value)
    elif op == 53:  # (*DVI*)
        context.sp -= 1
        a_value = context.store.get_value(context.sp)
        b_value = context.store.get_value(context.sp + 1)
        context.store[context.sp] = ('INT', a_value // b_value)
    elif op == 54:  # (*DVR*)
        context.sp -= 1
        a_value = context.store.get_value(context.sp)
        b_value = context.store.get_value(context.sp + 1)
        context.store[context.sp] = ('REEL', a_value / b_value)
    elif op == 55:  # (*MOV*)
        _, i2_value = context.pop()
        _, i1_value = context.pop()
        for i in range(q):
            context.store[i1_value + i] = context.store[i2_value + i]
    elif op == 56:  # (*LCA*)
        context.push(('ADR', q))
    elif op == 57:  # (*DEC*)
        value = context.store.get_value(context.sp)
        context.store[context.sp] = ('INT', value - q)
    if op == 58:  # (*STP*)
        context.running = False


def initialize_files(context: Context):
    context.store[INPUTADR] = ('INT', 0)
    context.store[PRDADR] = ('INT', 0)
    context.store[OUTPUTADR] = ('UNDEF', 0)
    context.store[PRRADR] = ('UNDEF', 0)


def interpret(input_stream, output_stream, input_file, output_file, code, store):
    context = Context(input_stream, output_stream, input_file, output_file, store)
    initialize_files(context)

    split_op_func = [ex0, ex1, ex2, ex3]
    count = 80

    while context.running:
        c = code[context.pc]
        op = c.op
        p = c.p
        q = c.q

        # print(f"{context.pc:10} {op:10}{p:10} {q:10}")

        context.pc += 1

        split_op_func[op // 16](op, p, q, context)

        # count-=1
        # if count == 0:
        #     context.running = False
