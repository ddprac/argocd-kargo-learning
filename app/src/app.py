from doctest import debug
from flask import Flask, jsonify
import os

app = Flask(__name__)
@app.route("/")
def home():
    return "Hello from Platform engineering"

@app.route("/health")

def health():
    return jsonify(status="healthy")

@app.route("/config")
def config():
    return jsonify(
        environment=os.getenv("APP_ENV","local")
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=9000,debug=True)