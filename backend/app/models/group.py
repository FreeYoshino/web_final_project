"""
群組模型(Group Model): 分帳群組的主要資料表
"""
from sqlalchemy import Column, String, Text, DateTime, text, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.db.database import Base


class Group(Base):
    """
    groups table
    
    屬性說明:
        id: 唯一識別碼(UUID)
        name: 群組名稱
        description: 群組描述 (optional) 使用Text類型儲存較長的文字
        creator_id: 建立者的使用者ID 外鍵關連到users.id
        avatar_url: 群組頭像圖片URL (optional)
        created_at: 
        updated_at: 

    關聯關係說明:
        creator: 群組建立者(多對一)
        members: 群組成員清單(透過GroupMember中介表的一對多關係)
        expenses: 此群組的費用紀錄清單
        settlements: 此群組的結算交易清單
    
    """
    __tablename__ = "groups"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
        nullable=False,
    )
    name = Column(String(100), nullable=False)
    description = Column(Text)
    creator_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
    )
    avatar_url = Column(String(500))
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
    creator = relationship("User", back_populates="created_groups")
    members = relationship("GroupMember", back_populates="group", cascade="all, delete-orphan")
    expenses = relationship("Expense", back_populates="group", cascade="all, delete-orphan")
    settlements = relationship("Settlement", back_populates="group", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Group(id={self.id}, name='{self.name}')>"


class GroupMember(Base):
    """
    group_members table
    
    屬性說明:
        id: 唯一識別碼(UUID)
        group_id: 群組ID 外鍵關連到groups.id
        user_id: 使用者ID 外鍵關連到users.id
        joined_at: 
        role: 群組成員的角色 ('admin' or 'member')

    唯一約束:
        確保同一使用者不能重複加入同一群組(group_id、user_id的組合必須唯一)

    關聯關係說明:
        group: 所屬群組(多對一)
        user: 對應的使用者(多對一)
    """
    __tablename__ = "group_members"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
        nullable=False,
    )
    group_id = Column(
        UUID(as_uuid=True),
        ForeignKey("groups.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    joined_at = Column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )
    role = Column(String(20), default="member", nullable=False)

    # Relationships
    group = relationship("Group", back_populates="members")
    user = relationship("User", back_populates="group_memberships")

    # 防止重複加入同一群組
    __table_args__ = (
        UniqueConstraint("group_id", "user_id", name="uq_group_member"),
    )

    def __repr__(self):
        return f"<GroupMember(group_id={self.group_id}, user_id={self.user_id}, role='{self.role}')>"
