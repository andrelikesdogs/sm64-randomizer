import yaml
import os
from pathlib import Path
from typing import NamedTuple
import json

from .Constants import application_path

from .Level import Level
from .Area import Area

# Which entries are allowed in levels[] (...) .properties[]
LEVEL_PROPERTY_DEFINITIONS = {
  'disabled': ["bool", "list"], # Disable randomization completely or different functionalities
  'continues_level': ["int"], # This Level continues as another level and both should be treated as one, for entry randomization
  'key_receive': ["int"], # This level, when beaten, will give a key
  'fly_stage': ["bool"], # This level is played with a wing-cap
  'slide': ["bool"], # This level contains a slide
  'disable_water_check': ["bool"], # This level should act as if no water existed (for water that can be disabled/lowered/raised)
  'overworld': ["bool"], # This level is an overworld, and contains level entries
  'end_game': ["bool"], # This level will end the game
  'shuffle_painting': ["list"], # Defines this levels painting to be shuffled
  'shuffle_painting[].sections': ["list"],
  'shuffle_painting[].sections[].segment_index': ["int"],
  'shuffle_painting[].sections[].segment_offset': ["int"],
  'shuffle_painting[].sections[].size': ["list"],
  'shuffle_painting[].sections[].name': ["str"],
  'requires_key': ["list", "int", "str"],
  'loading_zones': ["list"],
  'disable_planes': ["list"],
  'shuffle_warps': ["list"],
  'shuffle_warps[].to': ["list"],
  'shuffle_warps[].to[].course_id': ["int"],
  'shuffle_warps[].with[].course_id': ["int"],
  'shuffle_warps[].to[].area_id': ["int"],
  'shuffle_warps[].with[].area_id': ["int"],
}

# Which entries are allowed in objects[] (...) .rules[]
RULE_DEFINITIONS = {
  'underwater': ["bool", "str"], # Underwater checks "allowed", "only" and "never". bool sets "underwater" to "allowed",
  'no_floor_required': ["bool"],
  'floor_types_allowed': ["str"], # "restricted", "all"
  'drop_to_floor': ["bool", "str"], # Enable that objects drop to floor. True, False or "force" to apply this behaviour also when it would result in an underwater position
  'max_y': ["int"], # Maximum Y allowed
  'min_y': ["int"], # Minimum Y allowed
  'max_floor_steepness': ["float"], # Maximum Slope allowed, 0 = completely flat, 1 = 90º wall
  'disabled': ["bool"], # Disable this object for randomization
  'spawn_height': ["list"], # Min/Max heights above floor
  'distance_to': ["list"],
  'bounding_box': ["list"], # length, width, height
  'bounding_cylinder': ["list"], # radius, height, (offset x, offset y, offset z)
  'max_uneven_distance': ["int"]
}

# Which entries are allowed in objects[] (...) .match[]
MATCH_DEFINITIONS = {
  'behaviours': ["int", "list"],
  'bparam1': ["int"],
  'bparam2': ["int"],
  'bparam3': ["int"],
  'bparam4': ["int"],
  'source': ["str"],
  'course_property': ["str", "list"],
  'course_id': ["int", "list"],
  'area_id': ["int", "list"],
}

ROOT_LEVEL_FIELDS = [
  "name",
  "rom",
  "levels",
  "object_randomization",
  "constants_file",
  "collision_groups",
  "custom_paintings"
]

CONSTANT_FILE_FIELDS = [
  "collision_types"
]

NL = "\n"

