import csv
import os
from lxml import etree
from collections import OrderedDict
import re
import time

det_words = set("""
ваш
весь
всякий
всяк
другой
его
её
иной
ихний
их
каждый
каков
какой
какой-либо
какой-нибудь
какой-то
кой
который
который-нибудь
любой
многие
мой
наш
некий
некоторый
немногие
никакой
ничей
оный
прочий
проч.
пр.
свой
сей
таков
такой
твой
тот
чей
чей-либо
чей-нибудь
чей-то
этакий
этот
""".strip().replace('ё', 'е').split())
reg_exp = re.compile('[^=,]+') # ('[a-zA-z]+')
pos_mapper = {
'S':'NOUN',
'A':'ADJ',
'NUM':'NUM',
'ANUM':'ADJ',
'V':'VERB',
'ADV':'ADV',
'PRAEDIC':'ADV',
'PARENTH':'ADP',
'S-PRO':'PRON',
'SPRO':'PRON',
'A-PRO':'PRON',
'APRO':'PRON',
'ADVPRO':'PRON',
'ADV-PRO':'PRON',
'PRAEDICPRO':'PRON',
'PRAEDIC-PRO':'PRON',
'PR':'ADP',
'CONJ':'SCONJ',
'PART':'PART',
'INTJ':'INTJ',
'INIT': 'PROPN'
}
cconj = {'и', 'а', 'но', 'или'}
current_time = time.time()
PATH = 'C:/Users/Ольга/PycharmProjects/framebank'  # './isa_parser/data/original_framebank'


def extract_morpho(example):
    tree = etree.XML(example)
    res = OrderedDict()
    for se in tree:
        for w in se:
            if len(w) > 0:
                lex = w[0].attrib['lex']
                gr = w[0].attrib['gr']
                word = w[-1].tail
                sem = w[0].get('sem')
                sem2 = w[0].get('sem2')
                res[word] = [lex, gr, sem, sem2, None, None]  # если в предложении есть одинаковые слова, они потеряются
            else:
                res[w.text] = [None*6]
    return res


def examples_write_csv(fname, examples):
    with open(fname, 'w', encoding='utf-8') as wr:
        out = csv.writer(wr, delimiter='\t')
        # header = ('ExID', 'Wordform', 'Lex', 'Gr', 'Sem', 'Sem2', 'Role', 'Rank')
        conll_header = ('ID', 'FORM', 'LEMMA', 'UPOSTAG', 'XPOSTAG', 'FEATS', 'HEAD', 'DEPREL', 'DEPS', "MISC")
        out.writerow(conll_header)

        for ex in examples:
            for ind, w in enumerate(examples[ex]):
                """row = [ex] + [w] + examples[ex][w]
                out.writerow(row)"""
                string = examples[ex][w]
                underscore = '_'
                syntax_underscore = '-'
                #  pos_unified = '_'
                #  feats = '_'
                gram = string[1].split(' ')
                pos = gram[0]

                try:
                    pos_unified = pos_mapper[pos]
                    feats = '|'.join(gram[1:])

                except KeyError:
                    gram = gram[0]
                    if ',' in list(gram) or '=' in list(gram):
                        container = reg_exp.findall(gram)
                        pos = container[0]
                        pos_unified = pos_mapper[pos]
                        gram = container[1:]
                        feats = '|'.join(gram[1:])
                        """if feats == '' or feats == ' ':
                            feats = '_'
                        print('pos', pos, 'feats:', feats)
                        print()"""
                    else:
                        pos_unified = 'X'
                        #gram = underscore
                        #print('pos:', pos, 'gram:', gram)
                        #print()
                        pass

                if string[0] == 'быть':
                    pos_unified = 'AUX'
                elif w in det_words:
                    pos_unified = 'DET'
                elif w in cconj:
                    pos_unified = 'CCONJ'
                elif 'persn' in gram or 'famn' in gram or 'patrn' in gram:
                    pos_unified = 'PROPN'
                #feats = '|'.join(gram[1:])
                if feats == '' or feats == ' ':
                    feats = '_'
                row = [ind] + [w] + [string[0]] + [pos_unified] + [pos] + [feats] + [syntax_underscore]*3 + [underscore]
                out.writerow(row)
            out.writerow('')


def parse_framebank_examples(in_f, out_f):
    examples = OrderedDict()

    with open(os.path.join(PATH, in_f), 'r', encoding='utf-8') as ex:
        reader = csv.reader(ex, delimiter="\t")
        header = next(reader)
        i = 0
        
        for line in reader:
            
            if i%5000 == 0:
                print(i)
            
            try:
                i += 1
                #print('line number:', i)
                if not '<p' in line[1]:
                    line[1] = '<p>' + line[1] + '</p>'
                line[1] = line[1].split('</p>')[0] + '</p>'
                res = extract_morpho(line[1])
                examples[line[0]] = res # dictionary:
                # {ex_id: {word1: [lex, gr, sem, sem2]}, word2: [lex, gr, sem, sem2]}}
            except:
                pass
    examples_write_csv(out_f, examples)
                
if __name__ == '__main__':
    parse_framebank_examples('exampleindex.csv', 'parsed_framebank_big.csv')
    print("Elapsed time for reading: {:.3f} sec".format(time.time() - current_time))
