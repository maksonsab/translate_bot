import os
import datetime

from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.exceptions import TerminatedByOtherGetUpdates
import aiohttp
import langid


YANDEX_CATALOG_ID = os.environ.get('YANDEX_CATALOG_ID')
TELEGRAM_BOT_API = os.environ.get('TELEGRAM_BOT_API')
YANDEX_OAUTH = os.environ.get('YANDEX_OAUTH')


bot = Bot(token=TELEGRAM_BOT_API)
dp = Dispatcher(bot)
token = None
langid.set_languages(['de', 'en', 'ru'])


async def get_IAM_token() -> str:
    url = 'https://iam.api.cloud.yandex.net/iam/v1/tokens'
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json={'yandexPassportOauthToken': YANDEX_OAUTH}) as response:
            token = await response.json()
        return token


def is_token_valid(token: datetime.datetime.fromisoformat) -> bool:
    '''return False if token expired'''
    now = datetime.datetime.now(tz=datetime.timezone.utc)
    return token > now

async def detect_language(text: str) -> str:
    global token
    if not token or not is_token_valid(datetime.datetime.fromisoformat(token["expiresAt"])):
        token = await get_IAM_token()
    url = 'https://translate.api.cloud.yandex.net/translate/v2/detect'
    headers = {
        'Content-Type': 'application/json', 
        'Authorization': f'Bearer {token["iamToken"]}',
        }
    data = {
        'folderId': YANDEX_CATALOG_ID,
        'languageCodeHints' :['de'],
        'text': text,
        }
    async with aiohttp.ClientSession() as session:    
        async with session.post(url=url, json=data, headers=headers) as resp:
            response = await resp.json()
            return response



async def translate_message(message: str) -> str:
    global token
    if not token or not is_token_valid(datetime.datetime.fromisoformat(token["expiresAt"])):
        print('Requesting a new token')
        token = await get_IAM_token()
        print(token)
    else:
        print('WE HAVE A TOKEN')
    url = "https://translate.api.cloud.yandex.net/translate/v2/translate"
    data = {
        "folderId": YANDEX_CATALOG_ID,
        "texts": [message],
        "targetLanguageCode": 'ru'
        }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token['iamToken']}"
            }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url=url, json=data, headers=headers) as resp:
            response = await resp.json()
            return response['translations'][0]['text']


@dp.message_handler(lambda message: message.text and -1001775371117 == message.chat.id) #(-1001775371117 == message.chat.id and message.from_user == 2091201972))
async def get_all_messages(message: types.Message):
    
    if langid.classify(message.text)[0] != 'ru':
        lang = await detect_language(text=message.text)
        if lang['languageCode'] == 'de':
            answer = await translate_message(message.text)
            await message.reply(answer)
    else: 
        pass

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
