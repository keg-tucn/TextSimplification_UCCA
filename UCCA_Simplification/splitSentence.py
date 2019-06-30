from UCCA_Simplification.processGraph import Graph
from UCCA_Simplification.Service import CommonElement
from UCCA_Simplification.Service import Sentence


class Split:

    def __init__(self, parser, source_file):
        self.parser = parser
        dict_layers = self.parser.extract_data(source_file)
        self.list_layer0 = dict_layers['Layer0']
        self.list_layer1 = dict_layers['Layer1']
        self.passageID = dict_layers['passageID']
        self.extra = dict_layers['extra']
        self.graph = Graph(self.list_layer0, self.list_layer1, self.passageID, self.extra)

    @staticmethod
    def save_split_version(prop, fragment, nr):
        title = fragment+'_'+str(nr)+'.txt'
        f = open(title, 'w')
        f.write(prop)
        f.close()

    @staticmethod
    def split_rule1_text(words_linkers, sentence, subject_word):
        nr_prop = 0
        for wL in words_linkers:
            idx = int(wL['pos'])
            s_l = sentence[:idx - 1]
            s = Sentence.create_sentence(s_l, True, True)
            print(s)
            # save_split_version(s, source_file, nr_prop)
            nr_prop = nr_prop + 1
            sentence = sentence[idx:]
        last_sentence = Sentence.create_sentence(sentence, False, False)
        last_sentence = subject_word['text'].capitalize() + " " + last_sentence
        print(last_sentence)

    @staticmethod
    def split_rule2_text(list_correct_e, sentence):
        nr_prop = 0
        for w_e in list_correct_e:
            idx = int(w_e['common']['word']['pos'])
            s_e = sentence[:idx]
            s = Sentence.create_sentence(s_e, True, True)
            print(s)
            # save_split_version(s, source_file, nr_prop)
            nr_prop = nr_prop + 1
            sentence = sentence[idx + 1:]
        last_sentence = Sentence.create_sentence(sentence, False, False)
        last_sentence = w_e['common']['word']['text'].capitalize() + " " + last_sentence
        print(last_sentence)

    def split_rule1_new(self, source_file, destination_file_graph, destination_directory_data):
        nr_splitted = 0
        # get all linkers
        linkers = self.graph.get_id_edge_l()

        terminals_l = []

        # verify terminals
        # save the linkers which are terminals
        for l in linkers:
            if self.graph.is_parent_for_terminal(l['IDf']):
                terminals_l.append(l)

        words_linkers = []
        for tL in terminals_l:
            child = self.graph.get_child(tL['IDf'])
            word = self.graph.get_word(child)
            # If the linker is "at", "after" .... the sentence can not be splitted
            if word['text'].lower() == 'at' or word['text'].lower() == 'after' or word['text'].lower() == 'as' or word['text'].lower() == 'by':
                continue
            word['parent'] = tL['IDf']
            # h nodes
            dicth = {}
            dicth['list'] = self.graph.get_children_h_edge(tL['IDs'])
            if dicth['list'].__len__() < 2:
                continue
            dicth['parent'] = tL['IDs']
            word['hnodes'] = dicth
            # A nodes
            lists_of_nodes_a = []
            for h in dicth['list']:
                list_h = self.graph.get_children_a_edge(h)
                lists_of_nodes_a.append(list_h)
            word['list_of_nodes_a'] = lists_of_nodes_a
            coref = CommonElement.get_common_elem_for_rule1(self.graph, lists_of_nodes_a, self.list_layer1)
            if coref != "None":
                word['common'] = coref
                words_linkers.append(word)
        nr_splitted += self.parser.split_xml_file_rule1_new(source_file, destination_file_graph, destination_directory_data, words_linkers, self.list_layer0, self.list_layer1)
        if nr_splitted == 0:
            return False
        # Split the sentence
        # split_rule1_text(words_linkers, sentence, subject_word)
        return True


    def split_rule2(self, file, source_file, destination_graphs, destination_file):
        nr_splitted = 0
        # obtain the sentence from xml source_file
        dict_layers = self.parser.extract_data(source_file)
        list_layer0 = dict_layers['Layer0']
        list_layer1 = dict_layers['Layer1']
        sentence = self.graph.get_sentence()

        # get all Elaborators
        list_E = self.graph.get_id_edge_e()

        not_terminals_e = []
        # verify terminals
        # save the elaborators which are not terminals
        for e in list_E:
            if not self.graph.is_parent_for_terminal(e['IDf']):
                not_terminals_e.append(e)

        list_correct_e = []
        for elem in not_terminals_e:
            common = CommonElement.get_common_elem_for_rule2(self.graph, elem['IDs'], elem['IDf'], list_layer1, list_layer0)
            if common != "None":
                com_elem_e = {}
                com_elem_e['nodes_e'] = elem
                com_elem_e['common'] = common
                list_correct_e.append(com_elem_e)

        # verify verb
        # save the elaborators for which there is a verb in the subtree for IDf
        list_elaborators = []
        for e in list_correct_e:
            if self.graph.check_verb(e['nodes_e']['IDf']):
                list_elaborators.append(e)

        if list_elaborators.__len__() != 0:
            # Split the sentence
            nr_splitted += self.parser.split_xml_file_rule2(file, source_file, destination_graphs, destination_file, list_layer0, list_layer1, list_elaborators)
        if nr_splitted == 0:
            return False
        # split_rule2_text(list_correct_e, sentence)
        return True

