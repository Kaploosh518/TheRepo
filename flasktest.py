print("Hello World")
from flask import Flask, jsonify, request
app = Flask(__name__)


@app.route('/')
def hello():
    return "Hello, World!"

@app.route('/hello')
def hello_name():
    return "Hello Again!"




if __name__ == '__main__':
    app.run()