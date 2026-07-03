from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

# access api

@app.route("/api/data", methods=["GET"])
def get_data():
    pass

@app.route("/api/data", methods=["POST"])
def post_data():
    pass

@app.route("/api/update", methods=["GET"])
def update_data():
    pass

@app.route("/api/control", methods=["POST"])
def control_data():
    pass

# discord bot