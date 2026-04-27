#!/bin/bash

echo "=========================================="
echo "🧠 NeuroRAG Setup Script"
echo "=========================================="

# 1. Create Virtual Environment
echo ""
echo "[1/4] Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Virtual environment 'venv' created."
else
    echo "✓ Virtual environment already exists."
fi

# Activate virtual environment
source venv/bin/activate

# 2. Install Dependencies
echo ""
echo "[2/4] Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# 3. Setting up Environment Variables
echo ""
echo "[3/4] Setting up environment variables..."
if [ ! -f .env ]; then
    echo "GEMINI_API_KEY=your_api_key_here" > .env
    echo "FLASK_HOST=0.0.0.0" >> .env
    echo "FLASK_PORT=5000" >> .env
    echo "FLASK_DEBUG=True" >> .env
    echo "✓ Created .env file. PLEASE UPDATE IT WITH YOUR GEMINI API KEY!"
else
    echo "✓ .env file already exists. Skipping..."
fi

# 4. Preparing Data Directories
echo ""
echo "[4/4] Preparing data directories..."
mkdir -p data/raw data/extracted data/chunks data/index vector_store
echo "✓ Directories created."

echo ""
echo "=========================================="
echo "Setup Complete! 🎉"
echo "=========================================="
echo "Next Steps:"
echo "1. Add your Gemini API key to the .env file"
echo "2. Place your medical PDF in 'data/raw/'"
echo "3. Run 'python preprocess.py' to process the PDF and build FAISS indices"
echo "4. Run 'python app.py' to start the application!"
echo "=========================================="
