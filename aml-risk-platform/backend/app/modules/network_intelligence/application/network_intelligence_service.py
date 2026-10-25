from app.modules.workspace.api.workspace_router import get_workspace_data


class NetworkIntelligenceService:
    async def get_workspace_dashboard(self):
        return await get_workspace_data("network")