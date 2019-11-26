from flask import Flask, escape, request
import pickledb
from werkzeug.debug import DebuggedApplication
app = Flask(__name__)
db = pickledb.load('example.db', True,sig=False)

@app.route('/')
def hello():
    name = request.args.get("name", "World")
    return f'Hello, {escape(name)}!'

@app.route('/count')
def pageview():
    counter=db.get('count')
    counter+=1
    db.set('count',counter)
    return f'Nice {counter=}!'