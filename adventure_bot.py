#!python3

# This is the Bots for Adventure wandering (howie).
# written on July, 2017
# 
#          DEFINITIONS
#
# room  -  object of Room() class, location.
# coord  -  (int, int) coordinates of room or current position.
#           Used as identificator, e.g. key for bot.rooms[ coord : room ]
#
# item  -  object of Item() class, single item.
# basetype, type  -  kind (short name) of item. Standard is X-XXXX-XXX.
#           Used as key in [ basetype : [items] ]. 
# adj  -  adjective + ' '. Usually color. '' if not defined.
# fullname  -  adj + basetype (like 'sepia A-1234-XYZ'). Unique for the room.
# condition  -  basetype if item is pristine, or nested tuple:
#               (((A B) C) (D E) F)  <-- for item of basetype A
# missing  -  condition[1:], wrapped in a Counter.
# result  -  condition[0]. Next stage (after all current-stage details are added).
# stage  -  every item may go through several stages of repair:
#           0: A  missing
#           1:   B, missing
#           2:     C, missing
#           3:       (D missing E) and F

from collections import deque, Counter, namedtuple
from itertools import combinations
from pathlib import Path
from copy import copy
from enum import enum
import re
import sys

from cpp.um_emulator import UniversalMachine
from byteio import *
from clients import run

import logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.DEBUG,
    filename='bot.log',
    format='%(levelname)-10s %(message)s'
    )

Coord = namedtuple('Coord', 'x y')
quarters = ('north', 'east', 'south', 'west')
directions = ((0, -1), (1, 0), (0, 1), (-1, 0))


# ====================== SOME SMALL AUXILIARY ===========================#

# -----------------------------------------------------------------------#
# Take multinested list and return name of item after adding all details.
# [[['radio', ['antenna', 'pill']], 'button'], 'processor'] -> 'radio'.
# -----------------------------------------------------------------------#
def getbasetype(condition):
    while isinstance(condition, tuple) or isinstance(condition, list):
        condition = condition[0]
    return condition

# -----------------------------------------------------------------------#
# Take multinested list and return number of nested lists for [0] element.
# [[['radio', ['antenna', 'pill']], 'button'], 'processor'] -> 3.
# -----------------------------------------------------------------------#
def stage(condition):
    depth = 0
    while isinstance(condition, tuple) or isinstance(condition, list):
        if len(condition) > 1: depth += 1
        condition = condition[0]
    return depth

# -----------------------------------------------------------------------#
# Wrap whatever item to tuple / Counter.
# -----------------------------------------------------------------------#
def tuplewrap(foo):
    return foo if isinstance(foo, tuple) else (foo, )

def counterwrap(foo):
    return Counter(tuplewrap(foo))

# -----------------------------------------------------------------------#
# Difference between current and needed conditions, None if unreachable.
# -----------------------------------------------------------------------#
def missinglist(needed, current):
    if stage(needed) < stage(current): needed = (needed, )
    C = counterwrap(current)
    C.subtract(counterwrap(needed))
    return None if any(c < 0 for c in C.values()) else C - Counter()


# ============================= BASE BOT ================================#

class Bot:
    def __init__(self, position=Coord(0, 0)):
        self.position = position


    # def makemove(self, cmd):
    #     '''Shortcut for UM.run + log output.'''
    #     self.UM.run(cmd)
    #     text = self.UM.get_output()
    #     self.log += text
    #     return text


    def pos(self, coord=None):
        '''Uniform string with self.position for logger.'''
        if coord is None: coord = self.position
        return "(%2d %2d)  " % (coord.real, coord.imag)


    def go_to_the_room(self, destination):
        path = self.find_path(destination)
        if path == []:
            return self.makemove("x\n")
        for coord in path:
            quarter = quarters[directions.index(coord)]
            self.position += coord
            text = self.makemove("go " + quarter + "\n")
        assert self.position == destination
        return text



# =========================== EXPLORER BOT ==============================#

