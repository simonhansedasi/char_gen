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

priority_order = {'DEX': 1, 'INT': 2, 'WIS': 3, 'STR': 4, 'CHA': 5, 'CON': 6}



def roll_3d6():
    rolls = []
    for i in range(4):
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



def get_stat_combinations(stats):
    highest_two = sorted(stats.items(), key=lambda x: -x[1])[:2]
    lowest_two = sorted(stats.items(), key=lambda x: x[1])[:2]
    highest_lowest = [
        (highest_two[0][0], highest_two[0][1]), 
        (lowest_two[0][0], lowest_two[0][1])    
    ] 
    return {        
        'l2': lowest_two,
        'hl': highest_lowest,
        'h2': highest_two
    }





def get_species_name(species_id):
    conn = sqlite3.connect('dnd.db')
    cursor = conn.cursor()
    
    query = '''
        SELECT name
        FROM Species
        WHERE id = ?
    '''
    
    cursor.execute(query, (species_id,))
    result = cursor.fetchone()
    
    conn.close()
    
    return result[0]

def get_species_id(species_name):
    conn = sqlite3.connect('dnd.db')
    cursor = conn.cursor()
    
    query = '''
        SELECT id
        FROM Species
        WHERE name = ?
    '''
    
    cursor.execute(query, (species_name,))
    result = cursor.fetchone()
    
    conn.close()
    
    return result[0]


def get_species_stats(species_id):
    query_species_bonus = '''
        SELECT SB.stat_id, SB.bonus_value 
        FROM SpeciesBonus SB
        JOIN Species S ON SB.species_id = S.id
        WHERE S.name = ?
    '''
    cursor.execute(query_species_bonus, (species_id,))
    species_bonuses = cursor.fetchall()













def query_species(stat_id_pairs):
    conn = sqlite3.connect('dnd.db')
    cursor = conn.cursor()

    union_queries = []
    params = []

    for key in (stat_id_pairs.keys()):

        stat_id_1 = stat_id_pairs[key][0]
        stat_id_2 = stat_id_pairs[key][1]

        union_queries.append(f'''
            SELECT S.id, S.name, {key} as pair_index
            FROM Species S
            JOIN SpeciesBonus SB ON S.id = SB.species_id
            WHERE SB.stat_id IN (?, ?)
            GROUP BY S.id
            HAVING COUNT(DISTINCT SB.stat_id) = 2
        ''')
        
        # Add parameters for the current pair
        params.extend([stat_id_1, stat_id_2])

    complete_query = ' UNION ALL '.join(union_queries)

    cursor.execute(complete_query, params)
    results = cursor.fetchall()

    species_dict = {i: [] for i in range(len(stat_id_pairs))}

    for species_id, species_name, pair_index in results:
        species_dict[pair_index].append(species_id)
    conn.close()
    return species_dict











def query_flexible_species(stat_id_pairs):
    conn = sqlite3.connect('dnd.db')
    cursor = conn.cursor()

    queries = []
    params = []

    for key in (stat_id_pairs.keys()):
        stat_id_1 = stat_id_pairs[key][0]
        stat_id_2 = stat_id_pairs[key][1]

        queries.append(f'''
            SELECT S.id, S.name, {key} as pair_index
            FROM Species S
            JOIN Custom_Bonuses CB ON S.id = CB.species_id
            WHERE (CB.first_stat_id = ? AND CB.second_stat_id = ?) 
               OR (CB.first_stat_id = ? AND CB.second_stat_id = ?)
            AND S.id IN (8, 12)
        ''')

        params.extend([stat_id_1, stat_id_2, stat_id_2, stat_id_1])  # Include both orders

    results = []
    for n, query in enumerate(queries):
        cursor.execute(query, params[n * 4:n * 4 + 4])  # Adjusted to retrieve 4 params per query
        results.extend(cursor.fetchall())  # Flatten results

    
    species_dict = {i: [] for i in range(len(stat_id_pairs))}
    for species_id, species_name, pair_index in results:
        species_dict[pair_index].append(species_id)

    conn.close()
    return species_dict




