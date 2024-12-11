import random
import sqlite3
import openai

import os
from dotenv import load_dotenv
from itertools import product, groupby, combinations



stats = ['STR','DEX','CON','INT','WIS','CHA']


priority_order = {'DEX': 1, 'INT': 2, 'WIS': 3, 'STR': 4, 'CHA': 5, 'CON': 6}








def roll_3d6():
    rolls = []
    for i in range(4):
        rolls.append(random.randint(1,6))
    
    rolls.sort()        
    return sum(rolls[-3:])


def roll_stats():
    rolled_stats = {}
    roll_count = 0

    while True:
        # Roll stats for 6 abilities
        for i in range(6):
            rolled_stats[i] = roll_3d6()

        # Calculate the average of the rolled stats
        average_stat = sum(rolled_stats.values()) / len(rolled_stats)

        # Check if the average is at least 12 and if there is any stat >= 16
        if average_stat >= 12 and any(value >= 16 for value in rolled_stats.values()):
            break

        roll_count += 1

    return rolled_stats, roll_count






def sort_stats(stats):
    top_stats = sorted(stats, key=stats.get, reverse=True)
    stat_values = []
    
    for stat in top_stats:
        stat_values.append(stats[stat])
        
    top_stats = [stat + 1 for stat in top_stats]

    return list(zip(top_stats, stat_values))





def get_stat_combinations(stats):
    # Sort stats by value in descending and ascending order
    sorted_stats_desc = sorted(stats.items(), key=lambda x: -x[1])
    sorted_stats_asc = sorted(stats.items(), key=lambda x: x[1])

    # Find the highest and lowest values
    highest_value = sorted_stats_desc[0][1]
    lowest_value = sorted_stats_asc[0][1]

    # Get all stats with the highest and lowest values (to handle ties)
    highest_stats = [stat for stat, value in stats.items() if value == highest_value]
    lowest_stats = [stat for stat, value in stats.items() if value == lowest_value]

    # Check if we have enough unique stats for h2
    if len(highest_stats) < 2:
        # Fall back to the next highest stats if not enough for a pair
        next_highest_value = sorted_stats_desc[len(highest_stats)][1]
        highest_stats += [stat for stat, value in stats.items() if value == next_highest_value]

    # Generate combinations for the highest and lowest stats
    highest_combinations = list(combinations(set(highest_stats), 2))
    lowest_combinations = list(combinations(set(lowest_stats), 2)) if len(lowest_stats) > 1 else []

    # Create combinations of one highest and one lowest stat
    highest_lowest_combinations = [(h, l) for h in highest_stats for l in lowest_stats]

    return {
        'l2': lowest_combinations,
        'hl': highest_lowest_combinations,
        'h2': highest_combinations
    }


def get_stat_combos(top_stats):
    if len(top_stats) < 2:
        return None

    # Get the values of the highest and second-highest stats
    highest_value = top_stats[0][1]
    second_highest_value = None
    for stat in top_stats:
        if stat[1] < highest_value:
            second_highest_value = stat[1]
            break
    
    # Gather all stat IDs tied for the highest value
    primary_stats = [stat[0] for stat in top_stats if stat[1] == highest_value]
    
    # Gather all stat IDs tied for the second-highest value
    secondary_stats = [stat[0] for stat in top_stats if stat[1] == second_highest_value] if second_highest_value else []

    # Check if all primary and secondary stats meet the minimum threshold
    if highest_value < 16 or (second_highest_value and second_highest_value < 12):
        return None

    # Generate all combinations of primary and secondary stat pairs
    stat_combinations = list(product(primary_stats, secondary_stats))


    return stat_combinations

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


    # Handle special cases for Humans (8) and Half-Elves (12)
    if species_id in (8, 12):
        # Get the highest two stats, considering ties
        stat_combinations = get_stat_combinations(stats)
        highest_stats = stat_combinations['h2']

        # Check for ties in the highest stats
        tied_stats = [stat for stat in highest_stats if stat[0] in stats and stats[stat[0]] == stats[highest_stats[0][0]]]

        if species_id == 8:
            # For Humans: apply bonuses to two highest stats (considering ties)
            if len(tied_stats) >= 2:
                h1, h2 = tied_stats[0][0] + 1, tied_stats[1][0] + 1
            else:
                h1 = highest_stats[0][0] + 1
                h2 = highest_stats[0][1] + 1
            species_bonuses = [(h1, 1), (h2, 1)]

        elif species_id == 12:
            # For Half-Elves: similar handling, with an additional check for charisma (stat_id 6)
            if 6 not in [stat[0] for stat in highest_stats]:
                if len(tied_stats) >= 2:
                    h1, h2 = tied_stats[0][0] + 1, tied_stats[1][0] + 1
                else:
                    h1 = highest_stats[0][0] + 1
                    h2 = highest_stats[0][1] + 1
                species_bonuses = [(h1, 1), (h2, 1)]
            else:
                # If charisma is in the highest stats, use the next highest stats
                next_highest_stats = get_stat_combinations(stats)['hl']
                h1, h2 = next_highest_stats[0][0] + 1, next_highest_stats[1][0] + 1
                species_bonuses = [(h1, 1), (h2, 1)]
    
    # Handle all other species
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





