from PoS_Simplification.operations import operation
from PoS_Simplification.extractInfo import ExtractInfo
import os
import sys


class Rule2:

    @staticmethod
    def split_rule2_once(sentences):
        result = []
        for sentence in sentences:
            pos_WP = -1
            current_pos = 0
            for w in sentence:
                if w[1] == 'WP':
                    pos_WP = current_pos
                    break
                current_pos = current_pos + 1
            # if we found a WP word
            if pos_WP != -1 and pos_WP != 0:
                elem_before = sentence[pos_WP-1]
                sentence_before_comma = sentence[:pos_WP-1]
                # check if the elem_before is comma (,)
                if elem_before[0] == ',' and operation.is_noun(sentence[pos_WP-2]):
                    subject_list = []
                    for we in sentence[:pos_WP-1]:
                        subject_list.insert(0,we)
                    subject = operation.get_consecutive_NN(subject_list)
                    # get the position for the next comma or for the next point
                    pos_comma = operation.get_position_point_comma(sentence[pos_WP:])
                    # get the sentence after the comma or point
                    # if the sentence is empty or contains a verb after the comma
                    sentence_after_comma = sentence[pos_WP:][pos_comma+1:]
                    if sentence_after_comma.__len__() == 0 or operation.contains_verb(sentence_after_comma):
                        first_sentence = sentence_before_comma + sentence_after_comma
                        second_sentence = subject + sentence[pos_WP+1:][:pos_comma]
                        result.append(first_sentence)
                        result.append(second_sentence)
        return result

    @staticmethod
    def execute_rule2(file, destination_directory):
        source = file.split('/')
        source = source[source.__len__() - 1]
        source = source.split('.')
        dest_file = destination_directory + source[0]
        sentences = ExtractInfo.extract_part_of_speech(file)
        nr = 0
        for sentence in sentences:
            result = Rule2.split_rule2_once(sentences)
            if result.__len__() != 0:
                nr = nr + 1
                ind = 0
                nr_sentences = result.__len__()
                # os.remove(file)
                for s in result:
                    if ind < nr_sentences-1:
                        sentence_txt = operation.generate_sentence(s, True)
                    else:
                        sentence_txt = operation.generate_sentence(s, False)
                    with open(dest_file + '_' + str(ind) + '.txt', "w", encoding="utf8") as file:
                        file.write(sentence_txt)
                    ind = ind + 1
            else:
                sentence_txt = operation.generate_sentence(sentence)
                with open(dest_file + '.txt', "w", encoding="utf8") as file:
                    file.write(sentence_txt)
        if nr != 0:
            return True
        return False

    @staticmethod
    def execute_rule2_forall(source_directory, destination_directory):
        no_sentences_splitted = 0
        no_sentences = 0
        directory = os.fsencode(source_directory)
        for file in os.listdir(directory):
            filename = os.fsdecode(file)
            print(filename)
            is_splitted = Rule2.execute_rule2(source_directory + '/' + filename, destination_directory)
            if is_splitted:
                no_sentences_splitted += 1
            no_sentences += 1
        print("No of sentences = ", no_sentences)
        print("No of sentences splitted Rule 2 = ", no_sentences_splitted)

    @staticmethod
    def main():
        # Rule2.execute_rule2_forall('Result/Rule1', 'Result/Rule2/')
        simplified = Rule2.execute_rule2(sys.argv[1], './')
        if simplified == True:
            print("The sentence was successfully simplified using WP Rule.")
        else:
            print("The sentence can not be simplified using WP Rule.")


if __name__ == '__main__':
    Rule2.main()
