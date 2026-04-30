# char_gen

A population-scale stochastic simulation of D&D 5e (2014 PHB) character demographics, supporting the paper:

> **"The Fingerprint of Rules: Procedural Demographic Attractors in the D&D 5e Player's Handbook"**
> Simon-Hans Edasi

Rule-based generative systems implicitly define populations. This project treats the PHB's character creation rules as a generative demographic model and simulates 500,000 first-level characters to recover the theoretical population those rules produce — and to demonstrate a method for extracting latent population structure from any rule-based system.

## Key findings

- **Human-adjacent species** (Human, Human Variant, Half-Elf) account for ~37% of adventurers despite representing only 20% of available species — they function as global high-flexibility attractors.
- **Fighter** is the demographic default: ~25% of adventurers. Sensitivity analysis confirms this is entirely structural — not an artifact of the selection algorithm.
- **Physical-skill backgrounds** dominate; scholarly backgrounds (Sage) are the least represented.
- **Alignment** tracks world difficulty: stricter viability thresholds produce more "dead farmers" and shift the surviving population toward Evil/Chaotic alignments.

## Attractor taxonomy

The paper introduces *procedural demographic attractors* — stable configurations in a rule system's design space where structural constraints concentrate generated agents into recurring demographic patterns:

- **High-flexibility attractors** dominate the population (Fighter, human-adjacent species)
- **Conditional attractors** capture mass at specific configurations (Rangers, Clerics, classical demi-human species)
- **Low-density attractors** remain rare despite equal availability (Druids, Warlocks, fantastical species)
- **Dynamic attractors** shift under pressure (alignment, via the dead-farmer mechanism)

## Structure

```
gen.py                          core generation logic
simulate.py                     CLI Monte Carlo runner
tables.py                       LaTeX table generation from dnd.db
sensitivity_analysis.py         feat-weight sensitivity runner
dnd.db                          SQLite: game data + simulation results
main.tex                        paper (LaTeX)
references.bib                  bibliography
figs/                           generated figures
simulation.ipynb                main results analysis
attribute_class.ipynb           attribute–class correlations
attribute_correlation.ipynb     chi-squared residuals, Cramér's V
fighter_tiebreak_sensitivity.ipynb   tie-breaking sensitivity analysis
dndbeyond_comparison.ipynb      comparison with D&D Beyond 2023 player data
threshold_sensitivity.ipynb     viability threshold grid analysis
```

## Running the simulation

```bash
python simulate.py              # 50 runs × 10,000 characters (baseline)
```

Cached results are stored as `.pkl` files. Notebooks load from cache if present.

## Demographics at a glance

![Chi-squared residuals: species × class](chisq_resid_species_class.png)
![Attribute correlation across builds](attribute_correlation.png)

## Tech

Python, SQLite, NumPy, pandas, matplotlib, scipy, LaTeX, Jupyter
