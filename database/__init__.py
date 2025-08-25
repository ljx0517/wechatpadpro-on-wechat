import os
import sqlite3
from config import conf
import database.pymysqlpool as pymysqlpool

pymysqlpool.logger.setLevel(conf().get('debug') and 'DEBUG' or 'WARN')
DB_PATH = os.path.join(os.path.dirname(__file__), "group_members.db")



class SQLiteConnection:
    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = None

    def cursor(self):
        return SQLiteCursor(self.conn)
    def __enter__(self):
        self.conn = sqlite3.connect(self.db_name)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type:  # An exception occurred
            self.conn.rollback()
        else:
            self.conn.commit()
        self.conn.close()


class SQLiteCursor:
    def __init__(self, conn):
        self.conn = conn

    def __enter__(self):
        return self.conn.cursor()
    def __exit__(self, exc_type, exc_value, traceback):
        pass

def get_connection():
    if use_mysql:
        global mypool
        return mypool.get_connection()
    return SQLiteConnection(DB_PATH)

use_mysql = False
mypool = None
sql_holder = '?'


def init_db():
    # conn = sqlite3.connect(DB_PATH)
    with get_connection() as conn:
        with conn.cursor() as c:
            # 创建群成员表
            c.execute('''
            CREATE TABLE IF NOT EXISTS `group_members` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `group_id` varchar(255) COLLATE utf8mb4_0900_bin DEFAULT NULL,
  `group_name` varchar(255) COLLATE utf8mb4_0900_bin DEFAULT NULL,
  `wxid` varchar(255) COLLATE utf8mb4_0900_bin DEFAULT NULL,
  `display_name` varchar(255) COLLATE utf8mb4_0900_bin DEFAULT NULL,
  `nickname` varchar(255) COLLATE utf8mb4_0900_bin DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  `deleted_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `group_id` (`group_id`,`wxid`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_bin;
                    ''')
            c.execute('''
             CREATE TABLE IF NOT EXISTS `groups` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `group_id` varchar(255) COLLATE utf8mb4_0900_bin DEFAULT NULL,
  `group_name` varchar(255) COLLATE utf8mb4_0900_bin DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `deleted_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `group_id` (`group_id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_bin;
''')
            c.execute('''CREATE TABLE `group_messages` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `msg_id` bigint DEFAULT NULL,
  `group_id` varchar(255) COLLATE utf8mb4_0900_bin DEFAULT NULL,
  `group_name` varchar(255) COLLATE utf8mb4_0900_bin DEFAULT NULL,
  `content` text COLLATE utf8mb4_0900_bin,
  `receiver` varchar(255) COLLATE utf8mb4_0900_bin DEFAULT NULL,
  `create_time` int DEFAULT NULL,
  `type` varchar(255) COLLATE utf8mb4_0900_bin DEFAULT NULL COMMENT 'TEXT = 1  # 文本消息\nVOICE = 2  # 音频消息\nIMAGE = 3  # 图片消息\nFILE = 4  # 文件信息\nVIDEO = 5  # 视频信息\nSHARING = 6  # 分享信息\nEMOJI=7  #表情图片\n\nIMAGE_CREATE = 10  # 创建图片命令\nACCEPT_FRIEND = 19 # 同意好友请求\nJOIN_GROUP = 20  # 加入群聊\nPATPAT = 21  # 拍了拍\nFUNCTION = 22  # 函数调用\nEXIT_GROUP = 23 #退出\n\nNON_USER_MSG = 30  # 来自公众号、腾讯游戏、微信团队等非用户账号的消息\nSTATUS_SYNC  = 51   # 微信客户端的状态同步消息，可以忽略 eggs: 打开/退出某个聊天窗口\n\n',
  `from_user_id` int DEFAULT NULL,
  `from_user_name` varchar(255) COLLATE utf8mb4_0900_bin DEFAULT NULL,
  `from_user_nickname` varchar(255) COLLATE utf8mb4_0900_bin DEFAULT NULL,
  `to_user_id` varchar(255) COLLATE utf8mb4_0900_bin DEFAULT NULL,
  `to_user_nickname` varchar(255) COLLATE utf8mb4_0900_bin DEFAULT NULL,
  `info` json DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `msg_id` (`msg_id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_bin;''')

if conf().get('mysql_hostname') and \
        conf().get('mysql_username') and \
        conf().get('mysql_password') and \
        conf().get('mysql_database'):
    mysql_config = {'host': conf().get('mysql_hostname'),
                    'user':  conf().get('mysql_username'),
                    'password': conf().get('mysql_password'),
                    'database': conf().get('mysql_database'),
                    'autocommit': True}
    mypool = pymysqlpool.ConnectionPool(size=20, maxsize=30, pre_create_num=10,
                                        name='mypool',
                                        **mysql_config)
    use_mysql = True
    sql_holder = '%s'
else:
    init_db()