class ExplorerBot(Bot):

    def __init__(self, position=Coord(0, 0)):
        super().__init__()
        self.unvisited_coords = deque([complex(0, 0)])  # room zero is not parsed yet
        self.rooms = { complex(0, 0) : Room(complex(0, 0)) }
        self.strangelets = []




    # -------------------------------------------------------------------#
    # Given "English" text, convert it into list of sentences.
    # Delete empty lines and lines with '>: ' (command prompts). 
    # Hope there are no unexpected dots in the text.
    # -------------------------------------------------------------------#
    def split_sentences(self, text):
        known_words_with_dots = ("incl", "construction", 'Bus 2')

        for word in known_words_with_dots:
            text = re.sub(word + '.', word, text)
        # delete all prompts
        text = re.sub(re.compile("^.*?\n"), "", text)  # previous command
        text = re.sub(re.compile(">\:.*"), "", text)   # prompt for next

        text = text.replace("\n\n", ".")
        text = text.replace("\n", " ")
        lines = []
        for line in text.split('.'):
            line = line.lstrip(' ')
            if line:
                lines.append(line)
        return lines


    # =================== PARSE ROOM DESCRIPTION ========================#

    # -------------------------------------------------------------------#
    # Read description of the room and create a Room object.
    # -------------------------------------------------------------------#
    def parse_room(self, text):
        # is this a full description?
        if "Try switching your goggles" in text:
            logger.warning(self.pos() + "Switching to Reading")
            self.makemove("switch goggles Reading\n")
            text = self.makemove("x\n")

        # room is already created as "anticipated".
        text = self.split_sentences(text)
        room = self.rooms[self.position]
        room.name = text[0]
        logger.debug(self.pos() + "Parsing " + room.name + '.')

        regex_direction = re.compile("^From here,.*?")
        regex_item = re.compile(".+here is an? (\(broken\) )?(.+?)( here)?$")  # group(2)
        regexs_ignore = (
                re.compile("^You are standing.*?"),
                re.compile("A sign reads.*"),
                re.compile("There are more.*")
              )

        for line in text[1:]:
            if any(r.match(line) for r in regexs_ignore):
                # no interesting info
                pass

            elif regex_item.match(line):
                # There is an (item) here.
                fullname = regex_item.search(line).group(2)
                self.parse_item(fullname, room)

            elif regex_direction.match(line):
                # From here, you can go...
                self.parse_directions(line, room)

            else:
                # something unexpected
                room.strangelets.append(line)
        return room


    # -------------------------------------------------------------------#
    # Read "you can go..." line and make neighrooms and unvisited rooms
    # for any mentioned quarter.
    # -------------------------------------------------------------------#
    def parse_directions(self, line, room):
        for i in range(4):
            if not quarters[i] in line: 
                continue
            coord = self.position + directions[i]
            if not coord in self.rooms.keys():
                # meeting this room for the first time
                self.unvisited_coords.append(coord)
                self.rooms[coord] = Room(coord)
                
            # add as a neighroom and hope they are path-independent
            room.neighrooms[i] = self.rooms[coord]
            self.rooms[coord].neighrooms[i - 2] = room


    # ========================= PARSE ITEM ==============================#

    # -------------------------------------------------------------------#
    # Take list of items, call for description and parse into Item.
    # -------------------------------------------------------------------#
    def parse_item(self, fullname, room):
        regex_standard = re.compile(r".*\w\-(\w){4}\-(\w){3}") # X-XXXX-XXX
        regex_basetype = re.compile(".*?The (.*?) is.*")
        regex_adjective = re.compile("Interestingly, this one is (.*)")
        regex_alsobroken = re.compile("Also, it is broken: it is (.*)")

        basetype, adj = fullname, ''

        text = self.split_sentences(self.makemove('x ' + fullname + '\n'))
        for line in text:
            if regex_basetype.match(line):
                basetype = regex_basetype.search(line).group(1)
                condition = [basetype]   # default - item is pristine.
                
            elif regex_adjective.match(line):
                adj = regex_adjective.search(line).group(1) + ' '

            elif regex_alsobroken.match(line):
                conditiontext = regex_alsobroken.search(line).group(1)
                conditiontext = self.pre_parse_condition(conditiontext)
                _, condition = self.parse_condition_to_tuple(conditiontext, 1)

        assert adj + basetype == fullname 
        item = Item(basetype, adj)
        item.set_condition(condition)
        if not basetype in room.trash:
            room.trash[basetype] = []
        room.trash[basetype].append(item)
        room.pile.append((item.fullname()))
        if (not regex_standard.match(basetype) and 
                    not any(basetype in V for V in self.targets.values())):
            room.strangelets.append("Item named " + fullname)


    # -------------------------------------------------------------------#
    # Make some changes before recursively split condition text into lists:
    # items separated with '|', spaces between items are removed.
    # -------------------------------------------------------------------#
    def pre_parse_condition(self, line):
        t = []
        line = '(' + line + ')'
        line = re.sub('\(an? ', '(', line)
        line = re.sub(' missing ', ' | ', line)
        line = re.sub(' and ', ' | ', line)
        line = re.sub(' an? ', ' | ', line)
        for _ in range(10):
            line = re.sub('\| \|', '|', line)
        for _ in range(10):
            line = re.sub(' \| ', '|', line)
        for _ in range(10):
            line = re.sub('  ', ' ', line)
        return line


    # -------------------------------------------------------------------#
    # Make list-based "condition" out of prepared line.
    # '(a|b(c|d|e f))' -> ('a', 'b', ('c', 'd', 'e f'))
    # -------------------------------------------------------------------#
    def parse_condition_to_tuple(self, text, position):
        previous = position
        condition = []
        while position < len(text):
            if text[position] == '|':
                if previous < position:
                    condition.append(text[previous:position])
                previous = position + 1

            elif text[position] == '(':
                position, new_t = self.parse_condition_to_tuple(text, position + 1)
                condition.append(new_t)
                previous = position + 1      

            elif text[position] == ')':
                if previous < position:
                    condition.append(text[previous:position])
                return (position, tuple(condition))
            position += 1

        logger.error('Missing closing bracket in ' + text)
        return(position, tuple(condition))

    # ====================== LOCATIONS TRAVERSING =======================#

    # -------------------------------------------------------------------#
    # Choose pathfinding algorithm.
    # Returns set of directions: [(0+1j), (0+1j), (-1+0j) ...]
    # -------------------------------------------------------------------#
    def find_path(self, destination):
        return self.find_path_safe(destination)



    # -------------------------------------------------------------------#
    # Find route to the destination - assume there always is a passage.
    # -------------------------------------------------------------------#
    def find_path_simple(self, destination):
        def sgn(x):
            return (x > 0) - (x < 0)
        x = int(destination.real - self.position.real)
        y = int(destination.imag - self.position.imag)
        return [complex(sgn(x), 0)] * abs(x) + [complex(0, sgn(y))] * abs(y)


    # -------------------------------------------------------------------#
    # Find route to the destination by Dijkstra.
    # -------------------------------------------------------------------#
    def find_path_safe(self, destination):
        if (destination == self.position): return []
        routes = { coord : [] for coord in self.rooms }
        discovered = deque([self.rooms[self.position]])
        while discovered:
            currentroom = discovered.popleft()
            for neighroom in currentroom.neighrooms:
                if neighroom is None or routes[neighroom.coord]:
                    # no room or path is found.
                    continue
                discovered.append(neighroom)
                routes[neighroom.coord] = (routes[currentroom.coord]
                             + [neighroom.coord - currentroom.coord])
                if neighroom.coord == destination: 
                    return routes[neighroom.coord]
        logger.error('Cannot find path from ' + str(self.position) 
                                      + ' to ' + str(destination))


    def log_strangelets(self):
        '''Log all lines that did not match known patterns.'''
        text = "\n=== STRANGELETS ===\n"
        for s in self.strangelets:        
        for room in self.rooms.values():
            if not room.strangelets: continue
            text += self.pos(room.coord) + " " + room.name + ":\n"
            for strange in room.strangelets:
                text += "         " + str(strange) + '\n'
            text += '\n'
        logger.info(text)



    # =================== REPAIR ONE OF TARGET ITEMS ====================#

    # -------------------------------------------------------------------#
    #
    #                      SAMPLE INSTRUCTION TREE
    # [keypad] 
    #    |
    #    |--- [motherboard] 
    #    |        |
    #    |        |--- [A-1920-IXB]
    #    |        |       |             
    #    |        |       |--- [A-1920-IXB]
    #    |        |       |       |
    #    |        |       |       |--- [radio] -- [blue transistor]
    #    |        |       |       |--- [processor] -- [cache]
    #    |        |       |       |--- [bolt]
    #    |        |       |
    #    |        |       |--- [red transistor]
    #    |        |
    #    |        |--- [screw]
    #    |
    #    |--- [button]
    #
    # Instruction query:
    #       instruction stub (fullname and parent filled in)
    #       needed condition (types only, no fullnames)
    #       current condition (types only, no fullnames)
    # -------------------------------------------------------------------#

        INVENTORY_LIMIT = 6

        # pre-set list of things needed for uploader and downloader.
        self.targets = {"downloader" : ["USB cable", "display", "jumper shunt", "progress bar", "power cord"], 
                        "uploader" : ["MOSFET", "battery", "status LED", "RS232 adapter", "EPROM burner"]}
        #self.targets = {"" : ["keypad"]}
        self.inventory = []
        self.basic_inventory = []    # what should be left after assembling.

        # instruction generating globals (they should be passed in all
        # recursive calls, but are just stored here instead).
        self.instruction_root = None    # root of instructions tree
        self.simulation_tree = None     # copy of tree (destroyed in simulation)
        self.instruction_queries = []   # instructions to be done
        self.items_available = None
        self.simulations_count = 0      # just for infolog



    # -------------------------------------------------------------------#
    # Combine one of loader details in the room.
    # -------------------------------------------------------------------#
    def assemble_target_detail(self, room, target, detail):
        logger.debug(self.pos() + "Trying to repair " + detail)
        self.instruction_queries = [(Instruction(target), target, (target, detail))]
        self.instruction_root = self.instruction_queries[0][0]
        self.items_available = {}
        for x in room.trash:
            self.items_available[x] = room.trash[x].copy()
        self.simulation_count = 0

        commands = self.make_and_check_instruction_tree(0)
        logger.info(str(self.simulation_count) + " simulation runs for " + detail)

        if commands is None:
            logger.error("No working instruction tree found for " + detail)
            return

        for c in commands: self.makemove(c)
        logger.debug("...Successfully assembled")
        self.clear_inventory()


    # -------------------------------------------------------------------#
    # Take the next instruction query and call make_instruction.
    # If instruction tree is ready, run simulation.
    # No ambiguities at this stage. 
    # Return command list if found, None otherwise.
    # -------------------------------------------------------------------#
    def make_and_check_instruction_tree(self, pointer):
        if pointer >= len(self.instruction_queries):
            # tree is fully made, time to check.
            return self.simulate_assembling()

        # instruction stub (fullname and parent), needed and current conditions
        I, needed, current = self.instruction_queries[pointer]
        query_length = len(self.instruction_queries)

        if counterwrap(needed) == counterwrap(current):
            # Instruction is complete, take the next one
            return self.make_and_check_instruction_tree(pointer + 1)

        current = self.add_chain_of_stages(I, needed, current)
        missing = missinglist(needed, current)
        assert missing is not None

        result = self.make_instruction(I, missing, pointer + 1)
        if result is not None:
            # solution found! Just pass it back
            return result

        # no solution here - undo changes
        self.instruction_queries[query_length:] = []
        return None


    # -------------------------------------------------------------------#
    # Make chain of nested instruction queries:
    # (sepia A : needed [A, b] : current [[[A b c] d] e f]) ==> 
    # ==> ((sepia A, e f), (sepia A, d), (sepia A, c))
    # Return condition at the next stage and add others to queries.
    # -------------------------------------------------------------------#
    def add_chain_of_stages(self, I, needed, current):
        if stage(needed) == stage(current): return current
        stages = []
        while (stage(needed) < stage(current)):
            logger.debug("needed: " + str(needed) + " current: " + str(current))
            stages.append((Instruction(I.itemname), (current[0], ), current))
            current = current[0]
        stages.append((Instruction(I.itemname), needed, current))

        # set parents and add all stages but last as a query.
        stages[-1] = tuple([I] + list(stages[-1][1:]))
        for i in range(len(stages) - 1):
            stage_I, parent_I = stages[i][0], stages[i + 1][0]
            stage_I.itemname = I.itemname
            stage_I.parent = parent_I
            parent_I.children = [stage_I]
        self.instruction_queries += stages[:-1]
        return stages[-1][2]


    # -------------------------------------------------------------------#
    # Given incomplete instruction and Counter of missing items, add next
    # item to instructions.
    # This is the method for disambiguation between same-type items.
    # Returns command list if found, None otherwise.
    # -------------------------------------------------------------------#
    def make_instruction(self, I, missing, pointer):
        if not missing:
            # instruction is made - go to the next one
            return self.make_and_check_instruction_tree(pointer)

        needed = next(iter(missing))
        count = missing[needed]
        basetype = getbasetype(needed)
        if (not basetype in self.items_available or 
               len(self.items_available[basetype]) < count):
            return None

        del missing[needed]
        suitables = [item 
                     for item in self.items_available[basetype] 
                     if item.reachable(needed)]
        for C in combinations(suitables, count):
            # make changes
            for item in C:
                self.items_available[basetype].remove(item)
                new_I = Instruction(item.fullname())
                new_I.parent = I
                I.children.append(new_I)

                # whether item is ready or not is not this method's problem.
                self.instruction_queries.append((new_I, 
                                                 needed, 
                                                 item.condition()))

            # go for it!
            result = self.make_instruction(I, missing, pointer)
            if result is not None:
                # solution found! Just pass it back
                return result

            # undo changes
            for item in C:
                self.items_available[basetype].append(item)
            I.children[-count:] = []
            self.instruction_queries[-count:] = []

        missing[needed] = count
        # no solutions at this branch
        return None


    # -------------------------------------------------------------------#
    # Searches instruction set for full list of needed instructions.
    # -------------------------------------------------------------------#
    def list_needed_details(self):
        needed = set()
        for I in self.simulation_tree.traverse():
            needed.add(I.itemname)
        return needed


    # -------------------------------------------------------------------#
    # Trying to carry out given instructions.
    # -------------------------------------------------------------------#
    def simulate_assembling(self):
        # here item is always a fullname, not Item object.
        commands = []
        self.simulation_tree = self.instruction_root.copy()
        needed = self.list_needed_details()
        pile = self.rooms[self.position].pile.copy()
        self.inventory = self.basic_inventory.copy()
        self.simulation_count += 1
        if self.simulation_count % 20000 == 0: print("...", self.simulation_count)

        while pile:
            if len(self.inventory) >= self.INVENTORY_LIMIT:
                return None     # no more place :(

            item = pile.popleft()
            commands.append('take ' + item + '\n')
            if not item in needed:
                commands.append('inc ' + item + '\n')
            else:
                # trying to combine smth
                self.inventory.append(item)
                if self.revise_instructions(commands):
                    return commands


    # -------------------------------------------------------------------#
    # Try to carry out any instruction until no changes are made.
    # Any finished instruction (I.children is empty and I.itemname 
    # in inventory) is deleted. 
    # Return True, if root instruction is finished.
    # -------------------------------------------------------------------#
    def revise_instructions(self, commands):
        changed = True
        while changed:
            changed = False
            for I in self.simulation_tree.traverse():
                if I.itemname in self.inventory and not I.children:
                    # instruction is complete.
                    if I.parent is None:
                        # finished the last instruction.
                        return True
                    elif not I.parent.itemname in self.inventory: 
                        continue
                    elif I.parent.itemname == I.itemname:
                        # stage complete:
                        I.parent.children.remove(I)
                        changed = True
                    elif I.parent.itemname == I.parent.children[0].itemname:
                        # wrong stage
                        pass
                    else:
                        commands.append('combine ' + I.parent.itemname
                                        + ' with ' + I.itemname + '\n')
                        I.parent.children.remove(I)
                        changed = True
                        self.inventory.remove(I.itemname)
        return False


    # -------------------------------------------------------------------#
    # Create list of needed details - others may be burned.
    # -------------------------------------------------------------------#
    def clear_inventory(self):
        text = self.makemove('inventory\n').split('\n')
        regex_item = re.compile("^an? (\(broken\) )?(.+)([.,]|( and))$") # group 2
        for line in text:
            if not regex_item.match(line):
                continue
            name = regex_item.search(line).group(2)
            if not name in self.inventory:
                logger.error(self.pos() + "Unexpected item in inventory: " + name)
            if not name in self.basic_inventory:
                self.makemove('inc ' + name + '\n')
        self.inventory = self.basic_inventory.copy()




    # -------------------------------------------------------------------#
    # BOT GO!
    # -------------------------------------------------------------------#
    def run(self, UM):
        logger.info("\n\n  --- RUN ---")
        self.UM = UM
        self.log += UM.get_output()

        # traverse rooms for info
        while self.unvisited_coords:
            text = self.go_to_the_room(self.unvisited_coords.pop())
            self.parse_room(text)

        # assembly target items.
        assembly_order = ['downloader']
        for target in assembly_order:
            self.go_to_the_room(complex(0, 0))
            self.makemove('take ' + target + '\n')
            self.basic_inventory.append(target)
            # find rooms with missing details:
            for detail in self.targets[target]:
                for coord in self.rooms:
                    room = self.rooms[coord]
                    if detail in room.trash.keys():
                        break
                else: continue # not in this room
                # detail found
                self.go_to_the_room(coord)
                self.assemble_target_detail(room, target, detail)
            else: return       # nothing to make in this room            

        self.makemove('quit\nlogout\n')
        self.log_strangelets()
        return




