from pprint import pprint
import json
import copy
import itertools




with open('ontology_json.json', encoding='utf-8') as json_file:
    ontology_dict = json.load(json_file)


with open('result_json.json', encoding='utf-8') as json_file:
    result_json_list = json.load(json_file)



final_list = []

for each_elem in result_json_list:

    each_utter = each_elem['utters'][0]


    dialog_acts_list = each_utter['dialog_acts']


    target_slots = {}
    list_temp = []
    current_slots = []
    current_values = []

    for i in dialog_acts_list:
        if i['slot'] == None:
            continue
        target_slots[i['slot']] = ontology_dict[i['slot']]
        list_temp.append(ontology_dict[i['slot']])

        # ontology_combs_list의 각 튜플의 인덱스의 ontology(slot) 종류
        current_slots.append(i['slot'])
        current_values.append(i['value'])


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






    # =========================================================================================================
    '''
    for i in dialog_acts_list:
        ontology_col_name = i['slot']
        value = i['value']



        if ontology_col_name != None:

            if value == None:
                continue

            for ontology_elem in ontology_dict[ontology_col_name]:

                # immutable객체속성으로 복사
                each_utter_copy = copy.deepcopy(each_utter)

                if ontology_elem == value:
                    continue

                # 디버깅용 코드
                if len(dialog_acts_list) >= 2:
                    a = 1

                # 원본에서 ontology부분만 다양하게 replace해준다.
                each_utter_copy['text'] = each_utter['text'].replace(value, ontology_elem)
                each_utter_copy['dialog_acts'][i_idx]['value'] = ontology_elem

                temp_dict = {}
                temp_dict['session_id'] = ''
                temp_dict['utters'] = [each_utter_copy]

                result_list_copy.append(temp_dict)

        i_idx += 1
        '''



#pprint(final_list)
final_list_json = json.dumps(final_list, indent=4, ensure_ascii=False, sort_keys=True)


with open('multiplied_json.json', 'w', encoding='utf-8') as f:
    f.write(final_list_json)

