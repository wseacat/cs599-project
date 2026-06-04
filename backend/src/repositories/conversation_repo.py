from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.conversation import Conversation, Message
from src.repositories.base import GenericRepository


class ConversationRepository(GenericRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Conversation)

    async def get_user_conversations(self, user_id: int) -> list[Conversation]:
        stmt = select(Conversation).where(Conversation.user_id == user_id).order_by(Conversation.updated_at.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_user_conversations_with_counts(self, user_id: int) -> list[tuple[Conversation, int]]:
        stmt = (
            select(Conversation, func.count(Message.id).label("msg_count"))
            .outerjoin(Message, Message.conversation_id == Conversation.id)
            .where(Conversation.user_id == user_id)
            .group_by(Conversation.id)
            .order_by(Conversation.updated_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.all())

    async def get_conversation_with_messages(self, conversation_id: int) -> Conversation | None:
        stmt = (
            select(Conversation)
            .where(Conversation.id == conversation_id)
            .options(selectinload(Conversation.messages))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


class MessageRepository(GenericRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Message)

    async def get_conversation_messages(self, conversation_id: int, limit: int = 50) -> list[Message]:
        stmt = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        messages = list(result.scalars().all())
        messages.reverse()  # Return in chronological order
        return messages

    async def count_messages(self, conversation_id: int) -> int:
        stmt = select(func.count()).select_from(Message).where(Message.conversation_id == conversation_id)
        result = await self.session.execute(stmt)
        return result.scalar_one()
