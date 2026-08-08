from typing import Any
from uuid import UUID

from sqlalchemy import select

from app.database.session import SessionLocal
from app.models.profile import CitizenProfile


class ProfileService:
    """
    Service responsible for retrieving citizen profile
    information from PostgreSQL.
    """

    def get_profile(
        self,
        user_id: UUID,
    ) -> dict[str, Any]:
        """
        Retrieve a citizen profile from PostgreSQL.

        Returns an empty dictionary when the user/profile
        does not exist.
        """

        db = SessionLocal()

        try:
            profile = db.scalar(
                select(CitizenProfile).where(
                    CitizenProfile.user_id == user_id
                )
            )

            if profile is None:
                return {}

            return {
                "age": profile.age,
                "state": profile.state,
                "district": profile.district,
                "occupation": profile.occupation,
                "annual_income": (
                    float(profile.annual_income)
                    if profile.annual_income is not None
                    else None
                ),
                "is_student": profile.is_student,
                "land_acres": (
                    float(profile.land_acres)
                    if profile.land_acres is not None
                    else None
                ),
                "additional_information": (
                    profile.additional_information
                ),
            }

        finally:
            db.close()


profile_service = ProfileService()