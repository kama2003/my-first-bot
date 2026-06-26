from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from keyboards.main_menu import main_menu_kb

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        f"👋 Привет, <b>{message.from_user.first_name}</b>!\n\n"
        "Я помогу рассчитать себестоимость и цену продажи 3D-печати.\n\n"
        "Выбери действие в меню ниже 👇",
        parse_mode="HTML",
        reply_markup=main_menu_kb()
    )


@router.message(Command("menu"))
async def cmd_menu(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Главное меню:", reply_markup=main_menu_kb())


@router.message(lambda m: m.text == "ℹ️ Помощь")
async def cmd_help(message: Message):
    await message.answer(
        "📖 <b>Как пользоваться ботом:</b>\n\n"
        "🧮 <b>Рассчитать стоимость</b> — запускает расчёт\n"
        "⚙️ <b>Настройки</b> — задай цены материалов, электричество, амортизацию\n"
        "📊 <b>История</b> — последние расчёты\n"
        "📈 <b>Статистика</b> — сводные данные\n\n"
        "⏱ <b>Форматы времени:</b>\n"
        "• <code>4ч 35м</code>\n"
        "• <code>4:35</code>\n"
        "• <code>275</code> (минуты)\n\n"
        "Все настройки хранятся для каждого пользователя отдельно.",
        parse_mode="HTML",
        reply_markup=main_menu_kb()
    )
