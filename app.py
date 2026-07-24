import os
from flask import Flask, render_template, jsonify
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

def get_notion_data():
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    response = requests.post(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Error communicating with Notion: {response.text}")
    
    data = response.json().get("results", [])
    if not data:
        return {"score": 0.0, "bias": "Neutral CHF"}
    
    properties = data[0].get("properties", {})
    
    # Extract Score (handles number, formula, or rollup)
    score_val = 0.0
    score_field = properties.get("Score", {})
    s_type = score_field.get("type")
    if s_type == "number":
        score_val = score_field.get("number", 0.0) or 0.0
    elif s_type == "formula":
        f_type = score_field.get("formula", {}).get("type")
        score_val = score_field.get("formula", {}).get(f_type, 0.0) or 0.0
    elif s_type == "rollup":
        r_type = score_field.get("rollup", {}).get("type")
        if r_type == "number":
            score_val = score_field.get("rollup", {}).get("number", 0.0) or 0.0

    # Extract Bias (handles select, formula, or status)
    bias_val = "Neutral CHF"
    bias_field = properties.get("Bias", {})
    b_type = bias_field.get("type")
    if b_type == "select" and bias_field.get("select"):
        bias_val = bias_field.get("select").get("name")
    elif b_type == "status" and bias_field.get("status"):
        bias_val = bias_field.get("status").get("name")
    elif b_type == "formula":
        f_type = bias_field.get("formula", {}).get("type")
        bias_val = bias_field.get("formula", {}).get(f_type)

    return {"score": float(score_val), "bias": bias_val}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/data")
def api_data():
    try:
        data = get_notion_data()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)