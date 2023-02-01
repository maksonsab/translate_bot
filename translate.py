import datetime

from aiohttp import ClientSession

class yandex_translate():

    actions = {
        'get_token' : 'https://iam.api.cloud.yandex.net/iam/v1/tokens',
        'detect_lang' : 'https://translate.api.cloud.yandex.net/translate/v2/detect',
        'translate' : 'https://translate.api.cloud.yandex.net/translate/v2/translate'
    }
    
    
    def __init__(self, oauth: str, catalog_id: str, translate_to: str) -> None:
        self.oauth = oauth
        self.catalog_id = catalog_id
        self.full_token = None
        self.token = None
    
    async def make_request(self, action: str, text: str = None) -> dict:
        """This method handle requests to yandex translate API"""
        data = self.__generate_data(action, text)
        if self.token:
            headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}"
                }
        else: headers = None 
        async with ClientSession() as session:
            async with session.post(url=self.actions[action], json=data, headers=None if action =='get_token' else headers) as resp:
                response = await resp.json()
                return response
            
        
    async def __get_token(self) -> str:
        """Getting a 'full_token' if needed and return token string required for API requests.
           Also checking is the token valid."""
        if self.full_token:
            now = datetime.datetime.now(tz=datetime.timezone.utc)
            token_expires = datetime.datetime.fromisoformat(self.full_token["expiresAt"])
            if token_expires > now:
                print('Token is valid!')
                return self.full_token["iamToken"]
        else:
            print('No token... Requesting a new one.')
            
            self.full_token = await self.make_request(action='get_token')
            print(f'Full token is {self.full_token}\n\n')
            return await self.__get_token()

    async def _detect_lang(self, text: str) -> dict:
        """Return a language of a 'text'."""
        self.token = await self.__get_token()
        lang = await self.make_request(action='detect_lang', text=text)
        print(f'Language is {lang}')
        return lang.get('languageCode')
    
    async def translate(self, text: str) -> str:
        """Return a string which contains translated 'text'."""
        self.token = await self.__get_token()
        translation = await self.make_request(action='translate', text=text)
        return translation['translations'][0]['text']
    
    def __generate_data(self, action: str, text: str = None) -> dict:
        """Return a JSON-like dict with headers for api request. Depends on 'action'."""
        if action == 'get_token':
            data = {'yandexPassportOauthToken': self.oauth}
        elif action == 'detect_lang':
            data = {
                'folderId': self.catalog_id,
                'languageCodeHints' :['de'],
                'text': text,}
        else:
            data = {
                "folderId": self.catalog_id,
                "texts": [text],
                "targetLanguageCode": 'ru'}
        return data