# ============================== ROOM ===================================#

class Room:
    def __init__(self, coord):
        self.coord = coord
        self.name = ""
        self.trash =  {}       # [ shortname : list of items ]
        self.pile = deque()    # fullnames of items, take with popleft()
        self.neighrooms = [None] * 4
        self.strangelets = []


# ============================== ITEM ===================================#

class Item:
    def __init__(self, basetype, adj):
        self.type = basetype
        self.adj = adj
        self.result = None
        self.missing = []
        self.next_stage = None

    def __eq__(self, other):
        return self.type == other.type and self.adj == other.adj

    def fullname(self):
        return self.adj + self.type

    def condition(self):
        return self.result + self.missing

    def set_condition(self, condition):
        self.missing = (condition[1:], )
        self.result = condition[0]
        assert not isinstance(self.result, list)
        if isinstance(self.result, tuple):
            self.next_stage = Item(self.type, self.adj)
            self.next_stage.set_condition(self.result)

    def reachable(self, needed):
        current = self.condition()
        if not getbasetype(needed) == self.type or stage(needed) > stage(current):
            return False
        while stage(needed) < stage(current):
            # HACK: if X needs X (same condition), we might as well take the second.
            # This item is only usefull half-repaired.
            if current[0] in current[1:]: return None
            current = current[0]
        # now they are at the same stage
        return missinglist(needed, current) is not None


