"""Small response contracts for a future Telegram Mini App."""

from pydantic import BaseModel, ConfigDict


class MiniAppUser(BaseModel):
    model_config = ConfigDict(frozen=True)

    user_id: str
    language: str
    timezone: str


class MiniAppBootstrap(BaseModel):
    model_config = ConfigDict(frozen=True)

    user: MiniAppUser
    api_version: str = "v1"
    features: tuple[str, ...] = ()
