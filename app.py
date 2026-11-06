from flask import Flask, request, render_template_string
from datetime import datetime
import re

app = Flask(__name__)
LOGS = []

RULES = {
    "SQL Injection": [r"' OR", r"--", r"union select", r"'='", r"or 1=1"],
    "XSS": [r"<script", r"javascript:", r"onerror=", r"alert\("],
    "Path Traversal": [r"\.\./", r"/etc/passwd"],
}

INDEX_HTML = """
<!DOCTYPE html><html><head><title>Lasya | Cyber Security</title>
<style>body{font-family:Arial;background:#0f172a;color:white;text-align:center;padding:40px}
.card{background:#1e293b;padding:30px;border-radius:15px;max-width:600px;margin:auto}
input,textarea{width:90%;padding:12px;margin:10px;border-radius:8px;border:none}
button{padding:12px 25px;background:#22c55e;font-weight:bold;border:none;border-radius:8px}
.counter{color:#22c55e;font-size:20px;margin:15px}</style></head>
<body><div class="card">
<h1>Hi, I'm Lasya Thota</h1>
<p>Cyber Security Engineer | HoneyPortfolio traps hackers</p>
<div class="counter">Live hackers trapped: {{count}}</div>
<form method="POST" action="/"><input name="name" placeholder="Name" required>
<textarea name="msg" placeholder="Try: <script>alert(1)</script>" required></textarea>
<button type="submit">Send (Trap Test)</button></form>
{% if trapped %}<h2 style="color:red;">⚠️ ATTACK TRAPPED! Logged in SOC ⚠️</h2>{% endif %}
</div></body></html>
"""

SOC_HTML = """
<html><head><style>body{background:black;color:#00ff00;font-family:monospace;padding:20px}
table{width:100%;border-collapse:collapse} th,td{border:1px solid #00ff00;padding:8px}</style></head>
<body><h2>LIVE SOC - Hackers Trapped: {{logs|length}}</h2>
<table><tr><th>Time</th><th>IP</th><th>Type</th><th>Payload</th></tr>
{% for l in logs|reverse %}<tr><td>{{l.time}}</td><td>{{l.ip}}</td><td style="color:red">{{l.type}}</td><td>{{l.payload[:200]}}</td></tr>{% endfor %}
</table></body></html>
"""

def detect_attack(d):
    d=d.lower()
    for t, pats in RULES.items():
        for p in pats:
            if re.search(p,d,re.I): return t
    return None

@app.before_request
def check_all():
    data = request.full_path + str(request.args) + str(request.form)
    atk = detect_attack(data)
    if atk:
        LOGS.append({"time":datetime.now().strftime("%H:%M:%S"),"ip":request.headers.get('X-Forwarded-For',request.remote_addr),"type":atk,"payload":data[:500],"url":request.url})

@app.route("/", methods=["GET","POST"])
def home():
    trapped=False
    if request.method=="POST":
        if detect_attack(str(request.form)): trapped=True
    if detect_attack(str(request.args)): trapped=True
    return render_template_string(INDEX_HTML, count=len(LOGS), trapped=trapped)

@app.route("/soc")
def soc():
    if request.args.get("key")!="cyber20LPA": return "Unauthorized",403
    return render_template_string(SOC_HTML, logs=LOGS)

if __name__=="__main__":
    app.run(host="0.0.0.0",port=10000)
