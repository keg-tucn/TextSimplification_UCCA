
import json
import os
import xml.etree.ElementTree as ET

def extract_data(file):
    tree = ET.parse(file)
    root = tree.getroot()
    # iterate over children nodes
    dict_layers = {}
    list_layer0 = []
    list_layer1 = []
    for child in root:
        # layers
        if child.tag == "layer":
            if child.attrib.get('layerID') == "0":
                for child2 in child:
                    if child2.tag != "attributes" and child2.tag != "extra":
                        dict_layer0 = {}
                        dict_layer0['ID'] = child2.attrib.get('ID')
                        dict_layer0['type'] = child2.attrib.get('type')
                        for child3 in child2:
                            if child3.tag == 'attributes':
                                dict_layer0['text'] = child3.attrib.get('text')
                                dict_layer0['pos'] = child3.attrib.get('paragraph_position')
                                dict_layer0['paragraph'] = child3.attrib.get('paragraph')
                            if child3.tag == 'extra':
                                dict_layer0['dep'] = child3.attrib.get('dep')
                                dict_layer0['ent_iob'] = child3.attrib.get('ent_iob')
                                dict_layer0['ent_type'] = child3.attrib.get('ent_type')
                                dict_layer0['head'] = child3.attrib.get('head')
                                dict_layer0['lemma'] = child3.attrib.get('lemma')
                                dict_layer0['orig_paragraph'] = child3.attrib.get('orig_paragraph')
                                dict_layer0['orth'] = child3.attrib.get('orth')
                                dict_layer0['position'] = child3.attrib.get('pos')
                                dict_layer0['prefix'] = child3.attrib.get('prefix')
                                dict_layer0['shape'] = child3.attrib.get('shape')
                                dict_layer0['suffix'] = child3.attrib.get('suffix')
                                dict_layer0['tag'] = child3.attrib.get('tag')
                        list_layer0.append(dict_layer0)
                    else:
                        if child2.tag == "extra":
                            extra = child2.attrib.get('doc')
                            dict_layers['extra'] = extra
            else:
                for child2 in child:
                    if child2.tag == 'node':
                        dict_layer1 = {}
                        dict_layer1['ID'] = child2.attrib.get('ID')
                        dict_layer1['type'] = child2.attrib.get('type')
                        dict_layer1['edge'] = []
                        list_edges = []
                        for child3 in child2:
                            if child3.tag == 'edge':
                                dict_edges = {}
                                dict_edges['toID'] = child3.attrib.get('toID')
                                dict_edges['type'] = child3.attrib.get('type')
                                for child4 in child3:
                                    if child4.tag == 'attributes':
                                        dict_edges['remote'] = child4.attrib.get('remote')
                                list_edges.append(dict_edges)
                                dict_layer1['edge'] = list_edges
                        list_layer1.append(dict_layer1)
    dict_layers['Layer0'] = list_layer0
    dict_layers['Layer1'] = list_layer1
    dict_layers['passageID'] = root.get('passageID')
    dict_layers['tree'] = tree
    return dict_layers

def get_d(s, alignment1):
    for a in alignment1:
        if a['s'] == s:
            return a
    return None

def is_equal_l0(elem1, elem2):
    if elem1['dep'] == elem2['dep'] and elem1['ent_iob'] == elem2['ent_iob'] and elem1['ent_type'] == elem2['ent_type'] and elem1['head'] == elem2['head'] and elem1['lemma'] == elem2['lemma'] and elem1['orig_paragraph'] == elem2['orig_paragraph'] and elem1['orth'] == elem2['orth'] and elem1['prefix'] == elem2['prefix'] and elem1['position'] == elem2['position'] and elem1['shape'] == elem2['shape'] and elem1['suffix'] == elem2['suffix'] and elem1['tag'] == elem2['tag']:
        return True
    return False

def is_not_aligned(alignment_data, sentence, id):
    for a in alignment_data:
        if a['d'] == id and a['sentence'] == sentence:
            return False
    return True


def align_data():
    directory = os.fsencode('Input')
    dir = "Input/"
    dir_d = "Output/"
    dir_dest = os.fsencode('Output')
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        filename_wxml = filename.split('.')
        list_files = []
        name = ""
        for f in os.listdir(dir_dest):
            filename_a = os.fsdecode(f)
            if filename_a.startswith(filename_wxml[0] + '_') or filename_a.startswith(filename_wxml[0] + '.'):
                list_files.append(filename_a)
        if list_files.__len__() > 1:
            # extract data for the source file
            data_original = extract_data(dir + filename)
            alignment_data = []
            for e_orig in data_original['Layer0']:
                nr_sentence = 1
                for f in list_files:
                    data1 = extract_data(dir_d + f)
                    for elem in data1['Layer0']:
                        if e_orig['text'] == elem['text'] and is_equal_l0(e_orig, elem) and is_not_aligned(alignment_data, nr_sentence, elem['ID']):
                            dict_al = {}
                            dict_al['s'] = e_orig['ID']
                            dict_al['d'] = elem['ID']
                            dict_al['sentence'] = nr_sentence
                            alignment_data.append(dict_al)
                            break
                    nr_sentence = nr_sentence + 1
            with open('Alignment_data/' + filename_wxml[0] + '.json' , 'w') as outfile:
                json.dump(alignment_data, outfile)
        else:
            with open('Alignment_data/' + filename_wxml[0] + '.json' , 'w') as outfile:
                json.dump(None, outfile)

def main():
    align_data()

if __name__ == '__main__':
    main()