import os

import langid
from aiogram import Bot, Dispatcher, executor, types

from translate import yandex_translate

try:
    TELEGRAM_BOT_API = os.environ.get('TELEGRAM_BOT_API')
    TELEGRAM_CHAT_ID = int(os.environ['TELEGRAM_CHAT_ID'])
    TELEGRAM_TARGET_USER_ID = int(os.environ['TELEGRAM_TARGET_USER'])
    YANDEX_CATALOG_ID = os.environ.get('YANDEX_CATALOG_ID')
    YANDEX_OAUTH = os.environ.get('YANDEX_OAUTH')
    TRANSLATE_FROM = 'de'
except KeyError:
    print('No environment variables was set.')
    exit()
except ValueError:
    print('Not correct evironment vars.')
    exit()


bot = Bot(token=TELEGRAM_BOT_API)
dp = Dispatcher(bot)
token = None
langid.set_languages(['de', 'en', 'ru'])




@dp.message_handler(lambda message: message.text and (TELEGRAM_CHAT_ID == message.chat.id and message.from_user == TELEGRAM_TARGET_USER_ID))
async def get_all_messages(message: types.Message):
    """This handler works with messages from the exact user in specific chat. 
    If you want to handle all messages please delete the lambda function from 'message_handler'.
    """
    if langid.classify(message.text)[0] != 'ru':
        if lang:= await translate._detect_lang(message.text) == TRANSLATE_FROM:
            answer = await translate.translate(message.text)
            print(message.from_user)
            await message.reply(answer)
    else: 
        pass


if __name__ == '__main__':
    translate = yandex_translate(YANDEX_OAUTH, YANDEX_CATALOG_ID, translate_to='de')
    executor.start_polling(dp, skip_updates=True)
    
