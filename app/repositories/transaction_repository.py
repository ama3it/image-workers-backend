from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.transactions import Transaction

class TransactionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def log_transaction(self, transaction_data: dict):
        transaction = Transaction(**transaction_data)
        self.session.add(transaction)
        await self.session.commit()
        await self.session.refresh(transaction)
        return transaction

    async def get_transactions_by_user_id(self, user_id):
        result = await self.session.execute(
            select(Transaction).where(Transaction.user_id == user_id)
        )
        return result.scalars().all()
