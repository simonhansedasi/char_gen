import sqlite3


conn = sqlite3.connect('dnd.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS Stats (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL
    )
''')

stats = [
    (1, 'STR'),
    (2, 'DEX'),
    (3, 'CON'),
    (4, 'INT'),
    (5, 'WIS'),
    (6, 'CHA')
]

cursor.executemany('''
    INSERT OR IGNORE INTO Stats (id, name) VALUES (?, ?)
''', stats)




cursor.execute('''
    CREATE TABLE IF NOT EXISTS Species (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL
    )
''')

species = [
    (1, 'Dwarf (Hill)'),
    (2, 'Dwarf (Mountain)'),
    (3, 'Elf (High)'),
    (4, 'Elf (Wood)'),
    (5, 'Elf (Drow)'),
    (6, 'Halfling (Lightfoot)'),
    (7, 'Halfling (Stout)'),
    (8, 'Human Variant'),
    (9, 'Dragonborn'),
    (10, 'Gnome (Forest)'),
    (11, 'Gnome (Rock)'),
    (12, 'Half-Elf'),
    (13, 'Half-Orc'),
    (14, 'Tiefling'),
    (15, 'Human')
]

cursor.executemany('''
    INSERT OR IGNORE INTO Species (id, name) VALUES (?, ?)
''', species)




cursor.execute('''
    CREATE TABLE IF NOT EXISTS SpeciesBonus (
        species_id INTEGER,
        stat_id INTEGER,
        bonus_value INTEGER,
        PRIMARY KEY (species_id, stat_id),
        FOREIGN KEY (species_id) REFERENCES Species(id),
        FOREIGN KEY (stat_id) REFERENCES Stats(id)
    )
''')

species_bonuses = [
    (1, 3, 2),   # Dwarf (Hill): +2 CON
    (1, 5, 1),   # Dwarf (Hill): +1 WIS
    (2, 1, 2),   # Dwarf (Mountain): +2 STR
    (2, 3, 2),   # Dwarf (Mountain): +2 CON
    (3, 2, 2),   # Elf (High): +2 DEX
    (3, 4, 1),   # Elf (High): +1 INT
    (4, 2, 2),   # Elf (Wood): +2 DEX
    (4, 5, 1),   # Elf (Wood): +1 WIS
    (5, 2, 2),   # Elf (Drow): +2 DEX
    (5, 6, 1),   # Elf (Drow): +1 CHA
    (6, 2, 2),   # Halfling (Lightfoot): +2 DEX
    (6, 6, 1),   # Halfling (Lightfoot): +1 CHA
    (7, 2, 2),   # Halfling (Stout): +2 DEX
    (7, 3, 1),   # Halfling (Stout): +1 CON
    (9, 1, 2),   # Dragonborn: +2 STR
    (9, 6, 1),   # Dragonborn: +1 CHA
    (10, 2, 1),  # Gnome (Forest): +1 DEX
    (10, 4, 2),  # Gnome (Forest): +2 INT
    (11, 3, 1),  # Gnome (Rock): +1 CON
    (11, 4, 2),  # Gnome (Rock): +2 INT
    (12, 6, 2),  # Half-Elf: +2 CHA
    (13, 1, 2),  # Half-Orc: +2 STR
    (13, 3, 1),  # Half-Orc: +1 CON
    (14, 4, 1),  # Tiefling: +1 INT
    (14, 6, 2),  # Tiefling: +2 CHA
    (15, 1, 1),  # Human: +1 all
    (15, 2, 1),
    (15, 3, 1),
    (15, 4, 1),
    (15, 5, 1),
    (15, 6, 1)
]

cursor.executemany('''
    INSERT OR IGNORE INTO SpeciesBonus (species_id, stat_id, bonus_value) VALUES (?, ?, ?)
''', species_bonuses)




cursor.execute('''
    CREATE TABLE IF NOT EXISTS Custom_Bonuses (
        species_id INTEGER,
        first_stat_id INTEGER,
        second_stat_id INTEGER,
        bonus_value INTEGER,
        PRIMARY KEY (species_id, first_stat_id, second_stat_id),
        FOREIGN KEY (species_id) REFERENCES Species(id),
        FOREIGN KEY (first_stat_id) REFERENCES Stats(id),
        FOREIGN KEY (second_stat_id) REFERENCES Stats(id)
    )
