import os
from UCCA_Simplification.parseXML import Parser
import sys


class CCRule:

    @staticmethod
    def split_all_xml_rule1(source, destination):
        no_sentences_splitted = 0
        no_sentences = 0
        directory = os.fsencode(source)
        source_directory = source + "/"
        destination_directory_graphs = destination + "/"
        destination_directory_data = destination + "/"
        for file in os.listdir(directory):
            filename = os.fsdecode(file)
            parser = Parser(source_directory + filename)
            is_splitted = parser.split.split_rule1_new(filename, destination_directory_graphs, destination_directory_data)
            if is_splitted:
                no_sentences_splitted += 1
            no_sentences += 1
        print("No of sentences = ", no_sentences)
        print("No of sentences splitted Rule 1 = ", no_sentences_splitted)

    @staticmethod
    def apply_CCRule(filename):
        parser = Parser(filename)
        destination_directory_data = './'
        destination_directory_graphs = './'
        is_splitted = parser.split.split_rule1_new(filename, destination_directory_graphs, destination_directory_data)
        if is_splitted == True:
            print("The sentence was successfully simplified using CC Rule.")
        else:
            print("The sentence can not be simplified using CC Rule.")

    @staticmethod
    def main():
        if sys.argv.__len__() > 3:
            if sys.argv[3] == "-all":
                CCRule.split_all_xml_rule1(sys.argv[1], sys.argv[2])
        else:
            CCRule.apply_CCRule(sys.argv[1])


if __name__ == '__main__':
    CCRule.main()