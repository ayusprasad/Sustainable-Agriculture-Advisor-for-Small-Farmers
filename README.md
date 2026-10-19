# 🌾 Sustainable Agriculture Advisor for Small Farmers

An AI-driven agricultural decision-support application built with **Streamlit**, **LangChain**, and **Groq** to empower smallholder farmers with crop planning, organic pest control strategies, weather outlooks, and sustainable soil conservation guidance.

---

## 🌟 Key Features
- **Dynamic Agronomic Consultation:** Generates custom action plans for any crop and region using high-speed Groq LPU inference (LLaMA 3.3).
- **Farming Calendar Generation:** Automatically maps critical agricultural milestones (planting, weeding, irrigation, harvesting).
- **Yield Projection Index:** Estimates output quintals based on local soil conditions and simulated meteorological patterns.
- **Organic & Integrated Pest Management:** Focuses on affordable, biological, and sustainable pest remedies to reduce chemical reliance.
- **Production Containerization:** Standardized `app.py` entrypoint, pruned lightweight dependencies, and ready-to-run Docker image.

---

## 🚀 Quickstart

### 1. Local Run
```bash
# Clone repository
git clone https://github.com/ayusprasad/Sustainable-Agriculture-Advisor-for-Small-Farmers.git
cd Sustainable-Agriculture-Advisor-for-Small-Farmers

# Install requirements
pip install -r requirements.txt

# (Optional) Export Groq API key
export GROQ_API_KEY="your-groq-key"

# Launch Streamlit web app
streamlit run app.py
```
Open [http://localhost:8501](http://localhost:8501) in your browser.

---

### 2. Run with Docker
```bash
# Build container
docker build -t agriculture-advisor .

# Run container
docker run -p 8501:8501 -e GROQ_API_KEY="your-key" agriculture-advisor
```

---

## 📁 Repository Structure
```text
Sustainable-Agriculture-Advisor-for-Small-Farmers/
├── app.py                     # Standard Streamlit application entrypoint
├── app2.py                    # Backward compatibility launcher
├── requirements.txt           # Production Python dependencies
├── Dockerfile                 # Production container definition
├── .gitignore                 # Environment and temporary file ignores
└── README.md                  # Project documentation
```
