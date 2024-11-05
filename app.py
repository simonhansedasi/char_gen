from flask import Flask, render_template, request, jsonify
import gen as g  # Import your character generation code
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["http://localhost:4000", "https://simonhansedasi.github.io"]}})  # Allow specific origins

@app.route('/generate_character', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Run character generator logic when form is submitted
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
        
        printed_stats = {new_key: updated_stats[old_key] for new_key, old_key in zip(g.stats, updated_stats.keys())}
        
        # Generate the background text
        character_background = g.generate_background(
            recommended_species, chosen_class, background, updated_stats, dead_farmers
        )
        character_background = character_background.replace('\n', '<br>')
        # print(character_background)
        # If needed, return JSON for the GET request
        return jsonify({
            'stats': printed_stats,
            'species': recommended_species,
            'class': chosen_class,
            'background': background,
            'character_background': character_background
        })

    # If GET request, show empty form
    # return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
