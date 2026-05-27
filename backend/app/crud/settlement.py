from sqlalchemy.orm import Session

from app.models.settlement import Settlement
from app.schemas.settlement import SettlementCreate

class SettlementCrud:
    @staticmethod
    def create_settlement(db: Session, settlement_in: SettlementCreate) -> Settlement:
        """建立一筆結算紀錄"""

        new_settlement = Settlement(**settlement_in.model_dump())
        try:
            db.add(new_settlement)
            db.commit()
            db.refresh(new_settlement)
            return new_settlement
        except Exception:
            db.rollback()
            raise