''')

customizable_bonuses = []

stats_ids = [1, 2, 3, 4, 5, 6]  # STR, DEX, CON, INT, WIS, CHA

# Human Variant: +1 to any two stats
for i in range(len(stats_ids)):
    for j in range(i + 1, len(stats_ids)):
        customizable_bonuses.append((8, stats_ids[i], stats_ids[j], 1))

# Half-Elf: +1 to any two stats other than CHA (CHA is fixed +2)
for i in range(len(stats_ids)):
    for j in range(i + 1, len(stats_ids)):
        if stats_ids[i] != 6 and stats_ids[j] != 6:  # exclude CHA (id=6)
            customizable_bonuses.append((12, stats_ids[i], stats_ids[j], 1))

cursor.executemany('''
    INSERT OR IGNORE INTO Custom_Bonuses (species_id, first_stat_id, second_stat_id, bonus_value) VALUES (?, ?, ?, ?)
''', customizable_bonuses)




cursor.execute('''
    CREATE TABLE IF NOT EXISTS StartFeats (
        feat_id INTEGER PRIMARY KEY,
        feat_name STRING,
        feat_weight REAL,
        species_id INTEGER,
        FOREIGN KEY (species_id) REFERENCES Species(id)
    )
''')

start_feats = [
    (1,  'Darkvision',              6),
    (2,  'Superior Darkvision',     8),
    (3,  'Dwarven Resilience',      5),
    (4,  'Dwarven Combat Training', 5),
    (5,  'Stonecunning',            3),
    (6,  'Dwarven Toughness',       6),
    (7,  'Dwarven Armor Training',  3),
    (8,  'Skill Proficiency',       2),
    (9,  'Resist Charm',            5),
    (10, 'Trance',                  5),
    (11, 'Drow Magic',              5),
    (12, 'Drow Weapon Training',    5),
    (13, 'Cantrip',                 8),
    (14, 'Extra Language',          3),
    (15, 'Fleet of Foot',           5),
    (16, 'Mask of the Wild',        5),
    (17, 'Elf Weapon Training',     5),
    (18, 'Lucky',                   6),
    (19, 'Brave',                   5),
    (20, 'Nimbleness',              5),
    (21, 'Naturally Stealthy',      5),
    (22, 'Stout Resistance',        5),
    (23, 'Feat',                   10),
    (24, 'Draconic Ancestry',       5),
    (25, 'Breath Weapon',           5),
    (26, 'Damage Resistance',       5),
    (27, 'Gnome Cunning',           9),
    (28, 'Speak With Small Beasts', 5),
    (29, "Artificer's Lore",        5),
    (30, 'Tool Proficiency',        5),
    (31, 'Skill Proficiency + 1',   3),
    (32, 'Menacing',                5),
    (33, 'Relentless Endurance',    7),
    (34, 'Savage Attacks',          6),
    (35, 'Hellish Resistance',      5),
    (36, 'Infernal Legacy',         7),
    (37, 'Sunlight Sensitivity',   -5),
]

cursor.executemany('''
    INSERT OR IGNORE INTO StartFeats (feat_id, feat_name, feat_weight) VALUES (?, ?, ?)
''', start_feats)




cursor.execute('''
    CREATE TABLE IF NOT EXISTS SpeciesFeats (
        species_id INTEGER,
        feat_id INTEGER,
        PRIMARY KEY (species_id, feat_id),
        FOREIGN KEY (species_id) REFERENCES Species(id),
        FOREIGN KEY (feat_id) REFERENCES StartFeats(feat_id)
    )
