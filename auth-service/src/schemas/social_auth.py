from pydantic import BaseModel
from pydantic import EmailStr


class SocialOAuthUserModel(BaseModel):
    email: EmailStr
    login: str
    first_name: str
    last_name: str
    social_id: str
    social_name: str
