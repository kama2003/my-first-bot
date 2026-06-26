from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession
from models.user_settings import UserSettings
from models.material import Material
from models.calculation import Calculation


async def get_or_create_settings(session: AsyncSession, user_id: int) -> UserSettings:
    result = await session.execute(select(UserSettings).where(UserSettings.user_id == user_id))
    settings = result.scalar_one_or_none()
    if not settings:
        settings = UserSettings(user_id=user_id)
        session.add(settings)
        await session.commit()
        await session.refresh(settings)
        defaults = {
            "PLA": (2500, 1000), "PETG": (2800, 1000), "ABS": (2200, 1000),
            "TPU": (3500, 1000), "ASA": (3000, 1000), "Nylon": (4000, 1000),
        }
        for name, (price, weight) in defaults.items():
            mat = Material(user_id=user_id, name=name, filament_price=price, filament_weight=weight)
            session.add(mat)
        await session.commit()
    return settings


async def get_material(session: AsyncSession, user_id: int, name: str) -> Material | None:
    result = await session.execute(
        select(Material).where(Material.user_id == user_id, Material.name == name)
    )
    return result.scalar_one_or_none()


async def get_all_materials(session: AsyncSession, user_id: int) -> list[Material]:
    result = await session.execute(select(Material).where(Material.user_id == user_id))
    return list(result.scalars().all())


async def save_calculation(session: AsyncSession, calc: Calculation):
    session.add(calc)
    await session.commit()


async def get_history(session: AsyncSession, user_id: int, limit: int = 10) -> list[Calculation]:
    result = await session.execute(
        select(Calculation)
        .where(Calculation.user_id == user_id)
        .order_by(Calculation.created_at.desc())
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_statistics(session: AsyncSession, user_id: int) -> dict:
    result = await session.execute(
        select(
            func.count(Calculation.id),
            func.avg(Calculation.total_cost),
            func.avg(Calculation.sale_price),
            func.sum(Calculation.weight),
            func.sum(Calculation.print_time),
        ).where(Calculation.user_id == user_id)
    )
    row = result.one()
    return {
        "count": row[0] or 0,
        "avg_cost": round(row[1] or 0, 2),
        "avg_price": round(row[2] or 0, 2),
        "total_weight": round(row[3] or 0, 2),
        "total_time": round(row[4] or 0, 2),
    }


async def clear_history(session: AsyncSession, user_id: int):
    await session.execute(delete(Calculation).where(Calculation.user_id == user_id))
    await session.commit()


async def get_all_calculations(session: AsyncSession, user_id: int) -> list[Calculation]:
    result = await session.execute(
        select(Calculation).where(Calculation.user_id == user_id).order_by(Calculation.created_at)
    )
    return list(result.scalars().all())
