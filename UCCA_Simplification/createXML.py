import xml.etree.ElementTree as ET
from UCCA_Simplification.Service import Sentence


class CreateXML:

    def __init__(self, list_layer0, list_layer1, graph, parser):
        self.list_layer1 = list_layer1
        self.list_layer0 = list_layer0
        self.graph = graph
        self.parser = parser
        self.graphs_nodes = []

    def set_list_layer0(self, list_layer0):
        self.list_layer0 = list_layer0

    def set_list_layer1(self, list_layer1):
        self.list_layer1 = list_layer1

    # extract the graphs (connected components)
    def extract_graphs(self):
        # get the neighbours lists
        neighbours = []
        for l in self.list_layer1:
            neigh = self.graph.get_neighbours(l['ID'])
            dict = {}
            dict['node'] = l['ID']
            dict['neighbours'] = neigh
            neighbours.append(dict)
        for l in self.list_layer0:
            dict = {}
            dict['node'] = l['ID']
            dict['neighbours'] = []
            neighbours.append(dict)
        visited = []
        for n in neighbours:
            if n['node'] not in visited:
                subgraph = self.graph.dfs(n['node'], [], neighbours)
                visited = visited + subgraph
                self.graphs_nodes.append(subgraph)
        if self.graphs_nodes.__len__() < 2:
            return False
        else:
            for g in self.graphs_nodes:
                if g.__len__() < 3:
                    return False
        return True

    # create list_layer0 and list_layer1 for new graphs
    def create_layers_lists_for_graphs(self):
        list_layers = []
        for list in self.graphs_nodes:
            list_layer0 = []
            list_layer1 = []
            for node in list:
                if float(node) < 1.0:
                    list_layer0.append(node)
                else:
                    list_layer1.append(node)
            dict = {}
            dict['list_layer0'] = list_layer0
            dict['list_layer1'] = list_layer1
            list_layers.append(dict)
        return list_layers

    # Indent the xml file
    def indent(self, elem, level=0):
        i = "\n" + level * "  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
                self.indent(elem, level + 1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i

    def sort_pos(self, e):
        return int(e['pos'])

    def sort_id(self, e):
        if e != None:
            return e['ID']
        return '10'

    # update the position of words in the new sentence
    def update_position(self, list_layer0):
        list_layer0.sort(key=self.sort_pos)
        pos = 1
        for l in list_layer0:
            l['pos'] = str(pos)
            pos = pos + 1
        return list_layer0

    # get the new id for a given id
    def get_new(self, dict, id):
        for d in dict:
            if d['old'] == id:
                return d['new']
        return None

    # update the id for terminal nodes
    def update_id0(self, indice, list_layer0, list_layer1, rule):
        list_layer0.sort(key=self.sort_id)
        old_new = []
        ind = 1
        for l0 in list_layer0:
            if l0 != None:
                dict_old_new = {}
                dict_old_new['old'] = l0['ID']
                new_id = float('0.'+str(ind))
                # dict_old_new['new'] = str(float("{0:.2f}".format(new_id)))
                dict_old_new['new'] = '0.'+str(ind)
                old_new.append(dict_old_new)
                l0['ID'] = '0.'+str(ind)
                ind = ind + 1
        for l1 in list_layer1:
            if l1 != None:
                for e in l1['edge']:
                    id_new = self.get_new(old_new, e['toID'])
                    if id_new != None:
                        e['toID'] = id_new
        dict_layers = {}
        dict_layers['layer0'] = list_layer0
        dict_layers['layer1'] = list_layer1
        return dict_layers

    # update the id for nodes in layer1
    def update_id1(self, list_layer1):
        id_max = self.graph.get_id_max_layer1()
        old_new = []
        ind = 1
        for l1 in list_layer1:
            if l1 != None:
                dict_old_new = {}
                dict_old_new['old'] = l1['ID']
                dict_old_new['new'] = '1.' + str(ind)
                old_new.append(dict_old_new)
                l1['ID'] = '1.' + str(ind)
                ind = ind + 1
        for l1 in list_layer1:
            if l1 != None:
                for e in l1['edge']:
                    id_new = self.get_new(old_new, e['toID'])
                    if id_new != None:
                        e['toID'] = id_new
        if Sentence.check_list_LHU(self.graph.get_type_edges('1.1', list_layer1)) == False:
            old_new = []
            ind = 11
            for l1 in list_layer1:
                if l1 != None:
                    dict_old_new = {}
                    dict_old_new['old'] = l1['ID']
                    dict_old_new['new'] = '1.' + str(ind)
                    old_new.append(dict_old_new)
                    l1['ID'] = '1.' + str(ind)
                    ind = ind + 1
            for l1 in list_layer1:
                if l1 != None:
                    for e in l1['edge']:
                        id_new = self.get_new(old_new, e['toID'])
                        if id_new != None:
                            e['toID'] = id_new
            # add root 1.1
            node = {}
            id_new_root = 1.1
            node['ID'] = str(float("{0:.2f}".format(id_new_root)))
            node['type'] = 'FN'
            edge = {}
            old_root = Sentence.get_elem_id(list_layer1, '1.11')
            edge['toID'] = old_root['ID']
            edge['type'] = 'H'
            edge['remote'] = None
            list_edges = []
            list_edges.append(edge)
            node['edge'] = list_edges
            list_layer1.append(node)
            list_layer1.sort(key=self.sort_id)
        return list_layer1

    # create xml file
    def create_xml(self, ind, source_file, destination_directory_data, list_layer0, list_layer1, rule):
        source = source_file.split('.')
        dest_file = destination_directory_data + source[0] + "_" + str(ind) + '.xml'

        root = ET.Element("root")
        root.set("annotationID", "0")
        root.set("passageID", self.graph.passageID + str(ind))
        ET.SubElement(root, "attributes")

        # layer 0
        layer0 = ET.SubElement(root, "layer")
        layer0.set("layerID", "0")
        ET.SubElement(layer0, "attributes")
        extra_layer0 = ET.SubElement(layer0, "extra")
        extra_layer0.set("doc", self.graph.extra)

        list_layer0 = self.update_position(list_layer0)

        dict_layers = self.update_id0(ind, list_layer0, list_layer1, rule)
        list_layer0 = dict_layers['layer0']
        list_layer1 = dict_layers['layer1']

        list_layer1 = self.update_id1(list_layer1)

        for l0 in list_layer0:
            if l0 != None:
                node = ET.SubElement(layer0, "node")
                node.set("ID", l0['ID'])
                node.set("type", l0['type'])

                attr = ET.SubElement(node, "attributes")
                attr.set("paragraph", l0['paragraph'])
                attr.set("paragraph_position", l0['pos'])
                attr.set("text", l0['text'])

                extra = ET.SubElement(node, "extra")
                extra.set("dep", l0['dep'])
                extra.set("ent_iob", l0['ent_iob'])
                extra.set("ent_type", l0['ent_type'])
                extra.set("head", l0['head'])
                extra.set("lemma", l0['lemma'])
                extra.set("orig_paragraph", l0['orig_paragraph'])
                extra.set("orth", l0['orth'])
                extra.set("pos", l0['position'])
                extra.set("prefix", l0['prefix'])
                extra.set("shape", l0['shape'])
                extra.set("suffix", l0['suffix'])
                extra.set("tag", l0['tag'])

        # layer 1
        layer1 = ET.SubElement(root, "layer")
        layer1.set("layerID", "1")
        ET.SubElement(layer1, "attributes")

        for l1 in list_layer1:
            if l1 != None:
                node1 = ET.SubElement(layer1, "node")
                node1.set("ID", l1['ID'])
                node1.set("type", l1['type'])
                ET.SubElement(node1, "attributes")
                for edge in l1['edge']:
                    e = ET.SubElement(node1, "edge")
                    e.set("toID", edge['toID'])
                    e.set("type", edge['type'])
                    att = ET.SubElement(e, "attributes")
                    if edge['remote'] != None:
                        att.set("remote", edge['remote'])
        self.indent(root)
        tree = ET.ElementTree(root)
        # if ind == 1:
            # copyfile("./" + destination_directory_data + source_file, "./" + "Evaluation/Rules_nesimplificate/" + source_file)
            # os.remove("./" + destination_directory_data + source_file)

        tree.write(dest_file, xml_declaration=False, encoding='utf-8', method="xml")
        dict_return = {}
        dict_return['layer0'] = list_layer0
        dict_return['layer1'] = list_layer1
        dict_return['file'] = dest_file
        return dict_return

    # draw the resulting graph
    def draw_graph(self, ind, source_file, destination_directory_graph):
        source = source_file.split('/')
        source = source[source.__len__() - 1]
        source = source.split('.')
        dest_file = destination_directory_graph + source[0]
        # draw graph
        dict_layers = self.parser.extract_data(source_file)
        self.parser.draw_graph(dict_layers['Layer0'], dict_layers['Layer1'], dest_file)


    # generate XML files
    def create_graphs(self, source_file, destination_directory_data, destination_directory_graphs, rule):
        if self.extract_graphs():
            list_layers = self.create_layers_lists_for_graphs()
            for g in list_layers:
                list_layer0_new = []
                for l0 in g['list_layer0']:
                    node = self.graph.get_word(l0)
                    list_layer0_new.append(node)
                g['list_layer0'] = list_layer0_new
                list_layer1_new = []
                for l1 in g['list_layer1']:
                    node1 = self.graph.get_node(l1)
                    list_layer1_new.append(node1)
                g['list_layer1'] = list_layer1_new

            for g in list_layers:
                if g['list_layer0'].__len__() < 3:
                    return
            for g in list_layers:
                nr_s_p = 0
                for l1 in g['list_layer1']:
                    if l1 != None:
                        for edge in l1['edge']:
                            if edge['type'] == 'S' or edge['type'] == 'P':
                                nr_s_p = nr_s_p + 1
                if nr_s_p == 0:
                    return
            # create files
            ind = 1
            for g in list_layers:
                dict_return = self.create_xml(ind, source_file, destination_directory_data, g['list_layer0'], g['list_layer1'], rule)
                self.draw_graph(ind, dict_return['file'], destination_directory_graphs)
                ind = ind + 1
