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
    INSERT INTO Stats (id, name) VALUES (?, ?)
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
    INSERT INTO Species (id, name) VALUES (?, ?)
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
    (1, 3, 2),
    (1, 5, 1),
    (2, 1, 2),
    (2, 3, 2),
    (3, 2, 2),
    (3, 4, 1),
    (4, 2, 2),
    (4, 5, 1),
    (5, 2, 2),
    (5, 6, 1),
    (6, 2, 2),
    (6, 6, 1),
    (7, 2, 2),
    (7, 3, 1),
    (9, 1, 2),
    (9, 6, 1),
    (10, 2, 1),
    (10, 5, 2),
    (11, 3, 1), 
    (11, 5, 2),
    (12, 6, 2),
    (13, 1, 2),
    (13, 3, 1),
    (14, 4, 1),
    (14, 6, 2),
    (15, 1, 1),
    (15, 2, 1),
    (15, 3, 1),
    (15, 4, 1),
    (15, 5, 1),
    (15, 6, 1)
]

cursor.executemany('''
    INSERT INTO SpeciesBonus (species_id, stat_id, bonus_value) VALUES (?, ?, ?)
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

stats = [1, 2, 3, 4, 5, 6]  # Corresponds to STR, DEX, CON, INT, WIS, CHA
for i in range(len(stats)):
    for j in range(i + 1, len(stats)):
        customizable_bonuses.append((8, stats[i], stats[j], 1))  

for i in range(len(stats)):
    for j in range(i + 1, len(stats)-1):
        customizable_bonuses.append((12, stats[i], stats[j], 1))  

cursor.executemany('''
    INSERT INTO Custom_Bonuses (species_id, first_stat_id, second_stat_id, bonus_value) VALUES (?, ?, ?, ?)
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
    (1, 'Darkvision', 6),
    (2, 'Superior Darkvision', 8),
    (3, 'Dwarven Resilience', 5),
    (4, 'Dwarven Combat Training', 5),
    (5, 'Stonecunning', 3),
    (6, 'Dwarven Toughness', 6),
    (7, 'Dwarven Armor Training', 3),
    (8, 'Skill Proficiency', 2),
    (9, 'Resist Charm', 5),
    (10, 'Trance', 5),
    (11, 'Drow Magic', 5),
    (12, 'Drow Weapon Training', 5),
    (13, 'Cantrip', 8),
    (14, 'Extra Language', 3),
    (15, 'Fleet of Foot', 5),
    (16, 'Mask of the Wild', 5),
    (17, 'Elf Weapon Training', 5),
    (18, 'Lucky', 6),
    (19, 'Brave', 5),
    (20, 'Nimbleness', 5),
    (21, 'Naturally Stealthy', 5),
    (22, 'Stout Resistance', 5),
    (23, 'Feat', 10),
    (24, 'Draconic Ancestry', 5),
    (25, 'Breath Weapon', 5),
    (26, 'Damage Resistance', 5),
    (27, 'Gnome Cunning', 9),
    (28, 'Speak With Small Beasts', 5),
    (29, 'Artificer\'s Lore', 5),
    (30, 'Tool Proficiency', 5),
    (31, 'Skill Proficiency + 1', 3),
    (32, 'Menacing', 5),
    (33, 'Relentless Endurance', 7),
    (34, 'Savage Attacks', 6),
    (35, 'Hellish Resistance', 5),
    (36, 'Infernal Legacy', 7),
    (37, 'Sunlight Sensitivity', -5)
]

