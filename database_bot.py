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

    def create_guild_table(self):
        sql_create_guild_table = """CREATE TABLE IF NOT EXISTS guilds(
                                            guild text PRIMARY KEY NOT NULL,
                                            channel text NOT NULL
                                            )"""
        conn = self.create_connection()

        # create tables
        print(conn)
        if conn is not None:
            # create table
            self.create_table(conn, sql_create_guild_table)

        else:
            print("Error! cannot create the database connection.")

    def insert_values_bot(self, values):
        conn = self.create_connection()
        with conn:
            # tasks
            if type(values) == list and len(values) == 4:
                self.create_bot(conn, values)
            else:
                print('Incorrect format')

    def create_bot(self, conn, task):

        sql = ''' INSERT INTO bot(user,messaged,user_time,blocked)
                  VALUES(?,?,?,?) '''
        cur = conn.cursor()
        try:
            cur.execute(sql, task)
        except sqlite3.IntegrityError as e:
            pass
        return cur.lastrowid

    def create_guild(self, conn, task):

        sql = ''' INSERT INTO guilds(guild,channel) VALUES(?,?) '''
        cur = conn.cursor()
        try:
            cur.execute(sql, task)
        except sqlite3.IntegrityError as e:
            pass
        return cur.lastrowid

    def insert_values_guild(self, values):
        conn = self.create_connection()
        with conn:
            # tasks
            if type(values) == list and len(values) == 2:
                self.create_guild(conn, values)
            else:
                print('Incorrect format')

    def select_all_bot_tasks(self, conn):
        cur = conn.cursor()
        cur.execute("SELECT * FROM bot")

        rows = cur.fetchall()

        for row in rows:
            print(row)

    def select_all_guild_tasks(self, conn):
        cur = conn.cursor()
        cur.execute("SELECT * FROM guilds")

        rows = cur.fetchall()

        for row in rows:
            print(row)

    def read_database(self):
        conn = self.create_connection()
        with conn:
            print('--BOT DATABASE--')
            self.select_all_bot_tasks(conn)
            print('--GUILD DATABASE--')
            self.select_all_guild_tasks(conn)

    def read_user(self, user):
        conn = self.create_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM bot WHERE user = ?", [user])
        print([x for x in cur])

    def read_guild(self, guild):
        conn = self.create_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM guilds WHERE guild = ?", [guild])
        print([x for x in cur])

    def restart_database(self):
        conn = self.create_connection()
        cur = conn.cursor()
        cur.execute("""DROP TABLE IF EXISTS bot""")
        cur.execute("""DROP TABLE IF EXISTS guilds""")
        self.create_bot_table()
        self.create_guild_table()

    def update_timer(self, user, timer):
        sql = """ UPDATE bot
                  SET user_time = ?
                  WHERE user = ?
        """
        conn = self.create_connection()
        curr = conn.cursor()
        curr.execute(sql, [timer, user])
        conn.commit()
        self.read_user(user)

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
        self.read_user(user)

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
        self.read_user(user)

    def update_guild(self, guild, channel):
        sql = """ UPDATE guilds
                  SET channel = ?
                  WHERE guild = ?
        """
        conn = self.create_connection()
        curr = conn.cursor()
        curr.execute(sql, [channel, guild])
        conn.commit()
        self.read_guild(guild)

    def get_messaged_users(self):
        sql = """SElECT user FROM bot WHERE messaged = 1"""
        conn = self.create_connection()
        curr = conn.cursor()
        rows = curr.execute(sql)
        return [x[0] for x in rows]

    def get_blocked_users(self):
        sql = """SElECT user FROM bot WHERE blocked = 1"""
        conn = self.create_connection()
        curr = conn.cursor()
        rows = curr.execute(sql)
        return [x[0] for x in rows]

    def get_user_timings(self):
        sql = """SElECT user, user_time FROM bot"""
        conn = self.create_connection()
        curr = conn.cursor()
        rows = curr.execute(sql)
        return {x[0]: x[1] for x in rows}

    def get_guilds(self):
        sql = """SElECT guild, channel FROM guilds"""
        conn = self.create_connection()
        curr = conn.cursor()
        rows = curr.execute(sql)
        return {x[0]: x[1] for x in rows}

#bot = databse_bot(r"c:\users\Steven\PycharmProjects\HydrationBot\DiscordHydrationBot\BOT.db")
# #bot.create_bot_table()

