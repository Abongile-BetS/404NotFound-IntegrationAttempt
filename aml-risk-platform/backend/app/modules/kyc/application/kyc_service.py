from app.modules.kyc.infrastructure.kyc_repository import KycRepository
from app.modules.workspace.api.workspace_router import get_workspace_data


class KycService:

    def __init__(self):
        self.repository = KycRepository()

    async def list_records(self):
        return await self.repository.list_all()

    async def get_workspace_dashboard(self):
        return await get_workspace_data("kyc")

    async def get_customer_kyc(self, customer_id: str):
        return await self.repository.get_customer_kyc(customer_id)