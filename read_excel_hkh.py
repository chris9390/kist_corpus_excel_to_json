# -*- coding: utf-8 -*-
from openpyxl import load_workbook, Workbook
from dialogue import *
import json
import re

START_COLUMN_INDEX = 1 # openpyxl는 index 1 부터 시작함

not_all_none = False


def cell_value(row, column):
    global not_all_none
    val = sheet.cell(row=row, column=START_COLUMN_INDEX+column).value
    if type(val) is not str:
        val = str(val)
    val = val.replace("\"", "").rstrip()

    if val == 'None':
        val = None

    if not not_all_none:
        not_all_none = val is not None

    return val


def parse_goal_label(lienum, goal_label_str):
    items = re.findall(r"([^{:,\s]+[^{:,]*):([^,}]*)", goal_label_str)
    dic = dict()
    for item in items:
        if item[1] == 'TRUE':
            dic[item[0]] = 'True'
        elif item[1] == 'FALSE':
            dic[item[0]] = 'False'
        else:
            dic[item[0]] = item[1].strip()
    return dic


def convert2dict(session):
    utters = []
    for utter in session.utters:
        dialog_acts = []
        for dialog_act in utter.dialog_acts:
            dialog_act_dict = {
                "act": dialog_act.act,
                "slot": dialog_act.slot,
                "value": dialog_act.value,
            }
            dialog_acts += [dialog_act_dict]

        utter_dict = {
            "turn_index": utter.turn_index,
            "topic": utter.topic,
            "target_bio": utter.target_bio,
            "speaker": utter.speaker,
            "text": utter.text,
            "semantic_tagged": utter.semantic_tagged,
            "dialog_acts": dialog_acts,
            "goal_label": utter.goal_label,
            "method": utter.method,
            "requested": utter.requested,
        }
        utters += [utter_dict]

    session_dict = {
        "session_id": session.session_id,
        "utters": utters
    }
    return session_dict


if __name__ == '__main__':
    # file = 'domain/schedule/schedule_corpus_20180911.xlsx'
    file = 'export.xlsx'
    # file = 'modify_excel_script/export.xlsx'
    wb = load_workbook(filename=file)
    # sheet = wb.get_sheet_by_name('Sheet1')
    sheet = wb.get_sheet_by_name('Schedule Corpus')
    exception_lines = []

    sessions = []
    session = None
    init_state = True

    for i in range(2, 25290):
        # read cells from excel
        not_all_none = False
        session_id = cell_value(i, 0)
        turn_index = cell_value(i, 1)
        topic = cell_value(i, 2)
        target_bio = cell_value(i, 3)
        speaker = cell_value(i, 4)
        description = cell_value(i, 5)
        semantic_tagged = cell_value(i, 6)
        act = cell_value(i, 7)
        slot = cell_value(i, 8)
        value = cell_value(i, 9)
        goal_label = cell_value(i, 10)
        method = cell_value(i, 11)
        requested = cell_value(i, 12)

        if target_bio is not None and speaker is not None and turn_index is None: # turn_index 체크
            print('exception turn_index, line: %d' % i)
            print(session_id, turn_index, description)

        if topic is not None: # target_bio 체크
            if target_bio not in ('B', 'I', 'O'):
                print('exception target_bio, line: %d' % i)

        if target_bio is not None: # target_bio와 topic이 같이 존재하는지 체크
            if topic is None:
                print('exception target_bio, line: %d' % i)


        if not not_all_none:
            # all cells are None (this is session separator)
            if session is not None:
                sessions += [session]
                session = None

            init_state = True

            continue

        try:
            if turn_index is not None:
                if int(turn_index) == 1:
                    if session_id is not None and not init_state:
                        print('error line: %d' % i)

                    init_state = False

                    if session_id is not None:
                        session = Session(session_id)  # create new session
                        session.utters = []

                # create utterance
                utter = Utterance()
                session.utters += [utter]
                utter.dialog_acts = []

                utter.turn_index = turn_index
                utter.topic = topic
                utter.target_bio = target_bio
                utter.speaker = speaker
                utter.text = description
                utter.semantic_tagged = semantic_tagged

                if goal_label is not None:
                    utter.goal_label = parse_goal_label(i, goal_label)

                utter.method = method

                if requested is not None:
                    utter.requested.append(requested)

                dialog_act = DialogAct()
                if act is None:
                    continue

                dialog_act.act = act
                dialog_act.slot = slot
                dialog_act.value = value
                utter.dialog_acts += [dialog_act]

            elif act is not None:
                # just add additional dialog acts
                if semantic_tagged is not None:
                    utter.semantic_tagged = '%s %s' % (utter.semantic_tagged, semantic_tagged)  # concatenation

                dialog_act = DialogAct()
                dialog_act.act = act
                dialog_act.slot = slot
                dialog_act.value = value
                utter.dialog_acts += [dialog_act]

            else:
                exception_lines += [i]
                # print("exception line: %4d\t please check!!" % i)
        except Exception as e:
            print('line : ', i)
            print(e)
            exit()

    # end of for loop
    print(("\ntotal sessions: %d" % len(sessions)))

    # convert to dictionary
    converted = []
    for session in sessions:
        converted += [convert2dict(session)]

    print(len(converted))
    print(exception_lines)
    # dump sessions
    with open('schedule_corpus_ext2.json', 'w', encoding='utf-8') as wf:
        data = json.dumps(converted, indent=4, sort_keys=True)
        data = bytes(data, 'utf-8').decode('unicode_escape')
        wf.write(data)
        print("Saved corpus ext json file.")
