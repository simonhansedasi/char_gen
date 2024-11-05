from flask import Flask, render_template, request
import gen as g  # Import your character generation code
from flask_cors import CORS

app = Flask(__name__)

# import os
# from dotenv import load_dotenv

# load_dotenv()  # Load environment variables from .env file
# api_key = os.getenv("API_KEY")

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET', 'POST'])
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
        # printed_stats = {new_key: original_dict[old_key] for new_key, old_key in zip(new_keys, original_dict.keys())}
        # print(g.stats)
        
        printed_stats = {}
        for new_key, old_key in zip(g.stats, updated_stats.keys()):
            printed_stats[new_key] = updated_stats[old_key]
        
        
        # Generate the background text
        character_background = g.generate_background(
            recommended_species, chosen_class, background, updated_stats, dead_farmers
        )
        character_background = character_background.replace('\n', '<br>')

        # Send data to HTML template to display
        return render_template(
            'index.html', 
            stats = printed_stats, 
            species = recommended_species,
            character_class=chosen_class, 
            background=background,
            # dead_farmers=dead_farmers, 
            character_background=character_background
        )

    # If GET request, show empty form
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
