from core.config import settings
from authlib.integrations.starlette_client import OAuth
import httpx
from schemas.social_auth import SocialOAuthUserModel
from models.abstract_models.abstact_social_auth import (
    SocialFactory,
    AbstractSocialAuth,
)
from starlette.requests import Request
from starlette.responses import RedirectResponse


class YandexSocialAuth(SocialFactory, AbstractSocialAuth):
    def __init__(self):
        self.name = 'yandex'
        self.yandex_oauth = OAuth()
        self.yandex_oauth.register(
            name='yandex',
            client_id=settings.yandex.id,
            client_secret=settings.yandex.secret,
            access_token_url='https://oauth.yandex.ru/token',
            authorize_url='https://oauth.yandex.ru/authorize',
        )

    async def get_social_auth_url(self, request: Request) -> RedirectResponse:
        return await self.yandex_oauth.yandex.authorize_redirect(
            request, settings.yandex.redirect_uri
        )

    async def get_user_info(self, request: Request) -> SocialOAuthUserModel:
        token = await self.yandex_oauth.yandex.authorize_access_token(request)
        user = httpx.post(
            url='https://login.yandex.ru/info',
            headers={
                'Authorization': f'OAuth {token["access_token"]}',
            },
        ).json()
        return SocialOAuthUserModel(
            email=user.get('default_email'),
            login=user.get('login'),
            first_name=user.get('first_name'),
            last_name=user.get('last_name'),
            social_id=user.get('psuid'),
            social_name=self.name,
        )
