from flask import Flask, render_template, request, jsonify
import gen as g  # Import your character generation code
from flask_cors import CORS
# from collections import OrderedDict

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["http://localhost:4000", "https://simonhansedasi.github.io", "http://127.0.0.1:4000","https://872092e651ff.ngrok.app"]}})

@app.route('/generate_character', methods=['POST'])
def generate_character():

    print('poop')
    background = None
    species = None
    chosen_class = None
    dead_farmers = 0
    print(dead_farmers)

    # Main character generation loop
    while not (species and chosen_class and background):
        stats, attempts = g.roll_stats()
        dead_farmers += attempts
        species = g.recommend_species(stats)
        updated_stats = g.apply_species_bonus(stats, species)
        optimal_stats = g.sort_stats(updated_stats)
        background = g.pick_background(optimal_stats)
        chosen_class = g.select_class(optimal_stats)
    
    alignment = g.determine_alignment(dead_farmers)

    partial_response = jsonify({
        'stats': updated_stats,
        'species': species,
        'class': chosen_class,
        'background': background,  
        'dead_farmers': dead_farmers,
        'alignment': alignment,
        'backstory': "Generating character backstory...",  
    })
    return partial_response





@app.route('/generate_background', methods=['POST'])
def generate_background():
    try:
        stats = request.json.get('stats')
        species = request.json.get('species')
        chosen_class = request.json.get('class')
        background = request.json.get('background')
        dead_farmers = request.json.get('dead_farmers')
        alignment = request.json.get('alignment')
        # Log the received data
        print("Received data:", {
            'species': species,
            'class': chosen_class,
            'stats': stats,
            'dead_farmers': dead_farmers,
            'background': background,
            'alignment': alignment
        })

        # Validate input data
        if not all([species, chosen_class, background, stats, alignment]):
            return jsonify({"error": "Missing required fields"}), 400

        # Generate background based on character data
        character_background = g.generate_background(
            species,
            chosen_class,
            background,
            stats,
            dead_farmers,
            alignment
        )
        character_background = character_background.replace('\n', '<br>')

        return jsonify({'character_background': character_background})

    except Exception as e:
        print("Error in /generate_background:", str(e))
        return jsonify({"error": str(e)}), 500



if __name__ == '__main__':
    app.run( port = 5000, debug = True)

    
    
    
