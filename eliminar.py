from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "¡Hola, esta es tu app en Heroku!"

if __name__ == '__main__':
    app.run(debug=True)
