from flask import Flask, escape, request, jsonify
import pickledb
from werkzeug.debug import DebuggedApplication
app = Flask(__name__)
db = pickledb.load('example.db', True,sig=False)

@app.route('/')
def hello():
    name = request.args.get("name", "World")
    #return f'Hello, {escape(name)}!'
    return 'Hello'

@app.route('/count')
def pageview():
    counter=db.get('count')
    counter+=1
    db.set('count',counter)
    #return f'Nice {counter=}!'
    return str(counter)

@app.route('/calc',methods=['POST'])
def calc():
    expr = request.json.get("expression").split(' ')
    ret = ''
    if expr[1] == '+':
        ret = str(float(expr[0]) + float(expr[2]))
    elif expr[1] == '-':
        ret = str(float(expr[0]) - float(expr[2]))
    elif expr[1] == '*':
        ret = str(float(expr[0]) * float(expr[2]))
    elif expr[1] == '/':
        if float(expr[2]) == .0: ret = 'error'
        else: ret = str(float(expr[0]) / float(expr[2]))
    if ret == 'error':
        return "Error", 400
    return jsonify({'result':ret})
    #return jsonify({'op':request.json.get("expression"),'po':'po'}) 

@app.route('/variable/<name>',methods=['PUT'])
def assign(name):
    val = float(request.json.get('value'))
    db.set('var_'+name,val)
    return 'ok'

@app.route('/variable/<name>',methods=['GET'])
def read(name):
    ret = db.get('var_'+name)
    return jsonify({"value":ret})