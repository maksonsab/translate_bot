# TRANSLATE BOT
A simple [Telegram](https://telegram.org/) bot which translates messages in group chat. Translating works by [Yandex Translate](https://cloud.yandex.ru/services/translate).

To reduce API requests, by default bot handles messages for exact user in specific chat.

## Required environ variables
    TELEGRAM_BOT_API
    TELEGRAM_CHAT_ID
    TELEGRAM_TARGET_USER_ID
    YANDEX_CATALOG_ID
    YANDEX_OAUTH 
