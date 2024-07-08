from flask import Flask, render_template
import requests

app = Flask(__name__)

@app.route('/')
def hello():
    return render_template('index.html')

@app.route('/proxy/<path:path>')
def proxy(path):
    url = 'http://192.168.40.131/' + path.replace("/t", "?t")
    print(url)
    response = requests.get(url)
    return response.content


app.run(host='0.0.0.0', port=7929)