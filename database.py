import sqlite3
import datetime


class DB:
    def __init__(self):
        db_filename = 'linkshare2.db'
        self.conn = sqlite3.connect(db_filename)
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS links
              (post_id int, url text, username text, votes int,
              title text, image text, time date)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS comments
              (post_id text, comment_id int, comment text, username
              text, votes int, time date)''')

    def submitted(self, url):
        self.cursor.execute('SELECT * FROM links WHERE url=(?)', [url])
        existing = self.cursor.fetchall()
        if not existing:
            return False
        else:
            return True

    def submitted_id(self, post_id):
        self.cursor.execute('SELECT * FROM links WHERE post_id=(?)', [post_id])
        existing = self.cursor.fetchall()
        if not existing:
            return False
        else:
            return True

    def insert_link(self, url, link_username, title, image):
        self.cursor.execute('SELECT * FROM links')
        post_id = len(self.cursor.fetchall())
        time = datetime.datetime.now()
        self.conn.execute('INSERT INTO links VALUES (?, ?, ?, ?, ?, ?, ?)',
                          [post_id, url, link_username, 0, title, image, time])
        self.conn.commit()

    def get_post_list_string(self):
        response_string = "\n"
        links = self.cursor.execute('SELECT * FROM links ORDER BY votes DESC')
        for link in links:
            response_string += str(link)
        return(response_string)

    def get_post_list(self):
        return(self.cursor.execute('''SELECT * FROM links ORDER BY
                                   votes DESC''').fetchall())

    def get_link(self, post_id):
        link = self.cursor.execute('SELECT * FROM links WHERE post_id=(?)',
                                   [post_id])
        return(link.fetchone())

    def upvote_link(self, post_id):
        self.cursor.execute('SELECT * FROM links WHERE post_id=(?)', [post_id])
        exists = self.cursor.fetchone()
        if exists:
            votes = int(exists[3]) + 1
            payee_username = exists[2]
            self.conn.execute('UPDATE links SET votes = ? WHERE post_id = ?',
                              [votes, post_id])
            self.conn.commit()
            return True, payee_username
        else:
            return False, None

    def downvote_link(self, post_id):
        self.cursor.execute('SELECT * FROM links WHERE post_id=(?)', [post_id])
        exists = self.cursor.fetchone()
        if exists:
            votes = int(exists[3]) - 1
            self.conn.execute('UPDATE links SET votes = ? WHERE post_id = ?',
                              (votes, post_id))
            self.conn.commit()
            return True
        else:
            return False

    def insert_comment(self, post_id, comment, username):
        if self.submitted_id(post_id):
            comments = self.cursor.execute('''SELECT * FROM comments WHERE
                                           post_id=(?)''', [post_id])
            comment_id = len(comments.fetchall())
            time = datetime.datetime.now()
            self.conn.execute('INSERT INTO comments VALUES (?, ?, ?, ?, ?, ?)',
                              [post_id, comment_id, comment,
                               username, 0, time])
            self.conn.commit()
            return True
        else:
            return False

    def get_comment_list_string(self, post_id):
        response_string = "\n"
        for link in self.cursor.execute('''SELECT * FROM comments WHERE
                                        post_id=(?) ORDER BY votes DESC''',
                                        [post_id]):
            response_string += str(link) + '\n'
        return(response_string)

    def upvote_comment(self, post_id, comment_id):
        self.cursor.execute('''SELECT * FROM comments WHERE post_id=(?) AND
                            comment_id = ?''', [post_id, comment_id])
        exists = self.cursor.fetchone()
        if exists:
            votes = int(exists[4]) + 1
            payee_username = exists[3]
            self.conn.execute('''UPDATE comments SET votes = ? WHERE
                              post_id =? AND comment_id = ?''',
                              (votes, post_id, comment_id))
            self.conn.commit()
            return True, payee_username
        else:
            return False, None

    def get_comment_list(self, post_id):
        return (self.cursor.execute('''SELECT * FROM comments WHERE post_id =
                                    ? ORDER BY votes DESC''',
                                    [post_id]).fetchall())

    def downvote_comment(self, post_id, comment_id):
        self.cursor.execute('''SELECT * FROM comments WHERE post_id=(?) AND
                            comment_id = ?''', [post_id, comment_id])
        exists = self.cursor.fetchone()
        if exists:
            votes = int(exists[4]) - 1
            self.cursor.execute('''UPDATE comments SET votes = ? WHERE
                                post_id= ? AND comment_id = ?''',
                                (votes, post_id, comment_id))
            self.conn.commit()
            return True
        else:
            return False
