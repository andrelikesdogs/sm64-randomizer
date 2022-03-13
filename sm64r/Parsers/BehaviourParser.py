import os
from typing import List
from sm64r.Entities.Object3D import Object3D
from sm64r.Randoutils import format_binary
from sm64r.Entities.CollisionModel import CollisionModel
from sm64r.Constants import BEHAVIOUR_NAMES

TYPE_MAP = {
    0x00: "Mario",
    0x01: "Unusued",
    0x02: "Destruction Object",
    0x03: "Unused",
    0x04: "Enemy/Actor",
    0x05: "Group, pushable",
    0x06: "Level Objects",
    0x07: "Unusued",
    0x08: "Default List",
    0x09: "Collision Model",
    0x0A: "Poles/Hangable",
    0x0B: "Spawner",
    0x0C: "Unimportant Object"  # won't load if no object slots are available
}

CMD_NAMES = {
    0x00: "START",
    0x01: "STATE_LOOP",
    0x02: "JUMP_AND_LINK",
    0x03: "RETURN",
    0x04: "JUMP",
    0x05: "LOOP_N",
    0x06: "END_LOOP_N",
    0x07: "INFINITE_LOOP",
    0x08: "LOOP_START",
    0x09: "LOOP_END",
    0x0A: "END_BEHAVIOUR_SCRIPT",
    0x0B: "END_BEHAVIOUR_SCRIPT_UNUSUED",
    0x0C: "CALL_ASM",
    0x0D: "OFFSET_BY_FLOAT",
    0x0E: "SET_TO_FLOAT",
    0x0F: "OFFSET_BY_INTEGER",
    0x10: "SET_TO_INTEGER",
    0x11: "BIT_SET",
    0x12: "BIT_CLEAR",
    0x13: "ADD_RNG",
    0x14: "OBJECT_TYPE",
    0x15: "FLOAT_MUL",
    0x16: "FLOAT_ADD",
    0x17: "ADD_RNG_2",
    0x18: "NOOP",
    0x19: "NOOP",
    0x1A: "NOOP",
    0x1B: "CHANGE_MODEL_ID",
    0x1C: "LOAD_CHILD_OBJECT",
    0x1D: "DEACTIVATE",
    0x1E: "DROP_TO_GROUND",
    0x1F: "WAVE_GEN",
    0x20: "UNUSED",
    0x21: "SET_BILLBOARDING",
    0x22: "SET_RENDER_INVISIBLE",
    0x23: "COLLISION_CYLINDER_SIZE",
    0x24: "NOTHING",
    0x25: "STATE_CYCLE",
    0x26: "LOOP",
    0x27: "SET_WORD",
    0x28: "ANIMATE",
    0x29: "LOAD_CHILD_OBJECT",
    0x2A: "SET_COLLISION",
    0x2B: "SET_COLLISION_SPHERE",
    0x2C: "SPAWN_OBJECT",
    0x2D: "SET_INIT_POSITION",
    0x2E: "SET_HURTBOX",
    0x2F: "SET_INTERACTION",
    0x30: "SET_GRAVITY",
    0x31: "SET_INTERACTION_SUB_TYPE",
    0x32: "SCALE_OBJECT",
    0x33: "CHILD_OBJECT_CHANGE",
    0x34: "TEXTURE_ANIMATE_RATE",
    0x35: "CLEAR_GRAPH_FLAG",
    0x36: "SET_VALUE",
    0x37: "SPAWN_SOMETHING"
}

CMD_LENGTHS = {
    0x02: 8,
    0x04: 8,
    0x0C: 8,
    0x13: 8,
    0x14: 8,
    0x15: 8,
    0x16: 8,
    0x17: 8,
    0x1C: 12,
    0x23: 8,
    0x27: 8,
    0x29: 12,
    0x2A: 8,
    0x2B: 12,
    0x2C: 12,
    0x2E: 8,
    0x2F: 8,
    0x30: 20,
    0x31: 8,
    0x33: 8,
    0x36: 8,
    0x37: 8,
}

collision_indices = {}


