from flask import Flask, request, jsonify
import os
import requests
from analyzer import PythonComplexityAnalyzer

app = Flask(__name__)
analyzer = PythonComplexityAnalyzer()
RECURSIVE_ANALYZER_URL = os.getenv("RECURSIVE_ANALYZER_URL", "http://localhost:5001/analyze")

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json(force=True)
    code = data.get("code", "")
    if not code:
        return jsonify({"error": "Empty code"}), 400

    result = analyzer.analyze(code)

    # If recursion detected, forward to recursive-analyzer
    if result["recursive_functions"]:
        try:
            response = requests.post(RECURSIVE_ANALYZER_URL, json={"code": code})
            if response.status_code == 200:
                rec_result = response.json()
                result["recursive_analysis"] = rec_result
            else:
                result["recursive_analysis"] = f"Recursive analyzer returned status {response.status_code}"
        except Exception as e:
            result["recursive_analysis"] = str(e)

    return jsonify(result), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
