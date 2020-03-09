import sqlite3
from sqlite3 import Error


class databse_bot():

    def __init__(self, db_file):
        self.db_file = db_file

    def create_connection(self):
        conn = None
        try:
            conn = sqlite3.connect(self.db_file)
        except Error as e:
            print(e)
        return conn

    def create_table(self, conn, create_table_sql):
        """ create a table from the create_table_sql statement
        :param conn: Connection object
        :param create_table_sql: a CREATE TABLE statement
        :return:
        """
        try:
            c = conn.cursor()
            c.execute(create_table_sql)
        except Error as e:
            print(e)

    def create_bot_table(self):
        sql_create_bot_table = """CREATE TABLE IF NOT EXISTS bot(
                                    user text PRIMARY KEY NOT NULL,
                                    messaged integer NOT NULL,
                                    user_time integer NOT NULL,
                                    blocked integer NOT NULL
                                    )"""
        conn = self.create_connection()

        # create tables
        if conn is not None:
            # create table
            self.create_table(conn, sql_create_bot_table)

        else:
            print("Error! cannot create the database connection.")

    def insert_values(self, values):
        conn = self.create_connection()
        with conn:
            # tasks
            if type(values) == list and len(values) == 4:
                self.create_task(conn, values)
            else:
                print('Incorrect format')

    def create_task(self, conn, task):

        sql = ''' INSERT INTO bot(user,messaged,user_time,blocked)
                  VALUES(?,?,?,?) '''
        cur = conn.cursor()
        cur.execute(sql, task)
        return cur.lastrowid

    def select_all_tasks(self, conn):
        cur = conn.cursor()
        cur.execute("SELECT * FROM bot")

        rows = cur.fetchall()

        for row in rows:
            print(row)

    def read_database(self):
        conn = self.create_connection()
        with conn:
            self.select_all_tasks(conn)

    def restart_database(self):
        conn = self.create_connection()
        cur = conn.cursor()
        cur.execute("""DROP TABLE IF EXISTS bot""")
        self.create_bot_table()

    def update_timer(self, user, timer):
        sql = """ UPDATE bot
                  SET user_time = ?
                  WHERE user = ?
        """
        conn = self.create_connection()
        curr = conn.cursor()
        curr.execute(sql, [timer, user])
        conn.commit()
        self.read_database()

    def update_ban(self, user, ban_bool):
        sql = """ UPDATE bot
                  SET blocked = ?
                  WHERE user = ?
        """

        ban_bool_int = 1 if ban_bool is True else 0

        conn = self.create_connection()
        curr = conn.cursor()
        curr.execute(sql, [ban_bool_int, user])
        conn.commit()
        self.read_database()


    def update_messaged(self, user, messaged_bool):
        sql = """ UPDATE bot
                  SET messaged = ?
                  WHERE user = ?
        """

        messaged_int = 1 if messaged_bool is True else 0

        conn = self.create_connection()
        curr = conn.cursor()
        curr.execute(sql, [messaged_int, user])
        conn.commit()
        self.read_database()


# insert_values(r"c:\users\Steven\PycharmProjects\HydrationBot\DiscordHydrationBot\BOT.db")
