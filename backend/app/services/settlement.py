from sqlalchemy.orm import Session

from app.crud.settlement import SettlementCrud
from app.models.settlement import Settlement
from app.schemas.settlement import SettlementCreate

class SettlementService:
    @staticmethod
    def create_settlement(db: Session, settlement_in: SettlementCreate) -> Settlement:
        """
        商業邏輯: 驗證與建立結算記錄
        """
        return SettlementCrud.create_settlement(db, settlement_in)
