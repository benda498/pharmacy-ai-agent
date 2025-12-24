# Pharmacy Assistant - AI Agent

AI-powered pharmacy assistant that helps users check medication availability, prices, and information while maintaining strict safety policies.

---

## Features

- Medication search and availability check
- Price information
- Dosage and usage information
- Prescription validation
- Bilingual support (Hebrew + English)
- No medical advice policy

---

## Architecture
```
User -> Streamlit UI -> Agent (OpenAI GPT) -> Database (SQLite)
                          
3 Tools:
- medication_exists
- get_medication_availability
- get_medication_profile
```

**Components:**
- `app.py` - Streamlit UI
- `agent.py` - OpenAI agent with function calling
- `tools.py` - Tool definitions
- `database.py` - SQLite operations
- `init_db.py` - Database initialization

---

## Running with Docker

### Prerequisites
- Docker Desktop installed and running
- OpenAI API key

### Setup

1. Download all files from this GitHub repository
2. Open CMD/Terminal and navigate to the project folder:
```bash
   cd path\to\pharmacy-ai-agent
```
3. Make sure Docker Desktop is running

### Build
```bash
docker build -t pharmacy-agent .
```

### Run
```bash
docker run -p 8501:8501 -e OPENAI_API_KEY=your-key-here pharmacy-agent
```

### Access
Open browser: http://localhost:8501

---

## Test Users

Login with these IDs:
- `123456789` (David Cohen) - Has prescription
- `234567890` (Sarah Levi) - No prescription
- `567890123` (Yossi Avraham) - Has prescription

---

## Safety Policies

- No medical advice or recommendations
- Prescription validation for controlled medications
- Medical disclaimers on dosage information
- Redirect to healthcare professionals when appropriate



