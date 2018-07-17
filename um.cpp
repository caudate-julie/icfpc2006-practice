#include <vector>
#include <stringstream>

using std::vector;

typedef uint32_t uint32;

class UM {
	/**-----------------------------------------------------
	UNIVERSAL MACHINE (processor).
	Runs programs from input stream; writes them to output.
	Runs in chunks from input request to input request / 
	halt.
	------------------------------------------------------*/

public:
	vector<vector<uint32>> arrays;
	vector<uint32> abandoned;
	uint32 exec_finger;
	uint32 regs[8];
	bool halt;

	std::stringstream in;
	std::stringstream out;

	uint32 operator(uint32 platter) const {
		return platter >> 28;
	}


	uint32& A(uint32 platter) {
		return regs[(platter >> 6) & 7];
	}


	uint32& B(uint32 platter) {
		return regs[(platter >> 3) & 7];
	}


	uint32& C(uint32 platter) {
		return regs[platter & 7];
	}

	/*-----------------------------------------------------*/
	/**--------------- LIST OF COMMANDS -------------------*/
	
	void _0_conditional_move(uint32 p) {
		if C(p) A(p) = B(p);
	}


	void _1_array_index(uint32 p) {
		// TODO: abandonment failure
		A(p) = arrays[B(p)][C(p)];
	}


	void _2_array_amendment(uint32 p) {
		// TODO: abandonment failure
		arrays[A(p)][B(p)] = C(p);
	}


	void _3_addition(uint32 p) {
		A(p) = B(p) + C(p);
	}
	

	void _4_multiplication(uint32 p) {
		A(p) = B(p) * C(p);
	}
	

	void _5_division(uint32 p) {
		// TODO: zero division fail
		A(p) = B(p) / C(p);	
	}
	

	void _6_not_and(uint32 p) {
		A(p) = ~(B(p) & C(p))
	}
	

	void _7_halt(uint32 p) {
		halt = true;
	}
	

	void _8_allocation(uint32 p) {
		if (!abandoned.empty()) {
			B(p) = abandoned.back();
			abandoned.pop_back();
			arrays[B(p)] = vector<uint32>(C(p));
		}
		else {
			B(p) = arrays.size();
			arrays.push_back(vector<uint32>(C(p)));
		}
	}
	

	void _9_abandonment(uint32 p) {
		// ?TODO: abandonment failure
		abandoned.push_back(C(p));
	}
	

	void _10_output(uint32 p) {
		// TODO: >256 failure
		// TODO: echo mode
		out << (char)C(p);
	}
	

	void _11_input(uint32 p) {
		// TODO: EOF
		char c;
		in >> c;
		C(p) = (uint32)c;
		// TODO: copy input mode
	}
	

	void _12_load_program(uint32 p) {
		if (B(p)) arrays[0] = arrays[B(p)];
		exec_finger = C(p);
	}
	

	void _13_orthography(uint32 p) {
		uint32& A = regs((p >> 25) & 7);
		uint32 value = p && ((1 << 25) - 1);
		A = value;
	}
	

	void _14_15_illegal(uint32 p) {
		// TODO: fail
	}


	typedef void(UM::*operation)(uint32);
	operation[] operations =    {
								&UM::_0_conditional_move,
								&UM::_1_array_index,
								&UM::_2_array_amendment,
								&UM::_3_addition,
								&UM::_4_multiplication,
								&UM::_5_division,
								&UM::_6_not_and,
								&UM::_7_halt,
								&UM::_8_allocation,
								&UM::_9_abandonment,
								&UM::_10_output,
								&UM::_11_input,
								&UM::_12_load_program,
								&UM::_13_orthography,
								&UM::_14_15_illegal
								}
	

private:


}