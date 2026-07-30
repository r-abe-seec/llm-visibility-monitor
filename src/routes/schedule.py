from datetime import datetime

from fastapi import APIRouter, Request
from pydantic import BaseModel

from src.application.scheduled_runner import JOB_ID, parse_csv
from src.config import settings

router = APIRouter(prefix="/schedule", tags=["schedule"])


class ScheduleStatus(BaseModel):
    enabled: bool
    cron: str
    timezone: str
    providers: list[str]
    prompt_ids: list[str]
    next_run_time: datetime | None = None


@router.get("", response_model=ScheduleStatus)
def schedule_status(request: Request) -> ScheduleStatus:
    next_run_time = None
    scheduler = getattr(request.app.state, "scheduler", None)
    if scheduler is not None:
        job = scheduler.get_job(JOB_ID)
        if job is not None:
            next_run_time = job.next_run_time

    return ScheduleStatus(
        enabled=settings.schedule_enabled,
        cron=settings.schedule_cron,
        timezone=settings.schedule_timezone,
        providers=parse_csv(settings.schedule_providers),
        prompt_ids=parse_csv(settings.schedule_prompt_ids),
        next_run_time=next_run_time,
    )
