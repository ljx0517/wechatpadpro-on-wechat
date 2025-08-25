import json
import sqlite3
import os
from common.log import logger
from database import get_connection, sql_holder



def update_voice_message_text(msg_id, info):
    with get_connection() as conn:
        with conn.cursor() as c:
            sql = f'''
                    update group_messages set info = {sql_holder} where msg_id = {sql_holder};
            '''
            val = info
            if not isinstance(info, str):
                val = json.dumps(info)
            params = (
                val, msg_id
            )
            # print(sql % params)
            c.execute(sql, params)
            return c.lastrowid


def insert_chat_group_message(msg_id: int, group_name: str, group_id: str,
                              content: str, receiver: str, create_time: str,
                              type: int, from_user_id: str, from_user_name: str,
                              from_user_nickname: str, to_user_id: str, to_user_nickname: str):
    with get_connection() as conn:
        with conn.cursor() as c:
            sql = f'''
                                insert ignore INTO group_messages (msg_id, group_name, group_id, content, receiver, 
                                create_time, type, from_user_id, from_user_name, from_user_nickname, to_user_id, 
                                to_user_nickname)
                                VALUES ({sql_holder}, {sql_holder}, {sql_holder}, {sql_holder},{sql_holder} ,{sql_holder},
                                {sql_holder},{sql_holder},{sql_holder},{sql_holder},{sql_holder},{sql_holder})
                            '''
            params = (
                msg_id, group_name, group_id,
            content, receiver, create_time,
            type, from_user_id, from_user_name,
            from_user_nickname, to_user_id, to_user_nickname
            )
            # print(sql % params)
            c.execute(sql, params)
            return c.lastrowid
