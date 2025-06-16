from flask import Flask, render_template, request, jsonify, session
import json

app = Flask(__name__)
app.secret_key = 'your_very_secure_key_here'

def load_translations(lang):
    try:
        with open(f'translations/{lang}.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

with open('crops.json', 'r', encoding='utf-8') as f:
    crop_data = json.load(f)

@app.route('/')
def index():
    lang = session.get('lang', 'en')
    translations = load_translations(lang)
    
    # Prepare crops with translated names
    translated_crops = []
    for crop in crop_data['crops']:
        trans_key = f"crop_{crop['id']}_name"
        translated_name = translations.get(trans_key, crop['name'])
        translated_crops.append({
            'id': crop['id'],
            'name': translated_name,
            'original_name': crop['name']  # Keep original for reference
        })
    
    return render_template('index.html',
                         crops=translated_crops,
                         tr=translations,
                         lang=lang)

@app.route('/set_language/<lang>')
def set_language(lang):
    session['lang'] = lang
    return jsonify({"status": "success"})

@app.route('/get_crop/<int:crop_id>')
def get_crop(crop_id):
    lang = session.get('lang', 'en')
    translations = load_translations(lang)

    crop = next((c for c in crop_data['crops'] if c['id'] == crop_id), None)
    if not crop:
        return jsonify({"error": "Crop not found"}), 404

    # Create a copy to avoid modifying original data
    translated_crop = crop.copy()
    translated_crop['diseases'] = []

    # Translate ALL crop fields
    for field in ['name', 'sowing_time', 'harvest_time', 'soil_type', 'temperature', 'rainfall']:
        trans_key = f"crop_{crop_id}_{field}"
        if trans_key in translations:
            translated_crop[field] = translations[trans_key]

    # Translate ALL diseases and ALL their fields
    for i, disease in enumerate(crop['diseases']):
        translated_disease = {}
        
        # Translate each field in the disease
        for field, value in disease.items():
            trans_key = f"crop_{crop_id}_disease_{i}_{field}"
            translated_disease[field] = translations.get(trans_key, value)
        
        translated_crop['diseases'].append(translated_disease)

    return jsonify(translated_crop)

if __name__ == '__main__':
    app.run(debug=True)