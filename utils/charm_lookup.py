"""
Look up dict for charm rarity
"""
charm_lookup = {
  'Marathon Charm I':           4,
  'Marathon Charm II':          5,
  'Marathon Charm III':         6,

  'Fitness Charm I':            4,
  'Fitness Charm II':           5,
  'Fitness Charm III':          6,
  'Fitness Charm IV':           7,
  'Fitness Charm V':            8,

  'Sheathe Charm I':            4,
  'Sheathe Charm II':	          5,
  'Sheathe Charm III':	        6,

  'Challenger Charm I':	        5,
  'Challenger Charm II':        7,

  'Unscathed Charm I':	        5,
  'Unscathed Charm II':	        7,

  'Fury Charm I':	              5,
  'Fury Charm II':	            7,

  'Exploiter Charm I':	        5,
  'Exploiter Charm II':	        7,

  'Power Charm I':	            5,
  'Power Charm II':             7,
  'Power Charm III':	          8,

  'Mighty Charm I':	            5,
  'Mighty Charm II':	          7,

  'Surge Charm I':	            4,
  'Surge Charm II':	            5,
  'Surge Charm III':	          6,

  'Defense Charm I':	          2,
  'Defense Charm II':	          4,
  'Defense Charm III':	        5,
  'Defense Charm IV':	          6,
  'Defense Charm V':	          7,

  'Blessing Charm I':	          3,
  'Blessing Charm II':	        4,
  'Blessing Charm III':	        5,

  'Recovery Charm I':	          3,
  'Recovery Charm II':	        4,
  'Recovery Charm III':	        6,

  'Speed Heal Charm I':	        2,
  'Speed Heal Charm II':	      4,
  'Speed Heal Charm III':	      5,

  'Glutton\'s Charm I':	        2,
  'Glutton\'s Charm II':	      4,
  'Glutton\'s Charm III':	      5,

  'Earplugs Charm I':	          6,
  'Earplugs Charm II':	        7,

  'Windproof Charm I':	        4,
  'Windproof Charm II':	        5,
  'Windproof Charm III':	      6,

  'Tremor Charm I':             4,
  'Tremor Charm II':	          5,
  'Tremor Charm III':	          6,

  'Evasion Charm I':	          4,
  'Evasion Charm II':	          5,
  'Evasion Charm III':	        6,
  'Evasion Charm IV':	          7,

  'Leaping Charm I':	          4,
  'Leaping Charm II':	          5,
  'Leaping Charm III':	        6,

  'Fire Charm I':	              2,
  'Fire Charm II':	            4,
  'Fire Charm III':	            5,

  'Water Charm I':	            2,
  'Water Charm II':	            4,
  'Water Charm III':	          5,

  'Thunder Charm I':	          3,
  'Thunder Charm II':	          4,
  'Thunder Charm III':	        5,

  'Ice Charm I':	              3,
  'Ice Charm II':	              4,
  'Ice Charm III':	            6,

  'Dragon Charm I':	            3,
  'Dragon Charm II':	          4,
  'Dragon Charm III':	          5,

  'Blight Charm I':	            6,
  'Blight Charm II':	          7,

  'Poison Charm I':	            3,
  'Poison Charm II':	          6,
  'Poison Charm III':	          6,

  'Paralysis Charm I':	        2,
  'Paralysis Charm II':	        4,
  'Paralysis Charm III':	      6,

  'Sleep Charm I':	            3,
  'Sleep Charm II':	            4,
  'Sleep Charm III':	          5,

  'Stun Charm I':	              3,
  'Stun Charm II':	            4,
  'Stun Charm III':	            5,

  'Blast Charm I':	            3,
  'Blast Charm II':	            4,
  'Blast Charm III':	          5,

  'Botany Charm I':	            2,
  'Botany Charm II':	          3,
  'Botany Charm III':	          4,
  'Botany Charm IV':	          5,

  'Geology Charm I':	          2,
  'Geology Charm II':	          6,
  'Geology Charm III':	        6,

  'Breaker Charm I':	          5,
  'Breaker Charm II':	          7,

  'Bombardier Charm I':	        4,
  'Bombardier Charm II':	      5,
  'Bombardier Charm III':       6,

  'Mushroom Charm I':	          4,
  'Mushroom Charm II':          6,
  'Mushroom Charm III':         7,

  'Extension Charm I':	        3,
  'Extension Charm II':	        4,
  'Extension Charm III':	      5,

  'Friendship Charm I':	        3,
  'Friendship Charm II':	      4,
  'Friendship Charm III':	      4,
  'Friendship Charm IV':	      5,

  'Light Eater\'s Charm I':	    4,
  'Light Eater\'s Charm II':	  5,
  'Light Eater\'s Charm III':	  6,

  'Grit Charm I':	              4,
  'Grit Charm II':	            6,
  'Grit Charm III':	            7,

  'Impact Charm I':	            3,
  'Impact Charm II':	          4,
  'Impact Charm III':	          6,

  'Hungerless Charm I':	        2,

  'Hungerless Charm II':	      4,
  'Hungerless Charm III':	      5,

  'Counter Charm I':	          5,
  'Counter Charm II':	          6,
  'Counter Charm III':	        7,

  'Foray Charm I':	            4,
  'Foray Charm II':             6,

  'Phoenix Charm I':	          6,
  'Phoenix Charm II':	          7,

  'Chain Charm I':	            5,
  'Chain Charm II':	            7,

  'Counterattack Charm I':	    5,
  'Counterattack Charm II':	    7,

  'Descent Charm I':	          4,
  'Descent Charm II':	          6,

  'Bleed Charm I':	            3,
  'Bleed Charm II':	            5,
  'Bleed Charm III':	          6,

  'Guard Charm I':	            3,
  'Guard Charm II':	            5,
  'Guard Charm III':	          6,

  'Survival Charm I':	          3,
  'Survival Charm II':	        5,
  'Survival Charm III':	        6,

  'Maintenance Charm I':	      4,
  'Maintenance Charm II':	      6,
  'Maintenance Charm III':	    7,

  'Intimidator Charm I':	      3,
  'Intimidator Charm II':	      5,
  'Intimidator Charm III':	    6,

  'Escape Charm I':	            4,
  'Escape Charm II':	          6,
  'Escape Charm III':	          7,

  'Chainblade Charm I':	        4,
  'Chainblade Charm II':	      7,

  'Imbibe Charm I':	            7,

  'Convert Charm I':	          7,
  'Convert Charm II':	          8,

  'Sanity Charm I':	            5,
  'Sanity Charm II':	          6,
  'Sanity Charm III':	          7,

  'Hope Charm':                 5 
}