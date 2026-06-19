# 🧠 NeuroRAG - Advanced Clinical Assistant

<div align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/Flask-3.0.0-lightgrey.svg" alt="Flask">
  <img src="https://img.shields.io/badge/Gemini-API-orange.svg" alt="Gemini API">
  <img src="https://img.shields.io/badge/FAISS-Vector%20Search-green.svg" alt="FAISS">
  <img src="https://img.shields.io/badge/UI-Apple%20Design-black.svg" alt="UI Design">
</div>

<br/>

**NeuroRAG** is a powerful Retrieval-Augmented Generation (RAG) system built with Flask and the Google Gemini API. It acts as an intelligent clinical assistant for answering questions about neurological disorders, drawing heavily from a comprehensive 51-chapter medical handbook(by Alok Sharma).

## ✨ Key Features

- 🏥 **Advanced Clinical Dashboard**
  - **Red Flag Alert System:** Automatically detects and prominently flags critical medical emergencies, warnings, and severe symptoms (e.g., stroke, seizures) with high-contrast UI indicators.
  - **AI Reasoning Snapshot:** Provides a transparent view into the model's clinical logic, showing differential diagnoses, confidence levels, and treatment considerations.
  
- 🎯 **Dual-Mode Intelligence**
  - **Clinician Mode:** Uses precise medical terminology and advanced clinical reasoning suited for healthcare professionals.
  - **Patient Mode:** Uses simplified language, reassuring tones, and relatable analogies tailored for patients and families.

- 🔍 **Robust RAG Architecture**
  - Intelligent, chapter-based chunking matching (51 distinct FAISS indices).
  - High-precision semantic search using `text-embedding-004` and answer generation via `gemini-2.5-flash-lite`.
  - Real-time page citations and source referencing.

- 🔐 **User Management & Chat History**
  - Secure Login/Signup system with encrypted passwords.
  - Persistent, scrollable chat history tied to individual user profiles.

- 🎨 **Premium UI/UX Design**
  - Apple-grade "glassmorphism" aesthetic with a sophisticated dark mode.
  - Smooth micro-animations, seamless auto-scrolling, and responsive layouts.

## 🏗️ Architecture Pipeline

```text
User Query → Chapter Matching → FAISS Retrieval → Gemini Generation → Formatted Response
             (Keywords)         (Embeddings)      (RAG Context)
```

1. **Intelligent Chunking:** 51 chapters are processed and divided into 250-400 token chunks.
2. **Optimized Storage:** One FAISS index is maintained per chapter to ensure rapid, isolated retrieval.
3. **Generation:** Incorporates both top-k relevant chunks and system-level prompt guidelines tailored to the chosen interaction mode.

## 🚀 Setup & Installation

### 1. Prerequisites
- Python 3.8+
- Google Gemini API Key

### 2. Automated Setup (Recommended)
We provide a `setup.sh` script to automate the installation process for Mac/Linux environments:

```bash
# Make the script executable
chmod +x setup.sh

# Run the setup script
./setup.sh
```

### 3. Manual Installation
If you prefer setting up manually:

```bash
# 1. Clone the repository and navigate to the directory
cd neurorag

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

# 3. Install required dependencies
pip install -r requirements.txt

# 4. Create your .env file
echo "GEMINI_API_KEY=your_api_key_here" > .env
```

### 4. Provide the Data Source
Place your source PDF in the following directory:
```bash
data/raw/neurology_handbook.pdf
```
*(Note: Ensure the PDF corresponds to the 51-chapter index structure used in the preprocessing logic).*

### 5. Run the Preprocessing Pipeline
Extract text, build chunks, generate embeddings, and construct FAISS indices. This step will take some time depending on your API rate limits:
```bash
python preprocess.py
```

### 6. Launch the Application
```bash
python app.py
```
Access the application locally at: **http://localhost:5000**

## 🔧 Technical Details

Configuration can be modified inside `src/utils/config.py`:
- **Chunk Size:** `300` (target), `250` (min), `400` (max)
- **Top K Retrieval:** `5`
- **Embedding Model:** `text-embedding-004`
- **Generative Model:** `gemini-2.5-flash-lite`

## ⚠️ Disclaimer
**Educational Purpose Only:** This tool is designed as a supplementary clinical assistant and educational resource. It is **not** a substitute for professional medical advice, diagnosis, or treatment.

---
*Ready for deployment and built with a focus on premium clinical utility.*
