#include <pybind11/stl.h>
#include <pybind11/pybind11.h>
#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <sstream>
#include <cassert>
#include <optional>

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

	//  ctor          
	// ------> IDLE <-----+------+
	//          |         ^      |
	//          | run     |      | write_input
	//  +-------+---------+      |
	//  V                 V      |
	// HALT            WAITING --+
	//
	// RUNNING is an internal state, never to be seen by user.
	
	enum class State {
		IDLE, RUNNING, WAITING, HALT
	} state;

	std::optional<int> in;					// accepts input only when requested
	string out;
	std::optional<unsigned> output_buffer_limit;
	std::optional<unsigned> command_limit;
	string error_message;

	/**-----------------------------------------------------
	  Universal machine, gets the text of the program.
	  ----------------------------------------------------*/
	UMEmulator(const string& program) {
		for (uint32& x : regs) x = 0;
		arrays.emplace_back();
		exec_finger = 0;
		state = State::IDLE;
		in = std::nullopt;
		output_buffer_limit = std::nullopt;
		command_limit = std::nullopt;
		error_message = "";
		out = "";
	
		assert (program.size() % 4 == 0);	// file had 4x bytes

		uint32 word = 0;
		for (int i = 0; i < program.size(); i++) {
			word = (word << 8) + static_cast<uint8_t>(program[i]);
			if (i % 4 == 3) {
				arrays[0].push_back(word);
				word = 0;
			}
		}
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
		state = State::HALT;
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
		out.push_back((char)C(p));
	}
	
	void _11_input(uint32 p) {
		assert (state == State::RUNNING);
		if (in == std::nullopt) {
			state = State::WAITING;
			exec_finger--;
			return;
		}

		if (in < -1 || in > 255) return fail_operation("Not-ASCII output");
		C(p) = (uint32)in.value();
		in = std::nullopt;
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
		state = State::HALT;
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
	

	/**================= RUNS & RESULTS ===================*/
	
	/**-----------------------------------------------------
	 * Runs the current program from the previous pause
	 * untill halt or input request or buffer/command limit
	 * if set.
	 * Returns the new output accumulated.
	 * ---------------------------------------------------*/
	string run(/*string s*/) {
		assert (out.empty());
		if (state == State::HALT) return "";

		assert (state == State::IDLE);
		state = State::RUNNING;

		unsigned command_count = 0;
		while (state == State::RUNNING) {
			if (output_buffer_limit && out.size() >= output_buffer_limit
			    || command_limit && command_count >= command_limit) {
				state = State::IDLE;
				break;
			}
			uint32 platter = arrays[0][exec_finger++];
			uint32 cmd = get_command(platter);
			std::invoke(operationlist[cmd], this, platter);
			if (exec_finger >= arrays[0].size()) {
				fail_operation("Finger out of bounds");
				break;
			}
			command_count ++;
		}
		
		string result;
		result.swap(out);
		return result;
	}

	void write_input(int c) {
		assert (state == State::WAITING);
		assert (in == std::nullopt);
		in = c;
		state = State::IDLE;
	}

};



/**===================== BINDING ======================*/

namespace py = pybind11;

PYBIND11_MODULE(um_emulator, m) {
	m.doc() = "Universal Machine Emulator";

	py::class_<UMEmulator> UMclass(m, "UniversalMachine");
	UMclass
		.def(py::init([](py::bytes b) { return UMEmulator(b); }))
		.def(py::init<const UMEmulator&>())
		.def_readonly("error_message", &UMEmulator::error_message)
		.def_readonly("state", &UMEmulator::state)

		.def_readwrite("output_buffer_limit", &UMEmulator::output_buffer_limit)
		.def_readwrite("command_limit", &UMEmulator::command_limit)

		.def("run", [](UMEmulator& u) { return py::bytes(u.run()); })
		.def("write_input", &UMEmulator::write_input)
	;

	py::enum_<UMEmulator::State>(UMclass, "State")
	    .value("IDLE", UMEmulator::State::IDLE)
		.value("WAITING", UMEmulator::State::WAITING)
		.value("HALT", UMEmulator::State::HALT)
		.export_values()
	;
}
