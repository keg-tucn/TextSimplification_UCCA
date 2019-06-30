from PoS_Simplification.operations import operation
from PoS_Simplification.extractInfo import ExtractInfo
import os
import sys


class Rule1:

    @staticmethod
    def split_rule1_once(sentence):
        result = []
        pos_cc = -1
        current_elem = 0
        for elem in sentence:
            if elem[1] == 'CC' and elem[0] == 'and':
                pos_cc = current_elem
                break
            current_elem = current_elem + 1
        if pos_cc != -1:
            # split the sentence in 2 sentences
            first_sentence = sentence[:pos_cc]
            second_sentence = sentence[pos_cc + 1:]
            # check if both sentences contains at least one verb
            if operation.contains_verb(first_sentence) and operation.contains_verb(second_sentence):
                # check if the word after the CC is verb
                if operation.is_verb(sentence[pos_cc + 1]):
                    # find the subject for the second sentence
                    subject = operation.get_subject_rule1(first_sentence)
                    if subject.__len__() != 0:
                        second_sentence_new = subject + second_sentence
                        result.append(first_sentence)
                        result.append(second_sentence_new)
        return result

    @staticmethod
    def split_rule1(sentence):
        result = []
        new_sentences = Rule1.split_rule1_once(sentence)
        if new_sentences.__len__() != 0:
            result.append(new_sentences[0])
            result = result + Rule1.split_rule1(new_sentences[1])
        else:
            result.append(sentence)
        return result

    @staticmethod
    def execute_rule1(file, destination_directory):
        source = file.split('/')
        source = source[source.__len__() - 1]
        source = source.split('.')
        dest_file = destination_directory + source[0]
        sentences = ExtractInfo.extract_part_of_speech(file)
        # print(sentences)
        nr = 0
        for sentence in sentences:
            result = Rule1.split_rule1(sentence)
            if result.__len__() != 1:
                nr = nr + 1
                ind = 0
                nr_sentences = result.__len__()
                for s in result:
                    if ind < nr_sentences - 1:
                        sentence_txt = operation.generate_sentence(s, True)
                    else:
                        sentence_txt = operation.generate_sentence(s, False)
                    with open(dest_file + '_' + str(ind) + '.txt', "w", encoding="utf8") as file:
                        file.write(sentence_txt)
                    ind = ind + 1
            else:
                sentence_txt = operation.generate_sentence(result[0])
                with open(dest_file + '.txt', "w", encoding="utf8") as file:
                    file.write(sentence_txt)
        if nr != 0:
            return True
        return False

    @staticmethod
    def execute_rule1_forall(source_directory, destination_directory):
        no_sentences_splitted = 0
        no_sentences = 0
        directory = os.fsencode(source_directory)
        for file in os.listdir(directory):
            filename = os.fsdecode(file)
            is_splitted = Rule1.execute_rule1(source_directory + '/' + filename, destination_directory)
            if is_splitted:
                no_sentences_splitted += 1
            no_sentences += 1
        print("No of sentences = ", no_sentences)
        print("No of sentences splitted Rule 1 = ", no_sentences_splitted)

    @staticmethod
    def main():
        # Rule1.execute_rule1_forall('dev', 'Result/Rule1/')
        simplified = Rule1.execute_rule1(sys.argv[1], './')
        if simplified == True:
            print("The sentence was successfully simplified using CC Rule.")
        else:
            print("The sentence can not be simplified using CC Rule.")


if __name__ == '__main__':
    Rule1.main()