import enum
import uuid
from datetime import datetime
from sqlalchemy import DECIMAL, Column, DateTime, Enum, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class TransactionType(str, enum.Enum):
    TOPUP = "topup"
    DEBIT = "debit"
    REFUND = "refund"
    ADJUSTMENT = "adjustment"


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False) 
    wallet_id = Column(UUID(as_uuid=True), ForeignKey("wallet.id"), nullable=False)  # Added ForeignKey
    transaction_type = Column(Enum(TransactionType), nullable=False)
    reference_id = Column(String(255), nullable=False)
    amount = Column(DECIMAL(18, 2), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.now, onupdate=datetime.now, nullable=False)
    

    def __repr__(self):
        return f"<Transaction {self.id}: {self.user_id}>"

    def to_dict(self):
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "wallet_id": str(self.wallet_id),
            "transaction_type": self.transaction_type.value,
            "reference_id": self.reference_id,
            "amount": str(self.amount),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
