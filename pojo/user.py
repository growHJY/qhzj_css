class User:
    def __init__(self, uid, name, sname, uphone, password):
        self.uid = uid
        self.uname = name
        self.sname = sname
        self.pwd = password
        self.uphone = uphone

    def to_dict(self):
        return {
            "uid": self.uid,
            "uname": self.uname,
            "sname": self.sname,
            "pwd": self.pwd,
            "uphone": self.uphone
        }