# ============================ INSTRUCTION ==============================#

class Instruction:
    def __init__(self, fullname=""):
        self.itemname = fullname       # item we repair.
        self.parent = None
        self.children = []

    def copy(self, parent=None):
        I = Instruction(self.itemname)
        I.parent = parent
        for child in self.children:
            I.children.append(child.copy(I))
        return I

    def traverse(self):
        yield self
        for child in self.children:
            yield from child.traverse()


# =======================================================================#


# suppressing \r\n newlines.
# if sys.platform == "win32":
#    import os, msvcrt
#    msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)


def run_commands_from_file(UM, filename):
    try:
        with open(filename, 'r') as f_in:
            commandstring = f_in.read()
    except IOError as e:
        logger.error(e.message)
        raise e
    UM.run(input_string)


def main():
    timestart = time()

    # Load machine and run pre-defined commands from file
    UM = UniversalMachine(Path('umix.umz').read_bytes())
    infile = Path('logs/howie.in').open('rb')
    outfile = Path('logs/howie.out').open('wb')
    writers = ForkWriter(ByteWriter(outfile), TextWriter(sys.stdin))

    run(um, umin=ForkReader(ByteReader(infile), [writers]), umout=writers)

    # bot: traverse rooms
    explorer = ExplorerBot()
    try:
        explorer.run(UM, writers)
    except Exception as e:
        raise e
    finally:
        out.write(explorer.log)
    citymap = traverser.map()

    # first we run file...
    UM.run(input_string)
    out.write(UM.get_output())
        

    # Input file and bot are over, stop duplicating commands to stdout. Write input to file directly.
    UM.setmode(defaultmode)           

    input_string = ""
    # ...then keyboard.
    while UM.run(input_string):
        out.write(UM.get_output())
        input_string = input() +'\n'
        out.write(input_string)

    assert UM.halt
    # write last output
    out.write(UM.get_output())
    if UM.error_message:
        print("Error occured:\n      ", UM.error_message)

    print("\ntime elapsed: %.2f" % (time() - timestart))
    out.close()


if __name__ == "__main__":
    outfile = 'out.out' if len(sys_argv) == 1 else sys_argv[1]
    main(outfile)