import sqlite3

def read_quiz_questions(db_path='app.db'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, question, options, answer FROM quiz_questions")
    rows = cursor.fetchall()
    conn.close()
    return rows

if __name__ == '__main__':
    questions = read_quiz_questions()
    for q in questions:
        print(f"ID: {q[0]}")
        print(f"Question: {q[1]}")
        print(f"Options: {q[2]}")
        print(f"Answer: {q[3]}")
        print("-" * 40)
