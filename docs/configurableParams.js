configurableParams = [
  {
    "name": "seed",
    "label": "Random Seed",
    "category": "gameplay",
    "type": "text",
    "help": "Allows you to play the same version as a friend, simply enter the same seed as them and you will be playing the exact same ROM."
  },
  {
    "name": "shuffle-paintings",
    "label": "Painting (Art) randomization",
    "category": "aesthetics",
    "type": "select",
    "default": "match",
    "options": [
      {
        "value": "vanilla",
        "label": "Off"
      },
      {
        "value": "match",
        "label": "Match Levels"
      },
      {
        "value": "replace-unknown",
        "label": "Use Custom Paintings for Unknown Paintings"
      },
      {
        "value": "random",
        "label": "Randomized"
      }
    ],
    "help": "Change the behaviour of how the paintings in the castle are shuffled (\"match\" - matches randomized levels, i.e. painting = level, \"random\" - independently randomize paintings, \"off\" - leave paintings untouched)"
  },
  {
    "name": "custom-painting-author",
    "label": "Custom Painting (Art) Author",
    "category": "aesthetics",
    "type": "select",
    "default": "mika",
    "options": [
      {
        "value": "disable",
        "label": "Disabled"
      },
      {
        "value": "mika",
        "label": "Mika"
      }
    ],
    "help": "This property allows changing the custom paintings to a different author, if you want to add your own, see the sm64.vanilla.yml"
  },
  {
    "name": "shuffle-skybox",
    "label": "Sky randomization",
    "category": "aesthetics",
    "type": "checkbox",
    "default": false,
    "help": "Randomizes the sky-texture between different levels. The black skybox is excluded."
  },
  {
    "name": "shuffle-entries",
    "label": "Entrance Randomizer",
    "category": "gameplay",
    "type": "checkbox",
    "default": {
      "CLI": false,
      "WEB": true
    },
    "help": "Shuffles the levelentries. When you enter a level, you will end up at a random one."
  },
  {
    "name": "shuffle-mario-outfit",
    "label": "Mario's Outfit Randomizer",
    "category": "aesthetics",
    "type": "checkbox",
    "default": {
      "CLI": false,
      "WEB": true
    },
    "help": "Randomizes parts of Marios Outfit."
  },
  {
    "name": "shuffle-music",
    "label": "Music Randomizer",
    "category": "aesthetics",
    "type": "checkbox",
    "default": {
      "CLI": false,
      "WEB": false
    },
    "help": "Randomizes most songs in the game."
  },
  {
    "name": "shuffle-objects",
    "label": "Object Shuffle",
    "category": "gameplay",
    "type": "checkbox",
    "default": {
      "CLI": false,
      "WEB": true
    },
    "help": "Shuffles Objects in Levels"
  },
  {
    "name": "shuffle-colors",
    "label": "Randomize Colors",
    "category": "aesthetics",
    "type": "checkbox",
    "default": {
      "CLI": false,
      "WEB": true
    },
    "help": "Shuffle various colors in the game"
  },
  {
    "name": "shuffle-text",
    "label": "Randomize Dialog/Text",
    "category": "aesthetics",
    "type": "checkbox",
    "default": {
      "CLI": false,
      "WEB": true
    },
    "help": "Shuffle Dialog text, for signs, npc dialog, level dialog and prompts."
  },
  {
    "name": "shuffle-instruments",
    "label": "Instrument-Set Shuffle",
    "category": "aesthetics",
    "type": "checkbox",
    "default": {
      "CLI": false,
      "WEB": false
    },
    "help": "Shuffles instrument sounds around. Many different objects and songs use different instrument sets, as the N64 can't load all at once. This will shuffle them around. Might be wacky."
  },
  {
    "name": "disable-cutscenes",
    "label": "Disable Cutscenes/Intro",
    "category": "gameplay",
    "type": "checkbox",
    "default": {
      "CLI": false,
      "WEB": true
    },
    "help": "Disables some of the games cutscenes. (Peach Intro, Lakitu Intro, Bowser-Text on Entry)"
  }
]