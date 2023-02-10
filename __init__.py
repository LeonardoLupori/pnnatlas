from flask import Flask
import sys

app = Flask(__name__)

@app.route('/')
def homepage():
    return "Hello world. Test Flask app by Leonardo Lupori"

if __name__ == "__main__":
    app.run()
