import gen as g


def main():
    stats, attempts = g.roll_stats()
    dead_farmers = attempts
    
    
    
    
    
    recommended_species = None

    while recommended_species == None:
        stats, attempts = g.roll_stats()

        recommended_species = g.recommend_species(stats)
        dead_farmers += attempts
        
    print(recommended_species)
    print(dead_farmers)
    updated_stats = g.apply_species_bonus(stats, recommended_species)
    print(updated_stats)
    
if __name__ == "__main__":
    main()