"""
結算交易模型(Settlement Model): 記錄使用者之間的還款交易
"""
from sqlalchemy import Column, String, DateTime, text, ForeignKey, DECIMAL, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.db.database import Base


class Settlement(Base):
    """
    settlements table
    
    屬性說明:
        id: 唯一識別碼(UUID)
        payer_id: 付款人使用者ID 外鍵關連到users.id
        receiver_id: 收款人使用者ID 外鍵關連到users.id
        amount: 交易金額 使用DECIMAL(10,2)精確儲存
        method: 付款方式 (optional) 例如: 現金、銀行轉帳、信用卡等
        status: 交易狀態 預設為'pending'
                可選值: pending(待處理)、completed(已完成)、cancelled(已取消)
        group_id: 所屬群組ID 外鍵關連到groups.id
        expense_id: 相關費用ID (optional) 外鍵關連到expenses.id
        notes: 交易備註 (optional) 使用Text類型儲存較長文字
        transaction_date: 交易日期
        created_at: 
        updated_at: 
    
    關聯關係說明:
        payer: 付款人(多對一)
        receiver: 收款人(多對一)
        group: 所屬群組(多對一)
        expense: 相關費用(多對一)
    """
    __tablename__ = "settlements"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
        nullable=False,
    )
    payer_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
    )
    receiver_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
    )
    amount = Column(
        DECIMAL(10, 2),
        nullable=False,
    )
    method = Column(
        String(50),
    )
    status = Column(
        String(20),
        default="pending",
        nullable=False,
    )
    group_id = Column(
        UUID(as_uuid=True),
        ForeignKey("groups.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    expense_id = Column(
        UUID(as_uuid=True),
        ForeignKey("expenses.id", ondelete="SET NULL", onupdate="CASCADE"),
    )
    notes = Column(Text)
    transaction_date = Column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )
    created_at = Column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )

    # Relationships
    payer = relationship("User", back_populates="payer_settlements", foreign_keys=[payer_id])
    receiver = relationship("User", back_populates="receiver_settlements", foreign_keys=[receiver_id])
    group = relationship("Group", back_populates="settlements")
    expense = relationship("Expense", back_populates="settlements")

    def __repr__(self):
        return f"<Settlement(id={self.id}, payer_id={self.payer_id}, receiver_id={self.receiver_id}, amount={self.amount}, status='{self.status}')>"
