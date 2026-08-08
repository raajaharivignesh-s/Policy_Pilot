import uuid
from decimal import Decimal

from app.database.session import SessionLocal
from app.models.profile import CitizenProfile
from app.models.user import User
from app.services.profile_service import profile_service


def test_profile_service():

    db = SessionLocal()

    user = None

    try:
        # ==============================================
        # Create test user
        # ==============================================

        user = User(
            name="Profile Service Test",
            email=f"profile_{uuid.uuid4().hex[:8]}@example.com",
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        # ==============================================
        # Create test profile
        # ==============================================

        profile = CitizenProfile(
            user_id=user.id,
            age=24,
            state="Tamil Nadu",
            district="Erode",
            occupation="Farmer",
            annual_income=Decimal("150000"),
            is_student=False,
            land_acres=Decimal("2.50"),
            additional_information="Test profile",
        )

        db.add(profile)
        db.commit()
        db.refresh(profile)

        # ==============================================
        # Retrieve profile using ProfileService
        # ==============================================

        result = profile_service.get_profile(user.id)

        print("\n========================================")
        print("PROFILE SERVICE RESULT")
        print("========================================")
        print(result)

        # ==============================================
        # Verify returned data
        # ==============================================

        assert result["age"] == 24
        assert result["state"] == "Tamil Nadu"
        assert result["district"] == "Erode"
        assert result["occupation"] == "Farmer"
        assert result["annual_income"] == 150000.0
        assert result["is_student"] is False
        assert result["land_acres"] == 2.5

    finally:
        # ==============================================
        # Clean up test data
        # ==============================================

        if user is not None:
            db.delete(user)
            db.commit()

        db.close()