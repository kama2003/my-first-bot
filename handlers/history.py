from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from sqlalchemy.ext.asyncio import AsyncSession

from services.db_service import get_history, get_statistics, clear_history, get_all_calculations
from services.export import export_to_excel
from keyboards.main_menu import main_menu_kb, history_kb, admin_kb
from utils.time_parser import minutes_to_str

router = Router()


@router.message(F.text == "📊 История")
async def show_history(message: Message, session: AsyncSession):
    calcs = await get_history(session, message.from_user.id, limit=10)
    if not calcs:
        await message.answer("📭 История пуста.", reply_markup=main_menu_kb())
        return

    lines = ["📊 <b>Последние расчёты:</b>\n"]
    for i, c in enumerate(calcs, 1):
        date_str = c.created_at.strftime("%d.%m.%Y %H:%M") if c.created_at else "—"
        lines.append(
            f"<b>{i}. {date_str}</b>\n"
            f"   {c.material} · {c.weight}г · {minutes_to_str(c.print_time)}\n"
            f"   💰 {c.total_cost:.2f} ₽ → 💵 {c.sale_price:.2f} ₽\n"
        )

    await message.answer("\n".join(lines), parse_mode="HTML", reply_markup=history_kb())


@router.message(F.text == "📈 Статистика")
async def show_stats(message: Message, session: AsyncSession):
    stats = await get_statistics(session, message.from_user.id)
    if stats["count"] == 0:
        await message.answer("📭 Статистика пуста — сделай хотя бы один расчёт.", reply_markup=main_menu_kb())
        return

    await message.answer(
        "📈 <b>Статистика</b>\n\n"
        f"🔢 Расчётов: <b>{stats['count']}</b>\n"
        f"💰 Средняя себестоимость: <b>{stats['avg_cost']:.2f} ₽</b>\n"
        f"💵 Средняя цена продажи: <b>{stats['avg_price']:.2f} ₽</b>\n"
        f"⚖️ Общий вес: <b>{stats['total_weight']:.0f} г</b>\n"
        f"🕒 Общее время печати: <b>{minutes_to_str(stats['total_time'])}</b>",
        parse_mode="HTML",
        reply_markup=admin_kb()
    )


@router.callback_query(F.data == "admin_export")
async def export_history(callback: CallbackQuery, session: AsyncSession):
    calcs = await get_all_calculations(session, callback.from_user.id)
    if not calcs:
        await callback.answer("История пуста.", show_alert=True)
        return
    await callback.answer("Генерирую файл...")
    buf = export_to_excel(calcs)
    file = BufferedInputFile(buf.read(), filename="history.xlsx")
    await callback.message.answer_document(file, caption="📥 История расчётов в Excel")


@router.callback_query(F.data == "admin_clear")
async def clear_hist(callback: CallbackQuery, session: AsyncSession):
    await clear_history(session, callback.from_user.id)
    await callback.answer("✅ История очищена.", show_alert=True)


@router.callback_query(F.data == "admin_backup")
async def backup_db(callback: CallbackQuery):
    import aiofiles
    try:
        async with aiofiles.open("3d_print_bot.db", "rb") as f:
            data = await f.read()
        file = BufferedInputFile(data, filename="3d_print_bot_backup.db")
        await callback.message.answer_document(file, caption="💾 Резервная копия базы данных")
        await callback.answer()
    except Exception as e:
        await callback.answer(f"Ошибка: {e}", show_alert=True)
