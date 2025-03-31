from flask import Flask, render_template, request, jsonify
import subprocess
import re

app = Flask(__name__)

# Функция для выполнения локальных команд
def run_local_command(command):
    try:
        output = subprocess.check_output(command, shell=True, text=True)
        return output.strip()
    except subprocess.CalledProcessError as e:
        return f"Ошибка: {e.output}"

# Главная страница
@app.route("/", methods=["GET", "POST"])
def index():
    result = None  

    if request.method == "POST":
        command_type = request.form.get("command_type")

        if command_type == "add":
            host = request.form.get("host")
            wildcard = request.form.get("wildcard", "").strip()
            result = run_local_command(f"kvas add {host} {wildcard}")
        
        elif command_type == "ssr_update":
            ssr = request.form.get("ssr")
            result = run_local_command(f"echo -e 'y\n{ssr}' | kvas ssr new")

        elif command_type == "purge":
            result = run_local_command("kvas purge")

    return render_template("index.html", result=result)
    
@app.route("/kvas_list")
def kvas_list():
    result = run_local_command("kvas list")
    return result  
    
@app.route("/kvas_list_page")
def kvas_list_page():
    result = run_local_command("kvas list")
    result = re.sub(r'\x1B\[[0-9;]*m', '', result)  # Убираем цветовые коды
    lines = [line for line in result.strip().split("\n") if not line.startswith("----") and "список" not in line.lower()]
    return render_template("kvas_list.html", domains=lines)

@app.route("/delete_domain", methods=["POST"])
def delete_domain():
    domain = request.json.get("domain")
    if domain:
        result = run_local_command(f"kvas del {domain}")
        return {"status": "success", "message": result}
    return {"status": "error", "message": "Домен не указан"}, 400

@app.route("/vpn_status")
def vpn_status():
    raw_output = run_local_command("kvas vpn")  
    if "ПОДКЛЮЧЕНО" in raw_output:
        status = "ПОДКЛЮЧЕНО"
        color = "green"
    else:
        status = "ОТКЛЮЧЕНО"
        color = "red"
    return {"status": status, "color": color}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)