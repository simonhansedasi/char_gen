// Define the desired order for stats
const statOrder = ['STR', 'DEX', 'CON', 'INT', 'WIS', 'CHA'];

let baseUrl = '';

// Function to fetch the base URL from the config.txt file
async function fetchBaseUrl() {
    try {
        const response = await fetch('config.txt');
        if (!response.ok) {
            throw new Error('Failed to fetch config.txt');
        }
        const url = await response.text();
        baseUrl = url.trim();
        console.log("Base URL fetched:", baseUrl);
    } catch (error) {
        console.error('Error fetching base URL:', error);
        alert('Failed to fetch base URL. Please contact support.');
    }
}

// Custom function to handle fetch with a timeout
async function fetchWithTimeout(resource, options = {}) {
    console.log("Starting fetchWithTimeout...");

    const { timeout = 1000 } = options;
    const controller = new AbortController();
    const id = setTimeout(() => controller.abort(), timeout);

    try {
        console.log("Sending request to:", resource);

        const response = await fetch(resource, {
            ...options,
            signal: controller.signal
        });
        clearTimeout(id);
        if (!response.ok) {
            throw new Error(`Request failed with status ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error(`Fetch error: ${error.message}`);
        console.log('oopsy uh oh');
        throw error;
    }
}

// Main function to load the character data and update the UI
async function loadCharacter() {
    const characterContainer = document.getElementById("character-container");
    characterContainer.innerHTML = "Generating character...";
    console.log('starting up');

    try {
        // Ensure baseUrl is fetched first
        await fetchBaseUrl();

        console.log("Starting character generation...");

        // Fetch main character data without background
        const characterData = await fetchWithTimeout(`${baseUrl}/generate_character`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ /* your request payload */ })
        });

        // Log and validate character data
        console.log("Character data response:", characterData);

        if (!characterData || !characterData.stats) {
            throw new Error("Invalid character data: Missing stats.");
        }

        // Reorder stats based on the defined statOrder array
        const orderedStats = statOrder.reduce((acc, stat, index) => {
            if (characterData.stats && characterData.stats[index] !== undefined) {
                acc[stat] = characterData.stats[index];
            }
            return acc;
        }, {});

        if (Object.keys(orderedStats).length === 0) {
            throw new Error("No stats found after reordering.");
        }

        // Display basic character information
        characterContainer.innerHTML = `
            <h2>${characterData.alignment} ${characterData.species} ${characterData.class}</h2>
            <h3>Stats:</h3> [${Object.entries(orderedStats).map(([key, value]) => `${key}: ${value}`).join(', ')}]
            <p><strong>Background:</strong> ${characterData.background}</p>
            <p><strong>Character Backstory:</strong></p>
            <div id="backstory-container">Loading backstory...</div>
        `;
        console.log("Payload for generate_background:", {
            species: characterData.species,
            class: characterData.class,
            stats: characterData.stats,
            dead_farmers: characterData.dead_farmers,
            background: characterData.background,
            alignment: characterData.alignment
        });

        // Fetch background data including alignment
        const backgroundData = await fetchWithTimeout(`${baseUrl}/generate_background`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                species: characterData.species,
                class: characterData.class,
                stats: characterData.stats,
                dead_farmers: characterData.dead_farmers,
                background: characterData.background,
                alignment: characterData.alignment
            }),
            timeout: 100000
        });

        console.log("Background data response:", backgroundData);

        // Display the backstory in the UI
        if (backgroundData && backgroundData.character_background) {
            document.getElementById("backstory-container").innerHTML = backgroundData.character_background.replace(/\n/g, '<br>');
        } else {
            throw new Error("Invalid background data: Missing character backstory.");
        }

    } catch (error) {
        console.error("Error loading character:", error.message || error);
        characterContainer.innerHTML = `<p style="color: red;">Error loading character data: ${error.message}</p>`;
    }
}

// Delay the character generation to allow the backend to initialize
window.onload = () => setTimeout(loadCharacter, 1000);
