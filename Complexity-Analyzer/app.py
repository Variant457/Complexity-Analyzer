from flask import Flask, request, jsonify
import os
import requests
from analyzer import PythonComplexityAnalyzer

app = Flask(__name__)
analyzer = PythonComplexityAnalyzer()
RECURSIVE_ANALYZER_URL = os.getenv("RECURSIVE_ANALYZER_URL", "http://localhost:5001/analyze")

def get_worst_recursive_complexity(rec_results):
    worst_rank = -1
    worst_complexity = "O(1)"

    analysis_results = rec_results.get("recursive_functions_analyzed", {})
    if not analysis_results:
        return worst_complexity, worst_rank

    for details in analysis_results.values():
        big_o = details.get("estimated_big_o", "O(1)")
        rank = PythonComplexityAnalyzer.get_complexity_rank(big_o)
        if rank > worst_rank:
            worst_rank = rank
            worst_complexity = big_o

    return worst_complexity, worst_rank

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

    iterative_big_o = result.get("big_o", "O(1)")
    iterative_rank = PythonComplexityAnalyzer.get_complexity_rank(iterative_big_o)

    overall_big_o = iterative_big_o
    overall_rank = iterative_rank
    explaination_prefix = f"Overall Complexity Determined by interative loops: {iterative_big_o}. "

    # If recursion detected, forward to recursive-analyzer
    if result["recursive_functions"]:
        try:
            response = requests.post(RECURSIVE_ANALYZER_URL, json={"code": code})
            if response.status_code == 200:
                rec_result = response.json()
                result["recursive_analysis"] = rec_result

                rec_big_o, rec_rank = get_worst_recursive_complexity(rec_result)

                if rec_rank > overall_rank:
                    overall_big_o = rec_big_o
                    overall_rank = rec_rank
                    explaination_prefix = f"Overall Complexity Determined by recursion: {rec_big_o}. "
            else:
                result["recursive_analysis"] = f"Recursive analyzer returned status {response.status_code}"
        except Exception as e:
            result["recursive_analysis"] = str(e)

    result["big_o"] = overall_big_o
    result["explanation"] = explaination_prefix + result["explanation"]

    return jsonify(result), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
