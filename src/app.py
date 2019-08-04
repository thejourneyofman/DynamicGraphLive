# -*- coding: utf-8 -*-
from flask import Flask, Response, request, render_template, abort
import json
import random
from src.DynamicGraph import DynamicGraph as DG

app = Flask(__name__)

@app.route('/')
def get_index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    graph = DG.ProbGraph(node_num=int(data['N']), edge_num=int(data['E']))
    return json.dumps(graph.__dict__)

@app.route('/add', methods=['POST'])
def add():
    data = request.json
    if 'graph' not in data.keys() or not data['graph']:
        abort(404, {'message': 'You have to generate the graph first.'})
    if 'result' in data['graph'].keys() and data['graph']['result'] == 404:
        abort(404, {'message': 'You have to generate the graph first.'})

    # Copy the dict to the ProbGraph
    graph = DG.ProbGraph(node_num=0, edge_num=0, copy=True)
    graph.V = data['graph']['V']
    graph.E = data['graph']['E']
    graph.connected_nodes = data['graph']['connected_nodes']
    graph.connected_components = data['graph']['connected_components']
    graph.neighbours = {int(k):v for k,v in data['graph']['neighbours'].items()}
    graph.visited =  {int(k):v for k,v in data['graph']['visited'].items()}
    graph.source = data['graph']['source']
    graph.isolated_nodes = data['graph']['isolated_nodes']
    graph.copy = False

    try:
        graph.addDynamic(int(data['L']), int(data['K']))
    except Exception as e:
        abort(404, {'message': e.args})

    return json.dumps(graph.__dict__)

@app.route('/delete', methods=['POST'])
def delete():
    data = request.json

    if 'graph' not in data.keys() or not data['graph']:
        abort(404, {'message': 'You have to generate the graph first.'})
    if 'result' in data['graph'].keys() and data['graph']['result'] == 404:
        abort(404, {'message': 'You have to generate the graph first.'})

    # Copy the dict to the ProbGraph
    graph = DG.ProbGraph(node_num=0, edge_num=0, copy=True)
    graph.V = data['graph']['V']
    graph.E = [tuple(e) for e in data['graph']['E']]
    graph.connected_nodes = data['graph']['connected_nodes']
    graph.connected_components = data['graph']['connected_components']
    graph.neighbours = {int(k):v for k,v in data['graph']['neighbours'].items()}
    graph.visited =  {int(k):v for k,v in data['graph']['visited'].items()}
    graph.source = data['graph']['source']
    graph.isolated_nodes = data['graph']['isolated_nodes']
    graph.copy = False

    try:
        delNum = random.randint(1, int(len(graph.V)))
        delNodes = random.sample(graph.V, delNum)
        graph.delNodesFrom(delNodes)
    except Exception as e:
        abort(404, {'message': e.args})

    return json.dumps(graph.__dict__)

@app.errorhandler(404)
def error_handler(error):
    if 'message' in error.description:
        return json.dumps({'message': error.description['message'], 'result': error.code})
    else:
        return json.dumps({'message': error.description, 'result': error.code })

if __name__ == '__main__':
    app.run(port=8080,debug=True)