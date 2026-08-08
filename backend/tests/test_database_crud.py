import uuid
from decimal import Decimal

from sqlalchemy import select

from app.database.session import SessionLocal
from app.models.user import User
from app.models.profile import CitizenProfile
from app.models.conversation import Conversation
from app.models.message import Message


def test_database_crud():
    db = SessionLocal()

    test_user_id = None

    try:
        # ==================================================
        # 1. CREATE USER
        # ==================================================

        user = User(
            name="PolicyPilot Test User",
            email=f"test_{uuid.uuid4().hex[:8]}@example.com",
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        test_user_id = user.id

        print("\n========================================")
        print("CREATED USER")
        print("========================================")
        print("ID:", user.id)
        print("Name:", user.name)
        print("Email:", user.email)

        assert user.id is not None
        assert user.name == "PolicyPilot Test User"

        # ==================================================
        # 2. CREATE CITIZEN PROFILE
        # ==================================================

        profile = CitizenProfile(
            user_id=user.id,
            age=24,
            state="Tamil Nadu",
            district="Erode",
            occupation="Farmer",
            annual_income=Decimal("150000.00"),
            is_student=False,
            land_acres=Decimal("2.50"),
            additional_information="Test profile",
        )

        db.add(profile)
        db.commit()
        db.refresh(profile)

        print("\n========================================")
        print("CREATED PROFILE")
        print("========================================")
        print("Age:", profile.age)
        print("State:", profile.state)
        print("District:", profile.district)
        print("Occupation:", profile.occupation)
        print("Land:", profile.land_acres)

        assert profile.user_id == user.id
        assert profile.occupation == "Farmer"

        # ==================================================
        # 3. CREATE CONVERSATION
        # ==================================================

        conversation = Conversation(
            user_id=user.id,
            title="Farmer Scheme Query",
            status="active",
        )

        db.add(conversation)
        db.commit()
        db.refresh(conversation)

        print("\n========================================")
        print("CREATED CONVERSATION")
        print("========================================")
        print("ID:", conversation.id)
        print("Title:", conversation.title)
        print("Status:", conversation.status)

        assert conversation.user_id == user.id
        assert conversation.status == "active"

        # ==================================================
        # 4. CREATE MESSAGE
        # ==================================================

        message = Message(
            conversation_id=conversation.id,
            role="user",
            content=(
                "What financial assistance "
                "is available for farmers?"
            ),
        )

        db.add(message)
        db.commit()
        db.refresh(message)

        print("\n========================================")
        print("CREATED MESSAGE")
        print("========================================")
        print("Role:", message.role)
        print("Content:", message.content)

        assert message.conversation_id == conversation.id
        assert message.role == "user"

        # ==================================================
        # 5. READ USER
        # ==================================================

        saved_user = db.scalar(
            select(User).where(
                User.id == user.id
            )
        )

        print("\n========================================")
        print("READ USER")
        print("========================================")
        print("Name:", saved_user.name)
        print("Email:", saved_user.email)

        assert saved_user is not None
        assert saved_user.id == user.id

        # ==================================================
        # 6. READ PROFILE
        # ==================================================

        saved_profile = db.scalar(
            select(CitizenProfile).where(
                CitizenProfile.user_id == user.id
            )
        )

        print("\n========================================")
        print("READ PROFILE")
        print("========================================")
        print("Occupation:", saved_profile.occupation)
        print("District:", saved_profile.district)

        assert saved_profile is not None
        assert saved_profile.occupation == "Farmer"

        # ==================================================
        # 7. READ CONVERSATION
        # ==================================================

        saved_conversation = db.scalar(
            select(Conversation).where(
                Conversation.id == conversation.id
            )
        )

        print("\n========================================")
        print("READ CONVERSATION")
        print("========================================")
        print("Title:", saved_conversation.title)

        assert saved_conversation is not None
        assert saved_conversation.user_id == user.id

        # ==================================================
        # 8. READ MESSAGE
        # ==================================================

        saved_message = db.scalar(
            select(Message).where(
                Message.id == message.id
            )
        )

        print("\n========================================")
        print("READ MESSAGE")
        print("========================================")
        print("Content:", saved_message.content)

        assert saved_message is not None
        assert saved_message.conversation_id == conversation.id

        # ==================================================
        # 9. UPDATE PROFILE
        # ==================================================

        saved_profile.district = "Coimbatore"

        db.commit()
        db.refresh(saved_profile)

        print("\n========================================")
        print("UPDATED PROFILE")
        print("========================================")
        print("New District:", saved_profile.district)

        assert saved_profile.district == "Coimbatore"

        # ==================================================
        # 10. UPDATE CONVERSATION
        # ==================================================

        saved_conversation.title = (
            "Updated Farmer Scheme Query"
        )

        db.commit()
        db.refresh(saved_conversation)

        print("\n========================================")
        print("UPDATED CONVERSATION")
        print("========================================")
        print("New Title:", saved_conversation.title)

        assert (
            saved_conversation.title
            == "Updated Farmer Scheme Query"
        )

        # ==================================================
        # 11. DELETE USER
        #
        # Cascading foreign keys should remove:
        #
        # User
        #  ├── Profile
        #  └── Conversations
        #       └── Messages
        #
        # ==================================================

        db.delete(saved_user)
        db.commit()

        print("\n========================================")
        print("DELETED TEST USER")
        print("========================================")

        # ==================================================
        # 12. VERIFY USER WAS DELETED
        # ==================================================

        deleted_user = db.scalar(
            select(User).where(
                User.id == test_user_id
            )
        )

        assert deleted_user is None

        print("User successfully deleted.")

    finally:
        db.close()