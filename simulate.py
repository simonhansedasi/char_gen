"""
Run the D&D character generation simulation and save results to a pickle file.

Usage:
    python simulate.py                          # 10,000 chars x 50 sims (paper defaults)
    python simulate.py -n 1000 -s 10           # quick test run
    python simulate.py -o my_results.pkl       # custom output path
    python simulate.py --force                 # overwrite existing results
"""

import argparse
import os
import pickle

from tqdm import tqdm
import gen as g


def generate():
    dead_farmers = 0
    recommended_species = None
    chosen_class = None
    background = None

    while not (recommended_species and chosen_class and background):
        stats, attempts = g.roll_stats()
        dead_farmers += attempts
        recommended_species = g.recommend_species(stats)
        updated_stats = g.apply_species_bonus(stats, recommended_species)
        optimal_stats = g.sort_stats(updated_stats)
        chosen_class = g.select_class(optimal_stats)
        background = g.pick_background(optimal_stats)

    alignment = g.determine_alignment(dead_farmers)
    return stats, recommended_species, chosen_class, background, alignment, dead_farmers


def track_selections(num_iterations):
    species_count = {}
    classes_count = {}
    background_count = {}
    alignment_count = {}
    dead_farmers_count = {}
    species_class_count = {}
    species_background_count = {}
    class_background_count = {}
    stats_dict = {}

    for i in range(num_iterations):
        stats, species, chosen_class, chosen_background, alignment, dead_farmers = generate()

        species_count[species] = species_count.get(species, 0) + 1
        classes_count[chosen_class] = classes_count.get(chosen_class, 0) + 1
        background_count[chosen_background] = background_count.get(chosen_background, 0) + 1
        alignment_count[alignment] = alignment_count.get(alignment, 0) + 1
        dead_farmers_count[dead_farmers] = dead_farmers_count.get(dead_farmers, 0) + 1

        if species not in species_class_count:
            species_class_count[species] = {}
        species_class_count[species][chosen_class] = species_class_count[species].get(chosen_class, 0) + 1

        if species not in species_background_count:
            species_background_count[species] = {}
        species_background_count[species][chosen_background] = species_background_count[species].get(chosen_background, 0) + 1

        if chosen_class not in class_background_count:
            class_background_count[chosen_class] = {}
        class_background_count[chosen_class][chosen_background] = class_background_count[chosen_class].get(chosen_background, 0) + 1

        stats_dict[i] = stats

    return (
        species_count, classes_count, background_count,
        alignment_count, dead_farmers_count, species_class_count,
        species_background_count, class_background_count, stats_dict,
    )


def run_simulation(num_simulations, num_iterations):
    results = []
    for _ in tqdm(range(num_simulations), desc="Simulations"):
        results.append(track_selections(num_iterations))
    return results


def main():
    parser = argparse.ArgumentParser(description="D&D 5e character generation simulation")
    parser.add_argument("-n", "--num-iterations", type=int, default=10_000,
                        help="Characters per simulation (default: 10000)")
    parser.add_argument("-s", "--num-simulations", type=int, default=50,
                        help="Number of simulation runs (default: 50)")
    parser.add_argument("-o", "--output", default="sim_results.pkl",
                        help="Output pickle file (default: sim_results.pkl)")
    parser.add_argument("--force", action="store_true",
                        help="Overwrite existing results file")
    args = parser.parse_args()

    if os.path.exists(args.output) and not args.force:
        print(f"Results already exist at '{args.output}'. Use --force to overwrite.")
        return

    print(f"Running {args.num_simulations} simulations x {args.num_iterations:,} characters each...")
    results = run_simulation(args.num_simulations, args.num_iterations)

    with open(args.output, "wb") as f:
        pickle.dump(results, f)
    print(f"Saved to '{args.output}'")


if __name__ == "__main__":
    main()
