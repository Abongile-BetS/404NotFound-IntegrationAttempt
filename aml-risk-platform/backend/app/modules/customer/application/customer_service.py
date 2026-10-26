from app.modules.customer.infrastructure.customer_repository import CustomerRepository


class CustomerService:
    def __init__(self):
        self.repository = CustomerRepository()

    async def list_customers(self, limit: int = 100, offset: int = 0):
        return await self.repository.list_all(limit=limit, offset=offset)

    async def get_customer(self, customer_id: str):
        return await self.repository.get_by_id(customer_id)
