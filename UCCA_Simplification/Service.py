

class CommonElement:

    @staticmethod
    def get_common_elem(list):
        nr_elem = list.__len__()
        for i in range(0, nr_elem - 1):
            list_proviz = []
            list_proviz.append(list[i])
            list_proviz.append(list[i + 1])
            common_item = set.intersection(*map(set, list_proviz))
            if common_item.__len__() != 0:
                return common_item
        return []

    @staticmethod
    def get_common_elem_for_rule1(graph, list, list_layer1):
        if list.__len__() == 0:
            return "None"
        common_items = CommonElement.get_common_elem(list)
        if common_items.__len__() == 0:
            # explore the subnodes of these nodes
            list2 = []
            for l in list:
                l1 = l
                for elem in l:
                    l1 = l1 + graph.get_all_nodes_to_leaves(elem)
                list2.append(l1)
            common_items = set.intersection(*map(set, list2))
            if common_items.__len__() == 0:
                return "None"
        return common_items.pop()

    @staticmethod
    def get_common_elem_for_rule2(graph, node1, node2, list_layer1, list_layer0):
        ch1 = graph.get_childs(node1)
        ch2 = graph.get_childs(node2)
        l = []
        l.append(ch1)
        l.append(ch2)
        common_items = set.intersection(*map(set, l))
        if common_items.__len__() == 0:
            return "None"
        return common_items.pop()


class Sentence:
    # create sentence from a list of words
    @staticmethod
    def create_sentence(list_words, capital, dot):
        sentence = ""
        if list_words.__len__() != 0:
            if capital:
                list_words[0] = list_words[0].capitalize()
            if list_words[-1] == ",":
                list_words[-1] = "."
                dot = False
            for word in list_words:
                sentence += word
                sentence += " "
            if dot == True:
                sentence += "."
        return sentence

    # check if a list of strings contains other strings than L,H,U
    @staticmethod
    def check_list_LHU(list_strings):
        for l in list_strings:
            if l != 'L' and l != 'H' and l != 'U':
                return False
        return True

    # return the element of a list
    @staticmethod
    def get_elem_id(list_layer1, id):
        for l in list_layer1:
            if l != None:
                if l['ID'] == id:
                    return l
        return None
