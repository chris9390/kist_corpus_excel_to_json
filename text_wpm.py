import json
import re
from wpm.wpm_decoder_v2 import wpm_decoder

new_unit = {
    '_MM월': 100,
    '_MM월_': 100,
    '_DD일': 100,
    '_DD일_': 100,
    '_HH시': 100,
    '_HH시_': 100,
    '_NN분': 100,
    '_NN분_': 100,
    '_HH시간_': 100,
    '_n개': 100,
    '_n개_': 100,
    '_정오': 100,
    '_정오_': 100,
    '_회의': 100,
    '_결혼식': 100,
    '_먹기': 100,
    # '_롯데월드': 100
}

if __name__ == '__main__':

    with open('wpm/textTrainAllSystemUnitDB1315v2.json', 'r', encoding='utf-8') as f:
        unitDB = json.load(f)

    unitDB.update(new_unit)

    act_list = []
    seq_in_list = []
    seq_out_list = []

    new_unitDB_file = 'wpm/new_unitDB.json'
    with open(new_unitDB_file, 'w', encoding='utf-8') as f:
        json.dump(unitDB, f, indent=4, ensure_ascii=False)

    wpm = wpm_decoder(new_unitDB_file)

    with open('multiplied_json.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

        for session in data:
            session_id = session['session_id']

            for turn in session['utters']:
                turn_index = turn['turn_index']
                cleaned_text = None
                text = turn['text']
                semantic_tagged = turn['semantic_tagged']
                dialog_acts = turn['dialog_acts']

                result = wpm.decode(text)

                #
                # '는'으로 끝나는 것
                #
                find_result = re.findall(r'(?<![_\s])에는_', result)

                if len(find_result) > 0:
                    result = re.sub(r'(?<![_\s])에는_', ' 에는_', result)
                else:
                    result = re.sub(r'(?<![_\s])는_', ' 는_', result)

                #
                # '데'로 끝나는 것
                #
                find_result = re.findall(r'(?<![_\s])인데_', result)

                if len(find_result) > 0:
                    result = re.sub(r'(?<![_\s])인데_', ' 인데_', result)
                else:
                    result = re.sub(r'(?<![_\s])인_', ' 인_', result) # _엄마_ _생일인_ _거_

                #
                # '로'로 끝나는 것
                #
                find_result = re.findall(r'(?<![_\s])으로_', result)

                if len(find_result) > 0:
                    result = re.sub(r'(?<![_\s])으로_', ' 으로_', result) # _정기검진으로_
                else:
                    result = re.sub(r'(?<![_\s])로_', ' 로_', result) # _내일로_

                result = re.sub(r'(?<![_\s])부터_', ' 부터_', result)
                result = re.sub(r'(?<![_\s])까지_', ' 까지_', result)

                result = re.sub(r'(?<![_\s])에_', ' 에_', result)

                result = re.sub(r'(?<![_\s])을_', ' 을_', result)
                result = re.sub(r'(?<![_\s])를_', ' 를_', result)

                result = re.sub(r'(?<![_\s])은_', ' 은_', result)
                result = re.sub(r'(?<![_\s])이_', ' 이_', result)
                result = re.sub(r'(?<![_\s])가_', ' 가_', result)

                result = re.sub(r'(?<![_\s])라고_', ' 라고_', result)
                result = re.sub(r'(?<![_\s])이고_', ' 이고_', result)

                result = re.sub(r'(?<![_\s])이라_', ' 이라_', result) # 엄마_ _생신이라_
                result = re.sub(r'(?<![_\s])이 라고_', ' 이 라고_', result)  # _검 진이 라고_

                result = re.sub(r'(?<![_\s])쯤_', ' 쯤_', result)  # _내일쯤_
                result = re.sub(r'(?<![_\s])도_', ' 도_', result) # _내일도_

                result = re.sub(r'(?<![_\s])할_', ' 할_', result) # _방문할_ _거야_
                result = re.sub(r'(?<![_\s])갈_', ' 갈_', result)  # _병원갈_ _거야_
                result = re.sub(r'(?<![_\s])갈 ', ' 갈 ', result)  # _병원갈 거야_

                # result = re.sub(r'(?<![_\s])랑_', ' 랑_', result)  # _친구랑_ _만날_


                # if len(dialog_acts) == 1:
                #     continue

                print()

                results = result.split()

                bio_seq = []
                for i, wpm_token in enumerate(results):
                    bio_seq.append('O')


                act_label = None

                for dialog_act in dialog_acts:
                    print(dialog_act)
                    if dialog_act['slot'] == 'system_action' or dialog_act['slot'] == 'slot':
                        continue

                    if dialog_act['slot'] and not dialog_act['value']:
                        print('\n### Error : value not exist!')
                        print(session)
                        exit()
                    if dialog_act['value']:
                        if not act_label:
                            act_label = dialog_act['act']
                        else:
                            if act_label != dialog_act['act']:
                                print('\n### Error : act is not same!')
                                exit()

                        # if dialog_act['value'] == 'dontcare':
                        #     continue
                        #
                        # if dialog_act['value'] == '0개':
                        #     continue

                        values = dialog_act['value'].split()

                        wpm_token_idx = []

                        wpm_string = result.replace('_', '')

                        token_idx = 0
                        for wpm_char in wpm_string:
                            if wpm_char == ' ':
                                token_idx += 1
                                continue

                            wpm_token_idx.append(token_idx)



                        same_count = 0
                        has_sub_seq = False
                        wpm_idx = 0
                        bio_idx = []
                        total_space_count = 0
                        last_idx = 0

                        value_no_space = ''.join(values)
                        for char in value_no_space:
                            space_count = 0
                            for k, wpm_char in enumerate(wpm_string[wpm_idx:]):
                                last_idx = wpm_idx + k

                                if wpm_char == ' ':
                                    space_count += 1
                                    total_space_count += 1
                                    continue

                                if char == wpm_char:
                                    char_idx = last_idx - total_space_count

                                    if wpm_idx == 0:
                                        same_count += 1

                                        if wpm_token_idx[char_idx] not in bio_idx:
                                            bio_idx.append(wpm_token_idx[char_idx])

                                    elif wpm_idx > 0 and k - space_count == 0: # 같은 시퀀스
                                        same_count += 1

                                        if wpm_token_idx[char_idx] not in bio_idx:
                                            bio_idx.append(wpm_token_idx[char_idx])

                                    else:
                                        break

                                    wpm_idx += k + 1

                                    if same_count == len(value_no_space): # value의 크기와 일치하는 갯수가 같은 경우에 대해서 처리
                                        if len(wpm_string) == wpm_idx: # value가 문장 마지막에 등장하는 경우.
                                            has_sub_seq = True
                                        else:
                                            if wpm_string[wpm_idx] != ' ': # value가 문장 중간에 등장할 경우, 다음 값이 스페이스인지를 확인함.
                                                has_sub_seq = False
                                            else:
                                                has_sub_seq = True
                                    break

                            if has_sub_seq:
                                break

                        if not has_sub_seq:

                            print('\nsession_id :', session_id)
                            print('WPM result :', result)
                            print(wpm_string)
                            print('DA value :', dialog_act['value'])
                        else:
                            print(bio_idx)

                            for i, idx in enumerate(bio_idx):
                                if i == 0:
                                    bio_seq[idx] = 'B-' + dialog_act['slot'].upper()
                                else:
                                    bio_seq[idx] = 'I-' + dialog_act['slot'].upper()

                print(result)

                seq_out = ' '.join(bio_seq)
                print(seq_out)
                print(act_label)

                seq_in_list.append(result)
                seq_out_list.append(seq_out)
                act_list.append(act_label)

                if not act_label:
                    print('act cannot none.')
                    exit()


    with open('./seq.in', 'w', encoding='utf-8') as f:
        for elem in seq_in_list:
            f.write(elem + '\n')

    with open('./seq.out', 'w', encoding='utf-8') as f:
        for elem in seq_out_list:
            f.write(elem + '\n')

    with open('./label', 'w', encoding='utf-8') as f:
        for elem in act_list:
            f.write(elem + '\n')


    print("Finished!")