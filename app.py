from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scan', methods=['POST'])
def scan():
    url = request.form['url']
    result = {}

    try:
        response = requests.get(url)
        result['status'] = f"Status Code: {response.status_code}"
        soup = BeautifulSoup(response.text, 'html.parser')

        # XSS Check
        if "<script>" in response.text.lower():
            result['xss'] = "Possible XSS found"
        else:
            result['xss'] = "No XSS found"

        # Clickjacking Check
        headers = response.headers
        if 'X-Frame-Options' in headers:
            result['clickjacking'] = "Protected from clickjacking"
        else:
            result['clickjacking'] = "Vulnerable to clickjacking"

        # SQL Injection (basic test)
        test_url = url + "'"
        test_resp = requests.get(test_url)
        if "sql" in test_resp.text.lower() or "syntax" in test_resp.text.lower():
            result['sqli'] = "Possible SQL Injection vulnerability"
        else:
            result['sqli'] = "No SQL Injection vulnerability"

        # Security Headers
        result['headers'] = {
            'X-Content-Type-Options': headers.get('X-Content-Type-Options', 'Missing'),
            'Content-Security-Policy': headers.get('Content-Security-Policy', 'Missing'),
            'Strict-Transport-Security': headers.get('Strict-Transport-Security', 'Missing')
        }

    except Exception as e:
        result['error'] = str(e)

    return render_template('result.html', result=result, url=url)

if __name__ == '_main_':
    app.run(host='0.0.0.0', port=5050, debug=True)
