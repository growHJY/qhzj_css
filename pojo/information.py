class Information:
    def __init__(self, aid, uid, category, title, cover_img, content, publish_time, views):
        self.aid = aid
        self.uid = uid
        self.category = category
        self.title = title
        self.cover_img = cover_img
        self.content = content
        self.publish_time = publish_time
        self.views = views

    def to_dict(self):
        return {
            'aid': self.aid,
            'uid': self.uid,
            'category': self.category,
            'title': self.title,
            'cover_img': self.cover_img,
            'content': self.content,
            'publish_time': self.publish_time,
            'views': self.views
        }
