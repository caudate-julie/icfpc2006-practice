from dataclasses import dataclass

instructions = {}
regnames = [':A:', ':B:', ':C:', ':D:', ':E:', ':F:', ':G:', ':H:']

class IllegalInstructionError(Exception):
    def __init__(self, code):
        self.message = f'Illegal operation with code {code}'


def register_instruction(code):
    assert not callable(code)
    assert code not in instructions
    def registered(c):
        instructions[code] = c
        c.code = code
        return c
    return registered


def decode_registers(umcode):
    assert len(umcode) == 4, len(umcode)
    regs = (umcode[2] << 8) + umcode[3]
    A = (regs >> 6) & 7
    B = (regs >> 3) & 7
    C = regs & 7
    return (A, B, C)


def decode_instruction(umcode):
    assert len(umcode) == 4, len(umcode)
    code = umcode[0] >> 4
    if code == 14 or code == 15:
        raise IllegalInstructionError(code)
    return instructions[code].decode(umcode)


class AsmInsn:
    def __init__(self, A, B, C):
        self.A = A
        self.B = B
        self.C = C

    def encode(self):
        int_code = (self.code << 28) | (self.A << 6) | (self.B << 3) | self.C
        return int_code.to_bytes(4, byteorder='b')

    @classmethod
    def decode(cls, umcode: bytes):
        A, B, C = decode_registers(umcode)
        return cls(A, B, C)

    def result_stored(self):
        raise NotImplementedError()


@register_instruction(0)
class ConditionalMoveInsn(AsmInsn):
    # if (C(p)) A(p) = B(p);
    def __str__(self):
        return f'if {regnames[self.C]}: {regnames[self.B]} -> {regnames[self.A]}'

    def result_stored(self):
        return self.A


@register_instruction(1)
class ArrayIndexInsn(AsmInsn):
    # A(p) = arrays[B(p)][C(p)];
    def __str__(self):
        return f'code[{regnames[self.B]}][{regnames[self.C]}] -> {regnames[self.A]}'

    def result_stored(self):
        return self.A


@register_instruction(2)
class ArrayAmendmentInsn(AsmInsn):
    # arrays[A(p)][B(p)] = C(p);
    def __str__(self):
        return f'{regnames[self.C]} -> code[{regnames[self.A]}][{regnames[self.B]}]'
        raise NotImplementedError()

    def result_stored(self):
        return None


@register_instruction(3)
class AdditionInsn(AsmInsn):
    # A(p) = B(p) + C(p);
    def __str__(self):
        return f'{regnames[self.B]} + {regnames[self.C]} -> {regnames[self.A]}'

    def result_stored(self):
        return self.A


@register_instruction(4)
class MultiplicationInsn(AsmInsn):
    # A(p) = B(p) * C(p);
    def __str__(self):
        return f'{regnames[self.B]} * {regnames[self.C]} -> {regnames[self.A]}'

    def result_stored(self):
        return self.A


@register_instruction(5)
class DivisionInsn(AsmInsn):
    # A(p) = B(p) / C(p);	
    def __str__(self):
        return f'{regnames[self.B]} / {regnames[self.C]} -> {regnames[self.A]}'

    def result_stored(self):
        return self.A


@register_instruction(6)
class NotAndInsn(AsmInsn):
    # A(p) = ~(B(p) & C(p));
    def __str__(self):
        return f'~{regnames[self.B]} & {regnames[self.C]} -> {regnames[self.A]}'

    def result_stored(self):
        return self.A


@register_instruction(7)
class HaltInsn(AsmInsn):
    # state = State::HALT;
    def __init__(self):
        super().__init__(0, 0, 0)

    def __str__(self):
        return 'halt'

    def result_stored(self):
        return None

    @classmethod
    def decode(cls, umcode: bytes):
        return cls()


@register_instruction(8)
class AllocationInsn(AsmInsn):
    # 	uint32 index = arrays.size();
    # 	arrays.push_back(vector<uint32>(C(p)));
    # 	B(p) = index;
    def __init__(self, B, C):
        super().__init__(0, B, C)

    def __str__(self):
        return f'allocate {regnames[self.C]} bytes with address -> {regnames[self.B]}'

    def result_stored(self):
        return self.B

    @classmethod
    def decode(cls, umcode: bytes):
        _, B, C = decode_registers(umcode)
        return cls(B, C)



@register_instruction(9)
class AbandonmentInsn(AsmInsn):
    # abandoned.push_back(C(p));
    def __init__(self, C):
        super().__init__(0, 0, C)

    def __str__(self):
        return f'abandon code at {regnames[self.C]}'

    def result_stored(self):
        return None

    @classmethod
    def decode(cls, umcode: bytes):
        _, _, C = decode_registers(umcode)
        return cls(C)


@register_instruction(10)
class OutputInsn(AsmInsn):
    # out.push_back((char)C(p));
    def __init__(self, C):
        super().__init__(0, 0, C)

    def __str__(self):
        return f'{regnames[self.C]} -> [OUTPUT]'

    def result_stored(self):
        return None

    @classmethod
    def decode(cls, umcode: bytes):
        _, _, C = decode_registers(umcode)
        return cls(C)


@register_instruction(11)
class InputInsn(AsmInsn):
    # C(p) = (uint32)in.value();
    def __init__(self, C):
        super().__init__(0, 0, C)

    def __str__(self):
        return f'[INPUT] -> {regnames[self.C]}'

    def result_stored(self):
        return self.C

    @classmethod
    def decode(cls, umcode: bytes):
        _, _, C = decode_registers(umcode)
        return cls(C)



@register_instruction(12)
class LoadProgramInsn(AsmInsn):
    # if (B(p)) arrays[0] = arrays[B(p)];
    # exec_finger = C(p);
    def __init__(self, B, C):
        super().__init__(0, B, C)

    def __str__(self):
        return f'execute code[{regnames[self.B]}][{regnames[self.C]}]'

    def result_stored(self):
        return None

    @classmethod
    def decode(cls, umcode: bytes):
        _, B, C = decode_registers(umcode)
        return cls(B, C)


@register_instruction(13)
class OrthographyInsn(AsmInsn):
	# 	uint32 index = (p >> 25) & 7;
	# 	uint32 value = p & ((1 << 25) - 1);
	# 	regs[index] = value;
    def __init__(self, A, value):
        self.A = A
        self.value = value

    def __str__(self):
        return f'{self.value} -> {regnames[self.A]}'

    def result_stored(self):
        return self.A

    def encode(self):
        umcode = (self.code << 28) | (self.A << 25) | self.value
        return umcode.to_bytes(4, byteorder='b')

    @classmethod
    def decode(cls, umcode: bytes):
        assert len(uncode) == 4
        int_code = int.from_bytes(umcode, byteorder='big', signed=False)
        A = (int_code >> 25) & 7
        value = umcode & ((1 << 25) - 1)
        return cls(A, value)


# @register_instruction(14)
# @register_instruction(15)
# class IllegalInsn(AsmInsn):
#     # fail_operation("Illegal operation");
#     def __init__(self):
#         super().__init__(0, 0, 0)

#     def __str__(self):
#         return 'Illegal operation code'

#     def result_stored(self):
#         return None

#     def encode(self):
#         raise NotImplementedError()

if __name__ == '__main__':
    print (instructions)