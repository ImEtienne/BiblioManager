from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'  # Cette ligne doit être indentée de 4 espaces

if __name__ == '__main__':
    app.run(debug=True)
