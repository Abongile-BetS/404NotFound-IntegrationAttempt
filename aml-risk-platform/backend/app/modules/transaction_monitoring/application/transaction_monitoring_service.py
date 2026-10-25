from app.shared.database.connection import fetch_all
from app.modules.workspace.api.workspace_router import get_workspace_data


class TransactionMonitoringService:
    async def get_workspace_dashboard(self):
        return await get_workspace_data("transactions")

    async def list_transactions(self):
        return await fetch_all(
            """
            SELECT
                t.transaction_guid::text AS financial_transaction_id,
                c.customer_guid::text AS customer_id,
                a.account_guid::text AS account_id,
                tt.transaction_type_name AS transaction_type,
                t.transaction_amount::float AS transaction_amount,
                t.transaction_timestamp::text AS transaction_timestamp
            FROM public.financial_transaction AS t
            JOIN public.customer AS c ON c.id = t.fk_customer_id
            JOIN public.account AS a ON a.id = t.fk_account_id
            JOIN public.customer_transaction_type AS tt ON tt.id = t.fk_transaction_type_id
            ORDER BY t.transaction_timestamp DESC, t.id DESC
            """
        )