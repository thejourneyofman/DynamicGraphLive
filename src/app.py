# -*- coding: utf-8 -*-
from flask import Flask, Response, request, render_template, abort
import json
import random
import time
from src.DynamicGraph import DynamicGraph as DG

app = Flask(__name__)

class ServerSentEvent(object):
    def __init__(self, data, event_id):
        self.data = data
        self.event = None
        self.event_id = event_id
        self.desc_map = {
            self.data : 'data',
            self.event : 'event',
            self.event_id : 'id'
        }
    def encode(self):
        if not self.data:
            return ''
        lines = []
        graph_map = {
            str(self.data.V): 'V',
            str([list(row) for row in self.data.E]): 'E',
            str(self.data.connected_components): 'connected_components',
            str(self.data.connected_nodes): 'connected_nodes',
            #str(self.data.copy): 'copy',
            str(self.data.gamma): 'gamma',
            str(self.data.isolated_nodes): 'isolated_nodes',
            str(list(self.data.neighbours.values())): 'neighbours',
            str(self.data.source): 'source',
            str(self.data.temp_component): 'temp_component',
            str(list(self.data.visited.values())): 'visited'
        }
        for k, v in self.desc_map.items():
            if v == 'data':
                header = '%s:{' % v
                body = []
                for m, n in graph_map.items():
                    body.append('"%s":%s' % (n, m))
                lines.append(header + ','.join(body) + '}')
            elif k:
                lines.append('%s: %s' % (v, k))
        return '%s\n\n' % '\n'.join(lines)

@app.route('/')
def get_index():
    return render_template('index.html')

@app.route("/generate/<int:node_number>")
def generate(node_number):
    def gen():
        x = 0
        init_num = int(node_number * 0.1)
        interval = int(node_number * 0.1)
        try:
            graph = DG.ProbGraph(node_num=init_num, edge_num=init_num * 10)
            while x < node_number:
                graph.addDynamic(interval,interval * 10)
                x = len(graph.V) + interval
                ev = ServerSentEvent(graph, x)
                yield ev.encode()
        except GeneratorExit:
            raise Exception('Graph generation has been cancelled.')

    return Response(gen(), mimetype="text/event-stream")

@app.route("/add/<string:graph>")
def add(graph):
    data = json.loads(graph)
    def gen():
        interval = int(int(data['L']) * 0.1)
        if 'graph' in data.keys() and data['graph'] and 'V' in data['graph'].keys() and data['graph']['V']:
            graph = DG.ProbGraph(node_num=0, edge_num=0, copy=True)
            graph.V = data['graph']['V']
            graph.E = data['graph']['E']
            graph.connected_nodes = data['graph']['connected_nodes']
            graph.connected_components = data['graph']['connected_components']
            if isinstance(data['graph']['neighbours'], dict):
                graph.neighbours = {int(k): v for k, v in data['graph']['neighbours'].items()}
            if isinstance(data['graph']['neighbours'], list):
                graph.neighbours = {int(k): v for k, v in enumerate(data['graph']['neighbours'])}
            if isinstance(data['graph']['visited'], dict):
                graph.visited = {int(k): v for k, v in data['graph']['visited'].items()}
            if isinstance(data['graph']['visited'], list):
                graph.visited = {int(k): v for k, v in enumerate(data['graph']['visited'])}
            graph.source = data['graph']['source']
            graph.isolated_nodes = data['graph']['isolated_nodes']
            graph.copy = False
            x = 0
        else:
            init_num = int(int(data['L']) * 0.1)
            graph = DG.ProbGraph(node_num=init_num, edge_num=init_num * 10)
            x = init_num
        try:
            while x < int(data['L']):
                graph.addDynamic(interval, interval * 10)
                x += interval
                ev = ServerSentEvent(graph, x)
                yield ev.encode()
        except GeneratorExit:
            raise Exception('Graph generation has been cancelled.')

    return Response(gen(), mimetype="text/event-stream")

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
    if isinstance(data['graph']['neighbours'], dict):
        graph.neighbours = {int(k): v for k, v in data['graph']['neighbours'].items()}
    if isinstance(data['graph']['neighbours'], list):
        graph.neighbours = {int(k): v for k, v in enumerate(data['graph']['neighbours'])}
    if isinstance(data['graph']['visited'], dict):
        graph.visited = {int(k): v for k, v in data['graph']['visited'].items()}
    if isinstance(data['graph']['visited'], list):
        graph.visited = {int(k): v for k, v in enumerate(data['graph']['visited'])}
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