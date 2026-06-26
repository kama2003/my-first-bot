from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from handlers.states import SettingsStates
from services.db_service import get_or_create_settings, get_all_materials, get_material
from keyboards.main_menu import settings_menu_kb, materials_kb, cancel_kb, main_menu_kb

router = Router()


@router.message(F.text == "⚙️ Настройки")
async def settings_menu(message: Message, session: AsyncSession):
    settings = await get_or_create_settings(session, message.from_user.id)
    text = (
        "⚙️ <b>Настройки</b>\n\n"
        f"⚡ Электричество: <b>{settings.electricity_cost} ₽/кВт·ч</b>, потребление: <b>{settings.printer_power} кВт</b>\n"
        f"🖨 Принтер: <b>{settings.printer_cost:.0f} ₽</b>, срок: <b>{settings.printer_lifetime:.0f} ч</b>\n"
        f"⚠️ Брак: <b>{settings.defect_percent}%</b>\n"
        f"📦 Доп. расходы: <b>{settings.extra_cost} ₽</b>\n"
        f"💰 Наценка: <b>{settings.markup_percent}%</b>"
    )
    await message.answer(text, parse_mode="HTML", reply_markup=settings_menu_kb())


@router.callback_query(F.data == "settings_back")
async def settings_back(callback: CallbackQuery, session: AsyncSession):
    settings = await get_or_create_settings(session, callback.from_user.id)
    text = (
        "⚙️ <b>Настройки</b>\n\n"
        f"⚡ Электричество: <b>{settings.electricity_cost} ₽/кВт·ч</b>, потребление: <b>{settings.printer_power} кВт</b>\n"
        f"🖨 Принтер: <b>{settings.printer_cost:.0f} ₽</b>, срок: <b>{settings.printer_lifetime:.0f} ч</b>\n"
        f"⚠️ Брак: <b>{settings.defect_percent}%</b>\n"
        f"📦 Доп. расходы: <b>{settings.extra_cost} ₽</b>\n"
        f"💰 Наценка: <b>{settings.markup_percent}%</b>"
    )
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=settings_menu_kb())


@router.callback_query(F.data == "main_menu")
async def go_main_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.delete()
    await callback.message.answer("Главное меню:", reply_markup=main_menu_kb())


@router.callback_query(F.data == "settings_materials")
async def settings_materials(callback: CallbackQuery, session: AsyncSession):
    materials = await get_all_materials(session, callback.from_user.id)
    await callback.message.edit_text(
        "🧵 <b>Материалы</b>\nВыбери материал для редактирования:",
        parse_mode="HTML",
        reply_markup=materials_kb(materials)
    )


@router.callback_query(F.data.startswith("edit_material_"))
async def edit_material_start(callback: CallbackQuery, state: FSMContext):
    name = callback.data.replace("edit_material_", "")
    await state.update_data(editing_material=name)
    await state.set_state(SettingsStates.material_price)
    await callback.message.edit_text(
        f"🧵 <b>{name}</b> — введи <b>цену катушки</b> (₽):",
        parse_mode="HTML",
        reply_markup=cancel_kb()
    )


@router.message(SettingsStates.material_price)
async def edit_material_price(message: Message, state: FSMContext):
    try:
        price = float(message.text.replace(",", "."))
    except ValueError:
        await message.answer("❌ Введи число.")
        return
    await state.update_data(mat_price=price)
    await state.set_state(SettingsStates.material_weight)
    await message.answer("Введи <b>вес катушки</b> (г):", parse_mode="HTML", reply_markup=cancel_kb())


@router.message(SettingsStates.material_weight)
async def edit_material_weight(message: Message, state: FSMContext, session: AsyncSession):
    try:
        weight = float(message.text.replace(",", "."))
    except ValueError:
        await message.answer("❌ Введи число.")
        return
    data = await state.get_data()
    await state.clear()
    name = data["editing_material"]
    price = data["mat_price"]
    mat = await get_material(session, message.from_user.id, name)
    if mat:
        mat.filament_price = price
        mat.filament_weight = weight
        await session.commit()
    await message.answer(
        f"✅ <b>{name}</b>: {price:.0f} ₽ / {weight:.0f} г → <b>{price/weight:.2f} ₽/г</b>",
        parse_mode="HTML",
        reply_markup=main_menu_kb()
    )


@router.callback_query(F.data == "settings_electricity")
async def settings_electricity(callback: CallbackQuery, state: FSMContext):
    await state.set_state(SettingsStates.electricity_cost)
    await callback.message.edit_text(
        "⚡ Введи <b>стоимость 1 кВт·ч</b> (₽):\n<i>Например: 8</i>",
        parse_mode="HTML", reply_markup=cancel_kb()
    )


@router.message(SettingsStates.electricity_cost)
async def set_electricity(message: Message, state: FSMContext):
    try:
        val = float(message.text.replace(",", "."))
    except ValueError:
        await message.answer("❌ Введи число.")
        return
    await state.update_data(electricity_cost=val)
    await state.set_state(SettingsStates.printer_power)
    await message.answer(
        "⚡ Введи <b>среднее потребление принтера</b> (кВт):\n<i>Например: 0.12</i>",
        parse_mode="HTML", reply_markup=cancel_kb()
    )


