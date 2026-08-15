from flask import Flask, render_template, request, jsonify
import csv, os

app = Flask(__name__)

CSV_FILE = "stock.csv"

def load_stock():
    if not os.path.exists(CSV_FILE):
        return []
    with open(CSV_FILE, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/search")
def search():
    q = request.args.get("q", "").strip().lower()
    rows = load_stock()
    if not q:
        return jsonify(rows[:100])
    out = []
    for r in rows:
        text = " ".join(str(v or "") for v in r.values()).lower()
        if q in text:
            out.append(r)
    return jsonify(out[:100])

@app.route("/api/stats")
def stats():
    rows = load_stock()
    packs = 0
    value = 0
    for r in rows:
        try: packs += float(r.get("No of Packs", 0) or 0)
        except: pass
        try:
            value += float(r.get("MRP (Rs)", 0) or 0) * float(r.get("No of Packs", 0) or 0)
        except: pass
    return jsonify({
        "records": len(rows),
        "products": len(set((r.get("Product") or "").strip().lower() for r in rows if r.get("Product"))),
        "packs": int(packs),
        "value": value
    })

@app.route("/api/order", methods=["POST"])
def order():
    data = request.get_json(silent=True) or {}
    if not data.get("items"):
        return jsonify({"ok": False, "message": "Order is empty"}), 400
    # Order is intentionally not written to stock.csv.
    # WhatsApp remains the customer-facing order channel.
    return jsonify({"ok": True, "message": "Order received", "order": data})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
