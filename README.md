# KIST 로봇 코퍼스 처리를 위한 스크립트

## JSON 샘플 포맷
### Corpus 포맷

    [
        {
            "session_id": "ec066fb3-6b19-4dff-b32d-4955154af11f",
            "utters": [
                {
                    "dialog_acts": [
                        {
                            "act": "welcomemsg",
                            "slot": null,
                            "value": null
                        }
                    ],
                    
                    "semantic_tagged": "안녕하세요, 무엇을 도와드릴까요?",
                    "speaker": "System",
                    "text": "안녕하세요, 무엇을 도와드릴까요?",
                    "text_spaced": "안녕하세요, 무엇을 도와드릴까요?",
                    "topic": "OPENING",
                    "turn_index": "1"
                },
                {
                    "dialog_acts": [
                        {
                            "act": "inform",
                            "slot": "system_action",
                            "value": "create"
                        }
                    ],
                   
                    "semantic_tagged": "일정 등록해줘",
                    "speaker": "User",
                    "text": "일정 등록해줘",
                    "text_spaced": "일정 등록해줘",
                    "topic": "SCHEDULE",
                    "turn_index": "1"
                }
                ...
            ]
        }
    ...
    ]
  
### Ontology 포맷
    {
        'date': [
            '오늘',
            '내일',
            '모레'
        ],
        'time': [
            ...
        ]
    ...
    }

## WPM Decoder
입력 텍스트를 Word Piece Model에 의해 새로 tokenize 하는 모듈. 아래와 같이 실행할 수 있다.

```
wpm = wpm_decoder('textDB.json')

text = '내일 12시에 산책가기일정을 등록해줘'
result = wpm.decode(text)

print(result)

```
출력 결과는 아래와 같다.

```
_내일_ _1 2 시에_ _산책 가 기 일정을_ _등록 해줘_
```

      