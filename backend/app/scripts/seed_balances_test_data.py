from datetime import datetime, timezone
from decimal import Decimal

from app.db.database import SessionLocal
from app.models.expense import Expense, ExpenseSplit
from app.models.group import Group, GroupMember
from app.models.user import User

GROUP_NAME = "BALANCES_API_TEST_GROUP"

USERS = [
    {
        "username": "balance_user_1",
        "email": "balance_user_1@test.com",
        "name": "Balance User 1",
        "password_hash": "hash",
    },
    {
        "username": "balance_user_2",
        "email": "balance_user_2@test.com",
        "name": "Balance User 2",
        "password_hash": "hash",
    },
    {
        "username": "balance_user_3",
        "email": "balance_user_3@test.com",
        "name": "Balance User 3",
        "password_hash": "hash",
    },
]


def get_or_create_user(db, payload):
    user = db.query(User).filter(User.email == payload["email"]).first()
    if user:
        return user

    user = User(
        username=payload["username"],
        email=payload["email"],
        name=payload["name"],
        password_hash=payload["password_hash"],
    )
    db.add(user)
    db.flush()
    return user


def get_or_create_group(db, *, name, creator_id):
    group = db.query(Group).filter(Group.name == name).first()
    if group:
        return group

    group = Group(name=name, creator_id=creator_id)
    db.add(group)
    db.flush()
    return group


def sync_group_members(db, *, group_id, user_ids):
    db.query(GroupMember).filter(
        GroupMember.group_id == group_id,
        ~GroupMember.user_id.in_(user_ids),
    ).delete(synchronize_session=False)

    for user_id in user_ids:
        member = (
            db.query(GroupMember)
            .filter(GroupMember.group_id == group_id, GroupMember.user_id == user_id)
            .first()
        )
        if member is None:
            db.add(GroupMember(group_id=group_id, user_id=user_id, role="member"))

    db.flush()


def clear_group_expenses(db, *, group_id):
    expense_ids = [
        row[0]
        for row in db.query(Expense.id).filter(Expense.group_id == group_id).all()
    ]
    if not expense_ids:
        return

    db.query(ExpenseSplit).filter(ExpenseSplit.expense_id.in_(expense_ids)).delete(
        synchronize_session=False
    )
    db.query(Expense).filter(Expense.id.in_(expense_ids)).delete(synchronize_session=False)
    db.flush()


def create_expense_with_splits(
    db,
    *,
    group_id,
    paid_by_id,
    description,
    amount,
    expense_date,
    splits,
):
    expense = Expense(
        description=description,
        amount=amount,
        paid_by_id=paid_by_id,
        group_id=group_id,
        category="test",
        split_type="EXACT",
        expense_date=expense_date,
    )
    db.add(expense)
    db.flush()

    for user_id, split_amount in splits:
        db.add(
            ExpenseSplit(
                expense_id=expense.id,
                user_id=user_id,
                split_amount=split_amount,
            )
        )


def seed_balances_api_data():
    db = SessionLocal()
    try:
        user_1 = get_or_create_user(db, USERS[0])
        user_2 = get_or_create_user(db, USERS[1])
        user_3 = get_or_create_user(db, USERS[2])

        group = get_or_create_group(db, name=GROUP_NAME, creator_id=user_1.id)
        user_ids = [user_1.id, user_2.id, user_3.id]

        sync_group_members(db, group_id=group.id, user_ids=user_ids)
        clear_group_expenses(db, group_id=group.id)

        now = datetime.now(timezone.utc)

        create_expense_with_splits(
            db,
            group_id=group.id,
            paid_by_id=user_1.id,
            description="Dinner",
            amount=Decimal("120.00"),
            expense_date=now,
            splits=[
                (user_1.id, Decimal("40.00")),
                (user_2.id, Decimal("40.00")),
                (user_3.id, Decimal("40.00")),
            ],
        )

        create_expense_with_splits(
            db,
            group_id=group.id,
            paid_by_id=user_2.id,
            description="Taxi",
            amount=Decimal("60.00"),
            expense_date=now,
            splits=[
                (user_1.id, Decimal("30.00")),
                (user_2.id, Decimal("0.00")),
                (user_3.id, Decimal("30.00")),
            ],
        )

        create_expense_with_splits(
            db,
            group_id=group.id,
            paid_by_id=user_1.id,
            description="Snacks",
            amount=Decimal("30.00"),
            expense_date=now,
            splits=[
                (user_2.id, Decimal("15.00")),
                (user_3.id, Decimal("15.00")),
            ],
        )

        db.commit()

        print("Seed finished for balances API test.")
        print(f"Group ID: {group.id}")
        print("Expected balances:")
        print(f"- {user_1.id}: paid=150.00, owed=70.00, balance=80.00")
        print(f"- {user_2.id}: paid=60.00, owed=55.00, balance=5.00")
        print(f"- {user_3.id}: paid=0.00, owed=85.00, balance=-85.00")
        print("Net sum check: 80.00 + 5.00 + (-85.00) = 0.00")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_balances_api_data()
