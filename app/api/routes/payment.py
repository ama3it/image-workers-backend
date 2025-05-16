from locale import currency
from fastapi import APIRouter, Depends, HTTPException, status

import hmac
import hashlib
import razorpay
import uuid
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.middleware.authentication import supabaseauth
from app.schemas.TransactionSchemas import (
    PaymentCreateRequest,
    PaymentVerifyRequest,
    PaymentResponse,
)
from app.database import get_db
from app.repositories.wallet_repository import WalletRepository
from app.repositories.transaction_repository import TransactionRepository
from app.models.transactions import TransactionType
from app.config import settings

RAZORPAY_KEY_ID = settings.RAZORPAY_KEY_ID
RAZORPAY_KEY_SECRET = settings.RAZORPAY_KEY_SECRET

razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

router = APIRouter(
    tags=["payments"],
    prefix="/api",
    dependencies=[Depends(supabaseauth.get_current_user)],
)


@router.post("/create-order")
async def create_payment_order(request: PaymentCreateRequest):
    try:
        razorpay_order = razorpay_client.order.create(
            data={
                "amount": int(request.amount*100),
                "currency": "INR",
            }
        )
        return {
            "order_id": razorpay_order["id"],
            "amount": request.amount,
            "razorpay_key": RAZORPAY_KEY_ID,
            "currency": "INR",
            "name": "Virtual Space",
            "description": "TOPUP",
            "callback_url": "/verify",
        }

    except Exception as e:
        print("Razorpay order creation failed:", e)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create payment order: {str(e)}",
        )


@router.post("/verify-payment", status_code=status.HTTP_200_OK)
async def verify_payment(
    request: PaymentVerifyRequest,
    current_user: Dict[str, Any] = Depends(supabaseauth.get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Verify Razorpay payment and update user's wallet
    """
 
    generated_signature = hmac.new(
        bytes(settings.RAZORPAY_KEY_SECRET, "utf-8"),
        f"{request.order_id}|{request.payment_id}".encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    if generated_signature != request.signature:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid payment signature"
        )

    try:
        # Fetch payment details from Razorpay
        payment = razorpay_client.payment.fetch(request.payment_id)
        print(f"Payment details: {payment}")
        # Verify if payment is successful
        if payment["status"] != "authorized":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Payment not captured"
            )

        amount = float(payment["amount"]) / 100

        # Update user's wallet
        wallet_repo = WalletRepository(db)
        wallet =await wallet_repo.get_wallet_by_user_id(current_user["id"])

        if not wallet:
            # Create wallet if not exists
            wallet =await wallet_repo.create_wallet(
                {"user_id": current_user["id"], "balance": amount}
            )
        else:
            # Update existing wallet
           await wallet_repo.update_wallet(
                wallet.id, {"balance": float(wallet.balance) + amount}
            )

        # Log transaction
        transaction_repo = TransactionRepository(db)
        transaction =await transaction_repo.log_transaction(
            {
                "user_id": current_user["id"],
                "wallet_id": wallet.id,
                "transaction_type": TransactionType.TOPUP,
                "reference_id": request.payment_id,
                "amount": amount,
            }
        )

        return {
            "status": "success",
            "message": "Payment verified and wallet updated successfully",
            "transaction_id": str(transaction.id),
            "wallet_balance": str(wallet.balance),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to verify payment: {str(e)}",
        )


@router.get("/payment-history")
async def get_payment_history(
    current_user: Dict[str, Any] = Depends(supabaseauth.get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get payment history for the current user
    """
    try:
        transaction_repo = TransactionRepository(db)
        transactions = await transaction_repo.get_transactions_by_user_id(
            current_user["id"]
        )
        return {"transactions": [transaction.to_dict() for transaction in transactions]}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch payment history: {str(e)}",
        )


@router.get("/wallet-balance")
async def get_wallet_balance(
    current_user: Dict[str, Any] = Depends(supabaseauth.get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get wallet balance for the current user
    """
    try:
        wallet_repo = WalletRepository(db)
        wallet = await wallet_repo.get_wallet_by_user_id(current_user["id"])
        print(wallet)

        if not wallet:
            return {"balance": "0.00"}

        return {"balance": str(wallet.balance)}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch wallet balance: {str(e)}",
        )
