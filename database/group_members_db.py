import sqlite3
import os
from common.log import logger
import os
from common.log import logger
from config import conf
import database.pymysqlpool as pymysqlpool
from database import get_connection, sql_holder

pymysqlpool.logger.setLevel('DEBUG')
DB_PATH = os.path.join(os.path.dirname(__file__), "group_members.db")



















def save_group_members_to_db(group_id, members):
    with get_connection() as conn:
        with conn.cursor() as c:
            for member in members:
                # 修正字段名：实际API返回的是小写字段名
                user_name = member.get("user_name") or member.get("UserName") or member.get("wxid")
                nick_name = member.get("nick_name") or member.get("NickName") or member.get("nickname")
                display_name = member.get("display_name") or member.get("DisplayName")

                c.execute(f'''
                    insert INTO group_members (group_id, wxid, display_name, nickname)
                    VALUES ({sql_holder}, {sql_holder}, {sql_holder}, {sql_holder})
                    ON DUPLICATE KEY UPDATE display_name={sql_holder}, nickname={sql_holder}
                ''', (
                    group_id,
                    user_name,
                    display_name,
                    nick_name,
                    display_name,
                    nick_name,
                ))

def get_group_member_from_db(group_id, wxid):
    with get_connection() as conn:
        with conn.cursor() as c:
            c.execute(f'''
                SELECT group_name, display_name, nickname FROM group_members WHERE group_id={sql_holder} AND wxid={sql_holder}
            ''', (group_id, wxid))
            row = c.fetchone()
            if row:
                return {"display_name": row[0], "nickname": row[1]}
            return None

def save_group_info(group_id, group_name):
    """保存群名称到现有表"""
    with get_connection() as conn:
        with conn.cursor() as c:
            # 更新该群的所有记录，添加群名称
            # c.execute(f'''
            #     UPDATE group_members SET group_name = {sql_holder} WHERE group_id = {sql_holder}
            # ''', (group_name, group_id))
            c.execute(f'''
                        insert INTO group_members (group_id, group_name) values ({sql_holder} ,{sql_holder}) ON DUPLICATE KEY UPDATE group_name={sql_holder} 
                        ''', (group_name, group_id, group_name))
            c.execute(f'''
                        insert INTO `groups` (group_id, group_name) values ({sql_holder} ,{sql_holder}) ON DUPLICATE KEY UPDATE group_name={sql_holder} 
                        ''', (group_id, group_name, group_name))
            logger.debug(f"[db] 保存群名称: {group_id} -> {group_name}")

def get_group_id_by_name(group_name: list):
    placeholders = [sql_holder]
    is_list = False
    if isinstance(group_name, list):
        is_list = True
        placeholders = ', '.join([sql_holder] * len(group_name))
    """从现有表获取群名称"""
    with get_connection() as conn:
        with conn.cursor() as c:
            c.execute(f'''
                SELECT group_id, group_name FROM `groups` WHERE group_name in ({placeholders}) AND group_name IS NOT NULL LIMIT 1
            ''', tuple(group_name))
            rows = c.fetchall()
            return rows



def get_group_name_from_db(group_id):
    """从现有表获取群名称"""
    with get_connection() as conn:
        with conn.cursor() as c:
            c.execute(f'''
                SELECT group_name FROM `groups` WHERE group_id={sql_holder} AND group_name IS NOT NULL LIMIT 1
            ''', (group_id,))
            row = c.fetchone()
            if row and row[0]:
                return row[0]
            return None

def get_user_nickname_from_db(wxid):
    # TODO
    """从群成员数据库获取用户昵称（任意一个群中的昵称）"""
    with get_connection() as conn:
        with conn.cursor() as c:
            # 从群成员表中查找该用户的昵称（取任意一个群中的昵称）
            c.execute(f'''
                SELECT nickname FROM group_members WHERE wxid={sql_holder} AND nickname IS NOT NULL LIMIT 1
            ''', (wxid,))
            row = c.fetchone()
            if row and row[0]:
                return row[0]
            return None