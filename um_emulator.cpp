// cl /EHsc /LD um_emulator.cpp C:\Python37\libs\python37.lib /Feum_emulator.pyd /I C:\Python37\include
/*
cl /EHsc /LD /O2 um_emulator.cpp C:\Python37\libs\python37.lib /Feum_emulator.pyd /I C:\Python37\include && py temp.py
*/

#include <pybind11/stl.h>
#include <pybind11/pybind11.h>
#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <sstream>
#include <cassert>

using std::vector;
using std::string;

typedef uint32_t uint32;

class UMEmulator {

	/**-----------------------------------------------------
	  ----------------------------------------------------*/

	/**-----------------------------------------------------
	  UNIVERSAL MACHINE EMULATOR (processor).
	  Runs machine from file.
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
                debug = 1,		// special
                echo = 2,		// show output on screen (cout in addition to sstring)
                echoinput = 4,  // add input to output (not cout unless has echo mode)
    };
    unsigned mode;

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
		// clear input & output?
		//in.unsetf(std::ios::skipws);
		//out.unsetf(std::ios::skipws);
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
		if (B(p) >= arrays.size() || C(p) >= arrays[B(p)].size()) {
			return fail_operation("Index out of bounds");
		}
		A(p) = arrays[B(p)][C(p)];
	}

	void _2_array_amendment(uint32 p) {
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
		arrays[C(p)] = vector<uint32>();
		abandoned.push_back(C(p));
	}

	void _10_output(uint32 p) {
		if (C(p) > 255) return fail_operation("Not-ASCII output");
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
	  Load program from file.
	  Returns if the machine is waiting for input (input
	  stream is empty).
	  ----------------------------------------------------*/
	void load(string file) {
		std::ifstream s(file, std::ios::binary);
		if (!s.is_open()) {
			return fail_operation("Cannot open file");
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
		assert (count == 0);	// file had 4x bytes
	}


	void setmode(vector<MODE> modelist) {
		mode = 0;
		for (MODE m : modelist) mode |= m;
	}



	/**================= RUNS & RESULTS ===================*/
	
	/**-----------------------------------------------------

	  ----------------------------------------------------*/
	bool run(string s) {
		in.clear();
		in.str(string());
		in << s << std::flush;
		waiting_for_input = false;
		while (!halt && !waiting_for_input) {
			uint32 platter = arrays[0][exec_finger++];
			uint32 cmd = get_command(platter);
			std::invoke(operationlist[cmd], this, platter);
			if (exec_finger >= arrays[0].size()) fail_operation("Finger out of bounds");
		}
		assert (halt ^ waiting_for_input);
		return waiting_for_input;
	}


	/**-----------------------------------------------------
	  Returns and clears output.
	  ? Clear in separate method
	  ----------------------------------------------------*/
	string read() {
		string result = out.str();
		out.clear();
		out.str(string());
		return result;
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
		.def("read", &UMEmulator::read)
	;

	py::enum_<UMEmulator::MODE>(UMclass, "mode")
        .value("debug", UMEmulator::MODE::debug)
        .value("echo", UMEmulator::MODE::echo)
        .value("echoinput", UMEmulator::MODE::echoinput)
        .export_values()
    ;
}
