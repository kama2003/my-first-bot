from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from handlers.states import CalcStates
from services.db_service import get_or_create_settings, get_all_materials, get_material, save_calculation
from services.calculator import CalcInput, calculate
from models.calculation import Calculation
from keyboards.main_menu import material_select_kb, cancel_kb, skip_kb, main_menu_kb
from utils.time_parser import parse_time_to_minutes, minutes_to_str

router = Router()


@router.message(F.text == "🧮 Рассчитать стоимость")
async def calc_start(message: Message, state: FSMContext, session: AsyncSession):
    materials = await get_all_materials(session, message.from_user.id)
    if not materials:
        await get_or_create_settings(session, message.from_user.id)
        materials = await get_all_materials(session, message.from_user.id)

    await state.set_state(CalcStates.material)
    await message.answer(
        "🧵 <b>Выбери материал:</b>",
        parse_mode="HTML",
        reply_markup=material_select_kb(materials)
    )


@router.callback_query(CalcStates.material, F.data.startswith("calc_material_"))
async def calc_material(callback: CallbackQuery, state: FSMContext):
    material = callback.data.replace("calc_material_", "")
    await state.update_data(material=material)
    await state.set_state(CalcStates.weight)
    await callback.message.edit_text(
        f"✅ Материал: <b>{material}</b>\n\n"
        "⚖️ Введи <b>вес использованного пластика</b> (в граммах):\n"
        "<i>Например: 37.5</i>",
        parse_mode="HTML",
        reply_markup=cancel_kb()
    )


@router.message(CalcStates.weight)
async def calc_weight(message: Message, state: FSMContext):
    try:
        weight = float(message.text.replace(",", "."))
        if weight <= 0:
            raise ValueError
    except ValueError:
        await message.answer("❌ Введи число больше нуля. Например: <code>37.5</code>", parse_mode="HTML")
        return

    await state.update_data(weight=weight)
    await state.set_state(CalcStates.time)
    await message.answer(
        "🕒 Введи <b>время печати</b>:\n\n"
        "Форматы: <code>4ч 35м</code> · <code>4:35</code> · <code>275</code> (мин)",
        parse_mode="HTML",
        reply_markup=cancel_kb()
    )


@router.message(CalcStates.time)
async def calc_time(message: Message, state: FSMContext):
    minutes = parse_time_to_minutes(message.text)
    if minutes is None or minutes <= 0:
        await message.answer(
            "❌ Не понял формат. Попробуй: <code>4ч 35м</code>, <code>4:35</code> или <code>275</code>",
            parse_mode="HTML"
        )
        return

    await state.update_data(print_time=minutes)
    await state.set_state(CalcStates.copies)
    await message.answer(
        "📦 Сколько <b>экземпляров</b> печатаем?\n<i>По умолчанию: 1</i>",
        parse_mode="HTML",
        reply_markup=skip_kb()
    )


@router.message(CalcStates.copies)
async def calc_copies(message: Message, state: FSMContext):
    try:
        copies = int(message.text)
        if copies <= 0:
            raise ValueError
    except ValueError:
        await message.answer("❌ Введи целое число больше нуля.")
        return
    await state.update_data(copies=copies)
    await state.set_state(CalcStates.infill)
    await message.answer(
        "🔲 <b>Заполнение модели</b> (%)?\n<i>По умолчанию: 100%</i>",
        parse_mode="HTML",
        reply_markup=skip_kb()
    )


@router.callback_query(CalcStates.copies, F.data == "skip")
async def calc_copies_skip(callback: CallbackQuery, state: FSMContext):
    await state.update_data(copies=1)
    await state.set_state(CalcStates.infill)
    await callback.message.edit_text(
        "🔲 <b>Заполнение модели</b> (%)?\n<i>По умолчанию: 100%</i>",
        parse_mode="HTML",
        reply_markup=skip_kb()
    )


@router.message(CalcStates.infill)
async def calc_infill(message: Message, state: FSMContext):
    try:
        infill = float(message.text.replace(",", ".").replace("%", ""))
        if not (0 < infill <= 100):
            raise ValueError
    except ValueError:
        await message.answer("❌ Введи число от 1 до 100.")
        return
    await state.update_data(infill=infill)
    await state.set_state(CalcStates.delivery)
    await message.answer(
        "🚚 <b>Стоимость доставки</b> (₽)?\n<i>Необязательно</i>",
        parse_mode="HTML",
        reply_markup=skip_kb()
    )


