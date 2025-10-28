from flask import Flask, request, render_template, jsonify
import requests
import os
import json

app = Flask(__name__)

ANALYZER_URL = os.getenv("ANALYZER_URL", "http://complexity-analyzer:5000/analyze")

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        code = request.form.get("code", "")
        if not code:
            return render_template("index.html", error="No code provided.")

        try:
            payload = {"code": code}
            response = requests.post(ANALYZER_URL, json=payload)

            if response.status_code == 200:
                result_data = response.json()
                return render_template("index.html",
                                       code=code,
                                       result=result_data,
                                       result_json=json.dumps(result_data, indent=2))
            else:
                error_msg = f"Analyzer service returned status {response.status_code}: {response.text}"
                return render_template("index.html", code=code, error=error_msg)

        except requests.exceptions.ConnectionError:
            error_msg = f"Could not connect to the analyzer service at {ANALYZER_URL}. Is it running?"
            return render_template("index.html", code=code, error=error_msg)
        except Exception as e:
            return render_template("index.html", code=code, error=str(e))

    return render_template("index.html", code="")

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

app.run(host="0.0.0.0", port=5002)