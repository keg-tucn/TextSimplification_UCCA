
class Graph:
    def __init__(self, list_layer0, list_layer1, passageID, extra):
        self.list_layer0 = list_layer0
        self.list_layer1 = list_layer1
        self.passageID = passageID
        self.extra = extra

    # replace the word with id equal to actual_word_ID with new_word and set the position to 0 (first element in a sentence)
    def replace_word(self, actual_word_ID, new_word):
        for l0 in self.list_layer0:
            if l0['ID'] == actual_word_ID:
                l0['text'] = new_word.capitalize()
                # l0['pos'] = 0
        return self.list_layer0

    # delete H edges from node_start to all nodes in nodes_end
    def delete_edge_h(self, node_start, nodes_end):
        for ne in nodes_end:
            for l1 in self.list_layer1:
                if l1['ID'] == node_start:
                    list_new = []
                    for edge in l1['edge']:
                        if not (edge['toID'] == ne and edge['type'] == 'H'):
                            list_new.append(edge)
                    l1['edge'] = list_new
                    # l1['edge'] = [edge for edge in l1['edge'] if edge['toID'] !=ne or edge['type'] != 'H']
        return self.list_layer1

    # delete E edges from node_start to node_end
    def delete_edge_e(self, node_start, node_end):
        for l1 in self.list_layer1:
            if l1['ID'] == node_start:
                l1['edge'] = [edge for edge in l1['edge'] if edge['toID'] !=node_end or edge['type'] != 'E']
        return self.list_layer1

    # delete A edges from node_start to node_end
    def delete_edge_a(self, node_start, node_end):
        for l1 in self.list_layer1:
            if l1['ID'] == node_start:
                l1['edge'] = [edge for edge in l1['edge'] if edge['toID'] != node_end or edge['type'] != 'A']
        return self.list_layer1

    def delete_all_incoming_edges_for_node(self, node):
        for l1 in self.list_layer1:
            l1['edge'] = [edge for edge in l1['edge'] if edge['toID'] != node]
        return self.list_layer1

    def delete_all_incoming_edges_except_c_for_node(self, node):
        for l1 in self.list_layer1:
            l1['edge'] = [edge for edge in l1['edge'] if edge['toID'] != node or edge['type'] == 'C']
        return self.list_layer1

    def change_edge(self, node_start, node_end, new_target):
        no_change = False
        for l1 in self.list_layer1:
            if l1['ID'] == node_start:
                list_new = []
                first_elem = None
                for e in l1['edge']:
                    if e['toID'] == node_end:
                        first_elem = e
                        e['toID'] = new_target
                    else:
                        list_new.append(e)
                if first_elem != None:
                    list_new.insert(0, first_elem)
                else:
                    no_change = True
                l1['edge'] = list_new
        dict_result = {}
        dict_result['list'] = self.list_layer1
        dict_result['no_change'] = no_change
        return dict_result

    # delete all incoming edges which are annotated with LA or LR
    def delete_edge_la(self, node):
        for l1 in self.list_layer1:
            if l1['edge'] != None and l1['ID'] == node:
                l1['edge'] = [edge for edge in l1['edge'] if not (edge['type'] == 'LA' or edge['type'] == 'LR')]
        return self.list_layer1

    # delete edge f starting from node
    def delete_edge_f(self, node):
        id_f = None
        for l1 in self.list_layer1:
            if l1['ID'] == node:
                new_edge = []
                for edge in l1['edge']:
                    if edge['type'] != 'F':
                        new_edge.append(edge)
                    else:
                        id_f = edge['toID']
                l1['edge'] =  new_edge
        if id_f != None:
            list_nodes_to_leaves = self.get_all_nodes_to_leaves_inclusive(id_f)
            list_nodes_to_leaves.append(id_f)
            for n in list_nodes_to_leaves:
                if self.is_terminal(n):
                    list_layer0 = self.delete_node_layer0(n)
                else:
                    list_layer1 = self.delete_node_layer0(n)
        list_layers = []
        list_layers.append(self.list_layer0)
        list_layers.append(self.list_layer1)
        return list_layers

    # delete edge between node1 and node2
    def delete_edge(self, node1, node2):
        for elem in self.list_layer1:
            if elem['ID'] == node1:
                new_edge = []
                for edge in elem['edge']:
                    if edge['toID'] != node2:
                        new_edge.append(edge)
                elem['edge'] = new_edge
        return self.list_layer1

    # get the destination node for an edge R starting in node_start
    def get_id_final_edge_R(self, node_start):
        for l1 in self.list_layer1:
            if l1['ID'] == node_start:
                for e in l1['edge']:
                    if e['type'] == 'R':
                        return e['toID']

    # get the ids of the words for a phrase splitted in sentences
    def get_ids_words_for_sentences(self, words_linkers):
        list_ids = []
        nr_prop = 0
        prev_idx = 1
        for wL in words_linkers:
            idx = int(wL['pos'])
            list_ids_prop = []
            for i in range(prev_idx, idx):
                id = self.get_id_for_word(i)
                list_ids_prop.append(id)
            list_ids.append(list_ids_prop)
            prev_idx = idx
            nr_prop = nr_prop +1
        list_ids_prop = []
        for i in range (prev_idx, self.list_layer0.__len__()+1):
            id = self.get_id_for_word(i)
            list_ids_prop.append(id)
        list_ids.append(list_ids_prop)
        return list_ids

    # get all nodes to the root
    def get_nodes_to_the_root(self, node_id):
        list_nodes = []
        parents = self.get_parents(node_id)
        for p in parents:
            list_nodes.append(p)
            list_nodes = list_nodes + list(set(self.get_nodes_to_the_root(p)) - set(list_nodes))
        return list_nodes

    # get the list with common elements for all sentences
    def get_commons_elements_sentences(self, list_ids_sentences):
        return set.intersection(*map(set, list_ids_sentences))

    # get the list with the ids for every sentence
    def get_ids_nodes_sentences(self, lists_ids, words_linkers):
        # print(lists_ids)
        list_ids_sentences = []
        for l in lists_ids:
            list_parents_sentence = []
            for elem in l:
                list_parents = self.get_nodes_to_the_root(elem)
                # print(elem, " -> ", list_parents)
                list_parents_sentence = list_parents_sentence + list(set(list_parents) - set(list_parents_sentence))
            # print("Sentence: ")
            # print(list_parents_sentence)
            list_ids_sentences.append(list_parents_sentence)
        return list_ids_sentences

    # delete edges between two lists
    def delete_edges_two_lists(self, list1, list2):
        for e1 in list1:
            for e2 in list2:
                list_layer1 = self.delete_edge(e1, e2)
        return self.list_layer1

    def delete_back_edges(self, words_linkers):
        lists_ids = self.get_ids_words_for_sentences(words_linkers)
        list_ids_sentences = self.get_ids_nodes_sentences(lists_ids, words_linkers)
        list_commons = self.get_commons_elements_sentences(list_ids_sentences)
        list_ids_reversed = list(reversed(list(list_ids_sentences)))
        for i in range(0, list_ids_reversed.__len__()-1):
            list_2 = list(set(list_ids_reversed[i+1]) - set(list_commons))
            list_layer1 = self.delete_edges_two_lists(list_commons, list_2)
        return self.list_layer1

    def add_node_rule2(self, id_common, rule):
        list_subnodes = self.get_all_nodes_to_leaves_inclusive(id_common)
        list_subnodes.append(id_common)
        old_new_id0 = []
        old_new_id1 = []
        # create a copy for all subnodes
        for subnode in list_subnodes:
            if self.is_terminal(subnode):
                max_id0 = self.get_id_max_layer0()
                new_id0 = max_id0 + '1'
                old_new_dict0 = {}
                old_new_dict0['old'] = subnode
                old_new_dict0['new'] = new_id0
                old_new_id0.append(old_new_dict0)
                subnode_dict0 = self.get_word(subnode)
                self.add_node_layer0(new_id0, subnode_dict0)
            else:
                max_id1 = self.get_id_max_layer1()
                new_id1 = max_id1 + '1'
                old_new_dict1 = {}
                old_new_dict1['old'] = subnode
                old_new_dict1['new'] = new_id1
                old_new_id1.append(old_new_dict1)
                subnode_dict1 = self.get_node(subnode)
                self.add_node_layer1(new_id1, subnode_dict1)
        # change all edges
        for id in old_new_id1:
            for elem in self.list_layer1:
                if elem['ID'] == id['new']:
                    for edge in elem['edge']:
                        new_id = None
                        if self.is_terminal(edge['toID']):
                            new_id = self.get_new_id(edge['toID'], old_new_id0)
                        else:
                            new_id = self.get_new_id(edge['toID'], old_new_id1)
                        edge['toID'] = new_id
        new_id_common = self.get_new_id(id_common, old_new_id1)
        return new_id_common

    def add_edge(self, node1, node2):
        for elem in self.list_layer1:
            if elem['ID'] == node1:
                model = elem['edge'][0].copy()
                model['toID'] = node2
                model['type'] = 'A'
                model['remote'] = None
                elem['edge'].append(model)

    def get_sentence(self):
        sentence = ""
        s = []
        for elem in self.list_layer0:
            sentence += elem['text']
            sentence += " "
            s.append(elem['text'])
        # print(sentence)
        return s

    # get the max id from layer0
    def get_id_max_layer0(self):
        max_id = self.list_layer0[0]['ID']
        for elem in self.list_layer0:
            if elem['ID'] > max_id:
                max_id = elem['ID']
        return max_id

    # get the max id from layer1
    def get_id_max_layer1(self):
        max_id = self.list_layer1[0]['ID']
        for elem in self.list_layer1:
            if elem['ID'] > max_id:
                max_id = elem['ID']
        return max_id

    def add_node_layer0(self, node_id, model):
        wordDict = model.copy()
        wordDict['ID'] = node_id
        self.list_layer0.append(wordDict)

    def add_node_layer1(self, node_id, model):
        node_dict = {}
        node_dict['ID'] = node_id
        node_dict['type'] = model['type']
        node_dict['edge'] = []
        for e in model['edge']:
            new_edge = {}
            new_edge['toID'] = e['toID']
            new_edge['type'] = e['type']
            new_edge['remote'] = e['remote']
            node_dict['edge'].append(new_edge)
        self.list_layer1.append(node_dict)

    def delete_node_layer0(self, node_id):
        new_list_layer0 = []
        for elem in self.list_layer0:
            if elem['ID'] != node_id:
                new_list_layer0.append(elem)
        self.list_layer0 = new_list_layer0
        for elem1 in self.list_layer1:
            new_edge_list = []
            for edge in elem1['edge']:
                if edge['toID'] != node_id:
                    new_edge_list.append(edge)
            elem1['edge'] = new_edge_list
        return new_list_layer0

    def delete_node_layer1(self, node_id):
        new_list_layer1 = []
        for elem in self.list_layer1:
            if elem['ID'] != node_id:
                new_list_layer1.append(elem)
        self.list_layer1 = new_list_layer1
        return new_list_layer1

    # get the ID of the node which is the child node of an edge annotated with L
    def get_id_edge_l(self):
        list_l = []
        for elem in self.list_layer1:
            for e in elem['edge']:
                if e['type'] == 'L':
                    dict_l = {}
                    dict_l['IDs'] = elem['ID']
                    dict_l['IDf'] = e['toID']
                    list_l.append(dict_l)
        return list_l

    # get the ID of the node which is the child node of an edge annotated with E
    def get_id_edge_e(self):
        list_e = []
        for elem in self.list_layer1:
            for e in elem['edge']:
                if e['type'] == 'E':
                    dict_e = {}
                    dict_e['IDs'] = elem['ID']
                    dict_e['IDf'] = e['toID']
                    list_e.append(dict_e)
        return list_e

    # check if the node which is the children of an edge starting in nodeID is Terminal
    def is_parent_for_terminal(self, node_id):
        terminal = False
        nr = 0
        for elem in self.list_layer1:
            if elem['ID'] == node_id:
                for e in elem['edge']:
                    nr += 1
                    if e['type'] == 'Terminal' and elem['edge'].__len__() == 1:
                        terminal = True
        if nr == 1:
            return terminal
        else:
            return False

    # returns true if node_id is terminal
    def is_terminal(self, node_id):
        for elem in self.list_layer0:
            if elem['ID'] == node_id:
                return True
        return False

    # get an element from layer0 with id equals to node_id
    def get_word(self, node_id):
        for elem in self.list_layer0:
            if elem['ID'] == node_id:
                return elem
        return None

    # get an element from layer1 with id equals to node_id
    def get_node(self, node_id):
        for elem in self.list_layer1:
            if elem['ID'] == node_id:
                return elem
        return None

    def get_child(self, node_id):
        for elem in self.list_layer1:
            if elem['ID'] == node_id:
                for e in elem['edge']:
                    return e['toID']
        return None

    # get the nodes which are the childrens of an edge starting in nodeID and
    # annotated with H
    def get_children_h_edge(self, node_id):
        list_h = []
        for elem in self.list_layer1:
            if elem['ID'] == node_id:
                for e in elem['edge']:
                    if e['type'] == 'H':
                        list_h.append(e['toID'])
        return list_h

    def get_children_a_edge(self, node_id):
        list_a = []
        for elem in self.list_layer1:
            if elem['ID'] == node_id:
                for e in elem['edge']:
                    if e['type'] == 'A':
                        list_a.append(e['toID'])
        return list_a

    # get list of childs for a node
    def get_childs(self, node_id):
        list_childs = []
        for elem in self.list_layer1:
            if elem['ID'] == node_id:
                for e in elem['edge']:
                    list_childs.append(e['toID'])
        return list_childs

    # get list of labels for childs
    def get_childs_labels(self, node_id):
        list_childs_labels = []
        for elem in self.list_layer1:
            if elem['ID'] == node_id:
                for e in elem['edge']:
                    dictElem = {}
                    dictElem['type'] = e['type']
                    dictElem['ID'] = e['toID']
                    list_childs_labels.append(dictElem)
        return list_childs_labels

    # get all labels for nodes to leaves
    def get_all_labels_to_leaves(self, node_id):
        list_labels = []
        child_label_list = self.get_childs_labels(node_id)
        for child in child_label_list:
            list_labels.append(child)
            if not self.is_parent_for_terminal(child['ID']):
                list_labels = list_labels + self.get_all_labels_to_leaves(child['ID'])
        return list_labels

    def get_all_nodes_to_leaves(self, node_id):
        list_nodes = []
        child_list = self.get_childs(node_id)
        for child in child_list:
            list_nodes.append(child)
            if not self.is_parent_for_terminal(child):
                list_nodes = list_nodes + self.get_all_nodes_to_leaves(child)
        return list_nodes

    # get all nodes to leaves including leaves
    def get_all_nodes_to_leaves_inclusive(self, node_id):
        list_nodes = []
        child_list = self.get_childs(node_id)
        for child in child_list:
            list_nodes.append(child)
            if not self.is_terminal(child):
                list_nodes = list_nodes + self.get_all_nodes_to_leaves_inclusive(child)
        return list_nodes

    # get the ID of a word with position pos
    def get_id_for_word(self, pos):
        for elem in self.list_layer0:
            if int(elem['pos']) == pos:
                return elem['ID']
        return None

    # get parent for a node
    def get_parents(self, node_id):
        parents = []
        for elem in self.list_layer1:
            for edge in elem['edge']:
                if edge['toID'] == node_id:
                    parents.append(elem['ID'])
        return parents

    # chech if there is a verb in subtree for node_id
    def check_verb(self, node_id):
        list_labels = self.get_all_labels_to_leaves(node_id)
        for label in list_labels:
            if label['type'] == 'P' or label['type'] == 'S':
                child = self.get_child(label['ID'])
                if child != None:
                    return True
                else:
                    return False
        return False

    # get the new_id for node_id
    def get_new_id(self, node_id, dict):
        for elem in dict:
            if elem['old'] == node_id:
                return elem['new']
        return None

    # check if edge between node1 and node2 exists
    def edge_exist(self, node1, node2):
        for elem in self.list_layer1:
            if elem['ID'] == node1:
                for edge in elem['edge']:
                    if edge['toID'] == node2:
                        return True
        return False

    # find the node from list_nodes to which exists an edge from node_id
    def find_edge(self, node_id, list_nodes):
        for n in list_nodes:
            if self.edge_exist(node_id, n):
                return n
        return None

    # get the in-degree of a node
    def get_in_degree(self, node):
        degree = 0
        for l in self.list_layer1:
            if l['edge'] != None:
                for edge in l['edge']:
                    if edge['toID'] == node:
                        degree = degree + 1
        return degree

    # get the out-degree of a node
    def get_out_degree(self, node):
        degree = 0
        for l in self.list_layer1:
            if l['ID'] == node:
                degree = l['edge'].__len__()
                break
        return degree

    # delete all isolated nodes
    def delete_all_isolated_nodes(self):
        for l in self.list_layer1:
            in_degree = self.get_in_degree(l['ID'])
            out_degree = self.get_out_degree(l['ID'])
            if in_degree == 0 and out_degree == 0:
                self.delete_node_layer1(l['ID'])

    # get the neighbours of a node
    def get_neighbours(self, node):
        neighbours = []
        for l in self.list_layer1:
            if l['ID'] == node:
                if l['edge'] != None:
                    for edge in l['edge']:
                        neighbours.append(edge['toID'])
            else:
                if l['edge'] != None:
                    for e in l['edge']:
                        if e['toID'] == node:
                            neighbours.append(l['ID'])
                            break
        return neighbours

    # DFS
    def dfs(self, start, visited, neighbours):
        if start not in visited:
            visited.append(start)
            for n in neighbours:
                if n['node'] == start:
                    for v in n['neighbours']:
                        self.dfs(v, visited, neighbours)
        return visited

    # get the type for outcoming edges of a given node
    def get_type_edges(self, node, list_layer1):
        list_of_types = []
        for l1 in list_layer1:
            if l1 != None:
                if l1['ID'] == node:
                    for edge in l1['edge']:
                        list_of_types.append(edge['type'])
        return list_of_types
