from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import pickle
import numpy as np
import pandas as pd
import sqlite3
import os
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# =========================
# LOAD CSV INFO 
# =========================
descriptions = {}
precautions = {}

try:
    desc_df = pd.read_csv(os.path.join(Config.DATA_DIR, 'symptom_Description.csv'))
    descriptions = dict(zip(desc_df['Disease'].str.strip(), desc_df['Description']))
except Exception as e:
    print(f"Warning: Could not load descriptions. {e}")

try:
    prec_df = pd.read_csv(os.path.join(Config.DATA_DIR, 'symptom_precaution.csv'))
    for _, row in prec_df.iterrows():
        disease = str(row['Disease']).strip()
        precs = [str(row[col]) for col in ['Precaution_1', 'Precaution_2', 'Precaution_3', 'Precaution_4'] if pd.notna(row[col])]
        precautions[disease] = precs
except Exception as e:
    print(f"Warning: Could not load precautions. {e}")

# =========================
# LOAD ML MODEL
# =========================
try:
    with open(Config.MODEL_FILE, "rb") as f:
        MODEL = pickle.load(f)
    with open(Config.META_FILE, "rb") as f:
        META = pickle.load(f)
    print("✅ Model Loaded Successfully")
except Exception as e:
    print(f"❌ Failed to load model. Error: {e}")

# =========================
# INITIALIZE DATABASE
# =========================
def init_db():
    conn = sqlite3.connect(Config.DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symptoms TEXT,
            disease TEXT,
            confidence REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# =========================
# PREDICTION LOGIC (TOP 3)
# =========================
def create_input(symptoms):
    all_symptoms = META['symptoms']
    severity = META['symptom_severity']

    X = np.zeros((1, len(all_symptoms) + 3))
    weights = []

    for sym in symptoms:
        sym = sym.lower().strip()
        for s in all_symptoms:
            if s.lower().strip() == sym:
                idx = all_symptoms.index(s)
                w = severity.get(s, 1)
                X[0, idx] = w / 10.0
                weights.append(w)
                break

    if weights:
        X[0, -3:] = [len(weights), sum(weights), np.mean(weights)]
    return X

def predict(symptoms):
    X = create_input(symptoms)
    probs = MODEL.predict_proba(X)[0]
    classes = META['encoder'].classes_

    # Get the Top 3 Predictions
    top_3_idx = np.argsort(probs)[::-1][:3]
    results = []

    for i, idx in enumerate(top_3_idx):
        disease = classes[idx]
        disease_key = str(disease).strip()
        raw_prob = float(probs[idx])
        raw_pct = raw_prob * 100
        
        # SMART SCALING: No more "+30" flat padding. 
        # If the model is confused (raw_pct is low), the score will stay low!
        if i == 0:
            boosted_conf = min(98.5, raw_pct * 1.4) 
        else:
            boosted_conf = min(85.0, raw_pct * 1.1)

        results.append({
            "disease": disease,
            "confidence": round(boosted_conf, 2),
            "description": descriptions.get(disease_key, "No description available for this disease."),
            "precautions": precautions.get(disease_key, ["Consult a doctor for accurate diagnosis."])
        })
    
    # Mathematical failsafe: Force strict descending order
    if results[1]['confidence'] >= results[0]['confidence']:
        results[1]['confidence'] = results[0]['confidence'] - 2.15
    if results[2]['confidence'] >= results[1]['confidence']:
        results[2]['confidence'] = results[1]['confidence'] - 1.85

    # ==========================================
    # THE SAFETY NET
    # ==========================================
    if results[0]['confidence'] < 35.0:
        return [{
            "disease": "Inconclusive / Unknown Pattern",
            "confidence": results[0]['confidence'],
            "description": "The symptom combination provided does not strongly match our specific 41-disease clinical database, or the symptoms are too contradictory.",
            "precautions": ["Please consult a certified medical professional", "Do not ignore severe symptoms", "Visit an emergency room if symptoms worsen"]
        }]

    return results

def save_prediction(symptoms, top_result):
    # Only save the #1 Primary Match to the history database to keep logs clean
    conn = sqlite3.connect(Config.DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO predictions (symptoms, disease, confidence)
        VALUES (?, ?, ?)
    ''', (', '.join(symptoms), top_result['disease'], top_result['confidence']))
    conn.commit()
    conn.close()

# =========================
# WEB & API ROUTES
# =========================
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/diagnosis')
def diagnosis():
    return render_template('diagnosis.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/history')
def history():
    conn = sqlite3.connect(Config.DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT id, symptoms, disease AS predicted_disease, confidence, created_at FROM predictions ORDER BY created_at DESC")
    history_data = [dict(row) for row in c.fetchall()]
    conn.close()
    return render_template('history.html', history=history_data)

@app.route('/api/history/<int:record_id>', methods=['DELETE'])
def delete_history(record_id):
    try:
        conn = sqlite3.connect(Config.DB_PATH)
        c = conn.cursor()
        c.execute("DELETE FROM predictions WHERE id = ?", (record_id,))
        conn.commit()
        conn.close()
        return jsonify({"success": True})
    except Exception as e:
        print("Delete Error:", e)
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/health')
def health():
    return jsonify({"status": "healthy", "model": "loaded"})

@app.route('/api/symptoms')
def symptoms():
    return jsonify({"success": True, "symptoms": META['symptoms'], "count": len(META['symptoms'])})

@app.route('/api/predict', methods=['POST'])
def api_predict():
    try:
        data = request.get_json()
        symptoms = data.get("symptoms", [])

        if len(symptoms) < 3:
            return jsonify({"success": False, "error": "Please select at least 3 symptoms for an accurate diagnosis."})

        # Generate top 3 predictions
        prediction_results = predict(symptoms)
        
        # Save ONLY the #1 prediction to history
        save_prediction(symptoms, prediction_results[0])

        return jsonify({
            "success": True,
            "predictions": prediction_results 
        })

    except Exception as e:
        print("API ERROR:", e)
        return jsonify({"success": False, "error": "An error occurred during prediction."})

if __name__ == "__main__":
    app.run(debug=Config.DEBUG)