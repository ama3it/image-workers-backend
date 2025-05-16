from datetime import datetime
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.wallet import Wallet
from app.models.transactions import Transaction, TransactionType

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
    
    async def deduct_balance(self, wallet_id, amount: Decimal, reference: str, description: str = None):
        """
        Deduct specified amount from wallet balance and create a transaction record
        
        Args:
            wallet_id: ID of the wallet to deduct from
            amount: Amount to deduct
            reference: Reference ID for the transaction
            description: Optional description of the transaction
            
        Returns:
            Tuple[Wallet, Transaction]: Updated wallet and transaction record, or (None, None) if failed
        """
        # Get wallet
        wallet = await self.get_wallet_by_id(wallet_id)
        if not wallet or wallet.balance < amount:
            return None, None
            
        # Update wallet balance
        wallet.balance -= amount
        wallet.updated_at = datetime.now()
        
        # Create transaction record
        transaction = Transaction(
            user_id=wallet.user_id,
            wallet_id=wallet_id,
            transaction_type=TransactionType.DEBIT,
            reference_id=reference,
            amount=amount
        )
        
        # Add both to session and commit
        self.session.add(transaction)
        await self.session.commit()
        
        # Refresh objects
        await self.session.refresh(wallet)
        await self.session.refresh(transaction)
        
        return wallet, transaction