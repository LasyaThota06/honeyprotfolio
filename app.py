from flask import Flask, request, render_template
from datetime import datetime
app = Flask(__name__)
attack_logs = []
def detect(p):
    p=p.lower()
    if "' or" in p or "'=" in p or "--" in p: return 90, "SQL Injection"
    if "<script" in p or "onerror" in p: return 85, "XSS"
    if "../" in p or "/etc/passwd" in p: return 80, "Path Traversal"
    if "/admin" in p: return 70, "Recon Scan"
    return 0, "Normal"
@app.before_request
def log_attack():
    full = request.path + " " + str(request.args)
    score, typ = detect(full)
    if score>50:
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        attack_logs.insert(0, {"time": datetime.now().strftime("%H:%M:%S"), "ip": ip, "type": typ, "payload": full[:120]})
@app.route('/')
def home(): return render_template('index.html', count=len(attack_logs))
@app.route('/soc')
def soc():
    if request.args.get('key')!="cyber20LPA": return "404",404
    return render_template('soc.html', logs=attack_logs)
if __name__ == '__main__': app.run(host='0.0.0.0', port=10000)