@router.message(SettingsStates.printer_power)
async def set_printer_power(message: Message, state: FSMContext, session: AsyncSession):
    try:
        val = float(message.text.replace(",", "."))
    except ValueError:
        await message.answer("❌ Введи число.")
        return
    data = await state.get_data()
    await state.clear()
    settings = await get_or_create_settings(session, message.from_user.id)
    settings.electricity_cost = data["electricity_cost"]
    settings.printer_power = val
    await session.commit()
    await message.answer(
        f"✅ Электроэнергия: <b>{data['electricity_cost']} ₽/кВт·ч</b>, потребление: <b>{val} кВт</b>",
        parse_mode="HTML", reply_markup=main_menu_kb()
    )


@router.callback_query(F.data == "settings_printer")
async def settings_printer(callback: CallbackQuery, state: FSMContext):
    await state.set_state(SettingsStates.printer_cost)
    await callback.message.edit_text(
        "🖨 Введи <b>стоимость принтера</b> (₽):\n<i>Например: 65000</i>",
        parse_mode="HTML", reply_markup=cancel_kb()
    )


@router.message(SettingsStates.printer_cost)
async def set_printer_cost(message: Message, state: FSMContext):
    try:
        val = float(message.text.replace(",", "."))
    except ValueError:
        await message.answer("❌ Введи число.")
        return
    await state.update_data(printer_cost=val)
    await state.set_state(SettingsStates.printer_lifetime)
    await message.answer(
        "🖨 Введи <b>срок службы</b> (часов):\n<i>Например: 6000</i>",
        parse_mode="HTML", reply_markup=cancel_kb()
    )


@router.message(SettingsStates.printer_lifetime)
async def set_printer_lifetime(message: Message, state: FSMContext, session: AsyncSession):
    try:
        val = float(message.text.replace(",", "."))
    except ValueError:
        await message.answer("❌ Введи число.")
        return
    data = await state.get_data()
    await state.clear()
    settings = await get_or_create_settings(session, message.from_user.id)
    settings.printer_cost = data["printer_cost"]
    settings.printer_lifetime = val
    await session.commit()
    await message.answer(
        f"✅ Принтер: <b>{data['printer_cost']:.0f} ₽</b>, срок: <b>{val:.0f} ч</b> → <b>{data['printer_cost']/val:.2f} ₽/час</b>",
        parse_mode="HTML", reply_markup=main_menu_kb()
    )


@router.callback_query(F.data == "settings_defect")
async def settings_defect(callback: CallbackQuery, state: FSMContext):
    await state.set_state(SettingsStates.defect_percent)
    await callback.message.edit_text(
        "⚠️ Введи <b>процент брака</b> (%):\n<i>Например: 10</i>",
        parse_mode="HTML", reply_markup=cancel_kb()
    )


@router.message(SettingsStates.defect_percent)
async def set_defect(message: Message, state: FSMContext, session: AsyncSession):
    try:
        val = float(message.text.replace(",", ".").replace("%", ""))
    except ValueError:
        await message.answer("❌ Введи число.")
        return
    await state.clear()
    settings = await get_or_create_settings(session, message.from_user.id)
    settings.defect_percent = val
    await session.commit()
    await message.answer(f"✅ Процент брака: <b>{val}%</b>", parse_mode="HTML", reply_markup=main_menu_kb())


@router.callback_query(F.data == "settings_extra")
async def settings_extra(callback: CallbackQuery, state: FSMContext):
    await state.set_state(SettingsStates.extra_cost)
    await callback.message.edit_text(
        "📦 Введи <b>фиксированные доп. расходы</b> (₽):\n<i>Например: 20</i>",
        parse_mode="HTML", reply_markup=cancel_kb()
    )


@router.message(SettingsStates.extra_cost)
async def set_extra(message: Message, state: FSMContext, session: AsyncSession):
    try:
        val = float(message.text.replace(",", "."))
    except ValueError:
        await message.answer("❌ Введи число.")
        return
    await state.clear()
    settings = await get_or_create_settings(session, message.from_user.id)
    settings.extra_cost = val
    await session.commit()
    await message.answer(f"✅ Доп. расходы: <b>{val} ₽</b>", parse_mode="HTML", reply_markup=main_menu_kb())


@router.callback_query(F.data == "settings_markup")
async def settings_markup(callback: CallbackQuery, state: FSMContext):
    await state.set_state(SettingsStates.markup_percent)
    await callback.message.edit_text(
        "💰 Введи <b>наценку</b> (%):\n<i>Например: 150</i>",
        parse_mode="HTML", reply_markup=cancel_kb()
    )


@router.message(SettingsStates.markup_percent)
async def set_markup(message: Message, state: FSMContext, session: AsyncSession):
    try:
        val = float(message.text.replace(",", ".").replace("%", ""))
    except ValueError:
        await message.answer("❌ Введи число.")
        return
    await state.clear()
    settings = await get_or_create_settings(session, message.from_user.id)
    settings.markup_percent = val
    await session.commit()
    await message.answer(f"✅ Наценка: <b>{val}%</b>", parse_mode="HTML", reply_markup=main_menu_kb())
