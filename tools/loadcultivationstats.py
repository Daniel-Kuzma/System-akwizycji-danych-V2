import sys
from pathlib import Path
src_path = str(Path(__file__).resolve().parent.parent / "src")
sys.path.insert(0, src_path)

from src.database.core import LocalAsyncSession
from src.database.models import TypyOfCultivation
from sqlalchemy import insert
from src.core.server_logger import logger
import asyncio



async def load_cultivation_stats():
    try:
        async with LocalAsyncSession() as db:
            await db.execute(insert(TypyOfCultivation),[
                {"name_of_cultivation" : "Róża", "min_temperature" : 12, "max_temperature" : 28, "min_humidity" : 60, "max_humidity" : 85},
                {"name_of_cultivation" : "Tulipan", "min_temperature" : 12, "max_temperature" : 22, "min_humidity" : 65, "max_humidity" : 85},
                {"name_of_cultivation" : "Chryzantemy", "min_temperature" : 14, "max_temperature" : 25, "min_humidity" : 65, "max_humidity" : 85},
                {"name_of_cultivation" : "Anturium", "min_temperature" : 15, "max_temperature" : 30, "min_humidity" : 60, "max_humidity" : 90},
                {"name_of_cultivation" : "Gerbery", "min_temperature" : 14, "max_temperature" : 28, "min_humidity" : 60, "max_humidity" : 85},
                {"name_of_cultivation" : "Goździk", "min_temperature" : 8, "max_temperature" : 24, "min_humidity" : 60, "max_humidity" : 80},
                {"name_of_cultivation" : "Pelargonia", "min_temperature" : 10, "max_temperature" : 28, "min_humidity" : 60, "max_humidity" : 80},
                {"name_of_cultivation" : "Surfinie", "min_temperature" : 12, "max_temperature" : 28, "min_humidity" : 60, "max_humidity" : 80},
                {"name_of_cultivation" : "Petunia", "min_temperature" : 12, "max_temperature" : 28, "min_humidity" : 65, "max_humidity" : 75},
                {"name_of_cultivation" : "Aksamitka", "min_temperature" : 12, "max_temperature" : 28, "min_humidity" : 55, "max_humidity" : 80},
                {"name_of_cultivation" : "Begonia", "min_temperature" : 14, "max_temperature" : 28, "min_humidity" : 60, "max_humidity" : 80},
                {"name_of_cultivation" : "Bratki", "min_temperature" : 5, "max_temperature" : 20, "min_humidity" : 60, "max_humidity" : 80},
                {"name_of_cultivation" : "Lwia paszcza ", "min_temperature" : 8, "max_temperature" : 24, "min_humidity" : 60, "max_humidity" : 80},
                {"name_of_cultivation" : "Szałwia", "min_temperature" : 12, "max_temperature" : 28, "min_humidity" : 60, "max_humidity" : 80},
                {"name_of_cultivation" : "Cynie", "min_temperature" : 14, "max_temperature" : 30, "min_humidity" : 55, "max_humidity" : 75},
                {"name_of_cultivation" : "Lilie", "min_temperature" : 10, "max_temperature" : 25, "min_humidity" : 65, "max_humidity" : 85},
                {"name_of_cultivation" : "Storczyki", "min_temperature" : 10, "max_temperature" : 25, "min_humidity" : 65, "max_humidity" : 85},
            ])
            await db.commit()
    except Exception as e:
        await db.rollback()
        logger.exception("Critical problem with database trying to add new cultivation data")


if __name__ == "__main__":
    print("Successfully added basic type of cultivation")
    asyncio.run(load_cultivation_stats())

# python -m tools.loadcultivationstats