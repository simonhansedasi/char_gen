import random
import sqlite3

stats = ['STR','DEX','CON','INT','WIS','CHA']
stat_id_mapping = {
    'STR': 1,
    'DEX': 2,
    'CON': 3,
    'INT': 4,
    'WIS': 5,
    'CHA': 6
}

stat_id_mapping_inv = {v: k for k, v in stat_id_mapping.items()}
def roll_3d6():
    rolls = []
    for i in range(3):
        rolls.append(random.randint(1,6))
    
    rolls.sort()        
    return sum(rolls[-3:])

roll_3d6()

def roll_stats():
    rolled_stats = {}
    
    roll_count = 0
    
    while True:
    
        for stat in stats:
            rolled_stats[stat] = roll_3d6()

        if any(value >= 16 for value in rolled_stats.values()):
            break
        roll_count += 1
    return rolled_stats, roll_count









import sqlite3

# Define the priority mapping
priority_order = {'DEX': 1, 'INT': 2, 'WIS': 3, 'STR': 4, 'CHA': 5, 'CON': 6}

def recommend_species(stats):
    rolled_values = []
    
    # Convert stats to (stat_id, value) pairs
    for stat, value in stats.items():
        rolled_values.append((stat_id_mapping[stat], value))

    # Sort by value, and then by priority to handle ties
    rolled_values.sort(key=lambda x: (x[1], priority_order[stat_id_mapping_inv[x[0]]]), reverse=True)
    
    # Select the highest two stat ids
    highest_two_ids = [rolled_values[0][0], rolled_values[1][0]]  
    placeholder = ', '.join(['?'] * len(highest_two_ids))
    
    recommendations = []
    
    conn = sqlite3.connect('dnd.db')
    cursor = conn.cursor()
    
    # Query to recommend species based on the highest two stat ids
    query = f'''
        SELECT S.name 
        FROM Species S
        JOIN SpeciesBonus SB ON S.id = SB.species_id
        WHERE SB.stat_id IN ({placeholder})
        AND SB.bonus_value > 0
        GROUP BY S.id
        HAVING COUNT(SB.stat_id) = {len(highest_two_ids)}
    '''
    cursor.execute(query, highest_two_ids)

    for species_name, in cursor.fetchall():  # Unpack the tuple
        if species_name not in recommendations:
            recommendations.append(species_name)

    # Fetch flexible bonuses for Human and Half-Elf
    flexible_query = '''
        SELECT S.name 
        FROM Species S
        JOIN Custom_Bonuses CB ON S.id = CB.species_id
        WHERE CB.first_stat_id IN (?, ?) 
        AND CB.second_stat_id IN (?, ?)
        AND S.id IN (8, 12)  -- Assuming 8 is Human and 12 is Half-Elf
    '''

    params = highest_two_ids + highest_two_ids  
    cursor.execute(flexible_query, params)

    flexible_results = cursor.fetchall()

    # Process flexible species
    for (species_name,) in flexible_results:  # Unpack here as well
        if species_name not in recommendations:
            recommendations.append(species_name)

    species_probabilities = {
        'Human': 0.15,      # Reduced from 0.25
        'Dwarf': 0.15,
        'Elf': 0.10,        # Increased from 0.07
        'Halfling': 0.12,
        'Dragonborn': 0.08, # Increased from 0.05
        'Gnome': 0.1,
        'Half-Elf': 0.10,   # Reduced from 0.16
        'Half-Orc': 0.05,
        'Tiefling': 0.05,
    }
    
    # Filter recommendations based on probabilities
    weighted_recommendations = [(species, species_probabilities.get(species, 0)) for species in recommendations]

    # Select a species based on weighted probabilities
    species_names, probabilities = zip(*weighted_recommendations) if weighted_recommendations else ([], [])
    
    if probabilities:
        selected_species = random.choices(species_names, weights=probabilities, k=1)[0]
    else:
        selected_species = None
    
    conn.close()
    
    return selected_species

    
    
    
def apply_species_bonus(stats, recommended_species):
    updated_stat_arrays = []
    conn = sqlite3.connect('dnd.db')
    cursor = conn.cursor()

    stat_priority = ['DEX', 'INT', 'WIS', 'STR', 'CHA', 'CON']

    for species_name in recommended_species:

        query_species_bonus = '''
            SELECT SB.stat_id, SB.bonus_value 
            FROM SpeciesBonus SB
            JOIN Species S ON SB.species_id = S.id
            WHERE S.name = ?
        '''
        cursor.execute(query_species_bonus, (species_name,))
        species_bonuses = cursor.fetchall()

        updated_stats = stats.copy()  

        for stat_id, bonus_value in species_bonuses:
            stat_name = stat_id_mapping_inv[stat_id]
            updated_stats[stat_name] += bonus_value  

        updated_stat_arrays.append({species_name: updated_stats})

        if species_name in ['Human', 'Half-Elf']:

            # Create a list of rolled values with priority order
            rolled_values = [(stat, updated_stats[stat]) for stat in stats.keys()]
            rolled_values.sort(key=lambda x: (x[1], stat_priority.index(x[0])), reverse=True)

            if species_name == 'Half-Elf':
                rolled_values = [x for x in rolled_values if x[0] != 'CHA']  
                highest_two_stats = rolled_values[:2]
            else:
                highest_two_stats = rolled_values[:2] 

            highest_two_ids = [stat_id_mapping[highest_two_stats[0][0]], stat_id_mapping[highest_two_stats[1][0]]]

            query_custom_bonus = '''
                SELECT CB.first_stat_id, CB.second_stat_id 
                FROM Custom_Bonuses CB
                JOIN Species S ON CB.species_id = S.id
                WHERE S.name = ?
                AND CB.first_stat_id IN (?, ?)
                AND CB.second_stat_id IN (?, ?)
            '''
            cursor.execute(query_custom_bonus, (species_name, highest_two_ids[0], highest_two_ids[1], highest_two_ids[0], highest_two_ids[1]))
            custom_bonuses = cursor.fetchall()

            for first_stat_id, second_stat_id in custom_bonuses:
                first_stat_name = stat_id_mapping_inv[first_stat_id]
                second_stat_name = stat_id_mapping_inv[second_stat_id]

                updated_stats[first_stat_name] += 1  
                updated_stats[second_stat_name] += 1  
    conn.close()
    

    return updated_stat_arrays 



