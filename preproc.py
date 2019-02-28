import parseXML
import os


def generate_graphs():
    directory = os.fsencode('Data')
    source_directory = 'Data/'
    destination_directory = 'Graphs/'
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        print(filename)
        dict_layers = parseXML.extract_data(source_directory + filename)
        list_layer0 = dict_layers['Layer0']
        list_layer1 = dict_layers['Layer1']
        parseXML.draw_graph(list_layer0, list_layer1, destination_directory + dict_layers['passageID'])


def generate_one_graph_for_test():
    dict_layers = parseXML.extract_data('test.xml')
    list_layer0 = dict_layers['Layer0']
    list_layer1 = dict_layers['Layer1']
    parseXML.draw_graph(list_layer0, list_layer1, dict_layers['passageID'])


def main():
    generate_one_graph_for_test()
    # generate_graphs()


if __name__ == '__main__':
    main()
