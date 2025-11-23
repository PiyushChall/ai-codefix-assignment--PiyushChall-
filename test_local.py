import time
import requests

BASE_URL = "http://localhost:8000"

test_cases = [
    {
        "language": "java",
        "cwe": "CWE-89",
        "code": """
String query = "SELECT * FROM users WHERE username = '" + userInput + "'";
Statement stmt = connection.createStatement();
ResultSet rs = stmt.executeQuery(query);
""".strip()
    },
    {
        "language": "python",
        "cwe": "CWE-79",
        "code": """
from flask import request
@app.route("/search")
def search():
    q = request.args.get("q", "")
    return f"<h1>Results for {q}</h1>"
""".strip()
    },
    {
        "language": "javascript",
        "cwe": "CWE-200",
        "code": """
app.get("/debug", (req, res) => {
  res.send("Stack trace: " + global.stackTrace);
});
""".strip()
    },
]


def run_tests():
    for i, payload in enumerate(test_cases, start=1):
        print(f"\n=== Test case {i} | language={payload['language']} | cwe={payload['cwe']} ===")
        start = time.perf_counter()
        resp = requests.post(f"{BASE_URL}/local_fix", json=payload, timeout=300)
        end = time.perf_counter()

        elapsed_ms = int((end - start) * 1000)
        print(f"HTTP latency: {elapsed_ms} ms")
        print(f"Status: {resp.status_code}")

        if resp.ok:
            data = resp.json()
            print("\n--- Fixed code ---")
            print(data["fixed_code"])
            print("\n--- Diff ---")
            print(data["diff"])
            print("\n--- Explanation ---")
            print(data["explanation"])
            print("\n--- Token usage ---")
            print(data["token_usage"])
            print(f"Reported latency_ms: {data['latency_ms']}")
        else:
            print("Error response:", resp.text)


if __name__ == "__main__":
    run_tests()
