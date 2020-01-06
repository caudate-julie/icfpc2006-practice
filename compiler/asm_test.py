from . import asm

def test_reversibility():
    insns = [asm.ConditionalMoveInsn(1, 2, 3),
             asm.ArrayIndexInsn(3, 4, 5),
             asm.ArrayAmendmentInsn(6, 4, 3),
             asm.AdditionInsn(3, 1, 2),
             asm.MultiplicationInsn(3, 6, 7),
             asm.DivisionInsn(1, 4, 2),
             asm.NotAndInsn(5, 2, 4),
             asm.HaltInsn(),
             asm.AllocationInsn(4, 1),
             asm.AbandonmentInsn(3),
             asm.OutputInsn(1),
             asm.InputInsn(5),
             asm.LoadProgramInsn(6, 7),
             asm.OrthographyInsn(2, 567)]
    umcode = asm.encode_instructions(insns)
    new_insns = asm.decode_instructions(umcode)

    assert len(insns) == len(new_insns)
    for i1, i2 in zip(insns, new_insns):
        assert str(i1) == str(i2)