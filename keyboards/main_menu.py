from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


def main_menu_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="🧮 Рассчитать стоимость"))
    builder.row(
        KeyboardButton(text="⚙️ Настройки"),
        KeyboardButton(text="📊 История"),
    )
    builder.row(
        KeyboardButton(text="📈 Статистика"),
        KeyboardButton(text="ℹ️ Помощь"),
    )
    return builder.as_markup(resize_keyboard=True)


def settings_menu_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🧵 Материалы и цены", callback_data="settings_materials"))
    builder.row(InlineKeyboardButton(text="⚡ Электроэнергия", callback_data="settings_electricity"))
    builder.row(InlineKeyboardButton(text="🖨 Амортизация принтера", callback_data="settings_printer"))
    builder.row(InlineKeyboardButton(text="⚠️ Процент брака", callback_data="settings_defect"))
    builder.row(InlineKeyboardButton(text="📦 Доп. расходы", callback_data="settings_extra"))
    builder.row(InlineKeyboardButton(text="💰 Наценка", callback_data="settings_markup"))
    builder.row(InlineKeyboardButton(text="🔙 Главное меню", callback_data="main_menu"))
    return builder.as_markup()


def materials_kb(materials: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for mat in materials:
        price_per_g = mat.filament_price / mat.filament_weight
        builder.row(InlineKeyboardButton(
            text=f"{mat.name} — {mat.filament_price:.0f}₽/{mat.filament_weight:.0f}г ({price_per_g:.2f}₽/г)",
            callback_data=f"edit_material_{mat.name}"
        ))
    builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="settings_back"))
    return builder.as_markup()


def material_select_kb(materials: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for mat in materials:
        builder.row(InlineKeyboardButton(
            text=f"{mat.name} ({mat.filament_price/mat.filament_weight:.2f}₽/г)",
            callback_data=f"calc_material_{mat.name}"
        ))
    return builder.as_markup()


def cancel_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="❌ Отмена", callback_data="cancel"))
    return builder.as_markup()


def skip_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="⏭ Пропустить", callback_data="skip"))
    builder.row(InlineKeyboardButton(text="❌ Отмена", callback_data="cancel"))
    return builder.as_markup()


def admin_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="📥 Экспорт в Excel", callback_data="admin_export"))
    builder.row(InlineKeyboardButton(text="🗑 Очистить историю", callback_data="admin_clear"))
    builder.row(InlineKeyboardButton(text="💾 Резервная копия БД", callback_data="admin_backup"))
    return builder.as_markup()


def history_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="📥 Экспорт в Excel", callback_data="admin_export"))
    return builder.as_markup()