cursor.executemany('''
    INSERT INTO StartFeats (feat_id, feat_name, feat_weight) VALUES (?, ?, ?)
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
    (1, 1,),
    (1, 3,),
    (1, 4,),
    (1, 31),
    (1, 5),
    (1, 6),
    (2, 1),
    (2, 3),
    (2, 4),
    (2, 31),
    (2, 5),
    (2, 7),    
    (3, 1),
    (3, 8),
    (3, 9),
    (3, 10),
    (3, 13),
    (3, 17),
    (3, 14),    
    (4, 1),
    (4, 8),
    (4, 9),
    (4, 10),
    (4, 17),
    (4, 15),
    (4, 16),    
    (5, 3),
    (5, 8),
    (5, 9),
    (5, 10),
    (5, 11),
    (5, 12),
    (5, 37),
    (6, 18),
    (6, 19),
    (6, 30),
    (6, 31),
    (7, 18),
    (7, 19),
    (7, 30),
    (7, 32),
    (8, 8),
    (8, 23),
    (8, 14),
    (9, 35),
    (9, 36),
    (9, 37),
    (10, 1),
    (10, 37),
    (10, 13),
    (10, 38),
    (11, 1),
    (11, 37),
    (11, 39),
    (11, 30),
    (12, 1),
    (12, 31),
    (12, 9),
    (12, 14),
    (13, 1),
    (13, 32),
    (13, 33),
    (13, 34),
    (14, 1),
    (14, 35),
    (14, 36),
    (15, 14)
]

# Insert species feats into the table
cursor.executemany('''
    INSERT INTO SpeciesFeats (species_id, feat_id) VALUES (?, ?)
''', species_feats)








cursor.execute('''
    CREATE TABLE IF NOT EXISTS Classes (
        class_id INTEGER PRIMARY KEY,
        class_name TEXT NOT NULL
    )
''')

classes = [
    (1, 'Barbarian'),
    (2, 'Bard'),
    (3, 'Cleric'),
    (4, 'Druid'),
    (5, 'Fighter'),
    (6, 'Monk'),
    (7, 'Paladin'),
    (8, 'Rogue'),
    (9, 'Sorcerer'),
    (10, 'Warlock'),
    (11, 'Wizard'),
    (12, 'Ranger'),
    # (13, 'Artificer')
]

cursor.executemany('''
    INSERT INTO Classes (class_id, class_name) VALUES (?, ?)
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
    (1, 1, 3),
    # (1, 3, 1),
    # (1, 2, 3),
    # (1, 3, 2),
    (2, 6, 2),
    # (2, 6, 5),
    # (2, 6, 1),
    # (2, 6, 3),
    (3, 5, 1),
    (3, 5, 3),
    
    # (4, 5, 2),
    (4, 5, 3),
    # (4, 3, 5),
    
    (5, 2, 3),
    (5, 2, 4),
    (5, 1, 3),
    (5, 1, 4),
    
    (6, 2, 5),
    # (6, 1, 5),
    # (6, 5, 2),
    # (6, 2, 3),
    # (6, 3, 2),
    
    (7, 1, 6),
    # (7, 6, 1),
    
    (8, 2, 4),
    # (8, 2, 5),
    # (8, 2, 6),
    
    (9, 6, 3),
    # (9, 3, 6),
    
    # (10, 6, 3),
    (10, 6, 2),
    
    # (10, 6, 3),
    # (11, 4, 2),
    (11, 4, 3),
    # (11, 4, 1),
    
    # (11, 4, 3),
    
    (12, 2, 5),
    (12, 1, 5),
    # (12, 1, 5),
    # (13, 4, 3),
    # (13, 4, 1)
]

# Insert data into the table
cursor.executemany('''
    INSERT INTO ClassAttributes (class_id, primary_stat_id, secondary_stat_id) 
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
    (1, 'Acrobatics', 2), 
    (2, 'Animal Handling', 5),
    (3, 'Arcana', 4), 
    (4, 'Athletics', 1),
    (5, 'Deception', 6),
    (6, 'History', 4),
    (7, 'Insight', 5), 
    (8, 'Intimidation', 6), 
    (9, 'Investigation', 4),
    (10, 'Medicine', 5),
    (11, 'Nature', 5),
    (12, 'Perception', 5), 
    (13, 'Performance', 6),
    (14, 'Persuasion', 6), 
    (15, 'Religion', 4), 
    (16, 'Sleight of Hand', 2), 
    (17, 'Stealth', 2), 
    (18, 'Survival', 5),

]

# Insert data into the table
cursor.executemany('''
    INSERT INTO Skills (skill_id, skill_name, governing_attribute) VALUES (?, ?, ?)
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
    (1, 'Acolyte', 7, 9), 
    (2, 'Charlatan', 5, 16),
    (3, 'Criminal/Spy', 5, 17), 
    (4, 'Entertainer', 1, 13),
    (5, 'Folk Hero', 5, 18),
    (6, 'Gladiator', 1, 13),
    (7, 'Guild Artisan', 7, 14), 
    (8, 'Hermit', 10, 14), 
    (9, 'Knight', 7, 14),
    (10, 'Noble', 6, 14),
    (11, 'Outlander', 4, 18),
    (12, 'Pirate', 4, 12), 
    (13, 'Sage', 3, 6),
    (14, 'Sailor', 4, 12), 
    (15, 'Soldier', 4, 8), 
    (16, 'Urchin', 16, 17)

]

# Insert data into the table
cursor.executemany('''
    INSERT INTO Backgrounds (background_id, background_name, skill_1, skill_2) 
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






conn.commit()
conn.close()