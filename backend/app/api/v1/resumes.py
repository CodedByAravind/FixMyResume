from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_active_user
from app.database.db import get_db
from app.models.user import User
from app.schemas.resume import ResumeCreate, ResumeDetail, ResumeSummary, ResumeUpdate
from app.services import resume_service

router = APIRouter(tags=["resumes"])


@router.post("/resumes", response_model=ResumeDetail, status_code=status.HTTP_201_CREATED)
def create_resume(
    payload: ResumeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return resume_service.create_resume(db, current_user, payload)


@router.get("/resumes", response_model=list[ResumeSummary])
def list_resumes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return resume_service.list_resumes(db, current_user)


@router.get("/resumes/{resume_id}", response_model=ResumeDetail)
def get_resume(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return resume_service.get_resume(db, current_user, resume_id)


@router.put("/resumes/{resume_id}", response_model=ResumeDetail)
def update_resume(
    resume_id: int,
    payload: ResumeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return resume_service.update_resume(db, current_user, resume_id, payload)


@router.delete("/resumes/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_resume(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    resume_service.delete_resume(db, current_user, resume_id)
