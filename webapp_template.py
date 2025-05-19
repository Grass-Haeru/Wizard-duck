import os
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

if __name__=='__main__':
    if os.environ.get('RENDER')!='true':
        app.run(debug=True, use_reloader=False)