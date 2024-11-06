import random
import sqlite3
import openai

import os
from dotenv import load_dotenv


stats = ['STR','DEX','CON','INT','WIS','CHA']


priority_order = {'DEX': 1, 'INT': 2, 'WIS': 3, 'STR': 4, 'CHA': 5, 'CON': 6}



def roll_3d6():
    rolls = []
    for i in range(3):
        rolls.append(random.randint(1,6))
    
    rolls.sort()        
    return sum(rolls[-3:])


def roll_stats():
    rolled_stats = {}
    
    roll_count = 0
    
    while True:
    
        for i in range(6):
            rolled_stats[i] = roll_3d6()

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

def sort_stats(stats):
    top_stats = sorted(stats, key=stats.get, reverse=True)
    
    stat_values = []
    
    for stat in top_stats:
        stat_values.append(stats[stat])
        
    top_stats = [stat + 1 for stat in top_stats]

    return list(zip(top_stats, stat_values))


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



def get_species_stats(stats, species_id):
    conn = sqlite3.connect('dnd.db')
    cursor = conn.cursor()
    species_bonuses = []
    if species_id in (8, 12):
        highest_stats = get_stat_combinations(stats)['h2']
        
        
        # add 1 for sql indexing
        
        h1 = highest_stats[0][0] + 1
        h2 = highest_stats[1][0] + 1
        
        
        if species_id == 8:
            species_bonuses = [(h1, 1), (h2, 1)]
        elif species_id == 12 and 6 not in highest_stats:
            species_bonuses = [(h1, 1), (h2, 1)]
        elif species_id == 12 and 6 in highest_stats:
            next_highest_stats = get_stat_combinations(stats)['hl']
            h1 = next_highest_stats[0][0]
            h2 = next_highest_stats[1][0]
            species_bonuses = [(h1, 1), (h2, 1)]
            
        elif species_id == 12 and 6 in highest_stats:
            next_highest_stats = get_stat_combinations(stats)['l2']
            h1 = next_highest_stats[0][0]
            h2 = next_highest_stats[1][0]
            species_bonuses = [(h1, 1), (h2, 1)]


            
            
    if species_id != 8:
    
        species_bonus_query = '''
            SELECT SB.stat_id, SB.bonus_value
            FROM SpeciesBonus SB
            WHERE SB.species_id = ?
        '''
        cursor.execute(species_bonus_query, (species_id,))
        species_bonuses.extend(cursor.fetchall())
        
    conn.close()
    
    
    
    
    return species_bonuses