def query_species(stat_id_pairs_list):
    conn = sqlite3.connect('dnd.db')
    cursor = conn.cursor()

    union_queries = []
    params = []

    # Loop through each sublist in the list of stat_id_pairs
    for sublist_index, stat_id_pairs in enumerate(stat_id_pairs_list):
        for n, stat_id in enumerate(stat_id_pairs):
            stat_id_1, stat_id_2 = stat_id  # Unpack the tuple into stat_id_1 and stat_id_2
            stat_id_1 += 1  
            stat_id_2 += 1

            # Build the query for each stat pair in the current sublist
            union_queries.append(f'''
                SELECT S.id, S.name, {sublist_index} as sublist_index, {n} as pair_index
                FROM Species S
                JOIN SpeciesBonus SB ON S.id = SB.species_id
                JOIN SpeciesBonus SB1 ON S.id = SB1.species_id AND SB1.stat_id = ?
                JOIN SpeciesBonus SB2 ON S.id = SB2.species_id AND SB2.stat_id = ?
                GROUP BY S.id                
            ''')

            # Add the parameters for the current stat pair
            params.extend([stat_id_1, stat_id_2])

    # Combine all the individual queries using UNION ALL
    complete_query = ' UNION ALL '.join(union_queries)

    # Execute the final query with all the parameters
    cursor.execute(complete_query, params)
    results = cursor.fetchall()
    # Organize the results into a dictionary by sublist_index and pair_index
    species_dict = {}

    for species_id, species_name, sublist_index, pair_index in results:
        if sublist_index not in species_dict:
            species_dict[sublist_index] = {}
        if pair_index not in species_dict[sublist_index]:
            species_dict[sublist_index][pair_index] = []
        species_dict[sublist_index][pair_index].append((species_id, species_name))

    conn.close()

    return species_dict




