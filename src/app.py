# -*- coding: utf-8 -*-
from flask import Flask, Response, request, render_template, abort
import json
import random
import time
from PoisonGrapn import *

app = Flask(__name__)
graph_gen = []

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
            str(list(self.data.neighbours.values())): 'neighbours',
            str(self.data.Principals): 'Principals',
            str(self.data.deletedNodes): 'deletedNodes',
            str(self.data.PoisonNodes): 'PoisonNodes'
            # str(self.data.connected_components): 'connected_components',
            # str(self.data.connected_nodes): 'connected_nodes',
            # str(self.data.gamma): 'gamma',
            # str(self.data.isolated_nodes): 'isolated_nodes',
            #str(self.data.source): 'source',
            #str(self.data.temp_component): 'temp_component',
            #str(list(self.data.visited.values())): 'visited'
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
    graph_gen.clear()
    return render_template('index.html')

@app.route('/api/<string:action_type>/<int:node_number>')
def generate(action_type, node_number):
    print(graph_gen)
    def gen():
        if action_type == 'add_nodes' and graph_gen:
            graph = graph_gen.pop()
            x = 0
        elif action_type == 'add_poison':
            if graph_gen:
                graph = graph_gen.pop()
                graph_gen.clear()
                x = 0
            else:
                raise Exception
        else:
            graph_gen.clear()
            x = int(node_number * 0.1)
            graph = PoisonGraph(node_num=x, edge_num=x * 10)
            graph_gen.append(graph)
        interval = int(node_number * 0.1)
        try:
            while x < node_number:
                if x + interval >= node_number:
                    interval = node_number - x
                if action_type in ['new_graph', 'add_nodes']:
                    graph.addDynamic(interval, interval * 10)
                elif len(graph.PoisonNodes) < len(graph.V):
                    graph.addPoison(interval)
                x += interval
                ev = ServerSentEvent(graph, x)
                yield ev.encode()
                graph_gen.append(graph)
            print(graph_gen)
        except GeneratorExit:
            graph_gen.clear()
            raise Exception
    return Response(gen(), mimetype="text/event-stream")

@app.route('/api/scan/<int:node_number>', methods=['POST'])
def scan(node_number):
    print(graph_gen)
    if graph_gen:
        graph = graph_gen.pop()
    else:
        abort(404, {'message': 'Your Graph Is Empty. Generate A Graph First!'})
    if not graph.PoisonNodes:
        abort(404, {'message': 'Your Graph Has No Poisons. Generate An Initial Poison Nodes First!'})
    try:
        counted = graph.scanPoison(node_number)
        graph_gen.append(graph)
        print(graph_gen)
    except Exception as e:
        graph_gen.clear()
        abort(404, {'message': e.args})

    return json.dumps(graph.__dict__)

@app.route('/api/delete', methods=['POST'])
def delete():
    print(graph_gen)
    if graph_gen:
        graph = graph_gen.pop()
    else:
        abort(404, {'message': 'Your Graph Is Empty. Generate A Graph First!'})
    try:
        if graph.Principals:
            graph.delPoisonFrom(graph.Principals)
            graph.Principals.clear()
        else:
            delNum = random.randint(1, int(len(graph.V)))
            delNodes = random.sample(graph.V, delNum)
            graph.delNodesFrom(delNodes)
        if graph.V and graph.E:
            graph_gen.append(graph)
        print(graph_gen)
    except Exception as e:
        graph_gen.clear()
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