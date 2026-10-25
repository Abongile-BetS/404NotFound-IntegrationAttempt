from app.modules.screening.infrastructure.screening_repository import ScreeningRepository
from app.modules.workspace.api.workspace_router import get_workspace_data


class ScreeningService:

    def __init__(self):
        self.repository = ScreeningRepository()

    async def list_screening_results(self):
        return await self.repository.list_all()

    async def get_dashboard(self):
        return await self.repository.get_dashboard_data()

    async def get_workspace_dashboard(self):
        return await get_workspace_data("screening")

    async def get_customer_screening(self, customer_id: str):
        return await self.repository.get_customer_screening(customer_id)