from flask import Flask, request, jsonify, render_template
import openai
import os

app = Flask(__name__)

# Load your OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    text = data.get('text', '')

    detections = detect_using_gpt(text)
    return jsonify(detections)

@app.route('/generate_play', methods=['POST'])
def generate_play():
    data = request.json
    confirmed_inputs = data.get('confirmed_inputs', {})

    play_card = generate_play_using_gpt(confirmed_inputs)
    return jsonify(play_card)

# --- Use GPT to Detect Competitor, Persona, Objection ---
def detect_using_gpt(text):
    prompt = f"""
You are a Go-To-Market Intelligence Assistant.

Given the following call or email text:
\"\"\"{text}\"\"\"

Extract:
- The most likely Buyer Persona (e.g., CIO, CFO, VP Ops)
- Any Competitor Mentioned (e.g., Salesforce, Creatio, OutSystems)
- Any Objection Surfaced (e.g., pricing, speed-to-value, security)

Output in JSON:
{{
"persona": "Persona Name",
"competitor": "Competitor Name",
"objection": "Objection Theme"
}}
If you can't detect something, leave the field as "Unknown".
"""

    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    content = response['choices'][0]['message']['content']
    try:
        detections = eval(content)
    except Exception:
        detections = {
            "persona": "Unknown",
            "competitor": "Unknown",
            "objection": "Unknown"
        }
    return detections

# --- Use GPT to Generate Full Play Card ---
def generate_play_using_gpt(confirmed_inputs):
    prompt = f"""
You are a Competitive Battlecard Play Generator.

Given:
- Buyer Persona: {confirmed_inputs.get('persona')}
- Competitor Mentioned: {confirmed_inputs.get('competitor')}
- Objection Surfaced: {confirmed_inputs.get('objection')}

Generate a Play Card with the following sections:
- Strategic Narrative Frame (1 paragraph)
- Emotional Anchor (1-2 sentences)
- Landmine Trap (1 subtle destabilizing question)
- Competitive Counterpoint (1 clear sentence)
- Proof Point (optional, real-sounding case study)
- Psychological Reframe (smart twist)
- Next Best Action CTA

Output in JSON:
{{
"narrative": "...",
"emotional_anchor": "...",
"landmine": "...",
"counter": "...",
"proof": "...",
"reframe": "...",
"cta": "..."
}}
"""

    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4
    )

    content = response['choices'][0]['message']['content']
    try:
        play_card = eval(content)
    except Exception:
        play_card = {}

    return play_card

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
