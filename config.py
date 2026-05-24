import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class Config:
    SECRET_KEY = 'disease-prediction-system-secret-key'
    
    # Paths
    DATA_DIR = os.path.join(BASE_DIR, 'data')
    MODEL_DIR = os.path.join(BASE_DIR, 'models')
    
    # Files
    MODEL_FILE = os.path.join(MODEL_DIR, 'model.pkl')
    META_FILE = os.path.join(MODEL_DIR, 'meta.pkl')
    DB_PATH = os.path.join(BASE_DIR, 'predictions.db')
    
    # Set to False for production/deployment
    DEBUG = False