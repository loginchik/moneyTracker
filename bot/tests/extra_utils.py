from aiogram.types import User, Chat, Message, CallbackQuery, Update
from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey, BaseStorage
import datetime


TEST_USER = User(id=123, is_bot=False, first_name='Test1', last_name='bot', 
                 username='test1bot', language_code='ru-RU', is_premium=False)

TEST_USER_CHAT = Chat(id=12, type='private', username=TEST_USER.username, 
                      first_name=TEST_USER.first_name, last_name=TEST_USER.last_name)


def get_message(text: str) -> Message:
    return Message(message_id=123, date=datetime.datetime.now(), 
                   chat=TEST_USER_CHAT, from_user=TEST_USER, text=text)


def get_callback(callback_data: str) -> CallbackQuery:
    return CallbackQuery(id='callback', from_user=TEST_USER, chat_instance='chat_inst', 
                         message=get_message('some text'), data=callback_data)

    
def get_update(message: Message = None, call: CallbackQuery = None) -> Update:
    return Update(
        update_id=190, 
        message=message if message else None, 
        callback_query=call if call else None, 
    )
    
    
class TestHandlerBase:
    user = TEST_USER
    user_chat = TEST_USER_CHAT
    
    def make_state(self, storage: BaseStorage, bot: Bot) -> FSMContext:
        state = FSMContext(
            storage=storage, 
            key=StorageKey(
                bot_id=bot.id, 
                chat_id=self.user_chat.id, 
                user_id=self.user.id
            )
        )
        return state