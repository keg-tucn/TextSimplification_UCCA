import sys
import os
from UCCA_Simplification.parseXML import Parser
import json
import SAMSA.scene_sentence_alignment


class Evaluate_SAMSA:

    @staticmethod
    def extract_data(file):
        return Parser.extract_data(file)

    @staticmethod
    def index(list, elem):
        nr = 0
        for l in list:
            if l == elem:
                return nr
            nr = nr + 1
        return -1

    @staticmethod
    def get_text_for_pos(data_layer0, pos):
        for elem in data_layer0:
            if int(elem['pos']) == int(pos):
                return elem['ID']
        return None

    @staticmethod
    def is_terminal(data_layer0, node_id):
        for elem in data_layer0:
            if elem['ID'] == node_id and elem['type'] != 'PNCT':
                return True
        return False

    @staticmethod
    def get_children(node_id, data_layer1):
        list_childs = []
        for elem in data_layer1:
            if elem['ID'] == node_id:
                for e in elem['edge']:
                    list_childs.append(e['toID'])
        return list_childs

    @staticmethod
    def get_terminals(data_layer0, data_layer1, node_id):
        list_nodes = []
        child_list = Evaluate_SAMSA.get_children(node_id, data_layer1)
        for child in child_list:
            if not Evaluate_SAMSA.is_terminal(data_layer0, child):
                list_nodes = list_nodes + Evaluate_SAMSA.get_terminals(data_layer0, data_layer1, child)
            else:
                list_nodes.append(child)
        return list_nodes

    @staticmethod
    def get_node_l1(data_layer1, id):
        for elem in data_layer1:
            if elem['ID'] == id:
                return elem
        return None

    @staticmethod
    def get_node_l0(data_layer0, id):
        for elem in data_layer0:
            if elem['ID'] == id:
                return elem
        return None

    # a node is a scene if it has an outgoing edge with label P or S
    @staticmethod
    def is_scene(node, data_layer1):
        for elem in data_layer1:
            if elem['ID'] == node['ID']:
                for edge in elem['edge']:
                    if edge['type'] == 'S' or edge['type'] == 'P':
                        return True
        return False

    @staticmethod
    def get_nr_scenes(data_layer1):
        # returns the number of scenes
        scenes = [x for x in data_layer1 if x['type'] == "FN" and Evaluate_SAMSA.is_scene(x, data_layer1)]
        output = len(scenes)
        return output


    @staticmethod
    def get_nr_sentences(f, results):
        directory = os.fsencode(results)
        source_directory = results + "/"
        nr = 0
        for file in os.listdir(directory):
            filename = os.fsdecode(file)
            if filename.startswith(f + "_"):
                nr = nr + 1
        return nr

    @staticmethod
    def get_d_for_al(id, d, alignment1, sent):
        for a in alignment1:
            if a['s'] == id and a['d'] == d and a['sentence'] == sent:
                return a
        return None

    @staticmethod
    def is_aligned(alig_data, id, data_layer0, sent):
        ok = 0
        for elem in data_layer0:
            al = Evaluate_SAMSA.get_d_for_al(id, elem['ID'], alig_data, sent)
            if al != None:
                ok = 1
        if ok == 0:
            return False
        else:
            return True

    @staticmethod
    def get_sentences(f, results):
        sentences = []
        directory = os.fsencode(results)
        source_directory = results + "/"
        for file in os.listdir(directory):
            filename = os.fsdecode(file)
            if filename.startswith(f + "_"):
                data = Parser.extract_data(source_directory + filename)
                sentences.append(data)
        return sentences

    @staticmethod
    def get_scenes(data_layer0, data_layer1):
        """
        P is a ucca passage. Return all the scenes in each passage
        """
        scenes = [x for x in data_layer1 if x['type'] == "FN" and Evaluate_SAMSA.is_scene(x, data_layer1)]
        y = data_layer0
        output = []
        for sc in scenes:
            p = []
            d = Evaluate_SAMSA.get_terminals(data_layer0, data_layer1, sc['ID'])
            for i in list(range(0, len(d))):
                node_i = Evaluate_SAMSA.get_node_l0(data_layer0, d[i])
                p.append(node_i['pos'])
            output2 = []
            for k in p:
                if (len(output2)) == 0:
                    output2.append(str(Evaluate_SAMSA.get_text_for_pos(data_layer0,k)))
                elif str(Evaluate_SAMSA.get_text_for_pos(data_layer0,k)) != output2[-1]:
                    output2.append(str(Evaluate_SAMSA.get_text_for_pos(data_layer0,k)))

            output.append(output2)
        return (output)

    @staticmethod
    def get_cmrelations(data_layer1, data_layer0):
        scenes = [x for x in data_layer1 if x['type'] == "FN" and Evaluate_SAMSA.is_scene(x, data_layer1)]
        m = []
        # c = []
        for sc in scenes:
            mrelations = [e['toID'] for e in sc['edge'] if e['type'] == 'P' or e['type'] == 'S']
            for mr in mrelations:
                node = Evaluate_SAMSA.get_node_l1(data_layer1, mr)
                centers = [e['toID'] for e in node['edge'] if e['type'] == 'C']
                if centers != []:
                    while centers != []:
                        for c in centers:
                            node_c = Evaluate_SAMSA.get_node_l1(data_layer1, c)
                            ccenters = [e['toID'] for e in node_c['edge'] if e['type'] == 'C']
                        lcenters = centers
                        centers = ccenters
                    m.append(lcenters)
                else:
                    m.append(mrelations)
        output = []
        for scp in m:
            for par in scp:
                output2 = []
                p = []
                d = Evaluate_SAMSA.get_terminals(data_layer0, data_layer1, par)
                for i in list(range(0, len(d))):
                    node0 = Evaluate_SAMSA.get_node_l0(data_layer0, d[i])
                    p.append(node0['pos'])
                for k in p:
                    if (len(output2)) == 0:
                        output2.append(str(Evaluate_SAMSA.get_text_for_pos(data_layer0, k)))
                    elif str(Evaluate_SAMSA.get_text_for_pos(data_layer0, k)) != output2[-1]:
                        output2.append(str(Evaluate_SAMSA.get_text_for_pos(data_layer0, k)))
            output.append(output2)
        return (output)

    @staticmethod
    def get_cparticipants(data_layer0, data_layer1):
        scenes = [x for x in data_layer1 if x['type'] == "FN" and Evaluate_SAMSA.is_scene(x, data_layer1)]
        n = []
        for sc in scenes:  # find participant nodes
            m = []
            participants = [e['toID'] for e in sc['edge'] if e['type'] == 'A']
            for pa in participants:
                node = Evaluate_SAMSA.get_node_l1(data_layer1, pa)
                centers = [e['toID'] for e in node['edge'] if e['type'] == 'C']
                if centers != []:
                    while centers != []:
                        for c in centers:
                            node_c = Evaluate_SAMSA.get_node_l1(data_layer1, c)
                            ccenters = [e['toID'] for e in node_c['edge'] if
                                        e['type'] == 'C' or e['type'] == 'P' or e['type'] == 'S']  # also addresses center Scenes
                        lcenters = centers
                        centers = ccenters
                    m.append(lcenters)
                elif Evaluate_SAMSA.is_scene(node, data_layer1):  # address the case of Participant Scenes
                    scenters = [e['toID'] for e in node['edge'] if e['type'] == 'P' or e['type'] == 'S']
                    for scc in scenters:
                        node_scc = Evaluate_SAMSA.get_node_l1(data_layer1, scc)
                        centers = [e['toID'] for e in node_scc['edge'] if e['type'] == 'C']
                        if centers != []:
                            while centers != []:
                                for c in centers:
                                    node_c = Evaluate_SAMSA.get_node_l1(data_layer1, c)
                                    ccenters = [e['toID'] for e in node_c['edge'] if e['type'] == 'C']
                                lcenters = centers
                                centers = ccenters
                            m.append(lcenters)
                        else:
                            m.append(scenters)
                elif any(e['type'] == "H" for e in
                         node['edge']):  # address the case of multiple parallel Scenes inside a participant
                    hscenes = [e['toID'] for e in node['edge'] if e['type'] == 'H']
                    mh = []
                    for h in hscenes:
                        node_h = Evaluate_SAMSA.get_node_l1(data_layer1, h)
                        hrelations = [e['toID'] for e in node_h['edge'] if
                                      e['type'] == 'P' or e['type'] == 'S']  # in case of multiple parallel scenes we generate new multiple centers
                        for hr in hrelations:
                            node_hr = Evaluate_SAMSA.get_node_l1(data_layer1, hr)
                            centers = [e['toID'] for e in node_hr['edge'] if e['type'] == 'C']
                            if centers != []:
                                while centers != []:
                                    for c in centers:
                                        node_c = Evaluate_SAMSA.get_node_l1(data_layer1, c)
                                        ccenters = [e['toID'] for e in node_c['edge'] if e['type'] == 'C']
                                    lcenters = centers
                                    centers = ccenters
                                mh.append(lcenters[0])
                            else:
                                mh.append(hrelations[0])
                    m.append(mh)
                else:
                    m.append([pa])
            n.append(m)

        output = []
        s = []
        I = []
        for scp in n:
            r = []
            u = Evaluate_SAMSA.index(n, scp)
            for par in scp:
                if len(par) > 1:
                    d = Evaluate_SAMSA.index(scp, par)
                    par = [par[i:i + 1] for i in range(0, len(par))]
                    for c in par:
                        r.append(c)
                    I.append([u, d])
                else:
                    r.append(par)
            s.append(r)

        for scp in s:  # find the spans of the participant nodes
            output1 = []
            if scp.__len__() != 0:
                for par1 in scp:
                    par = [val for val in par1]
                    output2 = []
                    p = []
                    d = Evaluate_SAMSA.get_terminals(data_layer0, data_layer1, par)
                    for i in list(range(0, len(d))):
                        node_di = Evaluate_SAMSA.get_node_l0(data_layer0, d[i])
                        p.append(node_di['pos'])

                    for k in p:
                        if (len(output2)) == 0:
                            output2.append(str(Evaluate_SAMSA.get_text_for_pos(data_layer0, k)))
                        elif str(Evaluate_SAMSA.get_text_for_pos(data_layer0, k)) != output2[-1]:
                            output2.append(str(Evaluate_SAMSA.get_text_for_pos(data_layer0, k)))
                    output1.append(output2)
            output.append(output1)

        y = []  # unify spans in case of multiple centers
        for scp in output:
            x = []
            u = Evaluate_SAMSA.index(output, scp)
            for par in scp:
                for v in I:
                    if par == output[v[0]][v[1]]:
                        for l in list(range(1, len(n[v[0]][v[1]]))):
                            if (output[v[0]][v[1] + l]).__len__() != 0:
                                par.append((output[v[0]][v[1] + l])[0])

                        x.append(par)
                    elif all(par != output[v[0]][v[1] + l] for l in list(range(1, len(n[v[0]][v[1]])))):
                        x.append(par)
                if I == []:
                    x.append(par)
            y.append(x)
        return y

    @staticmethod
    def function_unu(filename, nr_s, u, align_data, results):
        list_files = []
        dest_directory = results + "/"
        directory = os.fsencode(results)
        for f in os.listdir(directory):
            filename_a = os.fsdecode(f)
            if filename_a.startswith(filename + '_') or filename_a.startswith(filename + '.'):
                list_files.append(filename_a)
        layer_data = Parser.extract_data(dest_directory + list_files[nr_s - 1])
        if Evaluate_SAMSA.is_aligned(align_data, u, layer_data['Layer0'], nr_s):
            return 1
        return 0

    @staticmethod
    def evaluate_all(source, results):
        score = 0
        nr_sentences_simplified = 0
        nr_sentences = 0
        directory = os.fsencode(source)
        source_directory = source + "/"
        for file in os.listdir(directory):
            filename = os.fsdecode(file)
            nr_sentences = nr_sentences + 1
            score_file = Evaluate_SAMSA.evaluate_one(source_directory + filename, results)
            if score_file != -1:
                nr_sentences_simplified = nr_sentences_simplified + 1
                score = score + score_file
        score = score / nr_sentences_simplified
        return score

    @staticmethod
    def evaluate_one(filename, results):
        file = filename.split('/')[-1].split('.')[0]
        # extract data from file
        data = Parser.extract_data(filename)
        data_layer0 = data['Layer0']
        data_layer1 = data['Layer1']

        L1 = Evaluate_SAMSA.get_nr_scenes(data_layer1)
        L2 = Evaluate_SAMSA.get_nr_sentences(file, results)
        M1 = Evaluate_SAMSA.get_cmrelations(data_layer1, data_layer0)
        A1 = Evaluate_SAMSA.get_cparticipants(data_layer0, data_layer1)

        if L2 == 0:
            return -1

        if L1 < L2:
            score = 0
        elif L1 > L2:
            scenes = Evaluate_SAMSA.get_scenes(data_layer0, data_layer1)
            sentences = Evaluate_SAMSA.get_sentences(file, results)
            with open('Alignment_data/' + file + '.json', 'r') as infile:
                align_data = json.loads(infile.read())
            # compute M
            #  for each scene get the sentence with the highest match
            M = []
            for sc in scenes:
                s = 1
                max = 0
                max_sentence = 0
                for sentence in sentences:
                    scor = 0
                    for id in sc:
                        if Evaluate_SAMSA.is_aligned(align_data, id, sentence['Layer0'], s):
                            scor = scor + 1
                    if scor > max:
                        max = scor
                        max_sentence = s
                    s = s + 1
                M.append(max_sentence)
            # print(M) # M contains the correspondent sentence for each scene

            score_sum = 0
            nr_scene = 0
            for sc in scenes:
                # primul termen al sumei
                if M1[nr_scene].__len__() == 0:
                    unu_mri = 0
                else:
                    unu_mri = Evaluate_SAMSA.function_unu(file, M[nr_scene], M1[nr_scene][0], align_data, results)
                # print("Unu_mri: ", unu_mri)
                # al doilea termen al sumei
                par = [val for sublist in A1[nr_scene] for val in sublist]
                sum2 = 0
                if par.__len__() != 0:
                    for p in par:
                        sum2 = sum2 + Evaluate_SAMSA.function_unu(file, M[nr_scene], p, align_data, results)
                    sum2 = sum2/par.__len__()
                # adunam cei doi termeni la suma totala
                score_sum = score_sum + unu_mri + sum2
                nr_scene = nr_scene + 1

            score = 1.0/(2.0*L1) * score_sum
        else: # L1 = L2
            scenes = Evaluate_SAMSA.get_scenes(data_layer0, data_layer1)
            sentences = Evaluate_SAMSA.get_sentences(file, results)
            with open('Alignment_data/' + file + '.json', 'r') as infile:
                align_data = json.loads(infile.read())
            # compute M
            #  for each scene get the sentence with the highest match
            M = []
            for sc in scenes:
                s = 1
                max = 0
                max_sentence = 0
                sent_remove = None
                for sentence in sentences:
                    scor = 0
                    for id in sc:
                        if Evaluate_SAMSA.is_aligned(align_data, id, sentence['Layer0'], s):
                            scor = scor + 1
                    if scor > max :
                        max = scor
                        max_sentence = s
                        sent_remove = sentence
                    s = s + 1
                M.append(max_sentence)
                if sent_remove in sentences:
                    sentences.remove(sent_remove)
            # print(M)  # M contains the correspondent sentence for each scene

            score_sum = 0
            nr_scene = 0
            for sc in scenes:
                # primul termen al sumei
                if M1[nr_scene].__len__() == 0:
                    unu_mri = 0
                else:
                    unu_mri = Evaluate_SAMSA.function_unu(file, M[nr_scene], M1[nr_scene][0], align_data, results)
                # print("Unu_mri: ", unu_mri)
                # al doilea termen al sumei
                par = [val for sublist in A1[nr_scene] for val in sublist]
                sum2 = 0
                if par.__len__() != 0:
                    for p in par:
                        sum2 = sum2 + Evaluate_SAMSA.function_unu(file, M[nr_scene], p, align_data, results)
                    sum2 = sum2 / par.__len__()
                # adunam cei doi termeni la suma totala
                score_sum = score_sum + unu_mri + sum2
                nr_scene = nr_scene + 1

            score = 1.0 / (2.0 * L1) * score_sum
        return score

    @staticmethod
    def main():
        SAMSA.scene_sentence_alignment.align_data(sys.argv[1], sys.argv[2])
        print("SAMSA score = " + str(Evaluate_SAMSA.evaluate_all(sys.argv[1], sys.argv[2])))


if __name__ == '__main__':
    Evaluate_SAMSA.main()