def query_species(stat_id_pairs):
    conn = sqlite3.connect('dnd.db')
    cursor = conn.cursor()

    union_queries = []
    params = []
    for n, stat_id in enumerate(stat_id_pairs):

        stat_id_1 = stat_id[0] + 1
        stat_id_2 = stat_id[1] + 1

        union_queries.append(f'''
            SELECT S.id, S.name, {n} as pair_index
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


def find_key_by_value(my_dict, target_value):
    for key, value in my_dict.items():
        if value == target_value:
            return key
    return None




def query_flexible_species(stat_id_pairs):
    conn = sqlite3.connect('dnd.db')
    cursor = conn.cursor()

    union_queries = []
    params = []
    for n, stat_id in enumerate(stat_id_pairs):

        stat_id_1 = stat_id[0] + 1
        stat_id_2 = stat_id[1] + 1

        union_queries.append(f'''
            SELECT S.id, {n} as pair_index
            FROM Species S
            JOIN Custom_Bonuses CB ON S.id = CB.species_id
            WHERE (CB.first_stat_id = ? AND CB.second_stat_id = ?) 
                OR (CB.first_stat_id = ? AND CB.second_stat_id = ?)          
            GROUP BY S.id
        ''')
        
        # Add parameters for the current pair
        params.extend([stat_id_1, stat_id_2, stat_id_2, stat_id_1])
    
    complete_query = ' UNION ALL '.join(union_queries)

    cursor.execute(complete_query, params)
    results = cursor.fetchall()
    
    species_dict = {i: [] for i in range(len(stat_id_pairs))}
    
    for species_id, pair_index in results:
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
    
    cursor.execute(feats_query, (species_id,))
    results = cursor.fetchall()
    conn.close()
    return results

    







def recommend_species(stats):
    stat_combos = get_stat_combinations(stats)
    stat_names = []
    
    stat_ids = []
    
    for key, value in stat_combos.items():
        stat_ids.append([value[0][0], value[1][0]])
        
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
                if species_index == 8:
                    species_weights[species_index] += key

    for key in species_weights:
        feat_weights = query_species_feats(key)
        for item in feat_weights:
            species_weights[key] += item[3]
    # print(all_species)

    species = list(species_weights.keys())
    weights = list(species_weights.values())

    chosen_species = random.choices(species, weights=weights, k=1)[0]


    recommended_species = get_species_name(chosen_species)
    
    
    return recommended_species





def apply_species_bonus(stats, recommended_species):
    species_id = get_species_id(recommended_species)
    species_stat_bonus = get_species_stats(stats, species_id)
    
    updated_stats = stats.copy()
    for stat_id, stat_value in stats.items():
        
        
        for bonus_id, bonus_value in species_stat_bonus:
            if stat_id+1 == bonus_id:
                
                
                updated_stats[stat_id] += bonus_value
                
    return updated_stats





def query_class(top_stats):
    conn = sqlite3.connect('dnd.db')
    cursor = conn.cursor()
    stat_ids = [stat_id for stat_id, value in top_stats if value >= 14]
    if not stat_ids:
        return []

    placeholders = ', '.join(['?'] * len(stat_ids))
    class_query = f'''
        SELECT C.class_id, C.class_name, CA.stat_id
        FROM Classes C
        JOIN ClassAttributes CA ON CA.class_id = C.class_id
        WHERE CA.stat_id IN ({placeholders})
    '''
    
    cursor.execute(class_query, stat_ids)
    results = cursor.fetchall()
    conn.close()
    
    return results


def select_class(top_stats):        
    potential_classes = query_class(top_stats)    
    classes = {}
    for item in potential_classes:
        class_id = item[0]
        class_name = item[1]
        class_stat = item[2] + 1
        # print(class_name)
        if class_name not in classes.keys():
            classes[class_name] = 1
        elif class_name in classes.keys():
            classes[class_name] += 1
            
            
    classes = {k: v for k, v in classes.items() if v >= 2}
    pcs = list(classes.keys())
    weights = list(classes.values())

    if pcs:
        return random.choices(pcs, weights=weights, k=1)[0]
    else:
        return None

    
    
    
def query_skills(optimal_stats):
    conn = sqlite3.connect('dnd.db')
    cursor = conn.cursor()
    
    
    stat_ids = [stat_id for stat_id, value in optimal_stats if value >= 14]
    if not stat_ids:
        return []

    placeholders = ', '.join(['?'] * len(stat_ids))
    
    skill_query = f'''
        SELECT S.skill_id, S.skill_name
        FROM Skills S
        WHERE S.governing_attribute in ({placeholders})
    '''
    cursor.execute(skill_query,stat_ids)
    results = cursor.fetchall()
    conn.close()
    return results
    

def query_backgrounds(skill_ids):
    conn = sqlite3.connect('dnd.db')
    cursor = conn.cursor()
    
    placeholders = ', '.join(['?'] * len(skill_ids))
    
    background_query = f'''
        SELECT B.background_name
        FROM Backgrounds B
        WHERE B.skill_1 AND skill_2 in ({placeholders})
    '''
    cursor.execute(background_query,skill_ids)
    results = cursor.fetchall()
    conn.close()
    return results
    
    
def pick_background(optimal_stats):

    preferred_skills = query_skills(optimal_stats)
    skill_ids = []
    for skill in preferred_skills:
        if skill[1] not in skill_ids:
            skill_ids.append(skill[0])
            
        else:
            continue
    backgrounds = query_backgrounds(skill_ids)
    if backgrounds:
        background = random.choice(backgrounds)
        return background[0]
    else:
        return None
    
    
def generate_background(
    recommended_species, 
    chosen_class, 
    background, 
    updated_stats,
    dead_farmers
):
        # Load environment variables
    load_dotenv()

    # Get the API key from environment variables
    api_key = os.getenv("OPENAI_API_KEY")
    openai.api_key = api_key
    # with open('key.txt', 'r') as file:
    #     api_key = file.read().strip()
        
    # openai.api_key = api_key

    prompt = (
        # f'
        f'Generate a D&D character background for a {chosen_class} and give them a name.'
        f'This {chosen_class} comes from a {background} background.'
        f'The stat array for this player is {updated_stats}.'
        f'Give them a personality trait based on their stat array.'
        # f'Pick an alignment at random also.'
        f'{dead_farmers} people died in this persons life before adventuring.'
        f'Give the character a quirk.'
        f'do not report the stat array'
    )
    
    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=[{'role': 'user', 'content': prompt}]
    )
    # print(response)
    # Extract the content from the response
    content = response['choices'][0]['message']['content']
    
    # print(content)
    
    return content
