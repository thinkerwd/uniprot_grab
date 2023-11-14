from threading import Thread, Lock
import requests
import json
from time import sleep

gene = []
gene_result = {}
gene_lock = Lock()
gene_result_lock = Lock()

def get_value(keyword):
    value = ''
    url = 'https://rest.uniprot.org/uniprotkb/search?query='+ keyword +'&format=json'
    try:
        all_fastas = requests.get(url).text
        y = json.loads(all_fastas)
        for result in y['results']:
            if 'HUMAN' in result['uniProtkbId']:
                for comment in result['comments']:
                    if 'SUBCELLULAR LOCATION' in comment['commentType']:
                        for l in comment['subcellularLocations']:
                            value += l['location']['value'] + ","
                        break
                break
    except:
        value = 'Error'
    return value

def read_key(filename):
    with open(filename) as f:
        lines = f.readlines()
        for l in lines:
            gene.append(l.replace('\n', ''))

def write_result(filename):
    with open(filename, 'w') as f:
        for key, value in gene_result.items():
            if ',' in value:
                value = '"' + value + '"' 
            f.write(key+','+value+'\n')

def analysis():
    flag = True
    key = ''
    value = ''
    while True:
        with gene_lock:
            if len(gene) == 0:
                flag = False
            else:
                key = gene.pop()
        if flag == False:
            break
        value = get_value(key)
        with gene_result_lock:
            gene_result[key] = value

if __name__ == '__main__':
    read_key("input.txt")
    thread_list = []
    for i in range(4):
        t = Thread(target=analysis)
        thread_list.append(t)
    for t in thread_list:
        t.start()
    for t in thread_list:
        t.join()
    write_result("output.txt")