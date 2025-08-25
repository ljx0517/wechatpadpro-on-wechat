import sys
import traceback

import plugins
from bot import bot_factory
from bridge.bridge import Bridge
from bridge.context import ContextType
from bridge.reply import Reply, ReplyType
from cache import data_cache
from channel.chat_channel import check_prefix, check_contain
from channel.chat_message import ChatMessage
import database.group_messages as db_msg
from plugins import *
from voice import voice
from voice.audio_convert import any_to_wav
from voice.factory import create_voice


@plugins.register(
    name="ChatLogger",
    namecn="ChatLogger",
    desire_priority=899,
    enabled=True,
    desc="群聊记录",
    version="1.0",
    author="Jaxon")
class ChatLogger(Plugin):
    def __init__(self):
        super().__init__()
        # btype = Bridge().btype['chat']
        # self.bot = bot_factory.create_bot(btype)
        voice_to_text_engine = conf().get('voice_to_text', False)
        if voice_to_text_engine:
            self.voiceEngine = create_voice(voice_to_text_engine)

        self.handlers[Event.ON_RECEIVE_MESSAGE] = self.on_receive_message
        self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context
        self.handlers[Event.ON_SEND_REPLY] = self.on_handle_before_send


    def on_handle_context(self, e_context: EventContext):
        # content = e_context['context']['content']
        context = e_context['context']
        file_path = context.content
        msg_id = e_context['context'].kwargs['msg'].msg_id
        if context.get("isgroup", False) and context.type == ContextType.VOICE and os.path.exists(file_path):  # 群聊
            # 在wxpad_message.py中已经处理好了文件路径，这里直接使用
            # 但保留对老版本客户端的兼容
            if file_path.endswith((".silk", ".sil", ".slk")):
                mp3_path = os.path.splitext(file_path)[0] + ".mp3"
                if os.path.exists(mp3_path):
                    logger.info(f"[chat_channel] 检测到SILK文件，使用同名MP3文件: {mp3_path}")
                    file_path = mp3_path

            wav_path = os.path.splitext(file_path)[0] + ".wav"
            try:
                any_to_wav(file_path, wav_path)
            except Exception as e:  # 转换失败，直接使用mp3，对于某些api，mp3也可以识别
                logger.warning("[chat_channel]any to wav error, use raw path. " + str(e))
                wav_path = file_path
            text = self.voiceEngine.voiceToText(wav_path)
            db_msg.update_voice_message_text(msg_id, {'text': text.content})


        # logger.debug("[ChatLogger]content: {}".format(content))
        # if content.startswith('$hello'):
        #     reply = Reply(ReplyType.TEXT, '你好！')
        #     e_context['reply'] = reply
        #     e_context.action = EventAction.BREAK_PASS

    def on_receive_message(self, e_context: EventContext):
        # btype = Bridge().btype['voice_to_text']
        # btype.voiceToText(voiceFile)
        logger.debug("[ChatLogger] {}".format(e_context))
        context = e_context['context']
        cmsg: ChatMessage = e_context['context']['msg']
        username = None
        session_id = cmsg.from_user_id
        if conf().get('channel_type', 'wx') == 'wx' and cmsg.from_user_nickname is not None:
            session_id = cmsg.from_user_nickname  # itchat channel id会变动，只好用群名作为session id

        if context.get("isgroup", False):
            username = cmsg.actual_user_nickname
            if username is None:
                username = cmsg.actual_user_id
        else:
            username = cmsg.from_user_nickname
            if username is None:
                username = cmsg.from_user_id
        logger.debug("[ChatLogger]content: {}".format(context))

        from_user_id = cmsg.from_user_id
        from_user_name = cmsg.actual_user_nickname
        from_user_nickname = cmsg.from_user_nickname
        to_user_id = cmsg.from_user_nickname
        to_user_nickname = cmsg.from_user_nickname
        is_triggered = False
        content = context.content
        if context.get("isgroup", False):  # 群聊
            if context.type == ContextType.TEXT or context.type == ContextType.VOICE:
                try:
                    id = db_msg.insert_chat_group_message(cmsg.msg_id, cmsg.group_name, cmsg.group_id,
                                                     content, context.kwargs.get('receiver', None),
                                                     context.kwargs['msg'].create_time,
                                                     context.type.name, from_user_id, from_user_name,
                                                     from_user_nickname, to_user_id, to_user_nickname
                    )

                    message_expires_in_seconds = int(conf().get('message_expires_in_seconds', 0))
                    if message_expires_in_seconds:
                        data_cache.setex(f'''message:{cmsg.msg_id}''', message_expires_in_seconds, 1)
                except Exception as e:
                    exc_type, exc_value, exc_traceback = sys.exc_info()
                    stack_info = ''.join(traceback.format_tb(exc_traceback))
                    logger.debug(stack_info)

        e_context.action = EventAction.BREAK_PASS
    def on_handle_before_send(self, e_context: EventContext):
        pass
        e_context.action = EventAction.BREAK_PASS


