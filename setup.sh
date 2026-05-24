#!/bin/bash

echo "=========================================="
echo "Disease Prediction System - Setup Script"
echo "=========================================="
echo ""

# Check Python installation
echo "Checking Python installation..."
if ! command -v python3 &> /dev/null
then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"
echo ""

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✓ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi
echo ""

# Train the model
echo "Training ML Model..."
echo "This may take 2-5 minutes..."
cd backend
python3 train_model.py

if [ $? -eq 0 ]; then
    echo "✓ Model trained successfully"
    cd ..
else
    echo "❌ Model training failed"
    exit 1
fi
echo ""

echo "=========================================="
echo "✓ Setup Complete!"
echo "=========================================="
echo ""
echo "To start the application, run:"
echo "  cd backend"
echo "  python3 app.py"
echo ""
echo "Then open your browser and go to:"
echo "  http://localhost:5000"
echo ""
