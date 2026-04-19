from app.db.database import SessionLocal
from app.models.group import Group, GroupMember
from app.models.user import User


def get_or_create_user(db, *, username, email, name, password_hash):
    user = db.query(User).filter(User.email == email).first()
    if user is not None:
        return user, False

    user = User(
        username=username,
        email=email,
        name=name,
        password_hash=password_hash,
    )
    db.add(user)
    db.flush()
    return user, True


def get_or_create_group(db, *, name, creator_id):
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


def seed():
    db = SessionLocal()
    try:
        user1, created_user1 = get_or_create_user(
            db,
            username="user1",
            email="u1@test.com",
            name="測試用戶1",
            password_hash="hash",
        )
        user2, created_user2 = get_or_create_user(
            db,
            username="user2",
            email="u2@test.com",
            name="測試用戶2",
            password_hash="hash",
        )

        new_group, created_group = get_or_create_group(
            db,
            name="測試群組",
            creator_id=user1.id,
        )

        member1, created_member1 = get_or_create_group_member(
            db,
            group_id=new_group.id,
            user_id=user1.id,
        )
        member2, created_member2 = get_or_create_group_member(
            db,
            group_id=new_group.id,
            user_id=user2.id,
        )

        db.commit()
        print("✅ Seed 完成")
        print(f"User 1 ID: {user1.id} ({'new' if created_user1 else 'existing'})")
        print(f"User 2 ID: {user2.id} ({'new' if created_user2 else 'existing'})")
        print(f"Group ID: {new_group.id} ({'new' if created_group else 'existing'})")
        print(f"Member 1 ID: {member1.id} ({'new' if created_member1 else 'existing'})")
        print(f"Member 2 ID: {member2.id} ({'new' if created_member2 else 'existing'})")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed()