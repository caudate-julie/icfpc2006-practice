from dataclasses import dataclass

instructions = {}
regnames = [':A:', ':B:', ':C:', ':D:', ':E:', ':F:', ':G:', ':H:']

def instruction(code):
    assert not callable(code)
    assert code not in instructions
    def registered(c):
        instructions[code] = c
        c.code = code
        return c
    return registered





class PreCommand:
    def __str__(self):
        raise NotImplementedError()

    def encode(self):
        raise NotImplementedError()

    def decode(self, umcode: bytes):
        raise NotImplementedError()


@instruction(0)
class ConditionalMoveCmd(PreCommand):
    # if (C(p)) A(p) = B(p);
    def __init__(self, A, B, C):
        self.A = A
        self.B = B
        self.C = C
        self.result = A

    def __str__(self):
        return f'if {regnames[self.C]}: {regnames[self.B]} -> {regnames[self.A]}'

    def encode(self):
        platter = (self.code << 28) | (self.A << 6) | (self.B << 3) | self.C
        return platter.to_bytes(4, byteorder='b')
        raise NotImplementedError()


@instruction(1)
class ArrayIndexCmd(PreCommand):
    # A(p) = arrays[B(p)][C(p)];
    def __init__(self, A, B, C):
        self.A = A
        self.B = B
        self.C = C
        self.result = A

    def __str__(self):
        return f'code[{regnames[self.B]}][{regnames[self.C]}] -> {regnames[self.A]}'

    def encode(self):
        raise NotImplementedError()


@instruction(2)
class ArrayAmendmentCmd(PreCommand):
    # arrays[A(p)][B(p)] = C(p);
    def __init__(self, A, B, C):
        self.A = A
        self.B = B
        self.C = C
        self.result = None

    def __str__(self):
        return f'{regnames[self.C]} -> code[{regnames[self.A]}][{regnames[self.B]}]'
        raise NotImplementedError()

    def encode(self):
        raise NotImplementedError()


@instruction(3)
class AdditionCmd(PreCommand):
    # A(p) = B(p) + C(p);
    def __init__(self, A, B, C):
        self.A = A
        self.B = B
        self.C = C
        self.result = A

    def __str__(self):
        return f'{regnames[self.B]} + {regnames[self.C]} -> {regnames[self.A]}'

    def encode(self):
        raise NotImplementedError()


@instruction(4)
class MultiplicationCmd(PreCommand):
    # A(p) = B(p) * C(p);

    def __init__(self, A, B, C):
        self.A = A
        self.B = B
        self.C = C
        self.result = A

    def __str__(self):
        return f'{regnames[self.B]} * {regnames[self.C]} -> {regnames[self.A]}'

    def encode(self):
        raise NotImplementedError()


@instruction(5)
class DivisionCmd(PreCommand):
    # A(p) = B(p) / C(p);	

    def __init__(self, A, B, C):
        self.A = A
        self.B = B
        self.C = C
        self.result = A

    def __str__(self):
        return f'{regnames[self.B]} / {regnames[self.C]} -> {regnames[self.A]}'

    def encode(self):
        raise NotImplementedError()


@instruction(6)
class NotAndCmd(PreCommand):
    # A(p) = ~(B(p) & C(p));
    def __init__(self, A, B, C):
        self.A = A
        self.B = B
        self.C = C
        self.result = A

    def __str__(self):
        return f'~{regnames[self.B]} & {regnames[self.C]} -> {regnames[self.A]}'

    def encode(self):
        raise NotImplementedError()


@instruction(7)
class HaltCmd(PreCommand):
    # state = State::HALT;
    def __init__(self):
        self.result = None

    def __str__(self):
        return 'halt'

    def encode(self):
        raise NotImplementedError()


@instruction(8)
class AllocationCmd(PreCommand):
    # 	uint32 index = arrays.size();
    # 	arrays.push_back(vector<uint32>(C(p)));
    # 	B(p) = index;

    def __init__(self, B, C):
        self.B = B
        self.C = C
        self.result = B

    def __str__(self):
        return f'allocate {regnames[self.C]} bytes with address -> {regnames[self.B]}'

    def encode(self):
        raise NotImplementedError()


@instruction(9)
class AbandonmentCmd(PreCommand):
    # abandoned.push_back(C(p));
    def __init__(self, C):
        self.C = C
        self.result = None

    def __str__(self):
        return f'abandon code at {regnames[self.C]}'

    def encode(self):
        raise NotImplementedError()


@instruction(10)
class OutputCmd(PreCommand):
    # out.push_back((char)C(p));
    def __init__(self, C):
        self.C = C
        self.result = None

    def __str__(self):
        return f'{regnames[self.C]} -> [OUTPUT]'

    def encode(self):
        raise NotImplementedError()


@instruction(11)
class InputCmd(PreCommand):
    # C(p) = (uint32)in.value();
    def __init__(self, C):
        self.C = C
        self.result = C

    def __str__(self):
        return f'[INPUT] -> {regnames[self.C]}'

    def encode(self):
        raise NotImplementedError()


@instruction(12)
class LoadProgramCmd(PreCommand):
    # if (B(p)) arrays[0] = arrays[B(p)];
    # exec_finger = C(p);
    def __init__(self, B, C):
        self.B = B
        self.C = C
        self.result = None

    def __str__(self):
        return f'execute code[{regnames[self.B]}][{regnames[self.C]}]'

    def encode(self):
        raise NotImplementedError()


@instruction(13)
class OrthographyCmd(PreCommand):
	# 	uint32 index = (p >> 25) & 7;
	# 	uint32 value = p & ((1 << 25) - 1);
	# 	regs[index] = value;
    def __init__(self, C, value):
        self.C = C
        self.value = value
        self.result = C

    def __str__(self):
        return f'{self.value} -> {regnames[self.C]}'

    def encode(self):
        raise NotImplementedError()


@instruction(14)
@instruction(15)
class IllegalCmd(PreCommand):
    # fail_operation("Illegal operation");
    def __init__(self):
        self.result = None

    def __str__(self):
        return 'Illegal operation code'

    def encode(self):
        raise NotImplementedError()

if __name__ == '__main__':
    print (instructions)