import os
from UCCA_Simplification.parseXML import Parser
import sys


class ShowUCCAGraph:

    @staticmethod
    def generate_graphs():
        directory = os.fsencode('Graphs/Result/Data/')
        source_directory = 'Graphs/Result/Data/'
        destination_directory = 'Graphs/Result/Graphs/'
        for file in os.listdir(directory):
            filename = os.fsdecode(file)
            print(filename)
            parser = Parser(source_directory + filename)
            dict_layers = parser.extract_data(source_directory + filename)
            list_layer0 = dict_layers['Layer0']
            list_layer1 = dict_layers['Layer1']
            Parser.draw_graph(list_layer0, list_layer1, destination_directory + dict_layers['passageID'])

    @staticmethod
    def show_graph(source_file, destination_file):
        dict_layers = Parser.extract_data(source_file)
        list_layer0 = dict_layers['Layer0']
        list_layer1 = dict_layers['Layer1']
        Parser.draw_graph(list_layer0, list_layer1, destination_file)

    @staticmethod
    def main():
        dest_file = sys.argv[1].split(".")[0]
        ShowUCCAGraph.show_graph(sys.argv[1],dest_file)


if __name__ == '__main__':
    ShowUCCAGraph.main()
