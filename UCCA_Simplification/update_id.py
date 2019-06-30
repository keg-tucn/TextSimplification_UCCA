import xml.etree.ElementTree as ET
import os

def get_new(dict, id):
    for d in dict:
        if d['old'] == id:
            return d['new']
    return None


def update(file):
    tree = ET.parse(file)
    root = tree.getroot()
    ind = 1
    old_new = []
    for child in root:
        # layers
        if child.tag == "layer":
            if child.attrib.get('layerID') == "0":
                for child2 in child:
                    if child2.tag != "attributes" and child2.tag != "extra":
                        dict_old_new = {}
                        dict_old_new['old'] = child2.attrib.get('ID')
                        new_id = '0.' + str(ind)
                        dict_old_new['new'] = new_id
                        old_new.append(dict_old_new)
                        child2.attrib['ID'] = new_id
                        ind = ind + 1
            else:
                for child2 in child:
                    if child2.tag == 'node':
                        for child3 in child2:
                            if child3.tag == 'edge':
                                id_new = get_new(old_new, child3.attrib.get('toID'))
                                if id_new != None:
                                    child3.attrib['toID']  = id_new
    tree.write(file)


def update_all():
    directory = os.fsencode('Update/test_xml/')
    source_directory = 'Update/test_xml/'
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        update(source_directory + filename)



def main():
    update_all()

if __name__ == '__main__':
    main()
