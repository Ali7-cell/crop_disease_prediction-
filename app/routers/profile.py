"""
Profile router — view and update user profile.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import User
from app.schemas.profile import ProfileResponse, ProfileUpdateRequest
from app.utils.auth_utils import get_current_user, hash_password

router = APIRouter(tags=["User Profile"])


@router.get("/profile", response_model=ProfileResponse)
def get_profile(current_user: User = Depends(get_current_user)):
    """Get current user's profile. Never returns password_hash."""
    return ProfileResponse(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        created_at=current_user.created_at,
    )


@router.put("/profile", response_model=ProfileResponse)
def update_profile(
    body: ProfileUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update current user's name, email, and/or password."""

    # Check if at least one field is provided
    if body.name is None and body.email is None and body.password is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="At least one field (name, email, password) must be provided",
        )

    # Update name if provided
    if body.name is not None:
        current_user.name = body.name

    # Update email if provided (check uniqueness)
    if body.email is not None:
        existing = db.query(User).filter(User.email == body.email, User.id != current_user.id).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A user with this email already exists",
            )
        current_user.email = body.email

    # Update password if provided (re-hash)
    if body.password is not None:
        current_user.password_hash = hash_password(body.password)

    db.commit()
    db.refresh(current_user)

    return ProfileResponse(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        created_at=current_user.created_at,
    )
