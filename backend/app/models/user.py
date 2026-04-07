"""
使用者模型(User Model): 群組分帳系統的核心使用者資料表
"""
from sqlalchemy import Column, String, DateTime, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.db.database import Base


class User(Base):
    """
    users table
    
    屬性說明:
        id: 唯一識別碼(UUID)
        username: 
        email: 電子郵件地址 唯一且不可為空(unique)
        phone: (optional)
        name: 真實姓名
        password_hash: 儲存加密後的密碼
        created_at: 
        updated_at: 

    關聯關係說明:
        created_groups: 此使用者所建立的群組清單(一對多)
        group_memberships: 此使用者加入的群組(透過GroupMember中介表)
        paid_expenses: 此使用者支付的費用清單
        expense_splits: 此使用者需要分攤的費用清單
        payer_settlements: 此使用者作為付款人的結算交易清單(還錢的明細)
        receiver_settlements: 此使用者作為收款人的結算交易清單(收債的明細)
    """
    __tablename__ = "users"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
        nullable=False,
    )
    username = Column(String(50), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(20))
    name = Column(String(100), nullable=False)
    password_hash = Column(String(255), nullable=False)
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
    created_groups = relationship("Group", back_populates="creator", cascade="all, delete-orphan")
    group_memberships = relationship("GroupMember", back_populates="user", cascade="all, delete-orphan")
    paid_expenses = relationship("Expense", back_populates="payer", foreign_keys="Expense.paid_by_id")
    expense_splits = relationship("ExpenseSplit", back_populates="user", cascade="all, delete-orphan")
    payer_settlements = relationship("Settlement", back_populates="payer", foreign_keys="Settlement.payer_id")
    receiver_settlements = relationship("Settlement", back_populates="receiver", foreign_keys="Settlement.receiver_id")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"
