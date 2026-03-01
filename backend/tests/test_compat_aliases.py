import os
import sys
from pathlib import Path


# Minimal env so app.config can initialize during model imports.
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost:5432/test_db")
os.environ.setdefault("SECRET_KEY", "test-secret-key-test-secret-key-123456")
os.environ.setdefault("OPENAI_API_KEY", "test-openai-key")

# Ensure backend package imports resolve in test runs from repo root.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.models.candidate import Candidate
from app.models.job import Job, JobTemplate, JobType


def test_job_employment_type_alias_maps_to_job_type():
    job = Job(title="Backend Engineer", description="Build APIs")
    job.employment_type = "contract"
    assert job.job_type == JobType.CONTRACT
    assert job.employment_type == "contract"


def test_job_created_by_id_alias_maps_to_created_by():
    job = Job(title="Backend Engineer", description="Build APIs")
    job.created_by_id = "abc-123"
    assert job.created_by == "abc-123"
    assert job.created_by_id == "abc-123"


def test_candidate_years_of_experience_alias_maps_to_total_experience_years():
    candidate = Candidate(first_name="Ada", last_name="Lovelace", email="ada@example.com")
    candidate.years_of_experience = 7
    assert candidate.total_experience_years == 7
    assert candidate.years_of_experience == 7


def test_job_template_employment_type_alias_maps_to_job_type():
    template = JobTemplate(name="Default", title="SE")
    template.employment_type = "full_time"
    assert template.job_type == JobType.FULL_TIME
    assert template.employment_type == "full_time"
