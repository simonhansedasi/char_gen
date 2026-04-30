"""
Species feat weight sensitivity analysis.

Tests how much the species distribution changes when feat weights are scaled
by different factors (including zeroing them out entirely). Outputs a summary
table and a plot suitable for the paper.
"""

import random
import sqlite3
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import entropy as kl_entropy
from tqdm import tqdm

import gen as g

# ---------------------------------------------------------------------------
# Patched version of recommend_species that accepts a feat weight scale factor
# ---------------------------------------------------------------------------

def recommend_species_scaled(stats, feat_scale=1.0):
    """Like g.recommend_species but multiplies all feat weights by feat_scale."""
    stat_combos = g.get_stat_combinations(stats)
    stat_ids = [value for _, value in stat_combos.items()]

    species = g.query_species(stat_ids)
    flex_species = g.query_flexible_species(stat_ids)

    all_species = {}
    max_index = max(max(species.keys(), default=-1), max(flex_species.keys(), default=-1))

    for i in range(max_index + 1):
        all_species[i] = {}
        if i in species:
            for pair_index, species_list in species[i].items():
                if pair_index not in all_species[i]:
                    all_species[i][pair_index] = set()
                all_species[i][pair_index].update(species_list)
        if i in flex_species:
            for pair_index, species_list in flex_species[i].items():
                if pair_index not in all_species[i]:
                    all_species[i][pair_index] = set()
                all_species[i][pair_index].update(species_list)
        for pair_index in all_species[i]:
            all_species[i][pair_index] = list(all_species[i][pair_index])

    species_weights = {}
    for sublist_index, pairs in all_species.items():
        for pair_index, species_list in pairs.items():
            for species_id, species_name in species_list:
                if species_id not in species_weights:
                    species_weights[species_id] = sublist_index
                if species_id not in (8, 12):
                    species_weights[species_id] += sublist_index

    for species_id in list(species_weights.keys()):
        feat_weights = g.query_species_feats(species_id)
        for item in feat_weights:
            species_weights[species_id] += item[3] * feat_scale   # <-- scaled here

    chosen_species_id = random.choices(
        list(species_weights.keys()),
        weights=list(species_weights.values()),
        k=1
    )[0]
    return g.get_species_name(chosen_species_id)


def generate_scaled(feat_scale=1.0):
    dead_farmers = 0
    recommended_species = None
    chosen_class = None
    background = None

    while not (recommended_species and chosen_class and background):
        stats, attempts = g.roll_stats()
        dead_farmers += attempts
        recommended_species = recommend_species_scaled(stats, feat_scale=feat_scale)
        updated_stats = g.apply_species_bonus(stats, recommended_species)
        optimal_stats = g.sort_stats(updated_stats)
        chosen_class = g.select_class(optimal_stats)
        background = g.pick_background(optimal_stats)

    alignment = g.determine_alignment(dead_farmers)
    return recommended_species, chosen_class, background, alignment


def run_sensitivity(feat_scales, n_chars=10000, n_sims=20):
    """
    For each feat_scale value, run n_sims simulations of n_chars characters.
    Returns a dict mapping scale -> DataFrame of species mean counts.
    """
    results = {}
    for scale in feat_scales:
        label = f"{scale:.1f}x"
        print(f"\nRunning feat_scale={label}")
        sim_counts = []
        for _ in tqdm(range(n_sims)):
            counts = {}
            for __ in range(n_chars):
                species, _, __, ___ = generate_scaled(feat_scale=scale)
                counts[species] = counts.get(species, 0) + 1
            sim_counts.append(counts)

        # Aggregate across simulations
        all_species = sorted(set(k for c in sim_counts for k in c))
        df = pd.DataFrame(
            [{s: c.get(s, 0) for s in all_species} for c in sim_counts]
        )
        results[scale] = df

    return results


