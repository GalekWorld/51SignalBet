"""User registration and Telegram interaction use cases."""

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User


class UserService:
    """Create or update the internal user record for a Telegram interaction."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def register_telegram_user(
        self,
        *,
        telegram_user_id: int,
        username: str | None,
        language: str | None,
        timezone_name: str | None,
    ) -> User:
        now = datetime.now(UTC)
        user = await self._session.scalar(
            select(User).where(User.telegram_user_id == telegram_user_id)
        )
        if user is None:
            user = User(
                telegram_user_id=telegram_user_id,
                username=username,
                language=language or "en",
                timezone=timezone_name or "UTC",
                last_active_at=now,
            )
            self._session.add(user)
        else:
            user.username = username
            if language:
                user.language = language
            if timezone_name:
                user.timezone = timezone_name
            user.last_active_at = now
            user.is_active = True
        await self._session.commit()
        return user

    async def get_timezone(self, telegram_user_id: int) -> str:
        """Return the user's presentation timezone with a safe default."""

        user = await self._session.scalar(
            select(User).where(User.telegram_user_id == telegram_user_id)
        )
        return user.timezone if user is not None else "UTC"
