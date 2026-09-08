import os, json, math
from flask import Flask, render_template, request, jsonify
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

CROPS = {
    "Wheat": {"season":"Rabi", "ph":[6.0,7.5], "water":"Moderate", "temp":[10,25], "n":"Medium-High", "roadmap":["Seed selection & land preparation","Sowing + first irrigation","Tillering & nutrient management","Disease/pest scouting","Grain filling + final irrigation","Harvest, grading & market preparation"]},
    "Rice": {"season":"Kharif / Rabi", "ph":[5.5,7.0], "water":"High", "temp":[20,35], "n":"High", "roadmap":["Nursery/seed preparation","Transplanting or direct sowing","Water + weed management","Tillering & nutrient management","Panicle/flowering care","Harvest, drying & market preparation"]},
    "Maize": {"season":"Kharif / Rabi", "ph":[5.8,7.0], "water":"Moderate", "temp":[18,30], "n":"Medium-High", "roadmap":["Land preparation & seed treatment","Sowing + emergence","Early weed and nutrient management","Tasseling/flowering protection","Grain filling + irrigation","Harvest, drying & storage"]},
    "Soybean": {"season":"Kharif", "ph":[6.0,7.5], "water":"Moderate", "temp":[20,30], "n":"Low-Medium", "roadmap":["Seed selection + inoculation","Sowing after suitable moisture","Weed management","Flowering/pod protection","Disease/pest scouting","Harvest + moisture-safe storage"]},
    "Cotton": {"season":"Kharif", "ph":[5.5,8.0], "water":"Moderate", "temp":[21,35], "n":"Medium-High", "roadmap":["Seed + land preparation","Sowing & plant establishment","Vegetative nutrition","Flowering/boll development","Pest scouting & irrigation","Boll opening, picking & grading"]},
    "Tomato": {"season":"Multiple", "ph":[6.0,7.0], "water":"Moderate", "temp":[18,30], "n":"Medium", "roadmap":["Nursery + healthy seedlings","Transplanting & staking","Vegetative growth + nutrition","Flowering & fruit set","Pest/disease monitoring","Harvest, sorting & quick sale"]},
    "Onion": {"season":"Rabi / Kharif", "ph":[6.0,7.5], "water":"Moderate", "temp":[13,25], "n":"Medium", "roadmap":["Nursery/seed preparation","Transplanting","Bulb development + irrigation","Thrips/disease scouting","Stop irrigation near maturity","Curing, grading & storage/sale"]},
    "Potato": {"season":"Rabi", "ph":[5.0,6.5], "water":"Moderate", "temp":[15,25], "n":"Medium", "roadmap":["Seed tuber selection","Planting + earthing up","Irrigation & nutrition","Late blight/pest scouting","Maturity & irrigation stop","Harvest, grading & cold/storage planning"]},
    "Chickpea": {"season":"Rabi", "ph":[6.0,8.0], "water":"Low-Moderate", "temp":[15,25], "n":"Low", "roadmap":["Seed selection & treatment","Sowing with residual moisture","Weed control","Flowering/pod care","Pod borer scouting","Harvest, drying & grading"]}
}

def clamp(v,a,b): return max(a,min(b,v))

def recommend_crops(soil, weather):
    ph = float(soil.get("ph") or 6.5)
    moisture = float(soil.get("moisture") or 45)
    temp = float(weather.get("temperature") or 25)
    rain = float(weather.get("rain") or 0)
    results=[]
    for name,c in CROPS.items():
        score=55
        if c["ph"][0] <= ph <= c["ph"][1]: score += 25
        else:
            dist=min(abs(ph-c["ph"][0]),abs(ph-c["ph"][1])); score += max(-20,15-dist*15)
        if c["temp"][0] <= temp <= c["temp"][1]: score += 12
        if c["water"]=="High" and moisture>65: score += 6
        if c["water"]=="Low-Moderate" and moisture<40: score += 6
        if rain>25 and c["water"]=="High": score += 3
        results.append((name,int(clamp(score,20,97))))
    results.sort(key=lambda x:x[1], reverse=True)
    return results[:3]

