from dataclasses import dataclass


@dataclass
class CalcInput:
    weight: float
    print_time: float
    filament_price_per_gram: float
    electricity_cost: float
    printer_power: float
    printer_cost: float
    printer_lifetime: float
    defect_percent: float
    extra_cost: float
    markup_percent: float
    copies: int = 1
    infill: float = 100.0
    delivery: float = 0.0
    packaging: float = 0.0
    postprocess: float = 0.0
    painting: float = 0.0
    assembly: float = 0.0
    desired_profit: float = 0.0


@dataclass
class CalcResult:
    cost_filament: float
    cost_electricity: float
    cost_amortization: float
    cost_extra: float
    cost_defect: float
    cost_delivery: float
    cost_packaging: float
    cost_postprocess: float
    cost_painting: float
    cost_assembly: float
    desired_profit: float
    total_cost: float
    sale_price: float


def calculate(inp: CalcInput) -> CalcResult:
    hours = inp.print_time / 60

    cost_filament = inp.weight * inp.filament_price_per_gram * (inp.infill / 100)
    cost_electricity = hours * inp.printer_power * inp.electricity_cost
    cost_amortization = hours * (inp.printer_cost / inp.printer_lifetime)
    cost_extra = inp.extra_cost

    subtotal = cost_filament + cost_electricity + cost_amortization + cost_extra
    subtotal *= inp.copies

    cost_defect = subtotal * (inp.defect_percent / 100)
    total_cost = subtotal + cost_defect

    additional = (inp.delivery + inp.packaging + inp.postprocess +
                  inp.painting + inp.assembly) * inp.copies
    total_cost += additional

    sale_price = total_cost * (1 + inp.markup_percent / 100) + inp.desired_profit

    return CalcResult(
        cost_filament=round(cost_filament * inp.copies, 2),
        cost_electricity=round(cost_electricity * inp.copies, 2),
        cost_amortization=round(cost_amortization * inp.copies, 2),
        cost_extra=round(cost_extra * inp.copies, 2),
        cost_defect=round(cost_defect, 2),
        cost_delivery=round(inp.delivery * inp.copies, 2),
        cost_packaging=round(inp.packaging * inp.copies, 2),
        cost_postprocess=round(inp.postprocess * inp.copies, 2),
        cost_painting=round(inp.painting * inp.copies, 2),
        cost_assembly=round(inp.assembly * inp.copies, 2),
        desired_profit=round(inp.desired_profit, 2),
        total_cost=round(total_cost, 2),
        sale_price=round(sale_price, 2),
    )