def summarize(results, n_chars=10000):
    """Build a summary DataFrame: mean ± std for each species at each scale."""
    scales = sorted(results.keys())
    all_species = sorted(set(
        col for df in results.values() for col in df.columns
    ))

    rows = []
    for scale in scales:
        df = results[scale]
        row = {"feat_scale": scale}
        for sp in all_species:
            if sp in df.columns:
                row[sp] = df[sp].mean()
            else:
                row[sp] = 0.0
        rows.append(row)

    summary = pd.DataFrame(rows).set_index("feat_scale")
    return summary


def compute_entropy(summary):
    """Shannon entropy of the species distribution at each scale."""
    entropies = {}
    for scale, row in summary.iterrows():
        probs = row.values / row.values.sum()
        probs = probs[probs > 0]
        entropies[scale] = kl_entropy(probs)
    return entropies


def plot_sensitivity(summary, entropies, filename="feat_weight_sensitivity.png"):
    fig, axes = plt.subplots(2, 1, figsize=(14, 10))

    # Top: species distribution heatmap across scales
    ax = axes[0]
    data = summary.T  # species as rows, scale as columns
    data_pct = data.div(data.sum(axis=0), axis=1) * 100
    im = ax.imshow(data_pct.values, aspect='auto', cmap='YlOrRd')
    ax.set_xticks(range(len(summary.index)))
    ax.set_xticklabels([f"{s:.1f}x" for s in summary.index], fontsize=11)
    ax.set_yticks(range(len(data_pct.index)))
    ax.set_yticklabels(data_pct.index, fontsize=10)
    ax.set_xlabel("Feat Weight Scale Factor", fontsize=13)
    ax.set_ylabel("Species", fontsize=13)
    ax.set_title("Species Distribution (%) vs. Feat Weight Scale", fontsize=14)
    plt.colorbar(im, ax=ax, label="% of Population")

    # Bottom: Shannon entropy vs scale
    ax2 = axes[1]
    scales = sorted(entropies.keys())
    ent_vals = [entropies[s] for s in scales]
    ax2.plot([f"{s:.1f}x" for s in scales], ent_vals, marker='o', linewidth=2)
    ax2.set_xlabel("Feat Weight Scale Factor", fontsize=13)
    ax2.set_ylabel("Shannon Entropy (nats)", fontsize=13)
    ax2.set_title("Species Distribution Diversity vs. Feat Weight Scale", fontsize=14)
    ax2.grid(axis='y', linestyle='--', alpha=0.7)

    plt.tight_layout()
    plt.savefig(filename, dpi=150)
    plt.show()
    print(f"Saved to {filename}")


def print_latex_sensitivity(summary):
    """Print a compact LaTeX table of species % at each scale."""
    data_pct = summary.div(summary.sum(axis=1), axis=0) * 100
    data_pct = data_pct.round(1)
    data_pct.index = [f"{s:.1f}x" for s in data_pct.index]
    print("\n=== LaTeX sensitivity table ===")
    print(data_pct.T.to_latex(float_format="%.1f"))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Scale factors to test: 0 (no feat weights), 0.5x, 1x (baseline), 2x, 4x
    FEAT_SCALES = [0.0, 0.5, 1.0, 2.0, 4.0]
    N_CHARS = 10000
    N_SIMS = 20         # fewer sims than main paper for speed; increase if needed

    results = run_sensitivity(FEAT_SCALES, n_chars=N_CHARS, n_sims=N_SIMS)
    summary = summarize(results, n_chars=N_CHARS)
    entropies = compute_entropy(summary)

    print("\n=== Shannon entropy per scale ===")
    for scale, ent in sorted(entropies.items()):
        print(f"  {scale:.1f}x: {ent:.4f} nats")

    plot_sensitivity(summary, entropies)
    print_latex_sensitivity(summary)

    import pickle
    with open("sensitivity_results.pkl", "wb") as f:
        pickle.dump({"results": results, "summary": summary, "entropies": entropies}, f)
    print("\nFull results saved to sensitivity_results.pkl")