def query_flexible_species(stat_id_pairs_list):
    conn = sqlite3.connect('dnd.db')
    cursor = conn.cursor()

    union_queries = []
    params = []

    # Loop through each sublist in the list of stat_id_pairs
    for sublist_index, stat_id_pairs in enumerate(stat_id_pairs_list):
        for n, stat_id in enumerate(stat_id_pairs):
            stat_id_1, stat_id_2 = stat_id  # Unpack the tuple into stat_id_1 and stat_id_2
            stat_id_1 += 1  # Increment stat_id_1 (adjusting for your system's indexing)
            stat_id_2 += 1

            # Exclude Half-Elves (ID 12) if one of the stats is Charisma (ID 6)
            exclude_halfelf = "AND S.id != 12" if 6 in [stat_id_1, stat_id_2] else ""

            # Create the query for the current stat pair
            union_queries.append(f'''
                SELECT S.id, S.name, {sublist_index} as sublist_index, {n} as pair_index
                FROM Species S
                JOIN Custom_Bonuses CB ON S.id = CB.species_id
                WHERE ((CB.first_stat_id = ? AND CB.second_stat_id = ?)
                    OR (CB.first_stat_id = ? AND CB.second_stat_id = ?))
                    {exclude_halfelf}
                GROUP BY S.id
            ''')

            # Add parameters for the current stat pair
            params.extend([stat_id_1, stat_id_2, stat_id_2, stat_id_1])

    # Combine all queries into one with UNION ALL
    complete_query = ' UNION ALL '.join(union_queries)

    # Execute the complete query with all parameters
    cursor.execute(complete_query, params)
    results = cursor.fetchall()
    # Organize the results into a dictionary by sublist_index and pair_index
    species_dict = {}
    for species_id, species_name, sublist_index, pair_index in results:
        if sublist_index not in species_dict:
            species_dict[sublist_index] = {}
        if pair_index not in species_dict[sublist_index]:
            species_dict[sublist_index][pair_index] = []
        species_dict[sublist_index][pair_index].append((species_id, species_name))

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
    
    
    stat_ids = []
    for key, value in stat_combos.items():
        stat_ids.append(value)

    
    species = query_species(stat_ids)
    flex_species = query_flexible_species(stat_ids)

    

    
    
    all_species = {}

    # Get the maximum sublist index from both dictionaries
    max_index = max(max(species.keys(), default=-1), max(flex_species.keys(), default=-1))

    # Iterate through all possible sublist indices
    for i in range(max_index + 1):
        all_species[i] = {}

        # Merge entries from `species` dictionary
        if i in species:
            for pair_index, species_list in species[i].items():
                if pair_index not in all_species[i]:
                    all_species[i][pair_index] = set()
                # Add species entries as a set to avoid duplicates
                all_species[i][pair_index].update(species_list)

        # Merge entries from `flex_species` dictionary
        if i in flex_species:
            for pair_index, species_list in flex_species[i].items():
                if pair_index not in all_species[i]:
                    all_species[i][pair_index] = set()
                # Add species entries as a set to avoid duplicates
                all_species[i][pair_index].update(species_list)

        # Convert sets back to lists for the final result
        for pair_index in all_species[i]:
            all_species[i][pair_index] = list(all_species[i][pair_index])
            
        
        
        species_weights = {}
                # Calculate base weights from `all_species`
        for sublist_index, pairs in all_species.items():
            for pair_index, species_list in pairs.items():
                for species_id, species_name in species_list:
                    if species_id not in species_weights:
                        species_weights[species_id] = sublist_index
                        
                    if species_id not in (8, 12):
                    # Increment the weight by the sublist index (you can adjust this logic if needed)
                        species_weights[species_id] += sublist_index
                    # if species_id in (8, 12):
                    #     species_weights[species_id] -= sublist_index
                    # if species_id == 12:
                    #     species_weights[species_id] -= sublist_index * 2
        
        for species_id in list(species_weights.keys()):
            feat_weights = query_species_feats(species_id)
            for item in feat_weights:
                species_weights[species_id] += item[3]
                
                
    species = list(species_weights.keys())
    weights = list(species_weights.values())

    # Choose a species based on the calculated weights
    chosen_species = random.choices(species, weights=weights, k=1)[0]

    # Get the name of the chosen species
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





def query_class(stat_combinations):
    if not stat_combinations:
        return []

    conn = sqlite3.connect('dnd.db')
    cursor = conn.cursor()
    # Flatten stat combinations for SQL query
    primary_stats = [combo[0] for combo in stat_combinations]
    secondary_stats = [combo[1] for combo in stat_combinations]

    # Format placeholders for SQL IN clause
    primary_placeholders = ','.join(['?'] * len(primary_stats))
    secondary_placeholders = ','.join(['?'] * len(secondary_stats))

    query = f'''
        SELECT DISTINCT c.class_name
        FROM ClassAttributes ca
        JOIN Classes c ON ca.class_id = c.class_id
        WHERE ca.primary_stat_id IN ({primary_placeholders})
          AND ca.secondary_stat_id IN ({secondary_placeholders})
    '''

    params = primary_stats + secondary_stats
    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()

    return results






