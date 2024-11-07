from flask import Flask, render_template, request, jsonify
import gen as g  # Import your character generation code
from flask_cors import CORS
from collections import OrderedDict

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["http://localhost:4000", "https://simonhansedasi.github.io", "https://char-gen.onrender.com", "http://127.0.0.1:5000"]}})
# Allow specific origins
@app.after_request
def add_security_headers(response):
    response.headers['Permissions-Policy'] = 'interest-cohort=()'  # Disable FLoC
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'  # Enforce HTTPS
    response.headers['Content-Security-Policy'] = "default-src 'self';"  # Add CSP
    response.headers['X-Frame-Options'] = 'DENY'  # Prevent iframe embedding
    response.headers['X-XSS-Protection'] = '1; mode=block'  # Prevent cross-site scripting
    response.headers['X-Content-Type-Options'] = 'nosniff'  # Prevent MIME-type sniffing
    return response


@app.route('/generate_character', methods=['POST'])
def generate_character():
    background = None
    species = None
    chosen_class = None
    dead_farmers = 0

    # Main character generation loop
    while not (species and chosen_class and background):
        stats, attempts = g.roll_stats()
        dead_farmers += attempts
        species = g.recommend_species(stats)
        updated_stats = g.apply_species_bonus(stats, species)
        optimal_stats = g.sort_stats(updated_stats)
        background = g.pick_background(optimal_stats)
        chosen_class = g.select_class(optimal_stats)

    partial_response = jsonify({
        'stats': updated_stats,
        'species': species,
        'class': chosen_class,
        'background': background,  
        'dead_farmers': dead_farmers,
        'backstory': "Generating character backstory...",  
    })
    return partial_response





# Separate route to generate and fetch the background
@app.route('/generate_background', methods=['POST'])
def generate_background():
    stats = request.json.get('stats')
    species = request.json.get('species')
    chosen_class = request.json.get('class')
    background = request.json.get('background')
    dead_farmers = request.json.get('dead_farmers')
    
    attributes = ['STR', 'DEX', 'CON', 'INT', 'WIS', 'CHA']

    ordered_stats = {attributes[i]: stats.get(i) for i in range(len(attributes))}


    # Generate background based on character data
    character_background = g.generate_background(species, chosen_class, background, ordered_stats, dead_farmers)
    character_background = character_background.replace('\n', '<br>')

    # Return the character background
    return jsonify({'character_background': character_background})


if __name__ == '__main__':
    app.run(debug=True)

    
    
    