class Config:
  def __init__(self, filename, source):
    self.filename = filename
    self.name = "Unknown ROM Config"
    self.rom_settings = None
    self.checksums = []
    self.levels = []
    self.levels_by_course_id = {}
    self.object_entries = []
    self.object_entries_by_name = {}
    self.custom_paintings = None
    self.constants = {}
    self.collision_groups = {}

    self.validation_errors = []
    self.validation_warnings = []

    #print(json.dumps(source, indent=2))

    if os.path.exists("sm64_rando_rules.log"):
      os.unlink("sm64_rando_rules.log")

    if not self.validate(source):
      print(f"Validation Error founds:{NL}{NL.join(self.validation_errors)}")
      raise TypeError(f"{filename} is invalid")
    
    if len(self.validation_warnings):
      print(f"Config Warning: {filename} has warnings:{NL}{NL.join(self.validation_warnings)}")
    
    self.parse(source)
    
  def validate_properties(self, property_list, definitions):
    def_path = '"' + "\" -> \"".join(definitions) + '"'
    for property_index, prop in enumerate(property_list):
      prop_def_type = f'Entry #{property_index}'

      prop_type = None
      prop_value = None
      if type(prop) is dict:
        if len(prop.keys()) > 1:
          self.validation_errors.append(f'Invalid Property in {def_path} property {prop_def_type} - only 1 key is allowed in property objects')
          break
        elif len(prop.keys()) == 0:
          self.validation_errors.append(f'Invalid Property in {def_path} property {prop_def_type} - empty object passed')
          break
        else:
          prop_type = list(prop.keys())[0]
          prop_def_type = prop_type
          prop_value = prop[prop_type]
      elif type(prop) is str:
        prop_type = prop
        prop_value = True
        prop_def_type = prop_type
      
      if prop_type not in LEVEL_PROPERTY_DEFINITIONS:
        self.validation_errors.append(f'Invalid Property in {def_path} property {prop_def_type} - property is unknown')
      else:
        is_bool = type(prop_value) is str
        is_arr = type(prop_value) is list
        is_int = type(prop_value) is int
        is_dict = type(prop_value) is dict

        allowed_prop_types = LEVEL_PROPERTY_DEFINITIONS[prop_type]

        if is_bool and "bool" not in "bool" in allowed_prop_types:
          self.validation_errors.append(f'Invalid Property in {def_path} property {prop_def_type} - property is bool, allowed is {",".join(allowed_prop_types)}')
          break
        if is_arr and "list" not in allowed_prop_types:
          self.validation_errors.append(f'Invalid Property in {def_path} property {prop_def_type} - property is list, allowed is {",".join(allowed_prop_types)}')
          break
        if is_int and "int" not in allowed_prop_types:
          self.validation_errors.append(f'Invalid Property in {def_path} property {prop_def_type} - property is int, allowed is {",".join(allowed_prop_types)}')
          break
        if is_dict and "dict" not in allowed_prop_types:
          self.validation_errors.append(f'Invalid Property in {def_path} property {prop_def_type} - property is dict, allowed is {",".join(allowed_prop_types)}')
          break

  def validate_rules(self, rules, parents):
    for rule in rules:
      rule_type = None
      rule_value = None
      if type(rule) is dict:
        if len(rule.keys()) > 1:
          self.validation_errors.append(f'Invalid Rule property in "{" => ".join(parents)}" - supplied too many properties inside rule')
          continue
        elif len(rule.keys()) == 0:
          self.validation_errors.append(f'Invalid Rule property in "{" => ".join(parents)}" - empty property set in rule')
          continue
        else:
          rule_type = list(rule.keys())[0]
          rule_value = rule[rule_type]
      elif type(rule) is str:
        rule_type = rule
        rule_value = True
      else:
        self.validation_errors.append(f'Invalid Rule in "{" => ".join(parents)}" - {rule} either specify as key:value, or key')
        continue
      
      if rule_type not in RULE_DEFINITIONS:
        self.validation_errors.append(f'Invalid Rule in "{" => ".join(parents)}" - "{rule_type}" is unknown')
        continue
      
      is_bool = type(rule_value) is bool
      is_str = type(rule_value) is str
      is_int = type(rule_value) is int
      is_float = type(rule_value) is float

      allowed_rule_types = RULE_DEFINITIONS[rule_type]

      if is_bool and "bool" not in allowed_rule_types:
        self.validation_errors.append(f'Invalid Rule value in "{" => ".join(parents)}" - {rule_type} cant be a bool. Allowed is "{", ".join(allowed_rule_types)}"')
        continue
      if is_str and "str" not in allowed_rule_types:
        self.validation_errors.append(f'Invalid Rule value in "{" => ".join(parents)}" - {rule_type} cant be a string. Allowed is "{", ".join(allowed_rule_types)}"')
        continue
      if is_int and "int" not in allowed_rule_types:
        self.validation_errors.append(f'Invalid Rule value in "{" => ".join(parents)}" - {rule_type} cant be an int. Allowed is "{", ".join(allowed_rule_types)}"')
        continue
      if is_float and "float" not in allowed_rule_types:
        self.validation_errors.append(f'Invalid Rule value in "{" => ".join(parents)}" - {rule_type} cant be a float. Allowed is "{", ".join(allowed_rule_types)}"')
        continue

  def validate_match(self, match, parents):
    if type(match) is int:
      # default is behaviour, int is valid
      return
    elif type(match) is list:
      for entry in match:
        match_type = None
        match_value = None
        if type(entry) is dict:
          if len(entry.keys()) > 1:
            self.validation_errors.append(f'Invalid Match property in "{" => ".join(parents)}" - supplied too many properties inside matching rule')
            continue
          elif len(entry.keys()) == 0:
            self.validation_errors.append(f'Invalid Match property in "{" => ".join(parents)}" - supplied an empty match rule')
            continue
          else:
            match_type = list(entry.keys())[0]
            match_value = entry[match_type]
        elif type(entry) is str:
          match_type = entry
          match_value = True
        elif type(entry) is int:
          match_type = "behaviours"
          match_value = [entry]
        elif type(entry) is list:
          match_type = "behaviours"
          match_value = entry
        else:
          self.validation_errors.append(f'Invalid Match property in "{" => ".join(parents)}" - supplied an invalid type of rule-set for a match property. Either boolean or key:value')
          continue
        
        if match_type not in MATCH_DEFINITIONS:
          self.validation_errors.append(f'Invalid Match type in "{" => ".join(parents)}" - {match_type} is an invalid matching rule')
          continue
        
        is_bool = type(match_value) is bool
        is_str = type(match_value) is str
        is_list = type(match_value) is list
        is_dict = type(match_value) is dict

        allowed_match_types = MATCH_DEFINITIONS[match_type]

        if is_bool and "bool" not in allowed_match_types:
          self.validation_errors.append(f'Invalid Match property in "{" => ".join(parents)}" - bool values are not allowed for {match_type}. Allowed is "{", ".join(allowed_match_types)}"')
          continue
        if is_str and "str" not in allowed_match_types:
          self.validation_errors.append(f'Invalid Match property in "{" => ".join(parents)}" - str values are not allowed for {match_type}. Allowed is "{", ".join(allowed_match_types)}"')
          continue
        if is_list and "list" not in allowed_match_types:
          self.validation_errors.append(f'Invalid Match property in "{" => ".join(parents)}" - list values are not allowed for {match_type}. Allowed is "{", ".join(allowed_match_types)}"')
          continue
        if is_dict and "dict" not in allowed_match_types:
          self.validation_errors.append(f'Invalid Match property in "{" => ".join(parents)}" - dict values are not allowed for {match_type}. Allowed is "{", ".join(allowed_match_types)}"')
          continue      
    else:
      self.validation_errors.append(f'Invalid Match property in "{" => ".join(parents)}" - must either be list or behaviour address')

  def validate_objects(self, entries, parents = []):
    name = entries["name"] if len(parents) > 0 else "*"

    for entry_index, entry in enumerate(entries["objects"]):
      entry_name = entry["name"] if "name" in entry else "group"
      rules = entry["rules"] if "rules" in entry else []
      if len(rules):
        self.validate_rules(rules, [*parents, entry_name])

      match = entry["match"] if "match" in entry else None
      if match is not None:
        self.validate_match(match, [*parents, entry_name])

      excluded = entry["excluded"] if "excluded" in entry else []
      if len(excluded):
        self.validate_match(excluded, [*parents, entry_name])

      if "objects" in entry:
        self.validate_objects(entry, [*parents, entry_name])

  def validate_collision_groups(self, groups):
    if not len(self.constants.keys()):
      return
    
    all_defined_collision_types = self.constants["collision_types"]

    for collision_group in groups:
      has_white_or_blacklist = False

      allowed_entry_names = []
      if "blacklist" in groups[collision_group]:
        has_white_or_blacklist = True

        allowed_entry_names = set(all_defined_collision_types.keys()) - set(groups[collision_group]["blacklist"])

      if "whitelist" in groups[collision_group]:
        has_white_or_blacklist = True

        allowed_entry_names = set(groups[collision_group]["whitelist"])

      for entry_name in allowed_entry_names:
        if entry_name not in all_defined_collision_types.keys():
          self.validation_errors.append(f'Unknown collision type referenced "{entry_name}", please define this collision type in the constants file for this configuration.')
          return False

      allowed_entries = dict(map(lambda entry_name: (entry_name, all_defined_collision_types[entry_name]), allowed_entry_names))

      if not has_white_or_blacklist:
        self.validation_errors.append(f'Collisiongroup "{collision_group}" is not constrained - missing either "blacklist" or "whitelist" or both.')
        return False
      
      self.collision_groups[collision_group] = allowed_entries

  def validate_custom_paintings(self, source):
    authors = source.keys()

    for author in authors:
      for painting_definition in source[author]:
        if "name" not in painting_definition:
          self.validation_errors.append(f'Missing "name" field for custom painting')
          return False

        if "file" not in painting_definition:
          self.validation_errors.append(f'Missing "file" field for custom painting')
          return False
        else:
          if not os.path.exists(os.path.join(application_path, painting_definition["file"])):
            self.validation_errors.append(f'File not found for custom painting "{painting_definition["name"]}": "{painting_definition["file"]}"')
            return False

  def validate_constants(self, source):
    if "collision_types" not in source:
      self.validation_errors.append(f'Missing "collision_type" field in constants file for this configuration')
      return False
    
    unknown_fields = set(source.keys()) - set(CONSTANT_FILE_FIELDS)

    for field in unknown_fields:
      self.validation_warnings.append(f'Unknown constant file root-level field "{field}" - please check the documentation in Config/README.md')
    
    self.constants = source
    return True

  def read_and_validate_constants(self, filename):
    constants_path = Path(os.path.join(application_path, 'Config', filename))

    if not constants_path.exists():
      self.validation_errors.append(f'Could not find constants file "{filename}"')
      return False

    with open(constants_path, 'r') as constants:
      parsed = None
      try:
        parsed = yaml.safe_load(constants.read())
      except Exception as parser_error:
        print(f"Could not load constants file {filename}, parsing error:")
        print(parser_error)

      self.validate_constants(parsed)


  def validate(self, source):
    self.validation_errors = []
    self.validation_warnings = []

    self.found_root_fields = []

    if "name" not in source:
      self.validation_errors.append('Missing "name" property in configuration file')

      
    if "rom" not in source:
      self.validation_errors.append('Missing "rom" property in configuration file')
    else:
      for entry_index, rom_def in enumerate(source["rom"]):
        if "name" not in rom_def:
          self.validation_errors.append(f'Missing "name" in "rom" definition #{entry_index} in configuration')

        rom_def_name = rom_def["name"] if "name" in rom_def else f"Entry #{entry_index}"

        if "checksum" not in rom_def:
          self.validation_errors.append(f'Missing "checksum" in "rom" definition "{rom_def_name}" in configuration')
        
        if "defined_segments" in rom_def:
          for segment_index, segment in enumerate(rom_def["defined_segments"]):
            segment_def_id = segment["segment"] if "segment" in segment else "Entry #{segment_index}"

            if "segment" not in segment:
              self.validation_errors.append(f'Missing "segment" in "defined_segments" definition in {segment_def_id}')
            
            if "start" not in segment:
              self.validation_errors.append(f'Missing "start" in "defined_segments" definition in {segment_def_id}')
            if "end" not in segment:
              self.validation_errors.append(f'Missing "end" in "defined_segments" definition in {segment_def_id}')

    if "levels" not in source:
      self.validation_warnings.append(f'Missing "levels" in configuration file - No Level Shuffle available / Object Shuffle')
    else:
      self.found_root_fields.append("levels")
      for level_index, level in enumerate(source["levels"]):
        level_def_name = level["name"] if "name" in level else f"Entry #{level_index}"
        if "name" not in level:
          self.validation_errors.append(f'Missing "name" in "level" definition in {level_def_name}')
        
        if "course_id" not in level:
          self.validation_errors.append(f'Missing "course_id" in "level" definition in {level_def_name}')
        
        if "properties" in level:          
          self.validate_properties(level["properties"], [level_def_name])
        
        if "areas" in level:
          for area_index, area in enumerate(level["areas"]):
            area_def_name = area["name"] if "name" in level else f"Entry #{area_index}"
            if "name" not in area:
              self.validation_errors.append(f'Missing "name" in "level.areas" definition in {area_def_name}')
            if "id" not in area:
              self.validation_errors.append(f'Missing "id" in "level.areas" definition in {area_def_name}')
            if "properties" in area:
              self.validate_properties(area["properties"], [level_def_name, area_def_name])
    
    if "object_randomization" in source:
      self.validate_objects(source["object_randomization"])

    if "constants_file" not in source:
      self.validation_errors.append(f'Missing "constants" file - please define the "constants_file" key in the configuration')
    else:
      self.read_and_validate_constants(source["constants_file"])

    if "collision_groups" in source:
      self.validate_collision_groups(source["collision_groups"])

    if "custom_paintings" in source:
      self.validate_custom_paintings(source["custom_paintings"])

    unknown_fields = set(source.keys()) - set(ROOT_LEVEL_FIELDS)
    for field in unknown_fields:
      self.validation_warnings.append(f'Unknown root-level field "{field}" - please read the documentation: Config/README.md"')

    if len(self.validation_errors) > 0:
      return False
    return True

  def parse_property(self, prop):
    prop_name = None
    prop_value = None
    if type(prop) is dict:
      prop_name = list(prop.keys())[0]
      prop_value = prop[prop_name]
    elif type(prop) is str:
      prop_name = prop
      prop_value = True
    
    return (prop_name, prop_value)
    

  def parse_levels(self, levels):
    for level in levels:
      properties = {}
      if "properties" in level:
        for prop in level["properties"]:
          (key, value) = self.parse_property(prop)
          properties[key] = value

      areas = {}
      if "areas" in level:
        for area in level["areas"]:
          area_name = area["name"] if "name" in area else f"{level['name']} Area {hex(area['id'])}"

          area_properties = {}
          if "properties" in area:
            for prop in area["properties"]:
              (key, value) = self.parse_property(prop)
              area_properties[key] = value

          new_area = Area(area["id"], area_name, area_properties)
          areas[area["id"]] = new_area

      new_level = Level(level["course_id"], level["name"], properties, areas)

      self.levels.append(new_level)
      self.levels_by_course_id[level["course_id"]] = new_level
  
  def parse_object_table(self, table, rules = None, match = None, exclude = None):
    if rules is not None:
      rules = {**rules}
    else:
      rules = dict() # not as param default, to create a new dict

    name = "Default"
    exclude = None

    # Object Name
    if "name" in table:
      name = table["name"]

    # Object randomization rules
    if "rules" in table:
      for entry in table["rules"]:
        (key, value) = self.parse_property(entry)
        rules[key] = value

    # Object matching rules
    if "match" in table:
      if match is not None:
        match = {**match}
      else:
        match = dict()

      if type(table["match"]) is int:
        match["behaviours"] = [table["match"]]
      else:
        if type(table["match"]) is list:
          for entry in table["match"]:
            if type(entry) is int:
              if "behaviours" not in match:
                match["behaviours"] = []
              
              match["behaviours"].append(entry)
            if type(entry) is dict:
              prop_name = list(entry.keys())[0]
              if prop_name == "behaviours":
                match[prop_name] = [entry[prop_name]]
              else:
                match[prop_name] = entry[prop_name]

    # Exclude Matching
    if "exclude" in table:
      if exclude is not None:
        exclude = {**exclude}
      else:
        exclude = dict()

      if type(table["exclude"]) is int:
        exclude["behaviours"] = [table["exclude"]]
      else:
        if type(table["exclude"]) is list:
          for entry in table["exclude"]:
            if type(entry) is int:
              if "behaviours" not in exclude:
                exclude["behaviours"] = []
              
              exclude["behaviours"].append(entry)
            if type(entry) is dict:
              prop_name = list(entry.keys())[0]
              exclude[prop_name] = entry[prop_name]

    # Object matching for existing objects
    if "for" in table:
      for obj_name in table["for"]:
        if obj_name == "*":
          all_object_entry_names = list(self.object_entries_by_name.keys())
          for target_obj_name in all_object_entry_names:
            target = self.object_entries_by_name[target_obj_name]
            new_entries = []
            target_match = target["match"] if "match" in target and target["match"] is not None else dict()
            target_exclude = target["exclude"] if "exclude" in target and target["exclude"] is not None else dict()
            target_rules = target["rules"] if "rules" in target and target["rules"] is not None else dict()

            parent_match = (match or dict())
            parent_exclude = (exclude or dict())

            # print(target["name"], len(list(target_match.keys())))
            # don't add nodes with no matching property, those are groups
            if len(list(target_match.keys())) > 0:
              # print(f"{name}: {target['name']}")
              # add the entry itself
              new_entries.append(dict(
                match={
                  **target_match, # target, i.e. for-matches
                  **parent_match, # parent
                },
                exclude={
                  **target_exclude,
                  **parent_exclude,
                },
                rules={
                  **target_rules,
                  **rules,
                },
                from_for=True,
                name=f"{name}: {target['name']}"
              ))

            # add the entries children
            if "children" in target:
              children = target["children"]
              for child in children:
                child_match = child["match"] if child and "match" in child and child["match"] is not None else dict()
                child_exclude = child["exclude"] if child and "exclude" in child and child["exclude"] is not None else dict()

                # don't add children with no matching property, those are groups
                if len(list(child_match.keys())) > 0:
                  new_entries.append(dict(
                    match={
                      **child_match,
                      **parent_match
                    },
                    rules={
                      **child["rules"],
                      **rules,
                    },
                    exclude={
                      **child_exclude,
                      **parent_exclude
                    },
                    from_for=True,
                    name=f"{name}: {child['name']}"
                  ))
                
              for new_entry in new_entries:
                self.object_entries_by_name[new_entry["name"]] = new_entry
                self.object_entries.append(new_entry)
        else:
          if obj_name not in self.object_entries_by_name:
            raise ValueError(f"The object '{obj_name}' is not known. Please ensure it is not referenced before it's declared. This is a current limitation.")
          else:
            target = self.object_entries_by_name[obj_name]
            new_entries = []
            target_match = target["match"] if "match" in target and target["match"] is not None else dict()
            target_exclude = target["exclude"] if "exclude" in target and target["exclude"] is not None else dict()
            target_rules = target["rules"] if "rules" in target and target["rules"] is not None else dict()

            parent_match = (match or dict())
            parent_exclude = (exclude or dict())

            # print(target["name"], len(list(target_match.keys())))
            # don't add nodes with no matching property, those are groups
            if len(list(target_match.keys())) > 0:
              # print(f"{name}: {target['name']}")
              # add the entry itself
              new_entries.append(dict(
                match={
                  **target_match, # target, i.e. for-matches
                  **parent_match, # parent
                },
                exclude={
                  **target_exclude,
                  **parent_exclude,
                },
                rules={
                  **target_rules,
                  **rules,
                },
                from_for=True,
                name=f"{name}: {target['name']}"
              ))

            # add the entries children
            if "children" in target:
              children = target["children"]
              for child in children:
                child_match = child["match"] if child and  "match" in child and child["match"] is not None else dict()
                child_exclude = child["exclude"] if child and "exclude" in child and child["exclude"] is not None else dict()

                # print(child["name"], len(list(child_match.keys())))
                # don't add children with no matching property, those are groups
                if len(list(child_match.keys())) > 0:
                  new_entries.append(dict(
                    match={
                      **child_match,
                      **parent_match
                    },
                    rules={
                      **child["rules"],
                      **rules,
                    },
                    exclude={
                      **child_exclude,
                      **parent_exclude
                    },
                    from_for=True,
                    name=f"{name}: {child['name']}"
                  ))
                
              for new_entry in new_entries:
                self.object_entries_by_name[new_entry["name"]] = new_entry
                self.object_entries.append(new_entry)

      # Discard this entry, do not add to the list without the items it matched with "for"
      return

    object_whitelist_entry = dict(
      match=None,
      name=name,
      rules=rules,
      exclude=exclude,
      children=[]
    )
    if match is not None:
      object_whitelist_entry["match"] = match

    if name in self.object_entries_by_name:
      raise ValueError(f"Duplicate name: '{name}'. Please use unique names for Object placement rules")
    self.object_entries_by_name[name] = object_whitelist_entry
    self.object_entries.append(object_whitelist_entry)

    if "objects" in table:
      for object_table in table["objects"]:
        child = self.parse_object_table(object_table, rules, match, exclude)
        object_whitelist_entry["children"].append(child)
    
    return object_whitelist_entry
    
  def parse(self, source):
    if "name" in source:
      self.name = source["name"]
    
    for rom_definition in source["rom"]:
      self.checksums.append(rom_definition)
    
    if "custom_paintings" in source:
      self.custom_paintings = source["custom_paintings"]

    if "levels" in source:
      self.parse_levels(source["levels"])
    
    if "object_randomization" in source:
      self.parse_object_table(source["object_randomization"])
    
    with open("sm64_rando_rules.log", "a") as rule_log:
      for object_entry in self.object_entries:
        rule_log.write(json.dumps(object_entry) + "\n")

    print(f"Configuration '{self.name}' loaded {len(self.object_entries)} object-rule entries")

  def has_checksum_configuration(self, checksum):
    for rom_definition in self.checksums:
      if checksum == rom_definition["checksum"]:
        return True

  def set_checksum_configuration(self, checksum):
    for rom_definition in self.checksums:
      if checksum == rom_definition["checksum"]:
        self.rom_settings = rom_definition

  def __str__(self):
    if self.rom_settings is None:
      return f'<Config "{self.filename}"> (unloaded) {len(self.checksums)} checksums available'
    else:
      return f'<Config "{self.filename}" loaded for "{self.rom_settings["name"]}">'

  @staticmethod
  def load_configurations():
    config_files_found = []
    for file in os.listdir(os.path.join(application_path, 'Config')):
      config_file = Path(os.path.join(application_path, 'Config', file))

      if config_file.suffix == '.yml' or config_file.suffix == '.yaml':
        if "constants.y" in config_file.name:
          # ignore constants files
          continue

        with open(config_file, 'r') as config:
          try:
            parsed = yaml.safe_load(config.read())
            config_files_found.append((file, parsed))
          except Exception as parser_error:
            print(f"Could not load {file}, parsing error:")
            print(parser_error)
      
    configurations = list(map(lambda tup: Config(*tup), config_files_found))
    return configurations

  @staticmethod
  def load_configuration_from_str(configuration: str):
    parsed = yaml.safe_load(configuration)
    return Config('str_config.yml', parsed)

  @staticmethod
  def find_configuration(checksum):
    configurations = Config.load_configurations()

    if not len(configurations):
      raise TypeError("No configurations found. Check /Config folder for .yaml/.yml files")

    for configuration in configurations:
      if configuration.has_checksum_configuration(checksum):
        configuration.set_checksum_configuration(checksum)

        return configuration

  @staticmethod
  def from_checksum(checksum):
    pass