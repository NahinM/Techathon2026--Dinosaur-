from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

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