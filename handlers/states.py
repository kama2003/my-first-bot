from aiogram.fsm.state import State, StatesGroup


class CalcStates(StatesGroup):
    material = State()
    weight = State()
    time = State()
    copies = State()
    infill = State()
    delivery = State()
    packaging = State()
    postprocess = State()
    painting = State()
    assembly = State()
    profit = State()


class SettingsStates(StatesGroup):
    filament_price = State()
    filament_weight = State()
    electricity_cost = State()
    printer_power = State()
    printer_cost = State()
    printer_lifetime = State()
    defect_percent = State()
    extra_cost = State()
    markup_percent = State()
    material_price = State()
    material_weight = State()
