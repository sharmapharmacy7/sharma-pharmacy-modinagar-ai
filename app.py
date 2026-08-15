from flask import Flask, render_template, request, jsonify
import csv, os
app=Flask(__name__)
CSV_FILE="stock.csv"
def stock():
    if not os.path.exists(CSV_FILE): return []
    with open(CSV_FILE,newline="",encoding="utf-8-sig") as f:return list(csv.DictReader(f))
@app.route("/")
def home(): return render_template("index.html")
@app.route("/api/search")
def search():
    q=request.args.get("q","").strip().lower(); rows=stock()
    if not q:return jsonify(rows[:100])
    return jsonify([r for r in rows if q in " ".join(str(v or "") for v in r.values()).lower()][:100])
@app.route("/api/stats")
def stats():
    rows=stock(); packs=0; value=0
    for r in rows:
        try:packs+=float(r.get("No of Packs",0) or 0)
        except:pass
        try:value+=float(r.get("MRP (Rs)",0) or 0)*float(r.get("No of Packs",0) or 0)
        except:pass
    return jsonify(records=len(rows),products=len(set((r.get("Product")or"").lower() for r in rows if r.get("Product"))),packs=int(packs),value=value)
@app.route("/api/order",methods=["POST"])
def order():
    d=request.get_json(silent=True) or {}
    return jsonify(ok=bool(d.get("items")),message="Order received")
if __name__=="__main__":
    app.run(host="0.0.0.0",port=int(os.environ.get("PORT",10000)))
