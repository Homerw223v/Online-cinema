import abc
from starlette.responses import RedirectResponse
from schemas.social_auth import SocialOAuthUserModel
from starlette.requests import Request
from exceptions.db_error import OAuthServiceDoesNotExist


class AbstractSocialAuth(abc.ABC):
    @abc.abstractmethod
    async def get_social_auth_url(self, request: Request) -> RedirectResponse:
        """
        Retrieve the social authentication URL.

        Args:
            request(Request): The request object.

        Returns:
            (RedirectResponse): The social authentication URL as a redirect response.
        """
        pass

    @abc.abstractmethod
    async def get_user_info(self, request: Request) -> SocialOAuthUserModel:
        """
        Retrieve user information for a given request.

        Args:
            request(Request): The request object.

        Returns:
            SocialOAuthUserModel: The user information as a SocialOAuthUserModel object.
        """
        pass


class SocialFactory:
    socials = None

    @classmethod
    def get_social_service(cls, service_name: str) -> AbstractSocialAuth:
        """
        Get the social service instance based on the provided service name.

        Args:
            service_name (str): The name of the social service.

        Returns:
            object: The social service instance.

        Raises:
            OAuthServiceDoesNotExist: If the service does not exist.
        """
        if not cls.socials:
            raw_subclasses: list = cls.__subclasses__()
            cls.socials: dict[str, AbstractSocialAuth] = {
                c().name: c() for c in raw_subclasses
            }
        if class_ := cls.socials.get(service_name, None):
            return class_
        raise OAuthServiceDoesNotExist(
            detail='Service %s not supported.' % service_name,
        )
