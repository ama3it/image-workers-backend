import uuid
from datetime import datetime
from sqlalchemy import DECIMAL, Column, DateTime
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base

class Wallet(Base):
    __tablename__ = "wallet"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False) 
    balance = Column(DECIMAL(18, 2), nullable=False, default=0.00)
    created_at = Column(DateTime(timezone=True), default=datetime.now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.now, onupdate=datetime.now, nullable=False)

    def __repr__(self):
        return f"<Wallet {self.id}: {self.user_id}>"

    def to_dict(self):
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "balance": str(self.balance),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
