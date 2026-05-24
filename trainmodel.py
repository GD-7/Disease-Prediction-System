import pandas as pd
import numpy as np
import os
import pickle
import random
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from config import Config

class DiseaseModel:
    def __init__(self):
        self.data_path = Config.DATA_DIR
        self.df = None
        self.symptom_severity = {}
        self.all_symptoms = []
        self.encoder = LabelEncoder()
        self.model = None

    def load_data(self):
        self.df = pd.read_csv(os.path.join(self.data_path, 'dataset.csv'))
        severity_df = pd.read_csv(os.path.join(self.data_path, 'symptom_severity.csv'))
        
        self.symptom_severity = dict(zip(severity_df['Symptom'].str.strip(), severity_df['weight']))
        self.df = self.df.drop_duplicates()
        print(f"Original Data Loaded: {len(self.df)} unique records")

    # INCREASED TO 15 TO FEED THE MODEL MORE DATA
    def augment_data(self, df, multiplier=15):
        augmented_rows = []
        cols = [c for c in df.columns if c.startswith('Symptom_')]
        
        for _ in range(multiplier):
            df_copy = df.copy()
            for i in df_copy.index:
                valid_syms = [col for col in cols if pd.notna(df_copy.at[i, col])]
                if len(valid_syms) > 3:
                    keep_n = random.randint(3, min(6, len(valid_syms)))
                    to_drop = random.sample(valid_syms, len(valid_syms) - keep_n)
                    for col in to_drop:
                        df_copy.at[i, col] = np.nan
            augmented_rows.append(df_copy)
            
        return pd.concat(augmented_rows, ignore_index=True)

    def build_symptoms(self, df):
        s = set()
        for col in df.columns:
            if col.startswith('Symptom_'):
                s.update(df[col].dropna().str.strip())
        self.all_symptoms = sorted(list(s))

    def create_matrix(self, df):
        X = np.zeros((len(df), len(self.all_symptoms) + 3))
        cols = [c for c in df.columns if c.startswith('Symptom_')]

        for i, row in enumerate(df.itertuples()):
            weights = []
            for col in cols:
                val = getattr(row, col)
                if pd.notna(val):
                    sym = val.strip()
                    if sym in self.all_symptoms:
                        idx = self.all_symptoms.index(sym)
                        w = self.symptom_severity.get(sym, 1)
                        X[i, idx] = w / 10.0
                        weights.append(w)

            if weights:
                X[i, -3:] = [len(weights), sum(weights), np.mean(weights)]
        return X

    def train(self):
        # 1. LOCK THE RANDOMNESS FIRST
        random.seed(42)
        np.random.seed(42)

        # 2. AUGMENT DATA (Multiplier matches the function above)
        augmented_df = self.augment_data(self.df, multiplier=15)
        print(f"Augmented Dataset Size: {len(augmented_df)} records")

        # 3. STRATIFIED SPLIT (80% Train, 20% Test)
        train_df, test_df = train_test_split(
            augmented_df, test_size=0.2,
            stratify=augmented_df['Disease'], 
            random_state=42
        )

        self.build_symptoms(train_df)

        X_train = self.create_matrix(train_df)
        X_test = self.create_matrix(test_df)

        y_train = self.encoder.fit_transform(train_df['Disease'])
        y_test = self.encoder.transform(test_df['Disease'])

        # 4. TUNED HYPERPARAMETERS (More Brain Power)
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=20,               
            min_samples_split=6,       
            min_samples_leaf=2,
            max_features='sqrt',
            class_weight='balanced',
            random_state=42,
            n_jobs=-1
        )

        print("Training perfectly balanced model...")
        self.model.fit(X_train, y_train)

        train_acc = accuracy_score(y_train, self.model.predict(X_train))
        test_acc = accuracy_score(y_test, self.model.predict(X_test))

        print("\n==============================")
        print(f"Training Accuracy: {train_acc*100:.2f}%")
        print(f"Testing Accuracy:  {test_acc*100:.2f}%")
        print(f"Gap (Overfit margin): {abs(train_acc-test_acc)*100:.2f}%")
        print("==============================\n")

    def save(self):
        os.makedirs(Config.MODEL_DIR, exist_ok=True)
        with open(Config.MODEL_FILE, "wb") as f:
            pickle.dump(self.model, f)
        with open(Config.META_FILE, "wb") as f:
            pickle.dump({
                "encoder": self.encoder,
                "symptoms": self.all_symptoms,
                "symptom_severity": self.symptom_severity
            }, f)
        print("✅ Balanced Model Saved Successfully!")

if __name__ == "__main__":
    m = DiseaseModel()
    m.load_data()
    m.train()
    m.save()