from flask import Flask, request, render_template_string, send_file, redirect, url_for, session
import os
import requests
import sqlite3
import subprocess

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # 
# Creating local DB
def init_db():
    conn = sqlite3.connect('test.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)''')
    c.execute("INSERT OR IGNORE INTO users (id, username, password) VALUES (1, 'admin', 'password')")
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    return render_template_string('''
        <h1>App for testing WAF rules</h1>
        <form action="/xss" method="post">
            <label>XSS:</label>
            <input type="text" name="xss_input">
            <button type="submit">Send</button>
        </form>
        <form action="/ssrf" method="post">
            <label>SSRF (Enter URL URL):</label>
            <input type="text" name="ssrf_url">
            <button type="submit">Send</button>
        </form>
        <form action="/rce" method="post">
            <label>RCE (enter command):</label>
            <input type="text" name="command">
            <button type="submit">Send</button>
        </form>
        <form action="/lfi" method="post">
            <label>LFI (Enter path for LFI):</label>
            <input type="text" name="file_path">
            <button type="submit">Send</button>
        </form>
        <form action="/sqli" method="post">
            <label>SQL Injection (enter username):</label>
            <input type="text" name="username">
            <button type="submit">Send</button>
        </form>
        <form action="/idor" method="get">
            <label>IDOR (Enter user ID):</label>
            <input type="text" name="user_id">
            <button type="submit">Sent</button>
        </form>
    ''')

# XSS 
@app.route('/xss', methods=['POST'])
def xss():
    xss_input = request.form.get('xss_input')
    return f"<h2>Result: {xss_input}</h2>"

# SSRF 
@app.route('/ssrf', methods=['POST'])
def ssrf():
    url = request.form.get('ssrf_url')
    try:
        response = requests.get(url)
        return f"<pre>{response.text}</pre>"
    except Exception as e:
        return f"Error SSRF: {str(e)}"

# RCE 
@app.route('/rce', methods=['POST'])
def rce():
    command = request.form.get('command')
    try:
        result = subprocess.check_output(command, shell=True).decode()
        return f"<pre>{result}</pre>"
    except Exception as e:
        return f"Error RCE: {str(e)}"

# LFI
@app.route('/lfi', methods=['POST'])
def lfi():
    file_path = request.form.get('file_path')
    try:
        return send_file(file_path)
    except Exception as e:
        return f"Error LFI: {str(e)}"

# SQL Injection 
@app.route('/sqli', methods=['POST'])
def sqli():
    username = request.form.get('username')
    conn = sqlite3.connect('test.db')
    c = conn.cursor()
    query = f"SELECT * FROM users WHERE username = '{username}'"
    try:
        c.execute(query)
        result = c.fetchone()
        if result:
            return f"User Found: {result}"
        else:
            return "User not found"
    except Exception as e:
        return f"Error SQL Injection: {str(e)}"
    finally:
        conn.close()

# IDOR 
@app.route('/idor', methods=['GET'])
def idor():
    user_id = request.args.get('user_id')
    if user_id == '1':
        return "ID: 1, Username: admin, Password: password"
    else:
        return f"ID: {user_id}, User data is inaccessible."

if __name__ == '__main__':
    app.run(debug=True)
