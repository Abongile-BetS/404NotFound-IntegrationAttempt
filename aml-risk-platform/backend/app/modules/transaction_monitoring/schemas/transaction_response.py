from pydantic import BaseModel


class TransactionResponse(BaseModel):
    financial_transaction_id: str
    customer_id: str
    account_id: str
    transaction_type: str
    transaction_amount: float
    transaction_timestamp: str