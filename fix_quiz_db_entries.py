import sqlite3

def fix_quiz_db(db_path='app.db'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT id, options, answer FROM quiz_questions')
    rows = cursor.fetchall()
    for row in rows:
        qid = row[0]
        options = row[1]
        answer = row[2]
        # Fix options: ensure comma and space separated
        options_list = [opt.strip() for opt in options.split(',')]
        fixed_options = ', '.join(options_list)
        # Fix answer: strip whitespace
        fixed_answer = answer.strip()
        cursor.execute('UPDATE quiz_questions SET options = ?, answer = ? WHERE id = ?', (fixed_options, fixed_answer, qid))
    conn.commit()
    conn.close()
    print("Database quiz_questions entries fixed.")

if __name__ == '__main__':
    fix_quiz_db()
