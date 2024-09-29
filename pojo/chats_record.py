from src.enum_tool.question_type_enum import QuestionTypeEnum


class ChatsRecord:
    def __init__(self, uid: int, talk_id: int, chat_type: QuestionTypeEnum, question_type: QuestionTypeEnum,
                 content_txt: str, generate_time: str, audio_url: str = None
                 ):
        self.cid = None
        self.uid = uid
        self.talk_id = talk_id
        self.chat_type = chat_type
        self.question_type = question_type
        self.content_txt = content_txt
        self.audio_url = audio_url
        self.generate_time = generate_time

    def to_dict(self):
        return {
            "cid": self.cid,
            "uid": self.uid,
            "talk_id": self.talk_id,
            "chat_type": self.chat_type,
            "question_type": self.question_type,
            "content_txt": self.content_txt,
            "audio_url": self.audio_url,
            "generate_time": self.generate_time
        }
