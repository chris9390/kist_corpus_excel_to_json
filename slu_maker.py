import json

with open('multiplied_json.json', encoding='utf-8') as json_file:
    multiplied_list = json.load(json_file)


f_seq_in = open('seq_in.txt', 'w', encoding='utf-8')


for each_elem in multiplied_list:
    each_utters = each_elem['utters']
    for each_utter in each_utters:
        f_seq_in.write(each_utter['text'] + '\n')





f_seq_in.close()