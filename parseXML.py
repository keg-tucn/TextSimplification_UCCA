import xml.etree.ElementTree as ET
from graphviz import Digraph

# Ordered graph
from networkx.classes.ordered import OrderedDiGraph


# extract data as dictionary
def extract_data(file):
    tree = ET.parse(file)
    root = tree.getroot()
    # iterate over children nodes
    dict_layers={}
    list_layer0=[]
    list_layer1=[]
    for child in root:
        # layers
        if child.tag == "layer":
            # process Layer0
            # print("Layer ", child.attrib.get('layerID'))
            if child.attrib.get('layerID') == "0":
                for child2 in child:
                    if child2.tag != "attributes" and child2.tag != "extra":
                        dict_layer0 = {}
                        dict_layer0['ID']=child2.attrib.get('ID')
                        dict_layer0['type'] = child2.attrib.get('type')
                        for child3 in child2:
                            if child3.tag == 'attributes':
                                dict_layer0['text'] = child3.attrib.get('text')
                                dict_layer0['pos'] = child3.attrib.get('paragraph_position')
                                list_layer0.append(dict_layer0)
                # print dictionary
                # for elemD0 in list_layer0:
                    # print(elemD0)
            # process Layer1
            else:
                for child2 in child:
                    if child2.tag == 'node':
                        dict_layer1 = {}
                        dict_layer1['ID']=child2.attrib.get('ID')
                        dict_layer1['type'] = child2.attrib.get('type')
                        dict_layer1['edge'] = []
                        list_edges = []
                        for child3 in child2:
                            if child3.tag == 'edge':
                                dict_edges = {}
                                dict_edges['toID'] = child3.attrib.get('toID')
                                dict_edges['type'] = child3.attrib.get('type')
                                list_edges.append(dict_edges)
                                dict_layer1['edge']=list_edges
                        list_layer1.append(dict_layer1)
                # print dictionary
                # for elemD1 in list_layer1:
                    # print(elemD1)
    # print(list_layer0)
    # newlistLayer0 = sorted(list_layer0, key=lambda k: k['ID'])
    # print(newlistLayer0)
    dict_layers['Layer0'] = list_layer0
    dict_layers['Layer1'] = list_layer1
    dict_layers['passageID']=root.get('passageID')
    return dict_layers


# Drawing the corresponding graph
def draw_graph(list_layer0, list_layer1, filename):
    graph = Digraph(comment='Graph')
    # add nodes
    for elemD0 in list_layer0:
        graph.node(elemD0['ID'], elemD0['text'], ordering='out')
    for elemD1 in list_layer1:
        graph.node(elemD1['ID'], elemD1['ID'], ordering='out')
    # add edges
    for elemD1 in list_layer1:
        for e in elemD1['edge']:
            graph.edge(elemD1['ID'], e['toID'], e['type'], ordering='out')
    # graph.render(filename+'.gv', view=True) #view is for open or not the file
    graph.render(filename + '.gv')


def draw_ordered_graph(list_layer0, list_layer1, filename):
    graph = OrderedDiGraph(comment='Graph')
    # add nodes
    for elemD0 in list_layer0:
        graph.add_node(elemD0['ID'])
    for elemD1 in list_layer1:
        graph.add_node(elemD1['ID'])
        # add edges
    for elemD1 in list_layer1:
        for e in elemD1['edge']:
            graph.add_edge(elemD1['ID'], e['toID'])
    print(graph.nodes)
    print(graph.edges)
