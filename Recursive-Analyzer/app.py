from flask import Flask, request, jsonify

app = Flask(__name__)

def analyze_recursion(code: str):
    ...

    return {
        "status": "analysis_pending",
        "message": "Recursion analysis not yet implemented.",
        "received_code_snippet": code[:50]
    }

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json(force=True)
    code = data.get("code", "")
    if not code:
        return jsonify({"error": "Empty code"}), 400

    result = analyze_recursion(code)

    return jsonify(result), 200

app.run(host="0.0.0.0", port=5001)
