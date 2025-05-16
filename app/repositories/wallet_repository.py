from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.wallet import Wallet

class WalletRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_wallet_by_id(self, wallet_id):
        result = await self.session.execute(
            select(Wallet).where(Wallet.id == wallet_id)
        )
        return result.scalars().first()

    async def get_wallet_by_user_id(self, user_id):
        result = await self.session.execute(
            select(Wallet).where(Wallet.user_id == user_id)
        )
        return result.scalars().first()

    async def create_wallet(self, wallet_data: dict):
        wallet = Wallet(**wallet_data)
        self.session.add(wallet)
        await self.session.commit()
        await self.session.refresh(wallet)
        return wallet

    async def update_wallet(self, wallet_id, update_data: dict):
        wallet = await self.get_wallet_by_id(wallet_id)
        if not wallet:
            return None
        for key, value in update_data.items():
            if hasattr(wallet, key):
                setattr(wallet, key, value)
        await self.session.commit()
        await self.session.refresh(wallet)
        return wallet