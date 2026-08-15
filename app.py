from flask import Flask, render_template, jsonify, request
from pathlib import Path
import csv, re

app = Flask(__name__)
CSV = Path(__file__).with_name("stock.csv")

def load():
    with CSV.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))
STOCK = load()

def norm(s):
    return re.sub(r"[^a-zA-Z0-9\u0900-\u097F]+", " ", str(s or "").lower()).strip()

def search(q, limit=30):
    qn = norm(q)
    if not qn:
        return []
    words = [w for w in qn.split() if len(w) > 1]
    out = []
    for r in STOCK:
        hay = norm(" ".join([r.get("Product",""), r.get("Form",""), r.get("Company",""), r.get("Barcode","")]))
        score = sum(w in hay for w in words)
        if qn in hay:
            score += 5
        if score:
            out.append((score, r))
    out.sort(key=lambda x: x[0], reverse=True)
    return [r for _, r in out[:limit]]

@app.get("/")
def home():
    return render_template("index.html")

@app.get("/api/search")
def api_search():
    return jsonify(search(request.args.get("q", "")))

@app.get("/api/stats")
def stats():
    def n(c):
        return sum(float(str(r.get(c, "")).replace(",", "") or 0) for r in STOCK)
    products = len(set(r.get("Product","") for r in STOCK if r.get("Product")))
    return jsonify({"records": len(STOCK), "products": products,
                    "packs": n("No of Packs"), "value": n("Stock Value (Rs)")})

@app.post("/api/reload")
def reload_data():
    global STOCK
    STOCK = load()
    return jsonify({"ok": True, "records": len(STOCK)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
