from random import shuffle, choice
import logging
import os

from sm64r.Constants import LVL_CASTLE_COURTYARD, LVL_CASTLE_INSIDE, LVL_CASTLE_GROUNDS, LVL_THI, ALL_LEVELS, LEVEL_ID_MAPPING, LEVEL_SHORT_CODES, LVL_BOWSER_1, LVL_BOWSER_1_BATTLE, LVL_BOWSER_2, LVL_BOWSER_2_BATTLE, LVL_BOWSER_3, LVL_BOWSER_3_BATTLE
from sm64r.Spoiler import SpoilerLog
from sm64r.RandomModules.Textures import TextureAtlas

if "SM64R" in os.environ and "WARPS" in os.environ["SM64R"]:
  import networkx as nx
  import plotly.offline as py
  import plotly.graph_objs as go
  
WARP_ID_MAPPING = {
  0xf0: 'SUCCESS',
  0xf1: 'FAILURE',
  0xf3: 'RECOVERY'
}

class WarpRandomizer:
  def __init__(self, rom : 'ROM'):
    self.rom = rom
    self.warps = []
    self.applied_change_list = []

  def _pick_best_fitting_warp(self, target_group_name, warp, warps_available):
    if target_group_name in list(warps_available.keys()):
      return choice(warps_available[target_group_name])

    target_key = choice(list(warps_available.keys()))
    return choice(warps_available[target_key])

  def shuffle_level_entries(self, settings : dict):
    # For different levels of SM64, we can assume there are 4 different types of warps we need to consider
    # these are not coded any differently, but they are important to find, to get a complete set of warps for any given "target level"
    # "entrances_src" - Found in Overworlds - Paintings, Holes in the floor
    # "entrances_dst" - Found in Target lvl - Entry positions into levels, mostly '0xa' for the beginning, marios spawn
    # "exits_dst"     - Found in Overworlds - Lead to themselves handle animations somehow. Level exit_srcs (0xf0, 0xf1, 0xf3) also lead to them
    # "exits_src"     - Found in Target lvl - `0xf0`, `0xf1` and `0xf3` (Win, Lose, Recovery/Pause-Exit)
    # 

    self.warps = []

    for level in self.rom.config.levels:
      for warp in self.rom.levelscripts[level].warps:
        self.warps.append(warp)

    # levels that contain entries to levels
    overworld_levels = list(filter(lambda level: "overworld" in level.properties, self.rom.config.levels))
    shuffle_warp_levels = list(filter(lambda level: "shuffle_warps" in level.properties, self.rom.config.levels))

    # both lists combined
    shuffleable_warp_levels = [*overworld_levels, *shuffle_warp_levels]

    target_levels = []

    # list of warps that are used for handling animations in ow levels
    all_exit_dst_warps = []

    # entrances for levels
    entrance_src_for_levels = {} # found in ow 
    entrance_dst_for_levels = {} # found in level
    exit_dst_for_levels = {} # found in ow
    exit_src_for_levels = {} # found in level

    # find warps *TO* levels
    # all levels that may contain entrance warps, this will find, e.g. overworld and HMC (to Metal Cap):
    # - entrance_srcs to levels
    # - exit_dsts from levels, not matched yet
    # 
    for level in shuffleable_warp_levels:
      for warp in self.rom.levelscripts[level].warps:
        target_level = self.rom.config.levels_by_course_id[warp.to_course_id]

        # Levels with disabled entry_shuffle
        if "disabled" in target_level.properties:
          if target_level.properties["disabled"] is True or "entry_shuffle" in target_level.properties["disabled"]:
            continue

        # Warps that lead to themselves
        if warp.to_warp_id == warp.warp_id and warp.to_area_id == warp.area_id and warp.to_course_id == warp.course_id:
          all_exit_dst_warps.append(warp) # we can't know where it's from until we check the levels
          continue
        
        # Levels that are overworlds
        if target_level in overworld_levels:
          continue
        
        if target_level not in entrance_src_for_levels:
          entrance_src_for_levels[target_level] = []

        if warp not in entrance_src_for_levels[target_level]:
          entrance_src_for_levels[target_level].append(warp)

        if target_level not in target_levels:
          target_levels.append(target_level)

    # find exits in levels we found entrances to
    # - exit_dsts in ow from levels, now matched
    # - exit_srcs in levels
    # - entrance_dsts in ow
    for level in entrance_src_for_levels.keys():
      # first, find all warps in the levels our entrance sources lead to
      for warp in self.rom.levelscripts[level].warps:
        # match with one of the exits we found in the overworlds/hub levels
        for exit_dst in all_exit_dst_warps:
          # matched warp must match area, course and warp-id
          if exit_dst.warp_id == warp.to_warp_id and exit_dst.course_id == warp.to_course_id and exit_dst.area_id == warp.to_area_id:
            if level not in exit_dst_for_levels:
              exit_dst_for_levels[level] = []

            if exit_dst not in exit_dst_for_levels[level]:
              # save anim type (success, failure or recovery) on exit_dst
              exit_dst.anim_type = WARP_ID_MAPPING[warp.warp_id] if warp.warp_id in WARP_ID_MAPPING else None

              exit_dst_for_levels[level].append(exit_dst) # this was previously not matched to a level

            if level not in exit_src_for_levels:
              exit_src_for_levels[level] = []

            if warp not in exit_src_for_levels[level]:
              exit_src_for_levels[level].append(warp)

        # match entrance destinations with level warps
        for entrance_src in entrance_src_for_levels[level]:
          # (course_id will always match, because we're checking the warps from and to this level)
          # must match warp_id <-> to_warp_id, area_id (in which area) <-> to_area_id
          if entrance_src.to_warp_id == warp.warp_id and entrance_src.to_area_id == warp.area_id and entrance_src.to_course_id == warp.course_id:
            if level not in entrance_dst_for_levels:
              entrance_dst_for_levels[level] = []

            if warp not in entrance_dst_for_levels[level]:
              entrance_dst_for_levels[level].append(warp)

      # add exit warps from continued levels, i.e. from the fight stages in bowser levels
      if "continues_level" in level.properties:
        course_ids = level.properties["continues_level"] if type(level.properties["continues_level"]) is list else [level.properties["continues_level"]]
        continued_levels = list(map(lambda x: self.rom.config.levels_by_course_id[x], course_ids))

        if level not in exit_dst_for_levels or level not in exit_src_for_levels:
          print(f"WARNING: continued level for \"{level.name}\" without any warps of itself - how is this even possible")
        else:
          for continued_level in continued_levels:
            for warp in self.rom.levelscripts[continued_level].warps:
              for exit_dst in all_exit_dst_warps:
                if exit_dst.warp_id == warp.to_warp_id and exit_dst.course_id == warp.to_course_id and exit_dst.area_id == warp.to_area_id:
                  # NOTE: we're adding the warp exits to the LEVELs exit destination warps, not to the continued levels destination warps
                  # as it won't have one seperately. this means during shuffling, the exits in this continued level will behave the same way
                  # as if the warps were simply in the original stage.

                  exit_dst.anim_type = WARP_ID_MAPPING[warp.warp_id] if warp.warp_id in WARP_ID_MAPPING else None
                  exit_dst_for_levels[level].append(exit_dst)
                  exit_src_for_levels[level].append(warp)

    # pool of warps that can be shuffled between
    warp_pools = {}
    # all warp sets
    all_warp_sets = []

    # Create "warp sets" that lead from ow to level and from level to ow
    for target_level in target_levels:
      #print(target_level.name)
      source_level = None
      warp_set = dict(
        source_level=None,
        target_level=target_level,
        allowed=[],
        entrance_srcs=[],
        entrance_dsts=[],
        exit_srcs=[],
        exit_dsts=[]
      )

      if target_level in entrance_src_for_levels:
        warp_set["entrance_srcs"] = entrance_src_for_levels[target_level]

        # use an entry from entrance sources to get the source level
        first_entrance = entrance_src_for_levels[target_level][0]
        source_level = self.rom.config.levels_by_course_id[first_entrance.course_id]
        warp_set["source_level"] = source_level

      if target_level in entrance_dst_for_levels:
        warp_set["entrance_dsts"] = entrance_dst_for_levels[target_level]

      if target_level in exit_src_for_levels:
        warp_set["exit_srcs"] = exit_src_for_levels[target_level]

      if target_level in exit_dst_for_levels:
        warp_set["exit_dsts"] = exit_dst_for_levels[target_level]

      if "shuffle_warps" in source_level.properties:
        # create whitelist for allowed shuffles
        satisfies_all_rules = None
        matching_ruleset = []
        
        for rules in source_level.properties["shuffle_warps"]:
          satisfies_all_rules = None
        
          for rule in rules["to"]:
            satisfies_all_rules = True

            if "course_id" in rule and rule["course_id"] != target_level.course_id:
              satisfies_all_rules = False
            
            if satisfies_all_rules:
              break
          
          if satisfies_all_rules:
            matching_ruleset = rules["with"]
        
        warp_set["allowed"] = matching_ruleset

      pool = frozenset([frozenset(rule.items()) for rule in warp_set["allowed"]])
      if pool not in warp_pools:
        warp_pools[pool] = []
      warp_pools[pool].append(warp_set)
      all_warp_sets.append(warp_set)
      #print("Appending", warp_set["target_level"].name, pool)

    # Existing level paintings
    lvl_painting_names = {}
    new_level_warps = []

    # This part will generate new warp connections until one is "valid" aka in logic
    while len(new_level_warps) == 0 or not self.validate_path_for_keys(new_level_warps):
      # because warps are grouped by the connections that are allowed, shuffling inside
      # these groups will always follow the rules
      # FIXME: one-way connections (i.e. wing-cap could be vanish cap but not the other way around)
      #        will not work and always result in unshuffled levels

      new_level_warps = []
      # go through pools, shuffle within those pools and assign warps
      for ruleset, warpsets in warp_pools.items():
        ### Debug Warpsets
        """
        print('-' * 30)
        print(ruleset)
        for warpset in warpsets:
          print(f"Warps from {warpset['source_level'].name} to {warpset['target_level'].name}")
          print(f" Entrances: SRC: {len(warpset['entrance_srcs'])}    DEST: {len(warpset['entrance_dsts'])}")
          print(f" Exits:     SRC: {len(warpset['exit_srcs'])}    DEST: {len(warpset['exit_dsts'])}")
        """

        ### Split into Overworld and Levels for each pool
        pool_warpset_ow = [] # from
        pool_warpset_lvl = [] # to

        for warpset in warpsets:
          # add painting to shuffle-able list of paintings
          if "shuffle_painting" in warpset["target_level"].properties:
            shuffle_painting_properties = warpset["target_level"].properties["shuffle_painting"]

            if len(shuffle_painting_properties) > 1:
              print(f'Warning: Only one painting shuffle is allowed per level. Please check properties of "{warpset["target_level"]}".')
            else:
              shuffle_painting_definiton = shuffle_painting_properties[0]
              # add in-game painting to shuffle-able list
              if "game_painting" in shuffle_painting_definiton.keys():
                lvl_painting_names[warpset["target_level"]] = shuffle_painting_definiton["game_painting"]

              # add custom painting to shuffle-able list
              if "custom_painting" in shuffle_painting_definiton.keys():
                lvl_painting_names[warpset["target_level"]] = shuffle_painting_definiton["custom_painting"]
            
          pool_warpset_ow.append(dict(
            level=warpset["target_level"],
            entrances=warpset["entrance_srcs"],
            exits=warpset["exit_dsts"]
          ))
          pool_warpset_lvl.append(dict(
            level=warpset["target_level"],
            entrances=warpset["entrance_dsts"],
            exits=warpset["exit_srcs"]
          ))

        # Perform the shuffle
        shuffle(pool_warpset_ow)
        shuffle(pool_warpset_lvl)

        # Link them back together
        for group_idx in range(len(pool_warpset_ow)):
          ow_set = pool_warpset_ow[group_idx]
          lvl_set = pool_warpset_lvl[group_idx]

          new_level_warps.append(
            (ow_set, lvl_set)
          )
      
      #for (ow_set, lvl_set) in new_level_warps:
        #print(f'{ow_set["level"].name} now goes to {lvl_set["level"].name}')
      #print('-' * 20)

    # If random paintings enabled, shuffle the key:value pairs in lvl_paintings
    if "shuffle_paintings" in settings:
      if settings["shuffle_paintings"] == "random":
        keys = list(lvl_painting_names.keys())
        shuffled_keys = [*keys]
        shuffle(shuffled_keys)
        for key in keys:
          lvl_painting_names[key] = lvl_painting_names[shuffled_keys]
    
    # list of changes that will be done
    change_list = []

    # actually link together warps
    for (ow_set, lvl_set) in new_level_warps:
      SpoilerLog.add_entry('warps', f'{ow_set["level"].name} leads to {lvl_set["level"].name}')
      #print(f'{ow_set["level"].name} now goes to {lvl_set["level"].name}')

      # link overworld entrances to new level
      for idx in range(len(ow_set["entrances"])):
        src = ow_set["entrances"][idx]
        dst = choice(lvl_set["entrances"])
        change_list.append((src, dst.course_id, dst.area_id, dst.warp_id))
      
      # relink exits
      for idx in range(len(lvl_set["exits"])):
        src = lvl_set["exits"][idx]
        src.anim_type = WARP_ID_MAPPING[src.warp_id] if src.warp_id in WARP_ID_MAPPING else None
        targets = []
        target = choice(ow_set["exits"]) # fallback: pick random if no fitting targets
        
        if not src.anim_type:
          # if an exit warp inside a level is not one of the success, defeat or recovery warp types
          # it means this level can link to another level. like HMC to MC
          continue
        
        for dst in ow_set["exits"]:
          if dst.anim_type == src.anim_type:
            targets.append(dst)
        
        if len(targets):
          target = choice(targets)
        
        change_list.append((src, target.course_id, target.area_id, target.warp_id))
      
      if "shuffle_paintings" in settings and settings["shuffle_paintings"] != "off":
        if "shuffle_painting" in ow_set["level"].properties:
          if len(ow_set["level"].properties["shuffle_painting"]) > 1:
            print(f'Warning: Only one painting shuffle is allowed per level. Please check properties of "{warpset["target_level"]}".')
          else:
            source_painting_definition = ow_set["level"].properties["shuffle_painting"][0]          
            
            # replace this
            source_painting_name = source_painting_definition["game_painting"] if "game_painting" in source_painting_definition else source_painting_definition["custom_painting"]

            # with this
            target_painting_name = lvl_painting_names[lvl_set["level"]]
            #print("setting painting from ", source_painting_name, " to ", target_painting_name)

            # don't copy if it's the same
            if source_painting_name != target_painting_name:
              # ensure we have a copy-able texture
              if not TextureAtlas.has_texture(target_painting_name):
                target_painting_name = "painting_unknown" # use replacement texture

              # ensure target is replaceable, textures loaded externally are not
              if TextureAtlas.is_replacable(source_painting_name):
                TextureAtlas.copy_texture_from_to(self.rom, target_painting_name, source_painting_name)

    self.applied_change_list = change_list

    for (target, course_id, area_id, warp_id) in change_list:
      target.set(self.rom, "to_course_id", course_id)
      target.set(self.rom, "to_area_id", area_id)
      target.set(self.rom, "to_warp_id", warp_id)

    ### Debug View
    '''
    for target_level in target_levels:
      print(f" Warps found for {target_level.name}")
      if target_level in entrance_src_for_levels:
        print(f" Entry Sources: {len(entrance_src_for_levels[target_level])}")
        for w in entrance_src_for_levels[target_level]:
          print(w)
      else:
        print(" No Entry Sources")
      
      if target_level in entrance_dst_for_levels:
        print(f" Entry Destinations: {len(entrance_dst_for_levels[target_level])}")
        for w in entrance_dst_for_levels[target_level]:
          print(w)
      else:
        print(" No Entry Destinations")
      
      if target_level in exit_src_for_levels:
        print(f" Exit Sources: {len(exit_src_for_levels[target_level])}")
        for w in exit_src_for_levels[target_level]:
          print(w)
      else:
        print(" No Exit Sources")
      
      
      if target_level in exit_dst_for_levels:
        print(f" Exit Destinations: {len(exit_dst_for_levels[target_level])}")
        for w in exit_dst_for_levels[target_level]:
          print(w)
      else:
        print(" No Exit Destinations")
      
      print("-" * 30)
    '''
  
  def validate_path_for_keys(self, changelist):
    indiv_key_requirements_per_level = {}
    total_key_requirements_per_level = {}
    key_sources = {}

    # from = original entry position
    # to = new entry position

    # collect requires_key and key_receive groups
    for (from_warps, to_warps) in changelist:
      key_requirements = []
      if "requires_key" in from_warps["level"].properties:
        requires_key = from_warps["level"].properties["requires_key"]
        key_requirements = [requires_key] if type(requires_key) is not list else requires_key

      if "key_receive" in to_warps["level"].properties:
        key_sources[to_warps["level"].properties["key_receive"]] = to_warps["level"]
        #print(to_warps["level"].name, " awards ", to_warps["level"].properties["key_receive"])
      
      #awards_text = "" if "key_receive" not in to_warps["level"].properties else f' and rewards \"{to_warps["level"].properties["key_receive"]}\"'
      #print(to_warps["level"].name, " now requires ", key_requirements, awards_text)
      indiv_key_requirements_per_level[to_warps["level"]] = key_requirements

    # define function to recursively gather all keys required per level
    def recurse_find_keys_needed(level, keys, acc):
      for key in keys:
        if key not in acc:
          acc.add(key)
          level_req = key_sources[key]
          #print("key ", key, " found in ", level_req)

          level_req_keys = indiv_key_requirements_per_level[level_req]
          recurse_find_keys_needed(level_req, level_req_keys, acc)
      return acc
    
    # define total keys per level via above recursive func
    for level, keys in indiv_key_requirements_per_level.items():
      total_key_requirements_per_level[level] = recurse_find_keys_needed(level, keys, set())
      #print(level, indiv_key_requirements_per_level[level], total_key_requirements_per_level[level])

      if "key_receive" in level.properties and level.properties["key_receive"] in total_key_requirements_per_level[level]:
        print(f"{level.name} requires {total_key_requirements_per_level[level]} but rewards {level.properties['key_receive']} - invalid")
        return False
        

    return True

  def plot_network(self):
    G = nx.DiGraph()

    def key_from_warp(warp):
      return f'{hex(warp.course_id)} ({hex(warp.area_id)}): {hex(warp.warp_id)}'

    warp_by_key = {}
    all_connections = {}

    for warp in self.warps:
      warp_key = key_from_warp(warp)
      warp_by_key[warp_key] = warp

    for warp in self.warps:
      target_key = f'{hex(warp.to_course_id)} ({hex(warp.to_area_id)}): {hex(warp.to_warp_id)}'
      target_warp = warp_by_key[target_key]
      all_connections[warp] = target_warp

    for (src_warp, target_course_id, target_area_id, target_warp_id) in self.applied_change_list:
      target_key = f'{hex(target_course_id)} ({hex(target_area_id)}): {hex(target_warp_id)}'
      target_warp = warp_by_key[target_key]
      all_connections[src_warp] = target_warp

    for src_warp, target_warp in all_connections.items():
      G.add_edge(key_from_warp(src_warp), key_from_warp(target_warp))

    pos = nx.spring_layout(G)

    #plt.subplot()
    #nx.draw(G, with_labels=True)
    #plt.show()
    edge_x = []
    edge_y = []
    for edge in G.edges():
      x0, y0 = pos[edge[0]]
      x1, y1 = pos[edge[1]]
      edge_x.append(x0)
      edge_x.append(x1)
      edge_x.append(None)
      edge_y.append(y0)
      edge_y.append(y1)
      edge_y.append(None)

    edge_trace = go.Scatter(
      x=edge_x, y=edge_y,
      line=dict(width=0.5, color='#888'),
      hoverinfo='none',
      mode='lines')

    node_x = []
    node_y = []
    node_text = []
    node_colors = []
    for node in G.nodes():
      x, y = pos[node]
      node_x.append(x)
      node_y.append(y)

      warp = warp_by_key[node]
      target_level = self.rom.config.levels_by_course_id[warp.to_course_id]
      #print(warp_by_key[node])
      node_text.append(f'{target_level.name} (Area: {hex(warp.area_id)}): {hex(warp.warp_id)}')

      if warp.warp_id in WARP_ID_MAPPING.values():
        node_colors.append('#ff0000')
      elif warp.warp_id == 0xa:
        node_colors.append('#0000ff')
      else:
        node_colors.append('#aeaeae')

    node_trace = go.Scatter(
      x=node_x, y=node_y,
      mode='markers',
      hoverinfo='text',
      marker=dict(
        color=[],
        colorscale='YlGnBu',
        line_width=2))
    
    node_trace.text = node_text
    #node_trace.color = node_colors
    fig = go.Figure(data=[edge_trace, node_trace],
             layout=go.Layout(
                showlegend=False,
                hovermode='closest',
                annotations=[ dict(
                    showarrow=False,
                    xref="paper", yref="paper",
                    x=0.005, y=-0.002 ) ],
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
    )
    
    py.plot(fig, filename=f'dumps/warp_graph/Warps.html', auto_open=True)
'''

  def shuffle_level_entries_old(self, painting_mode : str):
    # levels that contain entries to levels
    entry_levels = [LVL_CASTLE_COURTYARD, LVL_CASTLE_GROUNDS, LVL_CASTLE_INSIDE]
    entry_level_course_ids = [level.level_id for level in entry_levels]

    # anim warps are warps in the overworld that simply connect to themselves.
    # they confuse me but i suspect they only handle animation stuff

    anim_warps = [] # Warp, Warp, Warp
    ow_warps = {} # { (Level, Area): ([Entry Warp, Entry Warp], (Anim Exit, Anim Exit)), (Entry, Anim Exits), (Entry, Anim Exits)
    lvl_warps = {} # { (Level, Area): FAIL: [ Warp, Warp ], SUCCESS: Warp, Warp }

    # go through all levels that contain entries (all castle levels)
    for level in entry_levels:
      # go through all warps, take note of the special animated warps
      # they can be identified by their warp_id leading to their target_warp_id
      for warp in self.rom.levelscripts[level].warps:
        # painting warps and warp-ids that match levels without a painting a grouped by
        # target-level and target-area-id to ensure we don't break THI
        if warp.type == 'PAINTING' or  warp.to_course_id in COURSES_WITH_NO_PAINTING:
          target_level = LEVEL_ID_MAPPING[warp.to_course_id]
          key = (target_level, warp.to_area_id)

          ow_warps.setdefault(key, ([], {})) # level entries (paintings, holes, etc), anim exits (lead to themselves)

          ow_warps[key][0].append(warp)
        else:
          # special target == dest warps
          if warp.warp_id == warp.to_warp_id:
            anim_warps.append(warp)
    
    anim_warp_ids = [warp.warp_id for warp in anim_warps]

    # now collects all exits from the levels we have the entries of
    warp_types = {
      0xf0: "SUCCESS",
      0xf1: "FAILURE",
      #0xf3: "RECOVER", # ye let's not shuffle this for now
    }
    for key in ow_warps.keys():
      (level, area_id) = key

      lvl_warps[key] = {}

      # get all warps inside the level that target this level and this area_id
      search_targets = [level]
      if level in LEVEL_CONNECTED_WARPS:
        search_targets.extend(LEVEL_CONNECTED_WARPS[level])

      for search_level in search_targets:
        for warp in self.rom.levelscripts[search_level].warps:
          # 1. warp must lead to one of the anim exits from the overworld
          # 2. warp must lead to one of the OW levels
          # 3. warp must be of one of the warp types
          if warp.to_warp_id in anim_warp_ids and warp.to_course_id in entry_level_course_ids and warp.warp_id in warp_types:
            if level not in MUST_MATCH_AREA_LEVELS or warp.area_id == area_id:
              warp_type = warp_types[warp.warp_id]

              # add a specific warp-type to the exits list
              lvl_warps[key].setdefault(warp_type, []).append(warp)
              
              # add all the anim warps that this warp refers to
              ow_warps[key][1].setdefault(warp_type, []).extend([anim_warp for anim_warp in anim_warps if anim_warp.warp_id == warp.to_warp_id])

    # Debug View of all Warps found
    for ((level, area), (entry_warps, anim_warp_groups)) in ow_warps.items():
      logging.debug(f'Level: {level.name} Area: {hex(area)}')

      logging.debug("  Exits")
      for (warp_group, exit_warps) in lvl_warps[(level, area)].items():
        logging.debug(" " * 2 + str(warp_group))
        logging.debug(" " * 4 + repr([(hex(warp.to_warp_id), hex(warp.memory_address)) for warp in exit_warps]))
      logging.debug('')
      logging.debug("  Entries:")
      logging.debug(repr([(hex(warp.warp_id), hex(warp.memory_address)) for warp in entry_warps]))
      logging.debug('')
      logging.debug("  Anim Warps:")
      for (anim_warp_group, entry_anim_warps) in anim_warp_groups.items():
        logging.debug(" " * 2 + str(anim_warp_group))
        logging.debug(" " * 4 + repr([(hex(warp.to_warp_id), hex(warp.memory_address)) for warp in entry_anim_warps]))
      logging.debug('-' * 50)

    valid_warps = False
    target_warp_levels = list(lvl_warps.keys())
    #shuffle(target_warp_levels)

    while not valid_warps:
      shuffle(target_warp_levels)

      idx = 0
      valid_warps = True
      for ((original_level, original_area), ow_entry_exit_sets) in ow_warps.items():
        (target_level, target_area) = target_warp_levels[idx]

        # ensure correct order
        if target_level in ENFORCE_ORDER.keys():
          logging.info(f'ensuring validity with level {target_level.name}')
          # bowser in the fire sea for example can't be on the first floor, because that's the boss that gives you the key for the first floor
          if original_level in ENFORCE_ORDER[target_level]:
            logging.info(f'{target_level.name} cant be in {original_level}, because it cant be reached without it')
            valid_warps = False
            break
        idx += 1

    idx = 0
    for (original_level_area, (entries, anim_exits)) in ow_warps.items():
      level_area_target = target_warp_levels[idx]
      SpoilerLog.add_entry('warps', f'{original_level_area[0].name} leads to {level_area_target[0].name}')
      #print(f'{original_level_area[0].name} now leads to {level_area_target[0].name} ({len(entries)} entries updating)')
      for entry_warp in entries:
        #print(hex(level_area_target[0].level_id))
        entry_warp.set(self.rom, "to_course_id", level_area_target[0].level_id)
        entry_warp.set(self.rom, "to_area_id", level_area_target[1])

      orig_exits = lvl_warps[original_level_area]
      level_exits = lvl_warps[level_area_target]

      # replace all exit warps in the target level with ones leading to the original entry
      for (group_name, warps) in level_exits.items():
        logging.info(f'{level_area_target[0].name.ljust(40, " ")} (Area {hex(level_area_target[1])}): {group_name}: Animation Warps replacing {len(warps)} entries')
        for warp in warps:
          target_warp = self._pick_best_fitting_warp(group_name, warp, orig_exits)
          warp.set(self.rom, "to_course_id", target_warp.to_course_id)
          warp.set(self.rom, "to_warp_id", target_warp.to_warp_id)
          warp.set(self.rom, "to_area_id", target_warp.to_area_id)
      idx += 1


    if painting_mode == 'random':
      shuffle(target_warp_levels)

    # set paintings
    idx = 0
    for (original_level_area, (entries, anim_exits)) in ow_warps.items():
      if painting_mode != 'vanilla':
        level_area_target = target_warp_levels[idx]

        if original_level_area[0] in LEVEL_SHORT_CODES and level_area_target[0] in LEVEL_SHORT_CODES:
          from_code = f'painting_{LEVEL_SHORT_CODES[original_level_area[0]].lower()}'
          to_code = f'painting_{LEVEL_SHORT_CODES[level_area_target[0]].lower()}'

          if TextureAtlas.has_texture(from_code):
            if TextureAtlas.has_texture(to_code):
              TextureAtlas.copy_texture_from_to(self.rom, from_code, to_code)
            else:
              TextureAtlas.copy_texture_from_to(self.rom, from_code, 'painting_unknown')

      idx += 1

    original_warps = list(warp_connections.items())
    target_warps = list(warp_connections.items())
    shuffle(target_warps)

    for idx, (level, area) in enumerate(target_warps):
      original_warp = original_warps[idx]
      print(f'{original_warp[0][0].name} now leads to {level[0].name}')
      pass
      

    for level_exits in lvl_warps:
      for level_exit in level_exits:
        pass

    print(len(lvl_warps))
    print(len(ow_warps_by_level_by_area.keys()))
    #print('\n'.join([str(item) for item in ow_warps_cleaned_dict.items()]))'''