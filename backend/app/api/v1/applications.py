from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_active_user
from app.database.db import get_db
from app.models.user import User
from app.schemas.application import (
    APPLICATION_STATUSES,
    ORDER_VALUES,
    ApplicationCreate,
    ApplicationListOut,
    ApplicationOut,
    ApplicationUpdate,
)
from app.services import application_service

router = APIRouter(tags=["applications"])

SORT_VALUES = {"application_date", "created_at", "updated_at", "company"}


@router.get("/applications", response_model=list[ApplicationListOut])
def list_applications(
    status: str | None = Query(None),
    q: str | None = Query(None, max_length=100),
    sort_by: str = Query("application_date"),
    order: str = Query("desc"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if status is not None and status not in APPLICATION_STATUSES:
        raise HTTPException(status_code=422, detail="Invalid status filter")
    if sort_by not in SORT_VALUES:
        raise HTTPException(status_code=422, detail="Invalid sort_by")
    if order not in ORDER_VALUES:
        raise HTTPException(status_code=422, detail="Invalid order")
    return application_service.list_applications(
        db, user=current_user, status=status, q=q, sort_by=sort_by, order=order
    )


@router.post(
    "/applications",
    response_model=ApplicationOut,
    status_code=status.HTTP_201_CREATED,
)
def create_application(
    payload: ApplicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return application_service.create_application(db, user=current_user, payload=payload)


@router.get("/applications/{application_id}", response_model=ApplicationOut)
def get_application(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return application_service.get_application(db, user=current_user, application_id=application_id)


@router.put("/applications/{application_id}", response_model=ApplicationOut)
def update_application(
    application_id: int,
    payload: ApplicationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return application_service.update_application(db, user=current_user, application_id=application_id, payload=payload)


@router.delete("/applications/{application_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_application(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    application_service.delete_application(db, user=current_user, application_id=application_id)
