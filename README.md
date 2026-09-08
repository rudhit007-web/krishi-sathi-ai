# KrishiSaathi AI v2 🌱

A farmer-first smart farming platform that combines:
1. Soil inputs (N, P, K, pH, moisture, organic matter)
2. Air/weather context (temperature, humidity, rainfall, wind)
3. Crop recommendation
4. A crop-to-harvest roadmap
5. Irrigation, fertilizer and pest/disease tips
6. Harvest and selling roadmap
7. Customer-reach options: APMC/mandi, FPO/FPC, local retailers, processors, direct consumers and e-NAM
8. English, Hindi and Marathi UI + AI output
9. Live weather through Open-Meteo
10. Optional Gemini AI for personalized plans

## Why Flask?
The previous prototype used FastAPI/Pydantic. This version uses Flask so it is much easier to run on Python 3.14 and avoids the pydantic-core/Rust installation issue.

## Local setup

```powershell
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Create `.env` from `.env.example` and add a Gemini API key if you want live generative AI.

Run:

```powershell
python app.py
```

Open:
http://127.0.0.1:8000

## AI
The backend sends the farm context to Gemini through the REST generateContent endpoint. Keep GEMINI_API_KEY on the server; never put it in frontend JavaScript.

If no Gemini key is present, the app uses a deterministic fallback planner so the prototype remains usable.

## Weather
Open-Meteo is used for current weather and a 5-day forecast. The browser location is converted into latitude/longitude and the backend requests the forecast.

## Deployment: Render

Create a Web Service from the GitHub repository.

Build Command:
```bash
pip install -r requirements.txt
```

Start Command:
```bash
gunicorn app:app
```

Add Environment Variables:
GEMINI_API_KEY = your key
GEMINI_MODEL = gemini-2.5-flash

## Deployment: Railway

Deploy the repository and set the start command:
```bash
gunicorn app:app
```

Add the same environment variables.

## Important
This is a decision-support prototype. Crop recommendations should be validated with local agronomy/soil-test guidance before real-world application. Do not use the AI output as a pesticide dosage prescription.

## External services used
- Google Gemini API: https://ai.google.dev/api
- Open-Meteo Forecast API: https://open-meteo.com/en/docs
- e-NAM: https://enam.gov.in/
