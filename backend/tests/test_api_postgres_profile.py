import uuid
from decimal import Decimal

from fastapi.testclient import TestClient

from app.database.session import SessionLocal
from app.main import app
from app.models.profile import CitizenProfile
from app.models.user import User


client = TestClient(app)


def test_api_uses_postgresql_profile():

    db = SessionLocal()

    user = None

    try:
        # ==============================================
        # 1. Create test user in PostgreSQL
        # ==============================================

        user = User(
            name="API PostgreSQL Test User",
            email=f"api_profile_{uuid.uuid4().hex[:8]}@example.com",
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        # ==============================================
        # 2. Create citizen profile
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
        )

        db.add(profile)
        db.commit()

        print("\n========================================")
        print("TEST USER")
        print("========================================")
        print("User ID:", user.id)

        # ==============================================
        # 3. Send query using ONLY user_id
        # ==============================================

        response = client.post(
            "/api/v1/query",
            json={
                "query": "What financial assistance is available for farmers?",
                "user_id": str(user.id),
            },
        )

        print("\n========================================")
        print("API STATUS")
        print("========================================")
        print(response.status_code)

        print("\n========================================")
        print("API RESPONSE")
        print("========================================")
        print(response.json())

        # ==============================================
        # 4. Verify API response
        # ==============================================

        assert response.status_code == 200

        data = response.json()

        assert data["query"] == (
            "What financial assistance is available for farmers?"
        )

        assert data["intent"] == "scheme_discovery"

        assert data["domain"] == "agriculture"

        assert len(data["retrieved_documents"]) > 0

    finally:
        # ==============================================
        # 5. Cleanup
        # ==============================================

        if user is not None:
            db.delete(user)
            db.commit()

        db.close()