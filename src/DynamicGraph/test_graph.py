#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2019 Chao (Chase) Xu
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""Example showing how to generat the graph dynamically, add nodes and conduct
a breadth first search.
"""

from unittest import TestCase
from datetime import datetime
import matplotlib.pyplot as plt
import random
import copy

import DynamicGraph as DG

class TestGeneralReturns(TestCase):
    def __init__(self, node_num, edge_num, L, K):
        TestCase.__init__(self)
        self.node_num = node_num
        self.edge_num = edge_num
        self.L = L
        self.K = K
        self.graph = DG.ProbGraph(node_num=node_num, edge_num=edge_num)

    def test_NodeEdges(self):
        ##########################################################
        # Test to create a graph with correct nodes and edges
        ##########################################################
        self.assertEqual(len(self.graph.V), self.node_num,
                        "The number of nodes generated is not correct")
        self.assertTrue(len(self.graph.E) < self.edge_num,
                        "The number of edges generated is not correct")

    def test_Powerlaw(self):
        ##########################################################
        # Test the graph created that has its edge degrees follow
        # a power law distribution
        ##########################################################
        edge_degrees = []
        for v in self.graph.neighbours:
            edge_degrees.append(len(self.graph.neighbours[v]))
        plt.hist(edge_degrees, normed=True, bins=200)
        plt.ylabel('Probability of edge degree of all nodes')
        plt.show()

        ##########################################################
        # Test the graph created that has its cluster size follow
        # a power law distribution
        ##########################################################
        component_size = []
        for v in self.graph.getComponents():
            component_size.append(len(v))
        plt.hist(sorted(component_size)[:-1], normed=True, bins=200)
        plt.ylabel('Probability of size of connected components (Exclusive of the main frame)')
        plt.show()
        print("The size of the main frame is", sorted(component_size)[-1])
        self.assertTrue(sorted(component_size)[-1] < self.node_num / 3,
                        "In our algorithm, the size of main frame should be greater than 1/3 of all nodes")

        ##########################################################
        # Test the generated graph that has its sum of edge degrees
        # be same with the sum of connected nodes.
        ##########################################################
        self.assertEqual(len(self.graph.connected_nodes), sum(edge_degrees),
                         "The graph after nodes deleted is not correct")

    def test_bfsSearch(self, doValidation=False):
        ##########################################################
        # Test a none recursive breadth first search algorithm
        ##########################################################
        start_node = random.choice(self.graph.connected_nodes)
        visited = self.graph.bfsearch(start_node)
        print("bfs visited nodes from start node", start_node, visited)

        if doValidation:
            p = set([k for k, v in visited.items()])
            for i, v in enumerate(self.graph.connected_components):
                s = set(v)
                if len(tuple(s - p)) == 0:
                    print("The bfs returns the same result as it does from connected component", v)
                    break

    def test_addDynamic(self):
        ##########################################################
        # Test to add nodes dynamically to an existing graph.
        ##########################################################
        beforeNodesCount = len(self.graph.V)
        self.graph.addDynamic(self.L, self.K)
        self.assertEqual(len(self.graph.V), beforeNodesCount + self.L,
                         "The number of nodes generated is not correct")
        self.assertTrue(len(self.graph.E) < self.edge_num + self.K,
                        "The number of edges generated is not correct")

        ##########################################################
        # Test the graph after new nodes added that has its edge
        # degrees follow a power law distribution
        ##########################################################
        edge_degrees = []
        for v in self.graph.neighbours:
            edge_degrees.append(len(self.graph.neighbours[v]))
        plt.hist(edge_degrees, normed=True, bins=200)
        plt.ylabel('Probability of edge degree of all nodes')
        plt.show()

        ##########################################################
        # Test the graph after new nodes added that has its cluster
        # sizes follow a power law distribution
        ##########################################################
        component_size = []
        for v in self.graph.getComponents():
            component_size.append(len(v))
        plt.hist(sorted(component_size)[:-1], normed=True, bins=200)
        plt.ylabel('Probability of size of connected components (Exclusive of the main frame)')
        plt.show()
        print("The size of the main frame is", sorted(component_size)[-1])
        self.assertTrue(sorted(component_size)[-1] < (self.node_num + self.L) / 3,
                        "In our algorithm, the size of main frame should be greater than 1/3 of all nodes")

        ##########################################################
        # Test the graph after new nodes added that has its sum of
        # edge degrees be same with the sum of connected nodes.
        ##########################################################
        self.assertEqual(len(self.graph.connected_nodes), sum(edge_degrees),
                         "The graph after nodes added is not correct")

    def test_delDynamic(self):
        ##########################################################
        # Test to deletes nodes dynamically from an existing graph.
        ##########################################################
        delNum = random.randint(1, int(len(self.graph.V) * 0.1))
        delNodes = random.sample(self.graph.V, delNum)
        beforeNodesCount = len(self.graph.V)
        self.graph.delNodesFrom(delNodes)
        self.assertEqual(len(self.graph.V), beforeNodesCount - delNum,
                         "The number of nodes after deleted is not correct")

        ##########################################################
        # Test the graph after nodes deleted that has its edge
        # degrees follow a power law distribution
        ##########################################################
        edge_degrees = []
        for v in self.graph.neighbours:
            edge_degrees.append(len(self.graph.neighbours[v]))
        plt.hist(edge_degrees, normed=True, bins=200)
        plt.ylabel('Probability of edge degree of all nodes')
        plt.show()

        ##########################################################
        # Test the graph after nodes deleted that has its cluster
        # sizes follow a power law distribution
        ##########################################################
        component_size = []
        for v in self.graph.getComponents():
            component_size.append(len(v))
        plt.hist(sorted(component_size)[:-1], normed=True, bins=200)
        plt.ylabel('Probability of size of connected components (Exclusive of the main frame)')
        plt.show()
        print("The size of the main frame is", sorted(component_size)[-1])
        self.assertTrue(sorted(component_size)[-1] < (self.node_num - delNum) / 3,
                        "In our algorithm, the size of main frame should be greater than 1/3 of all nodes")

        ##########################################################
        # Test the graph after nodes deleted that has its sum of
        # edge degrees be same with the sum of connected nodes.
        ##########################################################
        self.assertEqual(len(self.graph.connected_nodes), sum(edge_degrees),
                         "The graph after nodes deleted is not correct")


if __name__ == '__main__':
    #############################
    # Test Scenario.
    # N - node count -  200,000
    # E - edge count - 2,000,000
    # 1 ADD(L, K)  -> L =  50,000, K = 500,000
    # 2 DEL(NODES) -> Random
    # 3 ADD(L, K)  -> L =  50,000, K = 500,000
    # 4 DEL(NODES) -> Random
    #############################
    start = datetime.now()
    print("Test Scenario Starts.....")
    #testRun = TestGeneralReturns(node_num=200000, edge_num=2000000,L=50000, K=500000)
    testRun = TestGeneralReturns(node_num=2000, edge_num=20000, L=500, K=5000)
    print("Time used to generate the graph from scratch ", datetime.now() - start)

    ## 1, Add nodes
    start = datetime.now()
    testRun.test_addDynamic()
    print("Time used to add new nodes dynamically ", datetime.now() - start)

    ## 2, Del nodes
    start = datetime.now()
    testRun.test_delDynamic()
    print("Time used to delete nodes dynamically ", datetime.now() - start)

    ## 3, Add nodes
    start = datetime.now()
    testRun.test_addDynamic()
    print("Time used to add new nodes dynamically ", datetime.now() - start)

    ## 4, Del nodes
    start = datetime.now()
    testRun.test_delDynamic()
    print("Time used to delete nodes dynamically ", datetime.now() - start)


