
class operation:

    @staticmethod
    def is_verb(elem):
        if elem[1][:2] == 'VB':
            if elem[1] == 'VBG':
                return False
            return True
        return False

    @staticmethod
    def is_noun(elem):
        if elem[1][:2] == 'NN':
            return True
        return False

    @staticmethod
    def is_pronoun(elem):
        if elem[1] == 'PRP':
            return True
        return False

    @staticmethod
    def get_consecutive_NN(list_elem):
        list_nns = []
        for elem in list_elem:
            if operation.is_noun(elem) or elem[1] == 'DT':
                list_nns.insert(0, elem)
            else:
                return list_nns
        return list_nns

    @staticmethod
    def get_position_point_comma(list_elem):
        current_pos = 0
        for elem in list_elem:
            if elem[0] == ',' or elem[1] == '.':
                return current_pos
            current_pos = current_pos + 1
        return -1

    @staticmethod
    def contains_verb(list_elem):
        for elem in list_elem:
            if operation.is_verb(elem):
                return True
        return False

    @staticmethod
    def get_subject_rule1(list_elem):
        pos_verb = -1
        pos_noun = -1
        pos_pronoun = -1
        current_pos = 0
        remaining_words = []
        for elem in reversed(list_elem):
            remaining_words.append(elem)
        for elem in reversed(list_elem):
            if pos_verb == -1:
                if operation.is_verb(elem):
                    pos_verb = current_pos

                    # check if this verb is correct (if we have a NN in the left)
                    pos_noun = -1
                    pos_pronoun = -1
                    current_pos1 = 0
                    for elem in reversed(list_elem):
                        if current_pos1 > current_pos:
                            if operation.is_pronoun(elem):
                                pos_pronoun = current_pos1
                                break
                            if operation.is_noun(elem):
                                pos_noun = current_pos1
                                break
                            if elem[1] != 'SYM' and not elem[1][0].isalpha() and not operation.is_verb(elem):
                                pos_verb = -1
                                break
                        current_pos1 = current_pos1 + 1
            current_pos = current_pos + 1
        subject = []
        if pos_pronoun != -1:
            subject.append(remaining_words[pos_pronoun])
        if pos_noun != -1:
            subject = operation.get_consecutive_NN(remaining_words[pos_noun:])
        return subject

    @staticmethod
    def generate_sentence(list_elem, point):
        sentence = ""
        i = 0
        for elem in list_elem:
            if i == 0:
                sentence = sentence + elem[0].capitalize() + " "
            else:
                sentence = sentence + elem[0] + " "
            i = i +1
        if point == True:
            sentence = sentence + "."
        return sentence
