from flask import Flask, render_template, request, jsonify
import gen as g  # Import your character generation code
from flask_cors import CORS
from collections import OrderedDict

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["http://localhost:4000", "https://simonhansedasi.github.io", "https://char-gen.onrender.com", "http://127.0.0.1:5000/"]}})
# Allow specific origins
@app.after_request
def add_security_headers(response):
    response.headers['Permissions-Policy'] = 'interest-cohort=()'  # Disable FLoC
    return response

@app.route('/generate_character', methods=['POST'])
def generate_character():
    background = None
    species = None
    chosen_class = None
    
    dead_farmers = 0

    # Main character generation without background
    while not (species and chosen_class and background):
        stats, attempts = g.roll_stats()
        dead_farmers += attempts
        species = g.recommend_species(stats)
        updated_stats = g.apply_species_bonus(stats, species)
        optimal_stats = g.sort_stats(updated_stats)
        chosen_class = g.select_class(optimal_stats)
        background = g.pick_background(optimal_stats)

    # Respond with essential data first
    partial_response = jsonify({
        'stats': updated_stats,
        'species': species,
        'class': chosen_class,
        'background': background,
        'character_background': "Generating character background...",
    })

    # Return this partial data while background is generated in the background
    return partial_response
    # # If GET request, show empty form
    # return render_template('index.html')
    

@app.route('/generate_background', methods=['POST'])
def generate_background():
    species = request.json.get('species')
    chosen_class = request.json.get('class')
    stats = request.json.get('stats')
    dead_farmers = request.json.get('dead_farmers')
    background = request.json.get('background')

    # Generate background based on character data
    character_background = g.generate_background(species, chosen_class, background, stats, dead_farmers)
    # character_background = character_background.replace('\n', '<br>')

    return jsonify({'character_background': character_background})
if __name__ == '__main__':
    app.run(debug=True)
