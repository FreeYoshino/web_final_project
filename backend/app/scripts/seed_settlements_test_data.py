"""
生成測試 POST /settlements API 的測試數據

這個腳本會：
1. 確保至少存在 2 個測試用戶和 1 個群組
2. 創建一些測試費用 (expenses)
3. 生成各種不同場景的 settlement 記錄用於測試 API

場景包括：
- 針對特定費用的立即還款 (帶 expense_id)
- 總額/批次結清 (無 expense_id)
- 不同的支付方式: cash, credit_card, bank_transfer
- 不同的狀態: pending, completed, cancelled
"""

from app.db.database import SessionLocal
from app.models.user import User
from app.models.group import Group, GroupMember
from app.models.expense import Expense
from app.models.settlement import Settlement
from datetime import datetime, timedelta
from decimal import Decimal
import uuid


def get_or_create_user(db, *, username, email, name, password_hash):
    """取得或創建用戶"""
    user = db.query(User).filter(User.email == email).first()
    if user is not None:
        return user, False

    user = User(
        username=username,
        email=email,
        name=name,
        password_hash="test_hash",  # 測試用密碼雜湊
    )
    db.add(user)
    db.flush()
    return user, True


def get_or_create_group(db, *, name, creator_id):
    """取得或創建群組"""
    group = (
        db.query(Group)
        .filter(Group.name == name, Group.creator_id == creator_id)
        .first()
    )
    if group is not None:
        return group, False

    group = Group(name=name, creator_id=creator_id)
    db.add(group)
    db.flush()
    return group, True


def get_or_create_group_member(db, *, group_id, user_id, role="member"):
    """取得或創建群組成員"""
    member = (
        db.query(GroupMember)
        .filter(GroupMember.group_id == group_id, GroupMember.user_id == user_id)
        .first()
    )
    if member is not None:
        return member, False

    member = GroupMember(group_id=group_id, user_id=user_id, role=role)
    db.add(member)
    db.flush()
    return member, True


def create_test_expense(db, *, description, amount, paid_by_id, group_id, expense_date=None):
    """創建測試費用"""
    if expense_date is None:
        expense_date = datetime.now()
    
    expense = Expense(
        description=description,
        amount=Decimal(str(amount)),
        paid_by_id=paid_by_id,
        group_id=group_id,
        category="food",
        split_type="EQUAL",
        expense_date=expense_date,
    )
    db.add(expense)
    db.flush()
    return expense


def create_test_settlement(db, *, payer_id, receiver_id, amount, method, status, group_id, 
                          expense_id=None, notes=None, transaction_date=None):
    """創建測試結算交易"""
    if transaction_date is None:
        transaction_date = datetime.now()
    
    settlement = Settlement(
        payer_id=payer_id,
        receiver_id=receiver_id,
        amount=Decimal(str(amount)),
        method=method,
        status=status,
        group_id=group_id,
        expense_id=expense_id,
        notes=notes,
        transaction_date=transaction_date,
    )
    db.add(settlement)
    db.flush()
    return settlement


