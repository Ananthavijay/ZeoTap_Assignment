from flask import Flask, render_template, request, redirect, url_for, flash
import requests

app = Flask(__name__)
app.secret_key = "^>+W7MzlIk'0cq`"

# API base URL
API_URL = "http://127.0.0.1:8000"

@app.route('/')
def index():
    rules = requests.get(f"{API_URL}/current_rules").json().get("rules", [])
    return render_template('index.html', rules=rules)

@app.route('/create_rule', methods=['POST'])
def create_rule():
    rule_name = request.form.get('rule_name')
    rule_string = request.form.get('rule_string')
    
    if not rule_name or not rule_string:
        flash("Please provide a rule name and rule string")
        return redirect(url_for('index'))
    
    response = requests.post(f"{API_URL}/create_rule", json={"rule_name": rule_name, "rule_string": rule_string})
    
    if response.status_code == 200:
        flash("Rule created successfully!")
    else:
        flash(f"Error: {response.json().get('detail')}")
    
    return redirect(url_for('index'))

@app.route('/evaluate_rule', methods=['POST'])
def evaluate_rule():
    rule_id = request.form.get('rule_id')
    data = request.form.get('data')
    
    if not rule_id or not data:
        flash("Please provide a rule ID and data")
        return redirect(url_for('index'))
    
    try:
        data_dict = eval(data)  # This is not safe in production
    except:
        flash("Invalid data format")
        return redirect(url_for('index'))
    
    response = requests.post(f"{API_URL}/evaluate_rule", json={"rule_id": int(rule_id), "data": data_dict})
    
    if response.status_code == 200:
        result = response.json().get('evaluation_result')
        flash(f"Evaluation Result: {result}")
    else:
        flash(f"Error: {response.json().get('detail')}")
    
    return redirect(url_for('index'))

@app.route('/combine_rules', methods=['POST'])
def combine_rules():
    combined_rule_name = request.form.get('combine_rule_name')  # Get the name for the combined rule
    selected_rules = request.form.getlist('rule_strings')
    
    if not combined_rule_name or not selected_rules:
        flash("Please provide a name for the combined rule and select at least one rule")
        return redirect(url_for('index'))
    
    response = requests.post(f"{API_URL}/combine_rules", json={"rule_name": combined_rule_name, "rule_strings": selected_rules})
    
    if response.status_code == 200:
        flash("Rules combined successfully!")
    else:
        flash(f"Error: {response.json().get('detail')}")
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(port=5000)
