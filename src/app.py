# -*- coding: utf-8 -*-
from flask import Flask, Response, request, render_template, abort
import json
import random
import time
from src.DynamicGraph import DynamicGraph as DG

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
            #str(self.data.connected_components): 'connected_components',
            #str(self.data.connected_nodes): 'connected_nodes',
            #str(self.data.gamma): 'gamma',
            #str(self.data.isolated_nodes): 'isolated_nodes',
            str(list(self.data.neighbours.values())): 'neighbours',
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

@app.route("/api/<string:action_type>/<int:node_number>")
def generate(action_type, node_number):
    def gen():
        if action_type == "add" and graph_gen:
            graph = graph_gen.pop()
            x = 0
        else:
            x = int(node_number * 0.1)
            graph = DG.ProbGraph(node_num=x, edge_num=x * 10)
        interval = int(node_number * 0.1)
        try:
            while x < node_number:
                if x + interval >= node_number:
                    interval = node_number - x
                graph.addDynamic(interval, interval * 10)
                x += interval
                ev = ServerSentEvent(graph, x)
                yield ev.encode()
            graph_gen.append(graph)
        except GeneratorExit:
            if graph_gen:
                graph_gen.clear()
            raise Exception('Graph generation has been cancelled.')

    return Response(gen(), mimetype="text/event-stream")

@app.route('/delete', methods=['POST'])
def delete():
    if graph_gen:
        graph = graph_gen.pop()
    else:
        abort(404, {'message': 'Your Graph Is Empty.'})
    try:
        delNum = random.randint(1, int(len(graph.V)))
        delNodes = random.sample(graph.V, delNum)
        graph.delNodesFrom(delNodes)
        if graph.V and graph.E:
            graph_gen.append(graph)
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