''')

species_feats = [
    # Dwarf (Hill)
    (1, 1),   # Darkvision
    (1, 3),   # Dwarven Resilience
    (1, 4),   # Dwarven Combat Training
    (1, 31),  # Skill Proficiency +1
    (1, 5),   # Stonecunning
    (1, 6),   # Dwarven Toughness
    # Dwarf (Mountain)
    (2, 1),   # Darkvision
    (2, 3),   # Dwarven Resilience
    (2, 4),   # Dwarven Combat Training
    (2, 31),  # Skill Proficiency +1
    (2, 5),   # Stonecunning
    (2, 7),   # Dwarven Armor Training
    # Elf (High)
    (3, 1),   # Darkvision
    (3, 8),   # Skill Proficiency
    (3, 9),   # Resist Charm
    (3, 10),  # Trance
    (3, 13),  # Cantrip
    (3, 17),  # Elf Weapon Training
    (3, 14),  # Extra Language
    # Elf (Wood)
    (4, 1),   # Darkvision
    (4, 8),   # Skill Proficiency
    (4, 9),   # Resist Charm
    (4, 10),  # Trance
    (4, 17),  # Elf Weapon Training
    (4, 15),  # Fleet of Foot
    (4, 16),  # Mask of the Wild
    # Elf (Drow)
    (5, 2),   # Superior Darkvision
    (5, 8),   # Skill Proficiency
    (5, 9),   # Resist Charm
    (5, 10),  # Trance
    (5, 11),  # Drow Magic
    (5, 12),  # Drow Weapon Training
    (5, 37),  # Sunlight Sensitivity
    # Halfling (Lightfoot)
    (6, 18),  # Lucky
    (6, 19),  # Brave
    (6, 20),  # Nimbleness
    (6, 21),  # Naturally Stealthy
    # Halfling (Stout)
    (7, 18),  # Lucky
    (7, 19),  # Brave
    (7, 20),  # Nimbleness
    (7, 22),  # Stout Resistance
    # Human Variant
    (8, 8),   # Skill Proficiency
    (8, 23),  # Feat
    (8, 14),  # Extra Language
    # Dragonborn
    (9, 24),  # Draconic Ancestry
    (9, 25),  # Breath Weapon
    (9, 26),  # Damage Resistance (elemental)
    # Gnome (Forest) — no Sunlight Sensitivity
    (10, 1),  # Darkvision
    (10, 27), # Gnome Cunning
    (10, 13), # Cantrip (Natural Illusionist)
    (10, 28), # Speak With Small Beasts
    # Gnome (Rock) — no Sunlight Sensitivity
    (11, 1),  # Darkvision
    (11, 27), # Gnome Cunning
    (11, 29), # Artificer's Lore
    (11, 30), # Tool Proficiency (Tinker)
    # Half-Elf
    (12, 1),  # Darkvision
    (12, 31), # Skill Proficiency +1
    (12, 9),  # Resist Charm
    (12, 14), # Extra Language
    # Half-Orc
    (13, 1),  # Darkvision
    (13, 32), # Menacing
    (13, 33), # Relentless Endurance
    (13, 34), # Savage Attacks
    # Tiefling
    (14, 1),  # Darkvision
    (14, 35), # Hellish Resistance
    (14, 36), # Infernal Legacy
    # Human
    (15, 14), # Extra Language
]

cursor.executemany('''
    INSERT OR IGNORE INTO SpeciesFeats (species_id, feat_id) VALUES (?, ?)
''', species_feats)




cursor.execute('''
    CREATE TABLE IF NOT EXISTS Classes (
        class_id INTEGER PRIMARY KEY,
        class_name TEXT NOT NULL
    )
''')

classes = [
    (1,  'Barbarian'),
    (2,  'Bard'),
    (3,  'Cleric'),
    (4,  'Druid'),
    (5,  'Fighter'),
    (6,  'Monk'),
    (7,  'Paladin'),
    (8,  'Rogue'),
    (9,  'Sorcerer'),
    (10, 'Warlock'),
    (11, 'Wizard'),
    (12, 'Ranger'),
]

cursor.executemany('''
    INSERT OR IGNORE INTO Classes (class_id, class_name) VALUES (?, ?)
''', classes)




cursor.execute('''
    CREATE TABLE IF NOT EXISTS ClassAttributes (
        class_id INTEGER,
        primary_stat_id INTEGER,
        secondary_stat_id INTEGER,
        PRIMARY KEY (class_id, primary_stat_id, secondary_stat_id)
    )