def seed_settlements_test_data():
    """主要的 seed 函數"""
    db = SessionLocal()
    try:
        print("🌱 開始生成 Settlements 測試數據...\n")

        # ==================== Step 1: 創建測試用戶 ====================
        print("📝 Step 1: 創建/取得測試用戶...")
        user1, created_user1 = get_or_create_user(
            db,
            username="settlement_test_user1",
            email="settlement1@test.com",
            name="結算測試用戶1",
            password_hash="test_hash",
        )
        user2, created_user2 = get_or_create_user(
            db,
            username="settlement_test_user2",
            email="settlement2@test.com",
            name="結算測試用戶2",
            password_hash="test_hash",
        )
        user3, created_user3 = get_or_create_user(
            db,
            username="settlement_test_user3",
            email="settlement3@test.com",
            name="結算測試用戶3",
            password_hash="test_hash",
        )
        print(f"✅ User 1: {user1.id} - {user1.name} ({'new' if created_user1 else 'existing'})")
        print(f"✅ User 2: {user2.id} - {user2.name} ({'new' if created_user2 else 'existing'})")
        print(f"✅ User 3: {user3.id} - {user3.name} ({'new' if created_user3 else 'existing'})\n")

        # ==================== Step 2: 創建群組 ====================
        print("📝 Step 2: 創建/取得測試群組...")
        test_group, created_group = get_or_create_group(
            db,
            name="結算測試群組",
            creator_id=user1.id,
        )
        print(f"✅ Group: {test_group.id} - {test_group.name} ({'new' if created_group else 'existing'})\n")

        # ==================== Step 3: 加入群組成員 ====================
        print("📝 Step 3: 添加群組成員...")
        member1, _ = get_or_create_group_member(
            db,
            group_id=test_group.id,
            user_id=user1.id,
            role="admin",
        )
        member2, _ = get_or_create_group_member(
            db,
            group_id=test_group.id,
            user_id=user2.id,
            role="member",
        )
        member3, _ = get_or_create_group_member(
            db,
            group_id=test_group.id,
            user_id=user3.id,
            role="member",
        )
        print(f"✅ Member 1: {member1.id}")
        print(f"✅ Member 2: {member2.id}")
        print(f"✅ Member 3: {member3.id}\n")

        # ==================== Step 4: 創建測試費用 ====================
        print("📝 Step 4: 創建測試費用...")
        now = datetime.now()
        
        # 費用 1: User1 支付午餐費用
        expense1 = create_test_expense(
            db,
            description="午餐 - 便當",
            amount=150.00,
            paid_by_id=user1.id,
            group_id=test_group.id,
            expense_date=now - timedelta(days=2),
        )
        
        # 費用 2: User2 支付晚餐費用
        expense2 = create_test_expense(
            db,
            description="晚餐 - 火鍋",
            amount=350.00,
            paid_by_id=user2.id,
            group_id=test_group.id,
            expense_date=now - timedelta(days=1),
        )

        # 費用 3: User3 支付飲料費用
        expense3 = create_test_expense(
            db,
            description="飲料費",
            amount=80.00,
            paid_by_id=user3.id,
            group_id=test_group.id,
            expense_date=now - timedelta(days=1),
        )

        print(f"✅ Expense 1: {expense1.id} - {expense1.description} (支付人: {user1.name}, 金額: ${expense1.amount})")
        print(f"✅ Expense 2: {expense2.id} - {expense2.description} (支付人: {user2.name}, 金額: ${expense2.amount})")
        print(f"✅ Expense 3: {expense3.id} - {expense3.description} (支付人: {user3.name}, 金額: ${expense3.amount})\n")

        # ==================== Step 5: 創建結算交易 ====================
        print("📝 Step 5: 創建測試結算交易（結算記錄）...\n")

        # ===== 場景 1: 針對特定費用的立即還款 (帶 expense_id) =====
        print("  📌 場景 1: 針對特定費用的立即還款 (帶 expense_id)")
        settlement1 = create_test_settlement(
            db,
            payer_id=user2.id,  # User2 支付
            receiver_id=user1.id,  # 給 User1
            amount=150.00,  # 還昨天午餐的錢
            method="cash",
            status="completed",
            group_id=test_group.id,
            expense_id=expense1.id,  # 針對 expense1
            notes="還昨天午餐的錢",
            transaction_date=now - timedelta(hours=2),
        )
        print(f"     ✅ Settlement 1: {settlement1.id}")
        print(f"        Payer: {user2.name}, Receiver: {user1.name}")
        print(f"        Amount: ${settlement1.amount}, Method: {settlement1.method}, Status: {settlement1.status}")
        print(f"        ExpenseID: {settlement1.expense_id}\n")

        # ===== 場景 2: 總額/批次結清 (無 expense_id) =====
        print("  📌 場景 2: 總額/批次結清 (無 expense_id)")
        settlement2 = create_test_settlement(
            db,
            payer_id=user1.id,
            receiver_id=user2.id,
            amount=350.00,
            method="bank_transfer",
            status="pending",
            group_id=test_group.id,
            expense_id=None,  # 沒有對應特定費用
            notes="五月份火鍋費用結清",
            transaction_date=now,
        )
        print(f"     ✅ Settlement 2: {settlement2.id}")
        print(f"        Payer: {user1.name}, Receiver: {user2.name}")
        print(f"        Amount: ${settlement2.amount}, Method: {settlement2.method}, Status: {settlement2.status}")
        print(f"        ExpenseID: {settlement2.expense_id}\n")

        # ===== 場景 3: 信用卡支付 =====
        print("  📌 場景 3: 信用卡支付")
        settlement3 = create_test_settlement(
            db,
            payer_id=user3.id,
            receiver_id=user1.id,
            amount=75.50,
            method="credit_card",
            status="completed",
            group_id=test_group.id,
            expense_id=None,
            notes="使用信用卡清償部分欠款",
            transaction_date=now - timedelta(hours=1),
        )
        print(f"     ✅ Settlement 3: {settlement3.id}")
        print(f"        Payer: {user3.name}, Receiver: {user1.name}")
        print(f"        Amount: ${settlement3.amount}, Method: {settlement3.method}, Status: {settlement3.status}\n")

        # ===== 場景 4: 已取消的結算 =====
        print("  📌 場景 4: 已取消的結算交易")
        settlement4 = create_test_settlement(
            db,
            payer_id=user2.id,
            receiver_id=user3.id,
            amount=100.00,
            method="cash",
            status="cancelled",
            group_id=test_group.id,
            expense_id=None,
            notes="此筆交易已取消",
            transaction_date=now - timedelta(hours=12),
        )
        print(f"     ✅ Settlement 4: {settlement4.id}")
        print(f"        Payer: {user2.name}, Receiver: {user3.name}")
        print(f"        Amount: ${settlement4.amount}, Method: {settlement4.method}, Status: {settlement4.status}\n")

        # ===== 場景 5: 大額批次結清 =====
        print("  📌 場景 5: 大額批次結清")
        settlement5 = create_test_settlement(
            db,
            payer_id=user1.id,
            receiver_id=user2.id,
            amount=1250.50,
            method="bank_transfer",
            status="pending",
            group_id=test_group.id,
            expense_id=None,
            notes="四月份五月份總結算轉帳",
            transaction_date=now + timedelta(days=1),
        )
        print(f"     ✅ Settlement 5: {settlement5.id}")
        print(f"        Payer: {user1.name}, Receiver: {user2.name}")
        print(f"        Amount: ${settlement5.amount}, Method: {settlement5.method}, Status: {settlement5.status}\n")

        # 提交所有更改
        db.commit()

        # ==================== 顯示完整的 ID 信息 ====================
        print("=" * 70)
        print("✅ Settlements 測試數據生成完成！")
        print("=" * 70)
        print("\n📊 生成的ID信息（用於 API 測試）:\n")
        print(f"Users:")
        print(f"  User 1 ID: {user1.id}")
        print(f"  User 2 ID: {user2.id}")
        print(f"  User 3 ID: {user3.id}")
        print(f"\nGroup:")
        print(f"  Group ID: {test_group.id}")
        print(f"\nExpenses:")
        print(f"  Expense 1 ID: {expense1.id} (User1 paid, ${expense1.amount})")
        print(f"  Expense 2 ID: {expense2.id} (User2 paid, ${expense2.amount})")
        print(f"  Expense 3 ID: {expense3.id} (User3 paid, ${expense3.amount})")
        print(f"\nSettlements (已創建，用於驗證):")
        print(f"  Settlement 1 ID: {settlement1.id} (與 Expense1 相關)")
        print(f"  Settlement 2 ID: {settlement2.id} (批次結清)")
        print(f"  Settlement 3 ID: {settlement3.id} (信用卡支付)")
        print(f"  Settlement 4 ID: {settlement4.id} (已取消)")
        print(f"  Settlement 5 ID: {settlement5.id} (大額批次結清)")
        print("\n" + "=" * 70)
        print("\n💡 測試建議:")
        print("  1. 使用上述 User 和 Group ID 創建新的 settlement 記錄")
        print("  2. 可選：使用現有的 Expense ID 以創建與特定費用相關的結算")
        print("  3. 測試不同的 method: cash, credit_card, bank_transfer")
        print("  4. 測試不同的 status: pending, completed, cancelled")
        print("  5. 測試有/無 expense_id 的情況")
        print("\n" + "=" * 70)

    except Exception as e:
        db.rollback()
        print(f"❌ 錯誤: {str(e)}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_settlements_test_data()