def fallback_plan(data):
    lang=data.get("language","English")
    soil=data.get("soil",{}); weather=data.get("weather",{}); crop=data.get("crop") or ""
    location=data.get("location") or "your area"
    qty=data.get("quantity") or "your expected quantity"
    c=CROPS.get(crop, {})
    ph=float(soil.get("ph") or 6.5)
    score=70
    if c and c["ph"][0] <= ph <= c["ph"][1]: score+=18
    if weather.get("rain") is not None and float(weather.get("rain") or 0)<5: score+=5
    score=int(clamp(score,35,96))
    market=[
        "Compare the nearby APMC/mandi price and buyer demand before harvest.",
        "Contact a local FPO/FPC to aggregate produce and improve buyer reach.",
        "For vegetables/fruits, approach retailers, hotels, processors and direct consumers early.",
        "Create a simple lot: crop + grade + quantity + harvest date + location + photos.",
        "Use e-NAM where your commodity and nearby mandi are supported; verify current registration/market requirements."
    ]
    return {
      "language":lang,"score":score,
      "summary": f"{crop or 'Your selected crop'} can be planned using your soil and weather context. Focus first on soil suitability, water management and a buyer plan before harvest.",
      "crop":crop,
      "soil_note": f"Soil pH entered: {ph}. Recommended pH for {crop or 'this crop'} is {c.get('ph',['check local guidance'])[0]}–{c.get('ph',['',''])[1] if c else 'check local guidance'}.",
      "weather_note": f"Current/entered air temperature: {weather.get('temperature','--')}°C, humidity: {weather.get('humidity','--')}%, rainfall signal: {weather.get('rain','--')} mm.",
      "roadmap": c.get("roadmap",["Prepare soil","Sow at suitable time","Manage water and nutrients","Scout pests/diseases","Prepare harvest","Grade, store and sell"]),
      "tips":[
        "Use a soil test and avoid applying fertilizer only by guesswork.",
        "Scout several plants across the field every few days and record changes.",
        "Adjust irrigation after rainfall and according to crop stage.",
        "Keep harvest quality, grading and storage in mind from the start."
      ],
      "market":market,
      "buyer_plan":[
        {"title":"APMC / Mandi","text":"Good for bulk sale and local price discovery. Check the nearest market and current commodity requirements."},
        {"title":"FPO / FPC","text":"Aggregate with other farmers to reach larger buyers and coordinate transport."},
        {"title":"Retailers / Processors","text":"Useful for vegetables, fruits and processing crops; contact buyers before harvest."},
        {"title":"Direct consumers","text":"For smaller quantities, use local shops, WhatsApp groups, weekly markets or farm-gate sales."},
        {"title":"e-NAM","text":"Explore online trading and price discovery where your commodity and mandi are supported."}
      ],
      "disclaimer":"Prototype decision support only. Confirm crop, fertilizer and plant-protection decisions with local agricultural experts and product labels."
    }

@app.route("/")
def home(): return render_template("index.html")

@app.route("/api/crops")
def crops(): return jsonify(CROPS)

@app.route("/api/weather")
def weather():
    lat=request.args.get("lat"); lon=request.args.get("lon")
    if not lat or not lon: return jsonify({"error":"latitude and longitude are required"}),400
    url=("https://api.open-meteo.com/v1/forecast"
         f"?latitude={lat}&longitude={lon}"
         "&current=temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m"
         "&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,weather_code"
         "&forecast_days=5&timezone=auto")
    r=requests.get(url,timeout=15); r.raise_for_status()
    return jsonify(r.json())

