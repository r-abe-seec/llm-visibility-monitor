import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from src.application.batch_prompt_runner import BatchPromptRunner
from src.config import settings
from src.factories.repository_factory import RepositoryFactory
from src.services.brand_service import BrandService
from src.services.prompt_service import PromptService

logger = logging.getLogger(__name__)

JOB_ID = "scheduled_prompt_runs"


def parse_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def resolve_prompt_ids(prompt_service: PromptService) -> list[str]:
    configured = parse_csv(settings.schedule_prompt_ids)
    if configured:
        return configured
    return [prompt.id for prompt in prompt_service.load_all()]


def run_scheduled_batch() -> None:
    """Execute the configured prompt set against each configured provider."""
    prompt_service = PromptService()
    brand_service = BrandService(settings.brands_file)
    result_repository = RepositoryFactory.create(settings.result_repository)

    prompt_ids = resolve_prompt_ids(prompt_service)
    if not prompt_ids:
        logger.warning("Scheduled run skipped: no prompts configured.")
        return

    brands = brand_service.load_all() if settings.analysis_enabled else []

    for provider_name in parse_csv(settings.schedule_providers):
        try:
            runner = BatchPromptRunner(
                prompt_service=prompt_service,
                result_repository=result_repository,
                brands=brands,
            )
            result = runner.run(
                provider_name=provider_name,
                prompt_ids=prompt_ids,
            )
            logger.info(
                "Scheduled run finished: provider=%s run_id=%s success=%d failure=%d",
                provider_name,
                result.run_id,
                result.success_count,
                result.failure_count,
            )
        except Exception:
            logger.exception(
                "Scheduled run failed for provider %s",
                provider_name,
            )


def create_scheduler() -> BackgroundScheduler:
    scheduler = BackgroundScheduler(timezone=settings.schedule_timezone)
    scheduler.add_job(
        run_scheduled_batch,
        CronTrigger.from_crontab(
            settings.schedule_cron,
            timezone=settings.schedule_timezone,
        ),
        id=JOB_ID,
        replace_existing=True,
    )
    return scheduler
