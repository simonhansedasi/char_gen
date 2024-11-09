import gen as g


def main():
    dead_farmers = 0
    
    
    
    recommended_species = None
    
    chosen_class = None
    
    background = None

    while not (recommended_species and background and chosen_class):
            
        stats, attempts = g.roll_stats()
        # print(stats)
        # stats = {0:15, 1:15, 2:13, 3:13, 4:14, 5:16}
        # print('rolled stats:', stats)
        # attempts = 0
        dead_farmers += attempts

        recommended_species = g.recommend_species(stats)
        
        
        updated_stats = g.apply_species_bonus(stats, recommended_species)
        
        optimal_stats = g.sort_stats(updated_stats)
    
        # optimal_stats = g.get_top_stats(updated_stats)
        # print(optimal_stats)
        background = g.pick_background(optimal_stats)
    
    
        chosen_class = g.select_class(optimal_stats)

    alignment = g.determine_alignment(dead_farmers)
    printed_stats = {}
    for new_key, old_key in zip(g.stats, updated_stats.keys()):
        printed_stats[new_key] = updated_stats[old_key]
    
    
    print(alignment)
    print(printed_stats)
    print(recommended_species)
    print(background)
    print(chosen_class)
    print(f'{dead_farmers} dead farmers')
    print('')

#     backstory = g.generate_background(
#         recommended_species,
#         chosen_class,
#         background,
#         updated_stats,
#         dead_farmers
#     )
    
#     print(backstory)
    
    # print(updated_stats)
if __name__ == "__main__":
    main()