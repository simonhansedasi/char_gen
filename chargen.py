import gen as g


def main():
    stats, attempts = g.roll_stats()
    dead_farmers = attempts
    
    
    
    
    
    recommended_species = None

    while recommended_species == None:
        stats, attempts = g.roll_stats()

        recommended_species, feats = g.recommend_species(stats)
        dead_farmers += attempts
        
    updated_stats = g.apply_species_bonus(stats, recommended_species)
    print(updated_stats)
    print(dead_farmers)
    
if __name__ == "__main__":
    main()