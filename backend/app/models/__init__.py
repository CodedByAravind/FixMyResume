# Import every model so SQLAlchemy’s registry is aware of all mappers
# (relationships reference classes by name/order_by) no matter the entry point.
from app.models.user import User  # noqa: F401
from app.models.token import RefreshToken  # noqa: F401
from app.models.resume import Resume  # noqa: F401
from app.models.education import EducationEntry  # noqa: F401
from app.models.experience import ExperienceEntry  # noqa: F401
from app.models.project import ProjectEntry  # noqa: F401
from app.models.skill import Skill  # noqa: F401
from app.models.certification import Certification  # noqa: F401
from app.models.resume_version import ResumeVersion  # noqa: F401
from app.models.version_source import (  # noqa: F401
    VersionSourceProfile,
    VersionSourceEducation,
    VersionSourceExperience,
    VersionSourceProject,
    VersionSourceSkill,
    VersionSourceCertification,
)
from app.models.version_tailored import (  # noqa: F401
    VersionTailoredProfile,
    VersionTailoredEducation,
    VersionTailoredExperience,
    VersionTailoredProject,
    VersionTailoredSkill,
    VersionTailoredCertification,
)
from app.models.application import JobApplication  # noqa: F401