def query_species_feats(species_id):
    conn = sqlite3.connect('dnd.db')
    cursor = conn.cursor()
    
    feats_query = '''
        SELECT SF.species_id, S.name, F.feat_name, F.feat_weight
        FROM SpeciesFeats SF
        JOIN StartFeats F ON SF.feat_id = F.feat_id
        JOIN Species S ON SF.species_id = S.id
        WHERE SF.species_id = ?
    '''
    
    cursor.execute(feats_query, (species_id,))  # Single ID as a tuple
    results = cursor.fetchall()
    conn.close()
    return results

    







def recommend_species(stats):
    stat_combos = get_stat_combinations(stats)
    stat_names = []
    
    for key in stat_combos.keys():
        stat_names.append([stat_combos[key][0][0], stat_combos[key][1][0]])
        
        
    
    stat_ids = {}
    
    for pair in stat_names:
        stat_ids[len(stat_ids)] = [stat_id_mapping[pair[0]],stat_id_mapping[pair[1]] ]
        
    species = query_species(stat_ids)
    flex_species = query_flexible_species(stat_ids)

    
    all_species = {}
    max_length = max(len(species), len(flex_species))

    # Merge the two dictionaries
    for i in range(max_length):
        all_species[i] = []
        if i in species:
            all_species[i].extend(species[i])
        if i in flex_species:
            all_species[i].extend(flex_species[i])

    
    
    species_weights = {}
    
    for key in all_species.keys():
        for species_index in all_species[key]:
            if species_index not in species_weights:
                species_weights[species_index] = key
            else:
                species_weights[species_index] += key / 2
    for key in species_weights:
        feat_weights = query_species_feats(key)
        for item in feat_weights:
            species_weights[key] += item[3]

    # print(species_weights)
    
    species = list(species_weights.keys())
    weights = list(species_weights.values())

    chosen_species = random.choices(species, weights=weights, k=1)[0]

#     chosen_species = max(species_weights, key=species_weights.get)

    recommended_species = get_species_name(chosen_species)
    
    
    # print(recommended_species)
    
    return recommended_species





def apply_species_bonus(stats, recommended_species):
    species_id = get_species_id(recommended_species)
    
    species_stat_bonus = get_species_stats(species_id)
    print(species_stat_bonus)

    
    
    
    
    
    
    
    
    stat_priority = ['DEX', 'INT', 'WIS', 'STR', 'CHA', 'CON']

    # Query for species-specific bonuses
    query_species_bonus = '''
        SELECT SB.stat_id, SB.bonus_value 
        FROM SpeciesBonus SB
        JOIN Species S ON SB.species_id = S.id
        WHERE S.name = ?
    '''
    cursor.execute(query_species_bonus, (recommended_species,))
    species_bonuses = cursor.fetchall()

    # Copy stats to avoid modifying the original
    updated_stats = stats.copy()

    # Apply the bonuses
    for stat_id, bonus_value in species_bonuses:
        stat_name = stat_id_mapping_inv[stat_id]
        updated_stats[stat_name] += bonus_value

    # Additional logic for custom bonuses for Humans and Half-Elves
    if recommended_species in ['Human', 'Half-Elf']:
        rolled_values = [(stat, updated_stats[stat]) for stat in stats.keys()]
        rolled_values.sort(key=lambda x: (x[1], stat_priority.index(x[0])), reverse=True)

        if recommended_species == 'Half-Elf':
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
        cursor.execute(query_custom_bonus, (recommended_species, highest_two_ids[0], highest_two_ids[1], highest_two_ids[0], highest_two_ids[1]))
        custom_bonuses = cursor.fetchall()

        for first_stat_id, second_stat_id in custom_bonuses:
            first_stat_name = stat_id_mapping_inv[first_stat_id]
            second_stat_name = stat_id_mapping_inv[second_stat_id]

            updated_stats[first_stat_name] += 1
            updated_stats[second_stat_name] += 1

    # Store the updated stats
    updated_stat_array[recommended_species] = updated_stats

    conn.close()
    return updated_stat_array
