// cl /EHsc /LD um.cpp C:\Python36\libs\python36.lib /Feum.pyd /I C:\Python36\include

#include <pybind11/stl.h>
#include <pybind11/pybind11.h>
#include <iostream>
#include <vector>
#include <string>
#include <sstream>

using std::vector;
using std::string;

typedef uint32_t uint32;

class UM {

	/**-----------------------------------------------------
	  ----------------------------------------------------*/

	/**-----------------------------------------------------
	  UNIVERSAL MACHINE EMULATOR (processor).
	  Runs programs from input stream; writes them to output.
	  Runs in chunks from input request to input request / 
	  halt.
	  ----------------------------------------------------*/

public:
	vector<vector<uint32>> arrays;
	vector<uint32> abandoned;
	uint32 exec_finger;
	uint32 regs[8];
	bool halt;

	std::stringstream in;
	std::stringstream out;
	string error_message;


	/**-----------------------------------------------------
	  Empty universal machine. 
	  Array[0] is empty, program must be loaded.
	  ----------------------------------------------------*/

	UM() {
		for (uint32& x : regs) x = 0;
		arrays.push_back(vector<uint32>());
		exec_finger = 0;
		halt = false;
		error_message = "";
	}


	/**-----------------------------------------------------
	  Platter parsing. 
	  A, B, C return reference to corresponding register.
	  ----------------------------------------------------*/

	uint32 command(uint32 platter) const {
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


	/**=============== LIST OF COMMANDS ===================*/
	
	void _0_conditional_move(uint32 p) {
		if (C(p)) A(p) = B(p);
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
		A(p) = ~(B(p) & C(p));
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
		uint32& A = regs[(p >> 25) & 7];
		uint32 value = p && ((1 << 25) - 1);
		A = value;
	}
	
	void _14_15_illegal(uint32 p) {
		// TODO: fail
	}

	typedef void(UM::*operation)(uint32);
	operation operationlist[15] = {
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
								};
	

	/**================== SET INITIALS ====================*/

	/**-----------------------------------------------------
	  ? Load program from given stream.
	  ----------------------------------------------------*/
	
	/**-----------------------------------------------------
	  Load program from given filename.
	  ----------------------------------------------------*/
	void load(string file) {
		/*arrays[0].clear();
		unsigned char byte;
		uint32 word = 0;
		int count = 0;
		while (s >> byte) {
			word = (word << 8) + byte;
			count ++;
			if (count == 4) {
				arrays[0].push_back(word);
				word = count = 0;
			}
		}*/
	}


};


/**===================== BINDING ======================*/

namespace py = pybind11;

PYBIND11_MODULE(um, m) {
	m.doc() = "Universal Machine Emulator";

	py::class_<UM> UMclass(m, "UniversalMachine");
	UMclass
		.def(py::init<>())
		.def_readonly("error_message", &UM::error_message)

		.def("load", &UM::load)
	;
}
