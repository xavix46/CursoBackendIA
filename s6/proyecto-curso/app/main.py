from app.services import gastos as gastos_service
from app.utils.formato import formatear_moneda

if __name__ == "__main__":
    gastos_service.registrar_gasto("Almuerzo", 12.50, "comida")
    gastos_service.registrar_gasto("Bus", 2.00, "transporte")

    for gasto in gastos_service.listar_gastos():
        print(f"{gasto['descripcion']}: {formatear_moneda(gasto['monto'])} ({gasto['categoria']})")
