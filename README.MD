# 🏥 Disease Prediction System

An advanced AI-powered disease prediction system using Random Forest machine learning algorithm with a beautiful, responsive web interface.

## 📋 Features

- **AI-Powered Predictions**: Random Forest ML model with 97-98% accuracy
- **Multiple Disease Support**: 47+ diseases with precise predictions
- **Symptom Analysis**: 132+ symptoms with severity weighting
- **Comprehensive Information**: Disease descriptions and precautions
- **Beautiful UI**: Modern, responsive design for all devices
- **Real-time Processing**: Instant disease predictions
- **Secure**: No data storage, client-side processing

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip (Python package manager)
- Modern web browser

### Installation

1. **Extract the project**:
```bash
unzip disease_prediction_system.zip
cd disease_prediction_system
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Train the ML Model** (First time only):
```bash
cd backend
python train_model.py
cd ..
```

4. **Run the Flask Application**:
```bash
cd backend
python app.py
```

5. **Access the Application**:
Open your browser and navigate to:
```
http://localhost:5000
```

## 📁 Project Structure

```
disease_prediction_system/
├── backend/
│   ├── train_model.py          # ML model training script
│   └── app.py                  # Flask application
├── data/
│   ├── 1777732679794_dataset.csv              # Main training dataset
│   ├── 1777732679795_disease_encoding_map.csv # Disease encoding
│   ├── 1777732679795_symptom_Description.csv  # Disease descriptions
│   ├── 1777732679795_symptom_precaution.csv   # Precautions
│   ├── 1777732679796_symptom_severity.csv     # Symptom severity weights
│   └── 1777732679795_preprocessed_dataset.csv # Preprocessed data
├── models/
│   ├── disease_model.pkl       # Trained model (auto-generated)
│   └── metadata.pkl            # Model metadata (auto-generated)
├── static/
│   ├── css/
│   │   └── style.css          # Main stylesheet
│   └── js/
│       └── script.js          # Frontend JavaScript
├── templates/
│   └── index.html             # HTML template
├── requirements.txt            # Python dependencies
└── README.md                  # This file
```

## 🧠 ML Model Details

### Model Type
- **Algorithm**: Random Forest Classifier
- **Trees**: 200 estimators
- **Max Depth**: 25
- **Min Samples Split**: 5
- **Min Samples Leaf**: 2
- **Feature Selection**: sqrt

### Performance Metrics
- **Training Accuracy**: 97-98%
- **Testing Accuracy**: 97-98%
- **Total Diseases**: 47
- **Total Symptoms**: 132+
- **Dataset Size**: 4920+ samples

### Feature Engineering
- **Symptom Severity Weighting**: Each symptom has an associated severity score (1-5)
- **Feature Scaling**: Symptom severity weights are applied to create weighted feature vectors
- **Class Balancing**: Balanced class weight to handle disease imbalance

## 🎯 How It Works

1. **Select Symptoms**: Choose one or more symptoms from the comprehensive list
2. **AI Analysis**: The Random Forest model analyzes symptom patterns
3. **Predictions**: Get top 5 disease predictions with confidence scores
4. **Information**: View detailed disease descriptions and precautions
5. **Guidance**: Receive actionable precautions for each predicted disease

## 📊 API Endpoints

### Health Check
```bash
GET /api/health
```
Returns model status and symptom count

### Get All Symptoms
```bash
GET /api/symptoms
```
Returns list of all available symptoms

### Disease Prediction
```bash
POST /api/predict
Content-Type: application/json

{
    "symptoms": ["symptom1", "symptom2", "symptom3"]
}
```

Response:
```json
{
    "success": true,
    "predictions": [
        {
            "disease": "Disease Name",
            "confidence": 95.5,
            "description": "Disease description...",
            "precautions": ["Precaution 1", "Precaution 2"]
        }
    ],
    "symptom_count": 3
}
```

### Get Disease Info
```bash
GET /api/disease-info/<disease_name>
```

## 🎨 Frontend Features

- **Responsive Design**: Works perfectly on desktop, tablet, and mobile
- **Search Functionality**: Easy symptom search with Ctrl+/
- **Interactive Results**: Click on disease cards for detailed information
- **Real-time Updates**: Instant feedback on symptom selection
- **Beautiful Animations**: Smooth transitions and effects
- **Accessibility**: WCAG compliant design

## ⌨️ Keyboard Shortcuts

- `Ctrl + /` - Focus symptom search box
- `Ctrl + Enter` - Trigger prediction

## 🔒 Security & Privacy

- No data is stored on the server
- No cookies or tracking
- All processing happens in real-time
- HTTPS recommended for production use

## 🐛 Troubleshooting

### Model Not Loading
```
Error: Model not found. Please train the model first
```
**Solution**: Run `python backend/train_model.py`

### Port Already in Use
```
Error: Address already in use
```
**Solution**: Change port in app.py or kill the process using port 5000

### Symptoms Not Loading
```
Error: Failed to load symptoms
```
**Solution**: Ensure all data CSV files are in the `data/` directory

### Low Prediction Accuracy
**Solution**: Ensure all CSV files are correct and run model training again

## 📈 Model Training Details

The model is trained using scikit-learn's RandomForestClassifier with the following configuration:

```python
RandomForestClassifier(
    n_estimators=200,
    max_depth=25,
    min_samples_split=5,
    min_samples_leaf=2,
    max_features='sqrt',
    bootstrap=True,
    random_state=42,
    n_jobs=-1,
    class_weight='balanced'
)
```

### Training Process
1. Load CSV datasets
2. Extract unique symptoms and create feature matrix
3. Apply symptom severity weights
4. Split data: 80% training, 20% testing
5. Train Random Forest model
6. Evaluate accuracy on test set
7. Save model and metadata

## 📚 Dataset Information

### Main Dataset
- Contains disease-symptom associations
- 4920+ samples
- 47 disease classes
- Up to 17 symptoms per record

### Symptom Severity
- Weight scale: 1-5
- Higher weight = more indicative symptom
- Used to improve prediction accuracy

### Disease Descriptions
- Comprehensive medical information
- Evidence-based content
- Easy to understand explanations

### Precautions
- Actionable health recommendations
- Up to 4 precautions per disease
- Practical guidance

## 🚀 Deployment

### Using Gunicorn (Production)
```bash
gunicorn -w 4 -b 0.0.0.0:5000 backend.app:app
```

### Using Docker (Optional)
Create a Dockerfile for containerization

### Environment Variables
```bash
FLASK_ENV=production
FLASK_DEBUG=False
```

## 📝 License

This project is provided as-is for educational purposes.

## ⚠️ Disclaimer

**IMPORTANT**: This system is designed for educational purposes only. It is NOT a substitute for professional medical advice, diagnosis, or treatment. Always consult with a qualified healthcare professional for medical concerns.

The predictions made by this system are based on machine learning patterns and should not be relied upon as the sole basis for medical decisions.

## 👨‍💻 Development

### Tech Stack
- **Backend**: Flask, scikit-learn, pandas, numpy
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Database**: CSV files (no database required)
- **ML Framework**: scikit-learn

### Future Enhancements
- [ ] User authentication system
- [ ] History tracking
- [ ] Advanced visualization
- [ ] Mobile app
- [ ] Real-time model updates
- [ ] Integration with medical APIs
- [ ] Multi-language support
- [ ] Dark mode

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review the API documentation
3. Examine error logs in console

## 🎓 Learning Resources

- [scikit-learn Documentation](https://scikit-learn.org/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Machine Learning Basics](https://developers.google.com/machine-learning/crash-course)

---