@router.callback_query(CalcStates.infill, F.data == "skip")
async def calc_infill_skip(callback: CallbackQuery, state: FSMContext):
    await state.update_data(infill=100.0)
    await state.set_state(CalcStates.delivery)
    await callback.message.edit_text(
        "🚚 <b>Стоимость доставки</b> (₽)?\n<i>Необязательно</i>",
        parse_mode="HTML",
        reply_markup=skip_kb()
    )


@router.message(CalcStates.delivery)
async def calc_delivery(message: Message, state: FSMContext):
    try:
        val = float(message.text.replace(",", "."))
    except ValueError:
        await message.answer("❌ Введи число.")
        return
    await state.update_data(delivery=val)
    await state.set_state(CalcStates.packaging)
    await message.answer("📦 <b>Стоимость упаковки</b> (₽)?", parse_mode="HTML", reply_markup=skip_kb())


@router.callback_query(CalcStates.delivery, F.data == "skip")
async def calc_delivery_skip(callback: CallbackQuery, state: FSMContext):
    await state.update_data(delivery=0.0)
    await state.set_state(CalcStates.packaging)
    await callback.message.edit_text("📦 <b>Стоимость упаковки</b> (₽)?", parse_mode="HTML", reply_markup=skip_kb())


@router.message(CalcStates.packaging)
async def calc_packaging(message: Message, state: FSMContext):
    try:
        val = float(message.text.replace(",", "."))
    except ValueError:
        await message.answer("❌ Введи число.")
        return
    await state.update_data(packaging=val)
    await state.set_state(CalcStates.postprocess)
    await message.answer("🔧 <b>Постобработка</b> (₽)?", parse_mode="HTML", reply_markup=skip_kb())


@router.callback_query(CalcStates.packaging, F.data == "skip")
async def calc_packaging_skip(callback: CallbackQuery, state: FSMContext):
    await state.update_data(packaging=0.0)
    await state.set_state(CalcStates.postprocess)
    await callback.message.edit_text("🔧 <b>Постобработка</b> (₽)?", parse_mode="HTML", reply_markup=skip_kb())


@router.message(CalcStates.postprocess)
async def calc_postprocess(message: Message, state: FSMContext):
    try:
        val = float(message.text.replace(",", "."))
    except ValueError:
        await message.answer("❌ Введи число.")
        return
    await state.update_data(postprocess=val)
    await state.set_state(CalcStates.painting)
    await message.answer("🎨 <b>Покраска</b> (₽)?", parse_mode="HTML", reply_markup=skip_kb())


@router.callback_query(CalcStates.postprocess, F.data == "skip")
async def calc_postprocess_skip(callback: CallbackQuery, state: FSMContext):
    await state.update_data(postprocess=0.0)
    await state.set_state(CalcStates.painting)
    await callback.message.edit_text("🎨 <b>Покраска</b> (₽)?", parse_mode="HTML", reply_markup=skip_kb())


@router.message(CalcStates.painting)
async def calc_painting(message: Message, state: FSMContext):
    try:
        val = float(message.text.replace(",", "."))
    except ValueError:
        await message.answer("❌ Введи число.")
        return
    await state.update_data(painting=val)
    await state.set_state(CalcStates.assembly)
    await message.answer("🔩 <b>Сборка</b> (₽)?", parse_mode="HTML", reply_markup=skip_kb())


@router.callback_query(CalcStates.painting, F.data == "skip")
async def calc_painting_skip(callback: CallbackQuery, state: FSMContext):
    await state.update_data(painting=0.0)
    await state.set_state(CalcStates.assembly)
    await callback.message.edit_text("🔩 <b>Сборка</b> (₽)?", parse_mode="HTML", reply_markup=skip_kb())


@router.message(CalcStates.assembly)
async def calc_assembly(message: Message, state: FSMContext):
    try:
        val = float(message.text.replace(",", "."))
    except ValueError:
        await message.answer("❌ Введи число.")
        return
    await state.update_data(assembly=val)
    await state.set_state(CalcStates.profit)
    await message.answer("💵 <b>Желаемая прибыль</b> (₽)?", parse_mode="HTML", reply_markup=skip_kb())


@router.callback_query(CalcStates.assembly, F.data == "skip")
async def calc_assembly_skip(callback: CallbackQuery, state: FSMContext):
    await state.update_data(assembly=0.0)
    await state.set_state(CalcStates.profit)
    await callback.message.edit_text("💵 <b>Желаемая прибыль</b> (₽)?", parse_mode="HTML", reply_markup=skip_kb())


@router.message(CalcStates.profit)
async def calc_profit(message: Message, state: FSMContext, session: AsyncSession):
    try:
        val = float(message.text.replace(",", "."))
    except ValueError:
        await message.answer("❌ Введи число.")
        return
    await state.update_data(desired_profit=val)
    await _finish_calc(message, state, session)


