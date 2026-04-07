"""
費用模型(Expense Model): 記錄群組內的每一筆支出費用
"""
from sqlalchemy import Column, String, DateTime, text, ForeignKey, DECIMAL, Boolean, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.db.database import Base


class Expense(Base):
    """
    expenses table
    
    屬性說明:
        id: 唯一識別碼(UUID)
        description: 費用描述
        amount: 費用金額 使用DECIMAL(10,2)精確儲存
        paid_by_id: 付款人的使用者ID 外鍵關連到users.id
        group_id: 所屬群組ID 外鍵關連到groups.id
        category: 費用類別 (optional) 例如:食物、交通、娛樂等
        split_type: 分攤類型 預設為'EQUAL'
                    可選值:EQUAL(均分)、EXACT(指定金額)、PERCENTAGE(百分比)、SHARES(份數)
        expense_date: 費用發生日期
        created_at: 
        updated_at: 

    關聯關係說明:
        payer: 付款人(多對一)
        group: 所屬群組(多對一)
        splits: 此費用的分攤明細清單
        settlements: 與此費用相關的結算交易清單
    
    """
    __tablename__ = "expenses"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
        nullable=False,
    )
    description = Column(String(255), nullable=False)
    amount = Column(
        DECIMAL(10, 2),
        nullable=False,
    )
    paid_by_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
    )
    group_id = Column(
        UUID(as_uuid=True),
        ForeignKey("groups.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    category = Column(String(50))
    split_type = Column(
        String(20),
        nullable=False,
        default="EQUAL",
    )
    expense_date = Column(
        DateTime(timezone=True),
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
    payer = relationship("User", back_populates="paid_expenses", foreign_keys=[paid_by_id])
    group = relationship("Group", back_populates="expenses")
    splits = relationship("ExpenseSplit", back_populates="expense", cascade="all, delete-orphan")
    settlements = relationship("Settlement", back_populates="expense")

    def __repr__(self):
        return f"<Expense(id={self.id}, name='{self.description}', amount={self.amount})>"


class ExpenseSplit(Base):
    """
    expense_splits table
    
    屬性說明:
        id: 唯一識別碼(UUID)
        expense_id: 費用ID 外鍵關連到expenses.id
        user_id: 分攤使用者ID 外鍵關連到users.id
        split_amount: 分攤金額 使用DECIMAL(10,2)精確儲存
        is_settled: 是否已結清 布林值 預設為false
        settled_at: 結清時間 (optional) 當is_settled為true時記錄

    唯一約束:
        確保同一費用對同一使用者只有一筆分攤記錄(expense_id、user_id的組合必須唯一)

    關聯關係說明:
        expense: 所屬費用(多對一)
        user: 分攤使用者(多對一)
    """
    __tablename__ = "expense_splits"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
        nullable=False,
    )
    expense_id = Column(
        UUID(as_uuid=True),
        ForeignKey("expenses.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    split_amount = Column(
        DECIMAL(10, 2),
        nullable=False,
    )
    is_settled = Column(
        Boolean,
        default=False,
        nullable=False,
    )
    settled_at = Column(
        DateTime(timezone=True),
    )

    # Relationships
    expense = relationship("Expense", back_populates="splits")
    user = relationship("User", back_populates="expense_splits")

    # 防止同一費用對同一使用者重複分攤
    __table_args__ = (
        UniqueConstraint("expense_id", "user_id", name="uq_expense_split"),
    )

    def __repr__(self):
        return f"<ExpenseSplit(expense_id={self.expense_id}, user_id={self.user_id}, amount={self.split_amount}, settled={self.is_settled})>"
