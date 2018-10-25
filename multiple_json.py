from pprint import pprint
import json
import copy
import itertools
import re




with open('./json/ontology_json.json', encoding='utf-8') as json_file:
    ontology_dict = json.load(json_file)


with open('./json/result_json.json', encoding='utf-8') as json_file:
    result_json_list = json.load(json_file)



final_list = []
# 일단 기존에 있던 데이터 모두 저장
for each_elem in result_json_list:
    final_list.append(each_elem)


for each_elem in result_json_list:

    each_utter = each_elem['utters'][0]


    dialog_acts = each_utter['dialog_acts']


    #target_slots = {}
    list_temp = []
    current_slots = []
    current_values = []

    for dialog_act in dialog_acts:
        if dialog_act['slot'] == None:
            continue
        #target_slots[dialog_act['slot']] = ontology_dict[dialog_act['slot']]
        list_temp.append(ontology_dict[dialog_act['slot']])

        # ontology_combs_list의 각 튜플의 인덱스의 ontology(slot) 종류
        current_slots.append(dialog_act['slot'])
        current_values.append(dialog_act['value'])


    if len(current_values) == 0:
        continue


    # slot-value의 가능한 모든 쌍 생성 (Cartesian Product)
    ontology_combs_list = list(itertools.product(*list_temp))



    # slot-value의 가능한 모든 쌍에 대한 문장 생성 루프
    for each_ontology_pairs in ontology_combs_list:
        # 여러 경우로 변환하기 위해 원본 복사
        each_utter_copy = copy.deepcopy(each_utter)
        ontol_idx = 0
        for each_ontology in each_ontology_pairs:

            before = current_values[ontol_idx]
            after = each_ontology

            if before == None:
                continue



            # '위' 같이 1글자인 value인 경우 '위치' 같은 단어에 걸려버릴 수 있기 때문에 한번 더 체크
            if len(before) == 1:
                not_value_list = ['위치']
                tokens = each_utter_copy['text'].split(' ')

                wpm_token_idx = []
                token_idx = 0
                for char in each_utter_copy['text']:
                    if char == ' ':
                        wpm_token_idx.append('_')
                        token_idx += 1
                        continue

                    wpm_token_idx.append(token_idx)


                for i, char in enumerate(each_utter_copy['text']):
                    if char == before:
                        if tokens[wpm_token_idx[i]] not in not_value_list:
                            tokens[wpm_token_idx[i]] = tokens[wpm_token_idx[i]].replace(before, after)
                            each_utter_copy['text'] = ' '.join(tokens)


            # 2글자 이상의 value인 경우는 그냥 replace
            else:
                # 텍스트에서 새로운 value에 해당하는 단어를 찾아서 변경하고
                each_utter_copy['text'] = each_utter_copy['text'].replace(before, after)



            afterword_len = len(after)
            afterword_index = each_utter_copy['text'].find(after)

            # after 단어 뒤에 나오는 조사의 시작 인덱스
            after_afterword_idx = afterword_index + afterword_len

            # after 단어 뒤에 나오는 문자
            after_afterword = ''
            # 공백 전까지가 조사에 해당하므로 after_afterword에 붙여준다.
            for i in range(after_afterword_idx, len(each_utter_copy['text'])):
                #if each_utter_copy['text'][i] == ' ':
                if ord(each_utter_copy['text'][i]) < ord('가') or ord(each_utter_copy['text'][i]) > ord('힣'):
                    break
                after_afterword += each_utter_copy['text'][i]



            code_point = ord(after[-1])
            is_jongsung = (code_point - 44032) % 28

            # 마지막 글자 받침 있는 명사 다음에 올 수 있는 조사 (메론을)
            with_jongsung = ['이', '은', '으로', '을', '과', '이면']
            # 마지막 글자 받침 없는 명사 다음에 올 수 있는 조사 (사과를)
            without_jongsung = ['가', '는', '로', '를', '와', '면']


            # value의 마지막 글자 받침 없음
            if is_jongsung == 0:
                if after_afterword in with_jongsung:
                    idx = with_jongsung.index(after_afterword)
                    correct_after_afterword = without_jongsung[idx]
                    correct_text = each_utter_copy['text'][0:after_afterword_idx] + correct_after_afterword + each_utter_copy['text'][after_afterword_idx + len(after_afterword):]
                    each_utter_copy['text'] = correct_text

            # value의 마지막 글자 받침 있음
            elif is_jongsung != 0:
                if after_afterword in without_jongsung:
                    idx = without_jongsung.index(after_afterword)
                    correct_after_afterword = with_jongsung[idx]
                    correct_text = each_utter_copy['text'][0:after_afterword_idx] + correct_after_afterword + each_utter_copy['text'][after_afterword_idx + len(after_afterword):]
                    each_utter_copy['text'] = correct_text




            # dialog_acts의 value값도 같이 변경하자
            each_utter_copy['dialog_acts'][ontol_idx]['value'] = each_ontology
            ontol_idx += 1

        temp_dict = {}
        temp_dict['session_id'] = ''
        temp_dict['utters'] = [each_utter_copy]


        # 텍스트 중복 체크
        is_duplicated = 0
        for i in final_list:
            if each_utter_copy['text'] == i['utters'][0]['text']:
                is_duplicated = 1
                break

        # 이미 있는 text면 리스트에 추가 하지 않음
        if is_duplicated == 1:
            continue

        final_list.append(temp_dict)






#pprint(final_list)
final_list_json = json.dumps(final_list, indent=4, ensure_ascii=False, sort_keys=True)


with open('./json/multiplied_json.json', 'w', encoding='utf-8') as f:
    f.write(final_list_json)

