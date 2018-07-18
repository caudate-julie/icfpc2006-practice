// cl /EHsc /LD um_emulator.cpp C:\Python36\libs\python36.lib /Feum_emulator.pyd /I C:\Python36\include

#include <pybind11/stl.h>
#include <pybind11/pybind11.h>
#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <sstream>
#include <cassert>
//#include <algorithm>

using std::vector;
using std::string;

typedef uint32_t uint32;

class UMEmulator {

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
	bool waiting_for_input;

	std::stringstream in;
	std::stringstream out;
	string error_message;

    enum MODE { 
                debug = 1,
                echo = 2,
                echoinput = 4,
    };
    unsigned int mode;

	/**-----------------------------------------------------
	  Empty universal machine. 
	  Array[0] is empty, program must be loaded.
	  ----------------------------------------------------*/

	UMEmulator() {
		for (uint32& x : regs) x = 0;
		arrays.push_back(vector<uint32>());
		exec_finger = 0;
		halt = waiting_for_input = false;
		error_message = "";
	}


	/**-----------------------------------------------------
	  Platter parsing. 
	  A, B, C return reference to corresponding register.
	  ----------------------------------------------------*/

	uint32 get_command(uint32 platter) const {
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
		for (uint32 x : abandoned) {
			if (x == B(p)) return fail_operation("Calling abandoned array");
		}
		if (arrays.size() <= B(p) || arrays[B(p)].size() <= C(p)) {
			return fail_operation("Index out of bounds");
		}
		A(p) = arrays[B(p)][C(p)];
	}

	void _2_array_amendment(uint32 p) {
		for (uint32 x : abandoned) {
			if (x == A(p)) {
				fail_operation("Calling abandoned array");
				return;
			}
		}
		if (A(p) >= arrays.size() || B(p) >= arrays[A(p)].size()) {
			return fail_operation("Index out of bounds");
		}
		arrays[A(p)][B(p)] = C(p);
	}

	void _3_addition(uint32 p) {
		A(p) = B(p) + C(p);
	}
	
	void _4_multiplication(uint32 p) {
		A(p) = B(p) * C(p);
	}
	
	void _5_division(uint32 p) {
		if (!C(p)) return fail_operation("Zero division");
		A(p) = B(p) / C(p);	
	}

	void _6_not_and(uint32 p) {
		A(p) = ~(B(p) & C(p));
	}
	
	void _7_halt(uint32 p) {
		halt = true;
	}

	void _8_allocation(uint32 p) {
		// don't use B(p) instead of index! B(p) and C(p) may be same register.
		if (abandoned.empty()) {
			uint32 index = arrays.size();
			arrays.push_back(vector<uint32>(C(p)));
			B(p) = index;
		}
		else {
			uint32 index = abandoned.back();
			abandoned.pop_back();
			arrays[index] = vector<uint32>(C(p));
			B(p) = index;
		}
	}

	void _9_abandonment(uint32 p) {
		if (C(p) == 0) return fail_operation("Abandoning working program");
		abandoned.push_back(C(p));
	}

	void _10_output(uint32 p) {
		if (C(p) > 255) return fail_operation("Output of non-ASCII");
		out << (char)C(p);
		if (mode & MODE::echo) std::cout << (char)C(p);
	}
	
	void _11_input(uint32 p) {
		unsigned char c;
		if (!(in >> c)) {
			waiting_for_input = true;
			exec_finger--;
			return;
		}
		C(p) = (uint32)c;
		if (mode & MODE::echoinput) _10_output(p);
	}
	
	void _12_load_program(uint32 p) {
		for (uint32 x : abandoned) {
			if (x == B(p)) return fail_operation("Calling abandoned array");
		}
		if (B(p)) arrays[0] = arrays[B(p)];
		if (C(p) >= arrays[0].size()) return fail_operation("Finger out of bounds");
		exec_finger = C(p);
	}
	
	void _13_orthography(uint32 p) {
		uint32 index = (p >> 25) & 7;
		uint32 value = p & ((1 << 25) - 1);
		regs[index] = value;
	}
	
	void _14_15_illegal(uint32 p) {
		fail_operation("Illegal operation");
	}

	void fail_operation(string message) {
		error_message = message;
		halt = true;
	}


	typedef void(UMEmulator::*operation)(uint32);
	constexpr static operation operationlist[] = {
								&UMEmulator::_0_conditional_move,
								&UMEmulator::_1_array_index,
								&UMEmulator::_2_array_amendment,
								&UMEmulator::_3_addition,
								&UMEmulator::_4_multiplication,
								&UMEmulator::_5_division,
								&UMEmulator::_6_not_and,
								&UMEmulator::_7_halt,
								&UMEmulator::_8_allocation,
								&UMEmulator::_9_abandonment,
								&UMEmulator::_10_output,
								&UMEmulator::_11_input,
								&UMEmulator::_12_load_program,
								&UMEmulator::_13_orthography,
								&UMEmulator::_14_15_illegal,
								&UMEmulator::_14_15_illegal
								};
	

	/**================== SET INITIALS ====================*/

	/**-----------------------------------------------------
	  ? Load program from given stream.
	  ----------------------------------------------------*/
	
	/**-----------------------------------------------------
	  Load program from given filename.
	  Returns if the machine is waiting for input (input 
	  stream is empty).
	  ----------------------------------------------------*/
	void load(string file) {
		std::ifstream s(file, std::ios::binary);
		if (!s.is_open()) {
			// TODO: fail
			return;
		}
		s.unsetf(std::ios::skipws);

		arrays[0].clear();
		unsigned char byte;
		uint32 word = 0;
		unsigned count = 0;

		while (s >> byte) {
			word = (word << 8) + byte;
			count ++;
			if (count == 4) {
				arrays[0].push_back(word);
				word = count = 0;
			}
		}
		assert (count == 0);
	}


	void setmode(vector<MODE> modelist) {
		mode = 0;
		for (MODE m : modelist) mode |= m;
	}


	/**-----------------------------------------------------
	  --------------------  RUUUUUUN!-----------------------
	  ----------------------------------------------------*/
	bool run(string s) {
		in.str(s);
		while (!halt && !waiting_for_input) {
			uint32 platter = arrays[0][exec_finger++];
			uint32 cmd = get_command(platter);
			std::invoke(operationlist[cmd], this, platter);
			if (exec_finger >= arrays[0].size()) fail_operation("Finger out of bounds");
		}
		assert (halt ^ waiting_for_input);
		return waiting_for_input;
	}


};



/**===================== BINDING ======================*/

namespace py = pybind11;

PYBIND11_MODULE(um_emulator, m) {
	m.doc() = "Universal Machine Emulator";

	py::class_<UMEmulator> UMclass(m, "UniversalMachine");
	UMclass
		.def(py::init<>())
		.def_readonly("error_message", &UMEmulator::error_message)

		.def("load", &UMEmulator::load)
		.def("setmode", &UMEmulator::setmode)
		.def("run", &UMEmulator::run)

	;

	py::enum_<UMEmulator::MODE>(UMclass, "mode")
        .value("debug", UMEmulator::MODE::debug)
        .value("echo", UMEmulator::MODE::echo)
        .value("echoinput", UMEmulator::MODE::echoinput)
        .export_values()
    ;
}
