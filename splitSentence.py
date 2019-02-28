from builtins import list

import parseXML as parseXML
import os


def get_sentence(list_layer0):
    sentence = ""
    s = []
    for elem in list_layer0:
        sentence += elem['text']
        sentence += " "
        s.append(elem['text'])
    print(sentence)
    return s


# create sentence from a list of words
def create_sentence(list_words):
    sentence = ""
    for word in list_words:
        sentence += word
        sentence += " "

    return sentence


def get_all_sentences():
    directory = os.fsencode('Data')
    source_directory = 'Data/'
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        dict_layers = parseXML.extract_data(source_directory + filename)
        list_layer0 = dict_layers['Layer0']
        sentence = get_sentence(list_layer0)
        print(sentence)


# get the ID of the node which is the child node of an edge annotated with L
def get_idl(list_layer1):
    dict_l = {}
    list_l = []
    for elem in list_layer1:
        for e in elem['edge']:
            if e['type'] == 'L':
                dict_l = {}
                dict_l['IDs'] = elem['ID']
                dict_l['IDf'] = e['toID']
                list_l.append(dict_l)
    return list_l


# check if the node which is the children of an edge starting in nodeID is Terminal
def is_terminal(node_id, list_layer1):
    terminal = False
    for elem in list_layer1:
        if elem['ID'] == node_id:
            for e in elem['edge']:
                if e['type'] == 'Terminal':
                    terminal = True
    return terminal


def get_word(node_id, list_layer0):
    wordDict = {}
    for elem in list_layer0:
        if elem['ID'] == node_id:
            wordDict['text'] = elem['text']
            wordDict['pos'] = elem['pos']
            return wordDict


def get_child(node_id, listLayer1):
    for elem in listLayer1:
        if elem['ID'] == node_id:
            for e in elem['edge']:
                return e['toID']


# get the nodes which are the childrens of an edge starting in nodeID and
# annotated with H
def get_children_h_edge(node_id, listLayer1):
    list_h = []
    for elem in listLayer1:
        if elem['ID'] == node_id:
            for e in elem['edge']:
                if e['type'] == 'H':
                    list_h.append(e['toID'])
    return list_h


def get_children_a_edge(node_id, list_layer1):
    list_a = []
    for elem in list_layer1:
        if elem['ID'] == node_id:
            for e in elem['edge']:
                if e['type'] == 'A':
                    list_a.append(e['toID'])
    return list_a


# get list of childs for a node
def get_childs(node_id, list_layer1):
    list_childs = []
    for elem in list_layer1:
        if elem['ID'] == node_id:
            for e in elem['edge']:
                list_childs.append(e['toID'])
    return list_childs


def get_all_nodes_to_leaves(node_id, list_layer1):
    list_nodes = []
    child_list = get_childs(node_id, list_layer1)
    for child in child_list:
        list_nodes.append(child)
        if not is_terminal(child, list_layer1):
            list_nodes = list_nodes + get_all_nodes_to_leaves(child, list_layer1)

    return list_nodes


def get_common_elem(list, list_layer1):
    if list.__len__() == 0:
        return "None"
    common_items = set.intersection(*map(set, list))
    if common_items.__len__() == 0:
        # explore the subnodes of these nodes
        list2 = []
        for l in list:
            l1 = l
            for elem in l:
                l1 = l1 + get_all_nodes_to_leaves(elem, list_layer1)
            list2.append(l1)
        common_items = set.intersection(*map(set, list2))
        if common_items.__len__() == 0:
            return "None"
    return common_items.pop()


def save_split_version(prop, fragment, nr):
    title = fragment+'_'+str(nr)+'.txt'
    print(title)
    f = open(title, 'w')
    f.write(prop)
    f.close()


def split_rule1(file):
    # obtain the sentence from xml file
    dict_layers = parseXML.extract_data(file)
    list_layer0 = dict_layers['Layer0']
    list_layer1 = dict_layers['Layer1']
    # draw the corresponding graph
    parseXML.draw_graph(list_layer0, list_layer1, file)
    sentence = get_sentence(list_layer0)
    print(sentence)

    # get all linkers
    listL = get_idl(list_layer1)
    # print(listL)

    terminals_l = []
    # verify terminals
    # save the linkers which are terminals
    for l in listL:
        if is_terminal(l['IDf'], list_layer1):
            terminals_l.append(l)
    # print(terminals_l)

    # get the words corresponding to terminals an their position in the sentence
    words_linkers = []
    for tL in terminals_l:
        child = get_child(tL['IDf'], list_layer1)
        word = get_word(child, list_layer0)
        words_linkers.append(word)
    # print(words_linkers)

    # obtain the nodes which are the child of an edge starting from
    # the node where the linkers starts
    nodes_h = []
    for tL in terminals_l:
        dict_h = {}
        dict_h['IDs'] = tL['IDs']
        dict_h['listOfHNodes'] = get_children_h_edge(tL['IDs'], list_layer1)
        nodes_h.append(dict_h)
    # print("Nodes H", nodes_h)

    # obtain the node to which the nodes_h are linked through an A edge
    # coreference
    lists_of_nodes_a = []
    for nH in nodes_h:
        for nodeH in nH['listOfHNodes']:
            list_h = get_children_a_edge(nodeH, list_layer1)
            lists_of_nodes_a.append(list_h)

    print("Nodes A: ", lists_of_nodes_a)



    coref = get_common_elem(lists_of_nodes_a, list_layer1)
    if coref != "None":
        subject_id = get_child(coref, list_layer1)
        # print(subject_id)
        subject_word = get_word(subject_id, list_layer0)
        # print(subject_word)
        # print("coreference:", coref)

        # Split the sentence
        # print(" ")
        nr_prop = 0
        for wL in words_linkers:
            idx = int(wL['pos'])
            s_l = sentence[:idx-1]
            s = create_sentence(s_l)
            # print(s)
            save_split_version(s, file, nr_prop)
            nr_prop = nr_prop + 1
            sentence = sentence[idx:]
        last_sentence = create_sentence(sentence)
        last_sentence = subject_word['text'].capitalize() + " " + last_sentence
        # print(last_sentence)
        save_split_version(last_sentence, file, nr_prop)
    else:
        print("No linker found")


def main():
    # get_sentence('test.xml')
    # get_all_sentences()
    split_rule1('Data/673010.xml')


if __name__ == '__main__':
    main()