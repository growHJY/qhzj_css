from src.utils.mysql_operation import MysqlOperation

if __name__ == '__main__':
    operation = MysqlOperation()
    conn = operation.connect()
    cursor = conn.cursor()
    sql = "insert into chats_record(uid, chat_type, question_type, content_txt, generate_time) values(%s,%s,%s,%s,%s)"
    cursor.execute(sql, (1, '1', '1', "hello", "123456"))
    conn.commit()

    conn.close()