class BehaviourParser:
    @staticmethod
    def from_objects(rom, objs: List[Object3D]):
        for obj in objs:
            yield BehaviourParser(rom, obj.behaviour)

    @staticmethod
    def from_object(rom, obj):
        return BehaviourParser(rom, obj.behaviour)

    @staticmethod
    def from_nested(rom, segment_addr, depth, model_id):
        return BehaviourParser(rom, segment_addr, depth, model_id)

    @staticmethod
    def clear_cache():
        BehaviourParser.parsedScripts = {}

    def __init__(self, rom, behaviourAddr, depth=0, model_id=None):
        self.rom = rom
        self.depth = depth

        self.behaviourAddr = behaviourAddr
        self.start = self.rom.read_segment_addr(behaviourAddr)
        self.cursor = self.start
        self.children = []

        self.current_model_id = model_id

        self.loop_layer = 0
        self.processed = []
        self.process_log = []
        self.success = True
        # try:
        self.process()
        # except Exception as err:
        #     self.success = False
        #     print("Behaviour Parse failed:", err)

        if "SM64R" in os.environ and "DUMP" in os.environ["SM64R"]:
            self.dump_log()

    def dump_log(self):
        path_target = os.path.join("dumps", "behaviour_scripts")
        if not os.path.exists(path_target):
            os.makedirs(path_target)

        with open(os.path.join(path_target, f"{' ' * self.depth}{hex(self.behaviourAddr)}.txt"), "w+") as output_file:
            for (bhrAddr, cursor, cmd_name, cmd_bytes) in self.process_log:
                output_file.write(
                    f"{' ' * self.depth} {hex(bhrAddr).ljust(10)} @ {hex(cursor).ljust(10)} {cmd_name.ljust(20)} {format_binary(cmd_bytes)}\n")

    def log(self, *msg):
        # print(self.depth * " ", *msg)
        pass

    def process(self, depth=0):
        if hex(self.behaviourAddr) in self.rom.behaviours:
            # already processed
            return

        while True:
            cmd_id = self.rom.read_integer(self.cursor)
            cmd_len = CMD_LENGTHS[cmd_id] if cmd_id in CMD_LENGTHS else 4

            cmd_bytes = self.rom.read_bytes(self.cursor, cmd_len)
            log_entry = (self.behaviourAddr,
                         self.cursor,
                         CMD_NAMES[cmd_id],
                         cmd_bytes,
                         "")

            if cmd_id == 0x00:
                ''' Start '''
                type_id = self.rom.read_integer(self.cursor + 1)

                type = TYPE_MAP[type_id]

                # bit_field = self.rom.read_bytes(self.cursor + 2, 2)
                behaviour_name = BEHAVIOUR_NAMES[hex(self.behaviourAddr)] if hex(
                    self.behaviourAddr) in BEHAVIOUR_NAMES else "unknown"
                self.log(
                    f"Start processing behaviour script for {type} at {hex(self.start)} - {behaviour_name}")
            elif cmd_id == 0x01:
                ''' State Loop '''
            elif cmd_id == 0x02:
                ''' Jump and Link '''
            elif cmd_id == 0x03:
                ''' Return '''
            elif cmd_id == 0x04:
                ''' Jump '''
                cmd_len = 8
            elif cmd_id == 0x05:
                ''' Loop N '''
            elif cmd_id == 0x06:
                ''' End Loop N '''
            elif cmd_id == 0x07:
                ''' Infinite Loop '''
            elif cmd_id == 0x08:
                ''' Loop Start '''
                self.loop_layer += 1
            elif cmd_id == 0x09:
                ''' Loop End '''
                self.loop_layer -= 1
                if self.loop_layer == 0:
                    break
            elif cmd_id == 0x0A:
                ''' End Behaviour Script '''
                break
            elif cmd_id == 0x0B:
                ''' End Behaviour Script. Unusued '''
            elif cmd_id == 0x0C:
                ''' Call ASM '''
            elif cmd_id == 0x0D:
                ''' Offset by Float '''
            elif cmd_id == 0x0E:
                ''' Set to Float '''
            elif cmd_id == 0x0F:
                ''' Offset by Integer '''
            elif cmd_id == 0x10:
                ''' Set Integer '''
            elif cmd_id == 0x11:
                ''' Bit Set '''
            elif cmd_id == 0x12:
                ''' Bit Clear. Unused '''
            elif cmd_id == 0x13:
                ''' Add RNG '''
            elif cmd_id == 0x14:
                ''' Object Type '''
            elif cmd_id == 0x15:
                ''' Float Multiply '''
            elif cmd_id == 0x16:
                ''' Float Add '''
            elif cmd_id == 0x17:
                ''' Add RNG 2. Unusued '''
            elif cmd_id == 0x18:
                ''' Unknown. Unused. '''
            elif cmd_id == 0x19:
                ''' Unknown. Unused. '''
            elif cmd_id == 0x1A:
                ''' Unknown. Unused. '''
            elif cmd_id == 0x1B:
                ''' Change Model ID '''
                self.current_model_id = self.rom.read_integer(
                    self.cursor + 2, 2)
                # print("new model id: ", hex(self.current_model_id))
            elif cmd_id == 0x1C:
                ''' Load Child Object '''

                model_id = self.rom.read_integer(self.cursor + 4, 4)
                segment_addr = self.rom.read_integer(self.cursor + 8, 4)
                # print("new model id: ", hex(model_id))

                self.log(
                    f"Nested Behaviour found (Load Child Object), defining ModelID: {model_id} @ {hex(segment_addr)}")

                nested_behaviour = BehaviourParser.from_nested(
                    self.rom, segment_addr, self.depth + 1, model_id)
                self.children.append(nested_behaviour)
            elif cmd_id == 0x1D:
                ''' Deactivate '''
            elif cmd_id == 0x1E:
                ''' Drop to Ground? '''
            elif cmd_id == 0x1F:
                ''' Float Sum. Waves and Bubbles '''
            elif cmd_id == 0x20:
                ''' Float Sum. Unusued '''
            elif cmd_id == 0x21:
                ''' Set Billboarding (flag 0x04) '''
            elif cmd_id == 0x22:
                ''' Set Invisible (flag 0x10) '''
            elif cmd_id == 0x23:
                ''' Define Collision Cylinder '''
                cmd_len = 8
            elif cmd_id == 0x24:
                ''' Nothing. Unusued '''
            elif cmd_id == 0x25:
                ''' State Cycle '''
            elif cmd_id == 0x26:
                ''' Loop. Unused '''
            elif cmd_id == 0x27:
                ''' Set Word '''
            elif cmd_id == 0x28:
                ''' Animate '''
            elif cmd_id == 0x29:
                ''' Load Child Object '''
            elif cmd_id == 0x2A:
                ''' Set Collision '''
                collision_addr = self.rom.read_integer(self.cursor + 4, 4)

                target_addr = self.rom.read_segment_addr(collision_addr)

                # print(format_binary(self.rom.read_bytes(self.cursor, 8)),
                #       "collision read at: ", hex(target_addr))
                if target_addr is not None:
                    hex_bhv = hex(self.behaviourAddr)

                    possible_name = BEHAVIOUR_NAMES[hex_bhv] if hex(
                        self.behaviourAddr) in BEHAVIOUR_NAMES else "unknown"

                    idx = collision_indices[hex_bhv] if hex_bhv in collision_indices else 0

                    collision_indices[hex_bhv] = idx + 1

                    for collision in CollisionModel.from_position(self.rom, target_addr, f"{possible_name}_{idx}"):
                        self.rom.collision_models_by_behaviour[self.behaviourAddr] = collision

                else:
                    self.log('Invalid collision segment referenced: ',
                             format_binary(self.rom.read_bytes(self.cursor, 8)))
            elif cmd_id == 0x2B:
                ''' Set Collision Sphere '''
                # self.log("collision load as sphere")
            elif cmd_id == 0x2C:
                ''' Spawn Object '''

                model_id = self.rom.read_integer(self.cursor + 4, 4)
                segment_addr = self.rom.read_integer(self.cursor + 8, 4)

                # print("new model id: ", hex(model_id))

                self.log(
                    f"Nested Behaviour found (Spawn Object), defining ModelID: {model_id} @ {hex(segment_addr)}")

                nested_behaviour = BehaviourParser.from_nested(
                    self.rom, segment_addr, self.depth + 1, model_id)
                self.children.append(nested_behaviour)
            elif cmd_id == 0x2D:
                ''' Set Init Position '''
            elif cmd_id == 0x2E:
                ''' Set Hurtbox '''
            elif cmd_id == 0x2F:
                ''' Set Interaction '''
            elif cmd_id == 0x30:
                ''' Set Gravity '''
            elif cmd_id == 0x31:
                ''' Set Interaction Subtype '''
            elif cmd_id == 0x32:
                ''' Scale Object '''
            elif cmd_id == 0x33:
                ''' Child Object Change '''
            elif cmd_id == 0x34:
                ''' Texture Animate Rate '''
            elif cmd_id == 0x35:
                ''' Clear Graph Flag (least significant bit) '''
            elif cmd_id == 0x36:
                ''' Set Value '''
            elif cmd_id == 0x37:
                ''' Spawn Something '''
            else:
                raise ValueError("Hit invalid command-id:", hex(cmd_id))

            command_bytes = self.rom.read_bytes(self.cursor, cmd_len)
            self.log(hex(self.cursor), format_binary(command_bytes))
            self.cursor += cmd_len