@app.post("/api/plan")
def plan():
    data=request.get_json(force=True)
    # Always produce a usable local plan first.
    base=fallback_plan(data)
    if not GEMINI_API_KEY:
        base["mode"]="local-planner"
        return jsonify(base)
    lang={"English":"English","Hindi":"Hindi","Marathi":"Marathi"}.get(data.get("language"),"English")
    system=f"""You are KrishiSaathi AI, a farmer-friendly agricultural decision-support assistant for India.
Reply in {lang}. Use simple words and short sections. Analyze the supplied soil, air/weather and farm details.
Return JSON with these keys exactly: summary, soil_note, weather_note, roadmap (array of 6 strings), tips (array of 5 strings),
market (array of 5 strings), buyer_plan (array of objects with title and text), disclaimer.
Recommend crops only when asked or when crop is blank. Never invent pesticide dosage. If chemical treatment is mentioned,
tell the farmer to follow the product label and local agriculture authority. For marketing, explain practical routes:
APMC/mandi, FPO/FPC, retailers/processors, direct consumers and e-NAM where applicable. Mention that actual prices and
buyer availability must be checked locally. This is decision support, not a substitute for an agricultural expert."""
    prompt=system+"\n\nFARM DATA:\n"+json.dumps(data,ensure_ascii=False)
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"

        headers = {
            "x-goog-api-key": GEMINI_API_KEY,
            "Content-Type": "application/json"
        }

        payload = {
            "systemInstruction": {
                "parts": [
                    {
                        "text": system
                    }
                ]
            },
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.25,
                "maxOutputTokens": 1600,
                "responseMimeType": "application/json"
            }
        }

        r = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=35
        )

        r.raise_for_status()

        txt = r.json()["candidates"][0]["content"]["parts"][0]["text"]

        ai = json.loads(txt)

        ai["mode"] = "gemini"
        ai["score"] = base["score"]
        ai["crop"] = data.get("crop")

        return jsonify(ai)

    except Exception as e:
        print("Gemini plan error:", repr(e))
        base["mode"] = "local-fallback"
        return jsonify(base)

@app.post("/api/chat")
def chat():
    data = request.get_json(force=True)

    if not GEMINI_API_KEY:
        return jsonify({
            "answer": "I am in demo mode. Add a Gemini API key to enable live AI answers. For now, use Farm Plan to generate your soil, crop, roadmap and selling plan.",
            "mode": "local"
        })

    lang = data.get("language", "English")

    system = f"""You are KrishiSaathi AI.
Answer in {lang}, using simple farmer-friendly language.

Use the supplied crop, soil, weather and market context.
Be practical and easy to understand.

Do not invent pesticide doses.
For disease or chemical treatment, encourage verification
with a local agricultural expert.

If asked how to sell, give actionable options such as:
APMC/mandi, FPO/FPC, retailers, processors,
direct consumers and e-NAM where applicable.
"""

    prompt = system + "\n\nFarmer Context:\n" + json.dumps(
        data,
        ensure_ascii=False
    )

    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"

        headers = {
            "x-goog-api-key": GEMINI_API_KEY,
            "Content-Type": "application/json"
        }

        payload = {
            "systemInstruction": {
                "parts": [
                    {
                        "text": system
                    }
                ]
            },
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.3,
                "maxOutputTokens": 700
            }
        }

        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=30
        )

        print("Gemini status:", response.status_code)

        if response.status_code != 200:
            print("Gemini error:", response.text)

            return jsonify({
                "answer": "Gemini API returned an error. Please check the Render logs.",
                "mode": "api-error"
            }), 500

        result = response.json()

        candidates = result.get("candidates", [])

        if not candidates:
            print("Gemini returned no candidates:", result)

            return jsonify({
                "answer": "Gemini returned no answer. Please try again.",
                "mode": "api-error"
            }), 500

        parts = candidates[0].get("content", {}).get("parts", [])

        if not parts:
            print("Gemini returned no text:", result)

            return jsonify({
                "answer": "Gemini returned an empty response.",
                "mode": "api-error"
            }), 500

        answer = parts[0].get("text", "")

        return jsonify({
            "answer": answer,
            "mode": "gemini"
        })

    except requests.exceptions.Timeout:
        print("Gemini request timed out")

        return jsonify({
            "answer": "Gemini request timed out. Please try again.",
            "mode": "timeout"
        }), 500

    except requests.exceptions.RequestException as e:
        print("Gemini connection error:", repr(e))

        return jsonify({
            "answer": "Could not connect to Gemini API.",
            "mode": "connection-error"
        }), 500

    except Exception as e:
        print("Gemini unexpected error:", repr(e))

        return jsonify({
            "answer": "An unexpected Gemini error occurred. Check Render logs.",
            "mode": "error"
        }), 500
        
@app.get("/health")
def health(): return jsonify({"status":"ok"})

if __name__=="__main__":
    app.run(host="0.0.0.0",port=int(os.getenv("PORT",8000)),debug=True)
