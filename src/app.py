# -*- coding: utf-8 -*-
from flask import Flask, Response, request, render_template, abort
import json
import random
import time
import queue
from src.PoisonGrapn import *

app = Flask(__name__)
graph_gen = queue.Queue()
poison_map = ['new_V', 'E', 'Principals','deletedNodes', 'InitialPoison', 'infected_nodes']

class ServerSentEvent(object):
    def __init__(self, data, event_id=0):
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
        new_V = [(key,len(self.data.neighbours[key])) for key in self.data.V & self.data.neighbours.keys()]
        graph_map = {
            str([list(row) for row in new_V]): 'new_V',
            str([list(row) for row in self.data.E]): 'E',
            str(self.data.Principals): 'Principals',
            str(self.data.deletedNodes): 'deletedNodes',
            str(self.data.InitialPoison): 'InitialPoison',
            str(self.data.infected_nodes): 'infected_nodes'
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

@app.route('/api/<string:action_type>/<int:node_number>')
def generate(action_type, node_number):
    def gen():
        try:
            if action_type in ['add_nodes', 'add_poison']:
                graph = graph_gen.get(None)
                graph.InitialPoison.clear()
                graph.infected_nodes.clear()
                x = 0
            else: #action_type in ['new_graph']:
                graph_gen.queue.clear()
                x = int(node_number * 0.1)
                graph = PoisonGraph(node_num=x, edge_num=x * 10)
            interval = int(node_number * 0.1)
            while x < node_number:
                if x + interval >= node_number:
                    interval = node_number - x
                if action_type in ['new_graph', 'add_nodes']:
                    graph.addDynamic(interval, interval * 10)
                elif len(graph.InitialPoison) < node_number:
                    graph.addPoison(interval)
                x += interval
                ev = ServerSentEvent(graph, x)
                yield ev.encode()
                graph_gen.put(graph)
        except queue.Empty:
            raise StopIteration
        except GeneratorExit:
            graph_gen.queue.clear()
    return Response(gen(), mimetype="text/event-stream")

@app.route('/api/scan/<int:node_number>', methods=['POST'])
def scan(node_number):
    try:
        graph = graph_gen.get(None)
        graph.scanPoison(node_number)
        graph_gen.put(graph)
    except queue.Empty:
        abort(404, {'message': 'Your Graph Is Empty. Generate A Graph First!'})
    return json.dumps(graph.__contains__(poison_map))

@app.route('/api/delete', methods=['POST'])
def delete():
    try:
        graph = graph_gen.get(None)
        if graph.Principals:
            graph.delPoisonFrom(graph.Principals)
            graph.Principals.clear()
        elif graph.V:
            delNum = random.randint(1, int(len(graph.V)))
            delNodes = random.sample(graph.V, delNum)
            graph.delNodesFrom(delNodes)
            graph_gen.put(graph)
        else:
            raise Exception
    except queue.Empty:
        abort(404, {'message': 'Your Graph Is Empty. Generate A Graph First!'})
    except Exception:
        abort(404, {'message': 'Your Graph Is Empty.'})
    return json.dumps(graph.__contains__(poison_map))

@app.errorhandler(404)
def error_handler(error):
    if 'message' in error.description:
        return json.dumps({'message': error.description['message'], 'result': error.code})
    else:
        return json.dumps({'message': error.description, 'result': error.code })

if __name__ == '__main__':
    app.run(port=8080,debug=True)