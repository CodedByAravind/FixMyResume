from typing import Callable, Type

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_active_user
from app.database.db import get_db
from app.models.user import User
from app.repositories import (
    certification_repository,
    education_repository,
    experience_repository,
    project_repository,
    skill_repository,
)
from app.schemas.resume import (
    CertificationCreate,
    CertificationOut,
    CertificationUpdate,
    EducationCreate,
    EducationOut,
    EducationUpdate,
    ExperienceCreate,
    ExperienceOut,
    ExperienceUpdate,
    ProjectCreate,
    ProjectOut,
    ProjectUpdate,
    SkillCreate,
    SkillOut,
    SkillUpdate,
)
from app.services import resume_section_service

router = APIRouter(tags=["resumes"])


def _register_section(
    *,
    base_path: str,
    create_model: Type[BaseModel],
    update_model: Type[BaseModel],
    out_model: Type[BaseModel],
    get_fn: Callable,
    create_fn: Callable,
    update_fn: Callable,
    delete_fn: Callable,
    next_position_fn: Callable,
) -> None:
    @router.post(
        base_path,
        response_model=out_model,
        status_code=status.HTTP_201_CREATED,
    )
    def create_section_entry(
        payload: create_model,
        resume_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user),
    ):
        data = payload.model_dump(exclude_unset=True)
        return resume_section_service.create_entry(
            db, current_user, resume_id,
            create_fn=create_fn,
            next_position_fn=next_position_fn,
            data=data,
        )

    @router.put(f"{base_path}/{{entry_id}}", response_model=out_model)
    def update_section_entry(
        entry_id: int,
        payload: update_model,
        resume_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user),
    ):
        data = payload.model_dump(exclude_unset=True)
        return resume_section_service.update_entry(
            db, current_user, resume_id, entry_id,
            get_fn=get_fn,
            update_fn=update_fn,
            data=data,
        )

    @router.delete(f"{base_path}/{{entry_id}}", status_code=status.HTTP_204_NO_CONTENT)
    def delete_section_entry(
        entry_id: int,
        resume_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user),
    ):
        resume_section_service.delete_entry(
            db, current_user, resume_id, entry_id,
            get_fn=get_fn,
            delete_fn=delete_fn,
        )


_register_section(
    base_path="/resumes/{resume_id}/education",
    create_model=EducationCreate,
    update_model=EducationUpdate,
    out_model=EducationOut,
    get_fn=education_repository.get_education_by_id,
    create_fn=education_repository.create_education,
    update_fn=education_repository.update_education,
    delete_fn=education_repository.delete_education,
    next_position_fn=education_repository.next_education_position,
)

_register_section(
    base_path="/resumes/{resume_id}/experience",
    create_model=ExperienceCreate,
    update_model=ExperienceUpdate,
    out_model=ExperienceOut,
    get_fn=experience_repository.get_experience_by_id,
    create_fn=experience_repository.create_experience,
    update_fn=experience_repository.update_experience,
    delete_fn=experience_repository.delete_experience,
    next_position_fn=experience_repository.next_experience_position,
)

_register_section(
    base_path="/resumes/{resume_id}/projects",
    create_model=ProjectCreate,
    update_model=ProjectUpdate,
    out_model=ProjectOut,
    get_fn=project_repository.get_project_by_id,
    create_fn=project_repository.create_project,
    update_fn=project_repository.update_project,
    delete_fn=project_repository.delete_project,
    next_position_fn=project_repository.next_project_position,
)

_register_section(
    base_path="/resumes/{resume_id}/skills",
    create_model=SkillCreate,
    update_model=SkillUpdate,
    out_model=SkillOut,
    get_fn=skill_repository.get_skill_by_id,
    create_fn=skill_repository.create_skill,
    update_fn=skill_repository.update_skill,
    delete_fn=skill_repository.delete_skill,
    next_position_fn=skill_repository.next_skill_position,
)

_register_section(
    base_path="/resumes/{resume_id}/certifications",
    create_model=CertificationCreate,
    update_model=CertificationUpdate,
    out_model=CertificationOut,
    get_fn=certification_repository.get_certification_by_id,
    create_fn=certification_repository.create_certification,
    update_fn=certification_repository.update_certification,
    delete_fn=certification_repository.delete_certification,
    next_position_fn=certification_repository.next_certification_position,
)
