import asyncio
import os
import logging

from dependency_injector.wiring import Provide, inject

from src.analyzer.polit_analyzator import MentionAnalyzer
from src.app_container import ApplicationContainer

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)


async def initialize_worker():
    logger.info("Начала работы analyzer")

    container = ApplicationContainer()
    os.environ["I_AM_WORKER"] = "true"
    os.environ["JOB_NAME"] = "analyzer"

    await container.init_resources()
    container.wire(modules=[__name__])
    await analyzer_cron()
    await container.shutdown_resources()

@inject
async def analyzer_cron(
    controller: MentionAnalyzer = Provide[ApplicationContainer.analyzer],
):
    logger.info("Starting epic worker")
    await controller.analyze()
    logger.info("Starting epic done")


if __name__ == "__main__":
    asyncio.run(initialize_worker())
