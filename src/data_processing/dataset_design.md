# Diseño del Schema del Dataset

Este documento describe el esquema propuesto para el dataset final que se utilizará para entrenar el modelo de predicción de acciones.

## Objetivo
Predecir el movimiento del precio de una acción (subida/bajada) en un horizonte temporal determinado (e.g., 1 mes, 3 meses) basándose en transacciones de insiders.

## Schema Propuesto (data/processed/final_dataset.parquet)

| Columna | Tipo de Dato | Descripción |
|---------|--------------|-------------|
| `transaction_id` | String | Identificador único de la transacción (generado) |
| `date` | Date | Fecha de la transacción |
| `ticker` | String | Símbolo de la empresa |
| `insider_id` | String | Identificador del insider |
| `insider_title` | String | Cargo del insider (CEO, CFO, Director, etc.) |
| `transaction_type` | Categorical | Compra (P) o Venta (S) |
| `price` | Float | Precio de la transacción |
| `quantity` | Integer | Cantidad de acciones |
| `value` | Float | Valor total de la transacción |
| `shares_owned_before` | Integer | Acciones poseídas antes de la transacción |
| `shares_owned_after` | Integer | Acciones poseídas después |
| `pct_change_holdings` | Float | Cambio porcentual en la tenencia del insider |
| `is_informative` | Boolean | Si la transacción se considera informativa (e.g., no es una concesión de opciones) |
| `stock_return_1w` | Float | Retorno de la acción 1 semana después (Target potencial) |
| `stock_return_1m` | Float | Retorno de la acción 1 mes después (Target potencial) |
| `stock_return_3m` | Float | Retorno de la acción 3 meses después (Target potencial) |
| `sector` | Categorical | Sector de la empresa |
| `industry` | Categorical | Industria de la empresa |
| `market_cap` | Float | Capitalización de mercado en el momento de la transacción |

## Pasos Siguientes
1. **Limpieza de Datos**: Estandarizar nombres, filtrar transacciones irrelevantes.
2. **Feature Engineering**: Calcular `pct_change_holdings`, agregar datos históricos de precios para calcular los returns.
3. **Enriquecimiento**: Cruzar con datos fundamentales (Sector, Market Cap).
