#!/usr/bin/python
# -*- coding: utf-8 -*-

import random
import copy
from src.DynamicGraph import DynamicGraph as DG

class PoisonGraph(DG.ProbGraph):
    u"""Derived class of ProbGraph for a poison network. Anything that can be
        represented by an initial infected nodes list. It returns a class of
        processed graph following a power-law rule of edge degrees for every
        node and size of components based on the node numbers, max edge numbers
        and special curves pattern.
       :param ProbGraph: totally generated nodes num.
       :param edge_num: max allowed edge numbers generating the graph.
       :param poison_number: number of the initial poison nodes
       :param gamma: It is a parameter of kurtosis for the distribution of edge
        degrees or cluster size that follows a power-law rules. If it is greater,
        the distribution of connected components will have a higher kurtosis.
       Conversely, the distribution of edges degrees will have a higher kurtosis.
       :param empty: If it is True, ProbGraph will be generated by nodes list
       only without any connections.
       If it is False, ProGraph will be generated from scratch.
       """
    def __init__(self, node_num, edge_num, poison_number=0, gamma=3, empty=False):
        self.V = list(range(node_num))
        self.E = []
        self.InitialPoison = list(range(poison_number))
        self.infected_nodes = list(range(poison_number))
        self.Principals = []
        self.deletedNodes = 0
        self.temp_component = []
        self.connected_nodes = []
        self.connected_components = []
        self.gamma = gamma
        self.neighbours = {}
        self.visited = {}
        self.source = gamma
        self.isolated_nodes = []

        #############################
        # Do the initialization
        #############################
        if self._initialize(node_num) and not empty:
            self._createEdges(edge_num)
            self.updateComponents()

    def __contains__(self, keys):
        if self.__dict__ is None:
            raise TypeError('not indexable')
        return dict((key,value) for key, value in self.__dict__.items() if key in keys)

    def addPoison(self, node_num):
        u"""Mark new poison nodes to an exiting graph without adding nodes
            :param node_num: the number of newly makred poison nodes.
        """
        self.InitialPoison.extend(random.sample([v for v in self.V if v not in self.InitialPoison], node_num))

    def getPoison(self):
        u"""Returns all poison nodes in an exiting graph
            :param None
        """
        return self.infected_nodes

    def delPoisonFrom(self, nodes):
        u"""Delete all infected nodes from an exiting graph using a recursive
            way with dfs algorithm to search nodes by their neighbours.
            :param nodes: the initial poison nodes list
        """
        self.deletedNodes = 0
        for v in [value for value in nodes if value in self.V]:
            self.V.remove(v)
            self.deletedNodes += 1
            self.connected_nodes[:] = (value for value in self.connected_nodes if value != v)
            self.isolated_nodes[:] = (value for value in self.isolated_nodes if value != v)
            self.infected_nodes[:] = (value for value in self.infected_nodes if value != v)
            self.InitialPoison[:] = (value for value in self.InitialPoison if value != v)
            for n in self.neighbours[v]:
                self.connected_nodes.remove(n)
                self.neighbours[n].remove(v)
                if not self.neighbours[n]:
                    self.isolated_nodes.append(n)
                if (n, v) in self.E:
                    self.E.remove((n, v))
                else:
                    self.E.remove((v, n))
                self.neighbours[v] = []

        sorted_components = sorted(self.connected_components, key=len, reverse=True)
        p = set(nodes)
        for i, component in enumerate(sorted_components):
            s = set(component)
            if len(tuple(s & p)) > 0:
                self.connected_components.remove(component)
                component[:] = (value for value in component if value not in list(tuple(s & p)))
                if len(component) <= 1:
                    continue
                for v in self._dfs_non_recursive(component):
                    self.V.remove(v)
                    self.deletedNodes += 1
                    self.connected_nodes[:] = (value for value in self.connected_nodes if value != v)
                    self.isolated_nodes[:] = (value for value in self.isolated_nodes if value != v)
                    self.infected_nodes[:] = (value for value in self.infected_nodes if value != v)
                    self.InitialPoison[:] = (value for value in self.InitialPoison if value != v)
                    for n in self.neighbours[v]:
                        self.connected_nodes.remove(n)
                        self.neighbours[n].remove(v)
                        if not self.neighbours[n]:
                            self.isolated_nodes.append(n)
                        if (n, v) in self.E:
                            self.E.remove((n, v))
                        else:
                            self.E.remove((v, n))
                        self.neighbours[v] = []
                p -= s
                if len(tuple(p)) == 0:
                    break


    def scanPoison(self, node_num):
        u""" It return a final count of nodes infected with poison in the entire
            graph after the spread of poison stops and a list of Principals node
            that if removed, would minimize scanPoison(InitialPoison).
            :param node_num: the number of principals poison nodes.
            the length should be between 1 and len(InitialPoison) - 1
        """
        if node_num > len(self.InitialPoison) - 1:
            return len(self.InitialPoison), self.InitialPoison
        sorted_components = sorted(self.connected_components, key=len, reverse=True)
        counted = 0
        p = set(self.InitialPoison)
        self.infected_nodes.extend(self.InitialPoison)
        for i, v in enumerate(sorted_components):
            s = set(v)
            if len(tuple(s & p)) > 0:
                counted += len(v)
                self.infected_nodes.extend(list(tuple(s - p)))
                if len(self.Principals) < node_num:
                    self.Principals.append(random.choice(tuple(s & p)))
                p -= s
                if len(tuple(p)) == 0:
                    break
        counted += len(p)
        if len(self.Principals) < node_num:
            if len(tuple(p)) > 0:
                self.Principals.extend(random.sample(p, node_num - len(principals)))
            else:
                self.Principals = random.sample(self.InitialPoison, node_num)
        return counted