from decimal import Decimal
from typing import Dict, Tuple
from fastapi import HTTPException, status
import uuid

from app.models.imageJob import JobType
from app.repositories.wallet_repository import WalletRepository

class WalletService:
    """Service to handle wallet operations like checking balance and deducting funds"""
    
    JOB_TYPE_PRICES: Dict[str, Decimal] = {
        JobType.GRAYSCALE: Decimal('25.00'),
        JobType.RESIZE: Decimal('15.00'),
        JobType.THUMBNAIL: Decimal('20.00')
    }
    
    PRIORITY_MULTIPLIERS: Dict[str, Decimal] = {
        "low": Decimal('1.0'),
        "medium": Decimal('1.5'),
        "high": Decimal('2.0'),
        "urgent": Decimal('3.0'),
    }
    
    def __init__(self, wallet_repository: WalletRepository):
        self.wallet_repository = wallet_repository
    
    def calculate_price(self, job_type: JobType, priority: str) -> Decimal:
        """Calculate the price based on job type and priority"""
        base_price = self.JOB_TYPE_PRICES.get(job_type, Decimal('1.00'))
        multiplier = self.PRIORITY_MULTIPLIERS.get(priority.lower(), Decimal('1.0'))
        return base_price * multiplier
    
    async def check_and_deduct_balance(self, user_id: str, job_type: JobType, priority: str, job_id: str = None) -> Tuple[bool, Decimal]:
        """
        Check if user has sufficient balance and deduct if they do
        
        Args:
            user_id: User's ID
            job_type: Type of image processing job
            priority: Job priority level
            job_id: Optional job ID for transaction reference
            
        Returns:
            Tuple[bool, Decimal]: (Success, Price)
        """
        # Get user's wallet
        wallet = await self.wallet_repository.get_wallet_by_user_id(user_id)
        
        if not wallet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Wallet not found for this user"
            )
        
        # Calculate price for this job
        price = self.calculate_price(job_type, priority)
        
        # Check if enough balance
        if wallet.balance < price:
            return False, price
        
        # Prepare transaction reference and description
        reference = f"job-{job_id}" if job_id else f"job-{uuid.uuid4()}"
        description = f"Payment for {job_type} job with {priority} priority"
        
        # Deduct from wallet and record transaction
        updated_wallet, transaction = await self.wallet_repository.deduct_balance(
            wallet_id=wallet.id,
            amount=price,
            reference=reference,
            description=description
        )
        
        if not transaction:
            return False, price
            
        return True, price