''')

class_abilities = [
    (1,  1, 3),  # Barbarian: STR/CON
    (2,  6, 2),  # Bard: CHA/DEX
    (3,  5, 1),  # Cleric: WIS/STR
    (3,  5, 3),  # Cleric: WIS/CON
    (4,  5, 3),  # Druid: WIS/CON
    (5,  2, 3),  # Fighter: DEX/CON
    (5,  2, 4),  # Fighter: DEX/INT
    (5,  1, 3),  # Fighter: STR/CON
    (5,  1, 4),  # Fighter: STR/INT
    (6,  2, 5),  # Monk: DEX/WIS
    (7,  1, 6),  # Paladin: STR/CHA
    (8,  2, 4),  # Rogue: DEX/INT
    (9,  6, 3),  # Sorcerer: CHA/CON
    (10, 6, 2),  # Warlock: CHA/DEX
    (11, 4, 3),  # Wizard: INT/CON
    (12, 2, 5),  # Ranger: DEX/WIS
    (12, 1, 5),  # Ranger: STR/WIS
]

cursor.executemany('''
    INSERT OR IGNORE INTO ClassAttributes (class_id, primary_stat_id, secondary_stat_id)
    VALUES (?, ?, ?)
''', class_abilities)




cursor.execute('''
    CREATE TABLE IF NOT EXISTS Skills (
        skill_id INTEGER PRIMARY KEY,
        skill_name STRING,
        governing_attribute INTEGER
    )
''')

skills = [
    (1,  'Acrobatics',      2),
    (2,  'Animal Handling', 5),
    (3,  'Arcana',          4),
    (4,  'Athletics',       1),
    (5,  'Deception',       6),
    (6,  'History',         4),
    (7,  'Insight',         5),
    (8,  'Intimidation',    6),
    (9,  'Investigation',   4),
    (10, 'Medicine',        5),
    (11, 'Nature',          5),
    (12, 'Perception',      5),
    (13, 'Performance',     6),
    (14, 'Persuasion',      6),
    (15, 'Religion',        4),
    (16, 'Sleight of Hand', 2),
    (17, 'Stealth',         2),
    (18, 'Survival',        5),
]

cursor.executemany('''
    INSERT OR IGNORE INTO Skills (skill_id, skill_name, governing_attribute) VALUES (?, ?, ?)
''', skills)




cursor.execute('''
    CREATE TABLE IF NOT EXISTS Backgrounds (
        background_id INTEGER PRIMARY KEY,
        background_name STRING,
        skill_1 INTEGER,
        skill_2 INTEGER
    )
''')

backgrounds = [
    (1,  'Acolyte',      7,  15),  # Insight, Religion
    (2,  'Charlatan',    5,  16),  # Deception, Sleight of Hand
    (3,  'Criminal/Spy', 5,  17),  # Deception, Stealth
    (4,  'Entertainer',  1,  13),  # Acrobatics, Performance
    (5,  'Folk Hero',    2,  18),  # Animal Handling, Survival
    (6,  'Gladiator',    1,  13),  # Acrobatics, Performance
    (7,  'Guild Artisan',7,  14),  # Insight, Persuasion
    (8,  'Hermit',       10, 15),  # Medicine, Religion
    (9,  'Knight',       6,  14),  # History, Persuasion (Noble variant)
    (10, 'Noble',        6,  14),  # History, Persuasion
    (11, 'Outlander',    4,  18),  # Athletics, Survival
    (12, 'Pirate',       4,  12),  # Athletics, Perception
    (13, 'Sage',         3,  6),   # Arcana, History
    (14, 'Sailor',       4,  12),  # Athletics, Perception
    (15, 'Soldier',      4,  8),   # Athletics, Intimidation
    (16, 'Urchin',       16, 17),  # Sleight of Hand, Stealth
]

cursor.executemany('''
    INSERT OR IGNORE INTO Backgrounds (background_id, background_name, skill_1, skill_2)
    VALUES (?, ?, ?, ?)
''', backgrounds)




cursor.execute('''
    CREATE TABLE IF NOT EXISTS Proficiencies (
        pfc_id INTEGER PRIMARY KEY,
        pfc_name STRING
    )
''')

proficiencies = [
    (1, 'Saving Throw'),
    (2, 'Skill'),
    (3, 'Simple Weapons'),
    (4, 'Martial Weapons'),
    (5, 'Light Armor'),
    (6, 'Medium Armor'),
    (7, 'Heavy Armor'),
    (8, 'Shields')
]

cursor.executemany('''
    INSERT OR IGNORE INTO Proficiencies (pfc_id, pfc_name) VALUES (?, ?)
''', proficiencies)


conn.commit()
conn.close()