@router.callback_query(CalcStates.profit, F.data == "skip")
async def calc_profit_skip(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    await state.update_data(desired_profit=0.0)
    await callback.answer()
    await _finish_calc(callback.message, state, session)


async def _finish_calc(message: Message, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    await state.clear()

    user_id = message.chat.id
    settings = await get_or_create_settings(session, user_id)
    mat = await get_material(session, user_id, data["material"])

    price_per_gram = (mat.filament_price / mat.filament_weight) if mat else (settings.filament_price / settings.filament_weight)

    inp = CalcInput(
        weight=data["weight"],
        print_time=data["print_time"],
        filament_price_per_gram=price_per_gram,
        electricity_cost=settings.electricity_cost,
        printer_power=settings.printer_power,
        printer_cost=settings.printer_cost,
        printer_lifetime=settings.printer_lifetime,
        defect_percent=settings.defect_percent,
        extra_cost=settings.extra_cost,
        markup_percent=settings.markup_percent,
        copies=data.get("copies", 1),
        infill=data.get("infill", 100.0),
        delivery=data.get("delivery", 0.0),
        packaging=data.get("packaging", 0.0),
        postprocess=data.get("postprocess", 0.0),
        painting=data.get("painting", 0.0),
        assembly=data.get("assembly", 0.0),
        desired_profit=data.get("desired_profit", 0.0),
    )

    res = calculate(inp)
    copies = data.get("copies", 1)
    copies_str = f" × {copies} шт." if copies > 1 else ""

    lines = [
        f"📦 <b>Вес модели:</b> {data['weight']} г{copies_str}",
        f"🕒 <b>Время печати:</b> {minutes_to_str(data['print_time'])}",
        f"🧵 <b>Материал:</b> {data['material']}",
        "",
        "──────────────",
        f"🧵 Пластик:              <b>{res.cost_filament:.2f} ₽</b>",
        f"⚡ Электроэнергия:   <b>{res.cost_electricity:.2f} ₽</b>",
        f"🖨 Амортизация:      <b>{res.cost_amortization:.2f} ₽</b>",
        f"📦 Доп. расходы:     <b>{res.cost_extra:.2f} ₽</b>",
    ]

    if res.cost_delivery:    lines.append(f"🚚 Доставка:             <b>{res.cost_delivery:.2f} ₽</b>")
    if res.cost_packaging:   lines.append(f"📫 Упаковка:             <b>{res.cost_packaging:.2f} ₽</b>")
    if res.cost_postprocess: lines.append(f"🔧 Постобработка:    <b>{res.cost_postprocess:.2f} ₽</b>")
    if res.cost_painting:    lines.append(f"🎨 Покраска:             <b>{res.cost_painting:.2f} ₽</b>")
    if res.cost_assembly:    lines.append(f"🔩 Сборка:                <b>{res.cost_assembly:.2f} ₽</b>")

    lines += [
        f"⚠️ Брак ({settings.defect_percent:.0f}%):          <b>{res.cost_defect:.2f} ₽</b>",
        "",
        "──────────────",
        f"💰 <b>Себестоимость:   {res.total_cost:.2f} ₽</b>",
        f"💵 <b>Цена продажи:    {res.sale_price:.2f} ₽</b>",
    ]

    if res.desired_profit:
        lines.append(f"📈 Желаемая прибыль: <b>{res.desired_profit:.2f} ₽</b>")

    await message.answer("\n".join(lines), parse_mode="HTML", reply_markup=main_menu_kb())

    calc = Calculation(
        user_id=user_id,
        material=data["material"],
        weight=data["weight"],
        print_time=data["print_time"],
        copies=copies,
        infill=data.get("infill", 100.0),
        cost_filament=res.cost_filament,
        cost_electricity=res.cost_electricity,
        cost_amortization=res.cost_amortization,
        cost_extra=res.cost_extra,
        cost_defect=res.cost_defect,
        cost_delivery=res.cost_delivery,
        cost_packaging=res.cost_packaging,
        cost_postprocess=res.cost_postprocess,
        cost_painting=res.cost_painting,
        cost_assembly=res.cost_assembly,
        desired_profit=res.desired_profit,
        total_cost=res.total_cost,
        sale_price=res.sale_price,
    )
    await save_calculation(session, calc)


@router.callback_query(F.data == "cancel")
async def cancel_handler(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Отменено.")
    await callback.message.answer("Главное меню:", reply_markup=main_menu_kb())