def select_class(sorted_stats):        
    stat_combos = get_stat_combos(sorted_stats)
    if not stat_combos:
        return None
    # Get potential classes from query_class
    potential_classes = query_class(stat_combos) 
#     
    
    
    
    if potential_classes is None:
        return None
    # Count the frequency of each class
    classes = {}
    for item in potential_classes:
        class_name = item[0]
        if class_name not in classes:
            classes[class_name] = 1
        else:
            classes[class_name] += 1
    
    # Filter out classes with count less than 1 (although it shouldn't be needed)
    classes = {k: v for k, v in classes.items() if v >= 1}

    # Find the maximum count
    max_count = max(classes.values(), default=0)
    
    # Get all classes that have the maximum count
    top_classes = [class_name for class_name, count in classes.items() if count == max_count]

    # If there is a tie, choose randomly among the tied classes
    if len(top_classes) > 1:
        return random.choice(top_classes)
    elif top_classes:
        return top_classes[0]  # Return the class with the highest count
    else:
        return None



def query_skills(optimal_stats):
    conn = sqlite3.connect('dnd.db')
    cursor = conn.cursor()
    
    
    stat_ids = [stat_id for stat_id, value in optimal_stats if value >= 16]
    if not stat_ids:
        return []

    placeholders = ', '.join(['?'] * len(stat_ids))
    
    skill_query = f'''
        SELECT S.skill_id, S.skill_name, S.governing_attribute
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
        WHERE B.skill_1 OR skill_2 in ({placeholders})
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
    dead_farmers,
    alignment
):
        # Load environment variables
    load_dotenv()

    # Get the API key from environment variables
    # api_key = os.getenv("OPENAI_API_KEY")
    # openai.api_key = api_key
    with open('key.txt', 'r') as file:
        api_key = file.read().strip()
        
    openai.api_key = api_key

    prompt = (
        f'Generate a detailed D&D character profile for a {alignment} {recommended_species} {chosen_class}. '
        f'Name the character and provide a structured response with the following sections: '
        f'\n\nBackground: Describe the character\'s backstory. The character comes from a {background} background. '
        f'{dead_farmers} people tragically died before this person became an adventurer. '
        f'Focus on how these events might have shaped the character\'s life. Avoid directly stating alignment.'
        f'\n\nGoal: Define the character\'s main objective or ambition without mentioning their alignment.'
        f'\n\nPersonality Trait: Provide a personality trait that reflects the character’s experiences and their stat array {updated_stats}.'
        f'\n\nQuirk: Give the character a unique quirk or habit that makes them memorable.'
    )
    
    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=[{'role': 'user', 'content': prompt}]
    )
    # Extract the content from the response
    content = response['choices'][0]['message']['content']
    
    
    return content




def determine_alignment(dead_farmers):
    
    alignments = {
        'Lawful Good': 100,
        'Neutral Good': 90,
        'Chaotic Good': 80,
        'Lawful Neutral': 70,
        'True Neutral': 40,
        'Chaotic Neutral': 55,
        'Lawful Evil': 14,
        'Neutral Evil': 15,
        'Chaotic Evil': 13,
    }
    for alignment in alignments:
        
        if 'Good' in alignment:
            alignments[alignment] = alignments[alignment] - dead_farmers
            
        if 'Neutral' in alignment:
            alignments[alignment] -= int(dead_farmers / 3)
            
        elif 'Evil' in alignment:
            alignments[alignment] += dead_farmers
            
        elif 'Lawful' in alignment:
            alignments[alignment] -= int(dead_farmers / 2)
            
        elif 'Chaotic' in alignment:
            alignments[alignment] += int(dead_farmers / 2)


    choices = list(alignments.keys())
    weights = list(alignments.values())

    return random.choices(choices, weights = weights, k = 1)[0]
















