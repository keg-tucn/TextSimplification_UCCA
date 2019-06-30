import xml.etree.ElementTree as ET
from builtins import print
from graphviz import Digraph
from networkx.classes.ordered import OrderedDiGraph
from UCCA_Simplification.splitSentence import Split
from UCCA_Simplification.createXML import CreateXML


class Parser:

    def __init__(self, source_file):
        self.source_file = source_file
        self.split = Split(self, self.source_file)
        self.createXML = CreateXML([], [], self.split.graph, self)

    @staticmethod
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
                                    dict_layer0['paragraph'] = child3.attrib.get('paragraph')
                                if child3.tag == 'extra':
                                    dict_layer0['dep'] = child3.attrib.get('dep')
                                    dict_layer0['ent_iob'] = child3.attrib.get('ent_iob')
                                    dict_layer0['ent_type'] = child3.attrib.get('ent_type')
                                    dict_layer0['head'] = child3.attrib.get('head')
                                    dict_layer0['lemma'] = child3.attrib.get('lemma')
                                    dict_layer0['orig_paragraph'] = child3.attrib.get('orig_paragraph')
                                    dict_layer0['orth'] = child3.attrib.get('orth')
                                    dict_layer0['position'] = child3.attrib.get('pos')
                                    dict_layer0['prefix'] = child3.attrib.get('prefix')
                                    dict_layer0['shape'] = child3.attrib.get('shape')
                                    dict_layer0['suffix'] = child3.attrib.get('suffix')
                                    dict_layer0['tag'] = child3.attrib.get('tag')
                            list_layer0.append(dict_layer0)
                        else:
                            if child2.tag == "extra":
                                extra = child2.attrib.get('doc')
                                dict_layers['extra'] = extra
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
                                    for child4 in child3:
                                        if child4.tag == 'attributes':
                                            dict_edges['remote'] = child4.attrib.get('remote')
                                    list_edges.append(dict_edges)
                                    dict_layer1['edge']=list_edges
                            list_layer1.append(dict_layer1)
        dict_layers['Layer0'] = list_layer0
        dict_layers['Layer1'] = list_layer1
        dict_layers['passageID']=root.get('passageID')
        dict_layers['tree'] = tree
        return dict_layers

    # Drawing the corresponding graph
    @staticmethod
    def draw_graph(list_layer0, list_layer1, filename):
        graph = Digraph(comment='Graph')
        # add nodes
        for elemD0 in list_layer0:
            if elemD0 != None:
                graph.node(elemD0['ID'], elemD0['text'], ordering='out')
        for elemD1 in list_layer1:
            if elemD1 != None:
                graph.node(elemD1['ID'], elemD1['ID'], ordering='out')
        # add edges
        for elemD1 in list_layer1:
            if elemD1 != None:
                for e in elemD1['edge']:
                    if e['toID'] != None:
                        graph.edge(elemD1['ID'], e['toID'], e['type'], ordering='out')
        graph.render(filename)

    @staticmethod
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

    # split the xml file with rule 1
    def split_xml_file_rule1(self, destination_file, words_linkers, list_layer0, list_layer1):
        dict_change = {}
        dict_change['no_change'] = True
        # replace the words for linkers by subject word
        for wl in words_linkers:
            if wl['subject']['node_word'] != None:
                list_layer0 = self.split.graph.replace_word(wl['ID'], wl['subject']['node_word']['text'])
                list_hnodes = []
                list_hnodes.append(wl['hnodes']['list'][-1])
                self.split.list_layer1 = self.split.graph.delete_edge_h(wl['hnodes']['parent'], list_hnodes)
                self.split.list_layer1 = self.split.graph.delete_all_incoming_edges_for_node(wl['parent'])
                for h in list_hnodes:
                    dict_change = self.split.graph.change_edge(h, wl['subject']['parent'], wl['parent'])
                list_la = wl['hnodes']['list'][:]
                list_la.remove(list_hnodes[0])
                for elem in list_la:
                    list_layer1 = self.split.graph.delete_edge_la(elem)
        if dict_change['no_change']:
            print("No changes")
            return 0
        else:
            self.split.list_layer1 = self.split.graph.delete_back_edges(words_linkers)
            Parser.draw_graph(self.split.list_layer0, self.split.list_layer1, destination_file)
            return 1

    def split_xml_file_rule1_new(self, source_file, destination_directory_graph, destination_directory_data, words_linkers, list_layer0, list_layer1):
        dict_change = {}
        dict_change['no_change'] = True
        # replace the words for linkers by subject word
        for wl in words_linkers:
            if wl['common'] != None:
                id_word_next = None
                if int(wl['pos']) != 1:
                    id_word_next = self.split.graph.get_id_for_word(int(wl['pos']) + 1)
                else:
                    id_word_next = self.split.graph.get_id_max_layer0()
                    word = self.split.graph.get_word(id_word_next)
                    while word['type'] == "Punctuation":
                        id_word_next = round(float(id_word_next) - 0.1, 1)
                        word = self.split.graph.get_word(str(id_word_next))
                list_nodes_to_root = self.split.graph.get_nodes_to_the_root(str(id_word_next))
                if wl['hnodes']['parent'] in list_nodes_to_root:
                    h1 = self.split.graph.find_edge(wl['hnodes']['parent'], list_nodes_to_root)
                    # delete all incoming edges for h1
                    self.split.graph.list_layer1 = self.split.graph.delete_all_incoming_edges_for_node(h1)

                    # add a new node corresponding to the common node
                    new_id = self.split.graph.add_node_rule2(wl['common'], '1')
                    self.split.graph.list_layer1 = self.split.graph.delete_all_incoming_edges_for_node(wl['parent'])
                    id0 = self.split.graph.get_child(wl['parent'])

                    # delete the linker node
                    self.split.graph.list_layer1 = self.split.graph.delete_edge(wl['parent'], id0)
                    self.split.graph.list_layer0 = self.split.graph.delete_node_layer0(id0)
                    self.split.graph.list_layer1 = self.split.graph.delete_node_layer1(wl['parent'])

                    # add an edge between h1 and the new common node
                    self.split.graph.add_edge(h1, new_id)

                    # delete the edge between the subnodes of h1 and the common element
                    list_subnodes_h1 = self.split.graph.get_all_nodes_to_leaves(h1)
                    list_subnodes_h1.append(h1)
                    for node in list_subnodes_h1:
                        self.split.graph.list_layer1 = self.split.graph.delete_edge(node, wl['common'])
                    dict_change['no_change'] = False
                for n_root in list_nodes_to_root:
                    self.split.graph.delete_edge_la(n_root)
        if dict_change['no_change']:
            print("No changes")
            return 0
        else:
            # self.split.list_layer1 = self.split.graph.delete_back_edges(words_linkers)
            self.split.graph.delete_all_isolated_nodes()
            self.createXML.set_list_layer0(self.split.graph.list_layer0)
            self.createXML.set_list_layer1(self.split.graph.list_layer1)
            # self.draw_graph(self.split.graph.list_layer0, self.split.graph.list_layer1, destination_directory_graph + source_file)
            self.createXML.create_graphs(source_file, destination_directory_data, destination_directory_graph, '1')
            return 1

    # split the xml file with rule 2
    def split_xml_file_rule2(self, file, source_file, destination_graph, destination_file, list_layer0, list_layer1, nodes_e):
        has_changed = False
        for e in nodes_e:
            list_layer1 = self.split.graph.delete_edge_e(e['nodes_e']['IDs'], e['nodes_e']['IDf'])
            list_layer1 = self.split.graph.delete_all_incoming_edges_except_c_for_node(e['common'])
            '''list_layers = delete_edge_f(e['nodes_e']['IDf'], list_layer1, list_layer0)
            list_layer0 = list_layers[0]
            list_layer1 = list_layers[1]'''
            if e['common'] != None:
                id_new = self.split.graph.add_node_rule2(e['common'], '2')
                self.split.graph.add_edge(e['nodes_e']['IDf'], id_new)
                has_changed = True
        if has_changed == False:
            print("No changes")
            return 0
        else:
            self.split.graph.delete_all_isolated_nodes()
            self.createXML.set_list_layer0(self.split.graph.list_layer0)
            self.createXML.set_list_layer1(self.split.graph.list_layer1)
            self.createXML.create_graphs(file, destination_file, destination_graph, '2')
            # Parser.draw_graph(self.split.list_layer0, self.split.list_layer1, destination_file)
            return 1
