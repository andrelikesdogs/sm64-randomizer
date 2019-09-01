import pytest

from Config import Config

def test_vanilla_rom():
  config = Config.find_configuration(0x635a42c5)  # Vanilla US ROM
  
  assert config is not None, "Configuration not found for Vanilla US ROM Checksum"

  assert config.name, "Missing Name"
  assert len(config.checksums) > 0, "Missing Checksums"
  assert len(config.levels) > 0, "Missing Levels"
  assert len(config.object_entries) > 0, "Missing Objects"
  assert not config.validation_errors
  assert not config.validation_warnings
  
  for entry in config.object_entries:
    print(entry)
    if entry["name"] != 'Default':
      assert entry["match"] is None or len(entry["match"]) > 0, "Empty matchings are only allowed for the 'Default' object definition"

simple_config_rom = '''
name: "Testing Suite Simple"
rom:
  - checksum: 0x123456
    name: "Testing Shit"
    macro_table_address: 0x0
    special_macro_table_address: 0x0
    defined_segments:
      - segment: 0x0
        start: 0x0
        end: 0x0

'''
simple_config_level = '''
levels:
  - name: "A Test Level"
    course_id: 0x12
    properties:
      - overworld

'''

# configuration with only one object
simple_config = \
  simple_config_rom + \
  simple_config_level + \
'''
object_randomization:
  objects:
    - name: "Test"
      match: 0x1234
      rules:
        - max_slope: 0.0

'''

def test_simple_config():
  config = Config.load_configuration_from_str(simple_config)

  assert config.name == 'Testing Suite Simple', "Invalid Name"
  assert config.checksums[0].get('checksum') == 0x123456, "Invalid Checksum"
  assert len(config.object_entries) == 2, "Invalid Object amount"
  assert config.object_entries[0].get('name') == 'Default', "No default object root"
  assert config.object_entries[1].get('name') == 'Test', "Invalid Order or no Test Object loaded"
  assert 0x12 in list(config.levels_by_course_id.keys()), "Level not loaded"

# configuration that nests objects with rules, checking if inheritance works
object_nesting_config = \
  simple_config_rom + \
  simple_config_level + \
'''
object_randomization:
  objects:
    - name: "Test"
      rules:
        - max_slope: 0.0
      objects:
        - name: "A"
          match: 0x1
          rules:
            - max_slope: 0.1
  
'''

def test_object_nesting():
  config = Config.load_configuration_from_str(object_nesting_config)

  assert len(config.object_entries) == 3, "Invalid Object amount"
  assert "Test" in list(map(lambda x: x["name"], config.object_entries)), "Name concatination invalid"
  assert len(config.object_entries[0].get('children')) == 1, "Invalid amount of children for root"

object_match_for_config = \
  simple_config_rom + \
  simple_config_level + \
'''
object_randomization:
  rules:
    - max_slope: 0.1
    - max_y: 1
    - underwater: never
  objects:
    - name: "Level 1"
      match: 0x13001234
      objects:
        - name: "Level 1 with [0x1]"
          match:
            - bparam1: 0x1
        - name: "Level 1 with [0x2]"
          match:
            - bparam1: 0x2
        - name: "Level 1 with 0x2"
          match:
            - bparam1: 0x3
    - name: "Level 1 but underwater"
      match:
        - course_property: disable_water_check
      for:
          - 'Level 1'
      rules:
        - underwater: allowed
'''

def test_object_match_for():
  config = Config.load_configuration_from_str(object_match_for_config)

  assert "Level 1" in list(map(lambda x: x["name"], config.object_entries)), "Level 1 did not get included"

  # match for rules
  assert "Level 1 but underwater: Level 1 with [0x1]" in list(map(lambda x: x["name"], config.object_entries)), "Nested object definitions did not get included"
  # main node too, not just children
  assert "Level 1 but underwater: Level 1" in list(map(lambda x: x["name"], config.object_entries)), "Nested object definition did not include the root object definition"
  
  for entry in config.object_entries:
    print(entry)
    if entry["name"] != 'Default':
      assert entry["match"] is not None and len(entry["match"]) > 0, "Empty matchings are only allowed for the 'Default' object definition"
