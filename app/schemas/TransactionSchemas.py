from pydantic import BaseModel, Field

class PaymentCreateRequest(BaseModel):
    amount: float = Field(..., gt=0, description="Amount to be paid (in INR)")

    class Config:
        json_schema_extra = {
            "example": {
                "amount": 500.0
            }
        }

class PaymentVerifyRequest(BaseModel):
    payment_id: str = Field(..., description="Razorpay payment ID")
    order_id: str = Field(..., description="Razorpay order ID")
    signature: str = Field(..., description="Razorpay signature")
    
class PaymentResponse(BaseModel):
    order_id: str
    amount: str
    currency: str
    receipt_id: str
    razorpay_key: str
    