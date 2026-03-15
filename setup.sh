#!/bin/bash
# Streamlit App Setup Script with Conda

echo "🚀 Setting up Streamlit App for Paytm Logo Detector..."

# Create conda environment
echo "📦 Creating conda environment..."
conda create -n streamlit-paytm python=3.11 -y

# Activate conda environment
echo "🔧 Activating conda environment..."
conda activate streamlit-paytm

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

echo "✅ Setup complete!"
echo ""
echo "To run the app:"
echo "  1. Activate environment: conda activate streamlit-paytm"
echo "  2. Run app: streamlit run app.py"
echo "  3. Open browser: http://localhost:8501"
echo ""
echo "To deactivate: conda deactivate"