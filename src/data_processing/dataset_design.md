# Diseño del Schema del Dataset

Este documento describe el esquema propuesto para el dataset final que se utilizará para entrenar el modelo de predicción de acciones.

## Objetivo
Predecir el movimiento del precio de una acción (subida/bajada) en un horizonte temporal determinado (e.g., 1 mes, 3 meses) basándose en transacciones de insiders.

## Schema Implementado (data/processed/insider_trades_with_targets.parquet)

### Features de Identificación
| Columna | Tipo de Dato | Descripción |
|---------|--------------|-------------|
| `ticker` | String | Símbolo de la empresa |
| `filing_date` | Date | Fecha en que la SEC publicó la transacción |
| `trade_date` | Date | Fecha real de la transacción |

### Features del Insider (Señal)
| Columna | Tipo de Dato | Descripción |
|---------|--------------|-------------|
| `insider_role` | String | Cargo del insider (CEO, CFO, Director, etc.) |
| `is_c_level` | Boolean | True si es ejecutivo de alto nivel (CEO, CFO, EVP, SVP) |
| `transaction_value` | Float | Valor total de la transacción en USD |
| `delta_owned` | Float | Qty / Owned_After (importancia relativa) |
| `owned_pct_change` | Float | Cambio % en la tenencia del insider (directo del CSV) |
| `reporting_lag` | Integer | Días entre trade_date y filing_date |
| `cluster_buy` | Integer | Número de insiders operando el **mismo día** |
| `cluster_size` | Integer | Número de insiders **únicos** en ventana de **7 días** |

**Nota sobre clustering**:
- `cluster_buy`: Captura compras el mismo día (útil pero restrictivo)
- `cluster_size`: Captura compras coordinadas en ventana de 7 días (señal más fuerte)
  - Valor 1 = compra individual
  - Valor 2-5 = cluster pequeño
  - Valor 6-20 = cluster grande (señal fuerte)
  - Valor 20+ = cluster masivo (señal extrema)
- Análisis mostró que **52.2% de transacciones ocurren en clusters de 7 días**

### Target Variables (Retornos Futuros)
| Columna | Tipo de Dato | Descripción |
|---------|--------------|-------------|
| `return_1w` | Float | Retorno 7 días después del filing_date |
| `return_1m` | Float | Retorno 30 días después del filing_date |
| `return_3m` | Float | Retorno 90 días después del filing_date |

### Features de Contexto Adicional (Notebook 03)
| Columna | Tipo de Dato | Descripción |
|---------|--------------|-------------|
| `insider_id` | String | Identificador único del insider (ticker + role) |
| `insider_trade_count` | Integer | Número de transacciones previas del insider (track record) |
| `days_since_last_trade` | Float | Días desde la última operación del insider (frecuencia) |
| `trade_day_of_week` | Integer | Día de la semana de la transacción (0=Lun, 4=Vie) |
| `cluster_c_level_pct` | Float | % de ejecutivos C-level en el cluster de 7 días |

### Features NO Implementadas (Datos Externos No Disponibles)
| Columna | Razón de No Implementación |
|---------|---------------------------|
| `sector` | No disponible en APIs gratuitas (Tiingo/yfinance) |
| `market_cap` | Datos muy inconsistentes o no disponibles |
| `relative_transaction_value` | Requiere market_cap confiable |
| `market_cap_category` | Requiere market_cap confiable |
| `industry` | No disponible en endpoints básicos |
| `owned_pct_change` | Redundante con `delta_owned` |

## Progreso del Pipeline

1. **Limpieza de Datos**: Implementado en **[01_data_cleaning.ipynb](01_data_cleaning.ipynb)**
   - Estandarización de fechas y valores numéricos
   - Cálculo de `delta_owned`, `reporting_lag`, `cluster_buy`, `cluster_size`
   - Identificación de roles C-Level
   - Filtrado de outliers (reporting_lag > 180 días, transaction_value < $50k)
   - **Feature de clustering**: `cluster_size` (insiders únicos en 7 días) - captura compras coordinadas
   
2. **Integración con Tiingo**: Implementado en **[02_tiingo_integration.ipynb](02_tiingo_integration.ipynb)** 
   - Sistema de caché persistente (531.74 MB, 7,398 tickers)
   - **45,242 transacciones** procesadas (dataset completo)
   - **Retornos calculados** con 90% cobertura:
     - Media 1w: +1.10% | 1m: +1.95% | 3m: +30.71%
   - **Señal prometedora**: Retornos positivos consistentes

3. **Feature Engineering Avanzado**: Implementado en **[03_feature_engineering.ipynb](03_feature_engineering.ipynb)**
   - `insider_id`: Identificador único del insider
   - `insider_trade_count`: Track record (experiencia)
   - `days_since_last_trade`: Frecuencia de trading
   - `trade_day_of_week`: Timing de la operación
   - `cluster_c_level_pct`: Calidad del cluster (% C-levels)
   - **Dataset final**: `insider_trades_final.parquet` (45,242 × 19 columnas)
   - **12,399 insiders únicos** identificados

