from flask import Flask, request, render_template_string, session, redirect, url_for
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = "lasya_pro_20LPA_2026"
attack_logs = []
SOC_SECRET = os.environ.get("SOC_KEY", "cyber20LPA")

def detect_attack(text):
    if not text: return None
    t = text.lower()
    if any(p in t for p in ["<script","alert(","onerror","<img","javascript:","<svg"]): return "XSS"
    if any(p in t for p in ["' or","union select","--","or 1=1","' or '",'";']): return "SQLi"
    return None

PORTFOLIO_HTML = '''
<!DOCTYPE html><html><head><title>Lasya | Cyber Security</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body{background:#0a0f1c;color:#e2e8f0;font-family:Segoe UI;margin:0}
header{background:#0f172a;padding:30px;text-align:center;border-bottom:2px solid #00ff9d}
header h1{color:#00ff9d;margin:0} .container{max-width:900px;margin:auto;padding:20px}
.card{background:#111a2e;border:1px solid #1e293b;border-radius:12px;padding:20px;margin:20px 0}
.skills span{display:inline-block;background:#1e293b;border:1px solid #00ff9d;color:#00ff9d;padding:6px 12px;border-radius:20px;margin:5px;font-size:13px}
input,textarea{width:100%;padding:12px;margin:8px 0;background:#0f172a;border:1px solid #334155;color:white;border-radius:8px;box-sizing:border-box}
button{background:#00ff9d;color:#000;padding:12px 25px;border:none;border-radius:8px;font-weight:bold;cursor:pointer;width:100%}
.live{color:#00ff9d;font-weight:bold;text-align:center;padding:10px;background:#0f172a;border-radius:8px;border:1px dashed #00ff9d}
a{color:#00ff9d;text-decoration:none} .trapped{background:#ff0055;color:white;padding:15px;text-align:center;border-radius:8px;margin:15px 0}
</style></head><body>
<header><h1>Lasya Thota | Cyber Security Analyst</h1><p>SOC Analyst | SIEM | Python | Honeypot Developer</p><p><a href="#">LinkedIn</a> | Vijayawada, AP</p></header>
<div class="container">
<div class="card"><h2 style="color:#00ff9d">About Me</h2><p>This portfolio is a <b>LIVE Honeypot</b> - every attack is trapped in my private SOC.</p></div>
<div class="card"><div class="live">🔴 LIVE Hackers Trapped: {{ count }} | Honeypot Active</div>
<h2 style="color:#00ff9d">Contact (Honeypot Active)</h2>
<form method="POST"><input type="text" name="name" placeholder="Your Name" required>
<textarea name="message" placeholder="Try: ' OR 1=1 or <script>alert(1)</script>" rows="4" required></textarea>
<button type="submit">Send & Test Security</button></form>
{% if trapped %}<div class="trapped">⚠️ ATTACK TRAPPED! Logged to SOC. IP: {{ ip }}</div>{% endif %}
{% if success %}<div style="background:#00ff9d;color:#000;padding:15px;text-align:center;border-radius:8px;margin:15px 0">✅ Message Received (Safe)</div>{% endif %}
</div></div></body></html>
'''

SOC_LOGIN_HTML = '''
<!DOCTYPE html><html><head><title>SOC Access</title>
<style>body{background:#000;color:#0f0;font-family:monospace;display:flex;justify-content:center;align-items:center;height:100vh;margin:0}
.box{border:2px solid #0f0;padding:30px;border-radius:10px;width:350px;text-align:center}
input{width:90%;padding:10px;background:#000;border:1px solid #0f0;color:#0f0;margin:10px 0}
button{background:#0f0;color:#000;padding:10px 20px;border:none;font-weight:bold;cursor:pointer;width:95%}
</style></head><body><div class="box">
<h2 style="color:red">⛔ SOC ACCESS DENIED</h2><p>Restricted Area</p>
<form method="POST"><input type="password" name="key" placeholder="Enter SOC Key" required>
<button>AUTHENTICATE</button></form>{% if error %}<p style="color:red">{{ error }}</p>{% endif %}</div></body></html>
'''

SOC_DASH_HTML = '''
<!DOCTYPE html><html><head><title>SOC Dashboard</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>body{background:#000;color:#0f0;font-family:monospace;padding:20px}
table{width:100%;border-collapse:collapse;margin-top:20px;word-break:break-all}
th,td{border:1px solid #0f0;padding:8px;text-align:left;font-size:13px}
th{background:#003300} a{color:#0f0;border:1px solid #0f0;padding:8px 15px;text-decoration:none}
</style></head><body>
<div style="display:flex;justify-content:space-between"><h1>SOC - Trapped: {{ count }}</h1><div><a href="/">Portfolio</a> <a href="/soc/logout">Logout</a></div></div>
<table><tr><th>Time</th><th>IP</th><th>Type</th><th>Name</th><th>Payload</th></tr>
{% for log in logs|reverse %}<tr><td>{{ log.time }}</td><td>{{ log.ip }}</td><td style="color:{% if log.type=='XSS' %}#ff0055{% else %}yellow{% endif %}">{{ log.type }}</td><td>{{ log.name }}</td><td>{{ log.payload }}</td></tr>{% endfor %}</table>
{% if not logs %}<p>No attacks yet...</p>{% endif %}</body></html>
'''

@app.route('/', methods=['GET','POST'])
def portfolio():
    trapped=False; success=False
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if request.method=='POST':
        name=request.form.get('name','')[:100]
        msg=request.form.get('message','')[:500]
        atype=detect_attack(name) or detect_attack(msg)
        if atype:
            attack_logs.append({"time":datetime.now().strftime("%H:%M:%S %d-%m-%Y"),"ip":ip,"type":atype,"name":name,"payload":msg})
            trapped=True
        else: success=True
    return render_template_string(PORTFOLIO_HTML,count=len(attack_logs),trapped=trapped,success=success,ip=ip)

@app.route('/soc', methods=['GET','POST'])
def soc():
    if session.get('soc_auth'):
        return render_template_string(SOC_DASH_HTML,logs=attack_logs,count=len(attack_logs))
    error=None
    if request.method=='POST':
        if request.form.get('key')==SOC_SECRET:
            session['soc_auth']=True
            return render_template_string(SOC_DASH_HTML,logs=attack_logs,count=len(attack_logs))
        else:
            error="Invalid Key!"
    return render_template_string(SOC_LOGIN_HTML,error=error)

@app.route('/soc/logout')
def logout():
    session.pop('soc_auth',None)
    return redirect(url_for('soc'))

if __name__=='__main__':
    app.run()
