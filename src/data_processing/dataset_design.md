# Diseño del Schema del Dataset

Este documento describe el esquema del dataset final ML-ready que se utilizará para entrenar el modelo de predicción de acciones.

## Objetivo
Predecir el movimiento del precio de una acción (subida/bajada) en un horizonte temporal determinado (e.g., 1 mes, 3 meses) basándose en transacciones de insiders.

## Schema Final (data/processed/insider_trades_ml_ready.parquet)

**Dataset:** 45,242 transacciones × 25 columnas (optimizado para ML)  
**Periodo:** 2018-2026  
**Tamaño:** 4.29 MB

---

### Features de Identificación
| Columna | Tipo | Descripción | Cobertura |
|---------|------|-------------|-----------|
| `ticker` | String | Símbolo de la empresa | 99.9% |
| `filing_date` | Datetime | Fecha en que la SEC publicó la transacción | 99.9% |
| `insider_id` | String | Identificador único: ticker + role | 99.9% |

---

### Features del Insider (Señal)
| Columna | Tipo | Descripción | Cobertura |
|---------|------|-------------|-----------
| `role_bucket` | Integer | **Jerarquía numérica del insider (1-4)** | 100.0% |
| `log_transaction_value` | Float | **Log del valor de transacción (normalizado)** | 99.9% |
| `delta_owned` | Float | Qty / Owned_After (importancia relativa) | 99.9% |
| `owned_pct_change` | Float | Cambio % en tenencia del insider | 99.9% |
| `insider_trade_count` | Integer | Track record del insider (# operaciones previas) | 99.9% |
| `days_since_last_trade` | Float | Frecuencia de trading | 72.5% |

**Jerarquía `role_bucket`:**
- **4** = Top (CEO, CFO, COO, Chairman, Board)
- **3** = High (President, EVP, SVP, VP)
- **2** = Director (Non-executive)
- **1** = Other (Officer, 10% Owner)

### Features del Evento
| Columna | Tipo | Descripción | Cobertura |
|---------|------|-------------|-----------|
| `reporting_lag` | Integer | Días entre trade_date y filing_date | 99.9% |
| `trade_day_of_week` | Integer | Día de la semana (0=Lun, 4=Vie) | 99.9% |
| `cluster_buy` | Integer | # insiders operando el mismo día | 99.9% |
| `cluster_size` | Integer | # insiders únicos en ventana de 7 días | 99.9% |
| `cluster_c_level_pct` | Float | % de C-levels en el cluster | 99.9% |

**Nota sobre clustering:**
- `cluster_size` captura compras coordinadas (ventana 7 días)
- 52.2% de transacciones ocurren en clusters
- Valores típicos: 1 (individual), 2-5 (pequeño), 6-20 (grande), 20+ (masivo)

### Features Fundamentales 
| Columna | Tipo | Descripción | Cobertura | Fuente |
|---------|------|-------------|-----------|--------|
| `log_market_cap`| Float | Log de capitalización bursátil (normalizado) | 100.0% | yfinance |
| `sector` | String | Sector industrial (categórico) | 73.3% | yfinance |

** Feature Eliminada:** `market_cap` (outliers masivos, reemplazado por `log_market_cap`)

**Nota:** 66.3% de tickers tienen `market_cap` en yfinance. Los faltantes usan `log_market_cap = 0`.

### Features Técnicas 
| Columna | Tipo | Descripción | Cobertura | Fuente |
|---------|------|-------------|-----------|--------|
| `price_range_position` | Float | (Price - Low52) / (High52 - Low52) | 90.2% | Tiingo |
| `volatility_30d` | Float | Volatilidad 30d anualizada (Std × √252) | 87.4% | Tiingo |

**`price_range_position` (0 a 1):**
- **0.0** = En mínimos anuales (señal MUY fuerte de compra insider)
- **0.5** = En medio del rango
- **1.0** = En máximos anuales (momentum/sobrecompra)

**Distribución observada:**
- Media: **0.347** (mayoría compra en rango bajo/medio)
- En mínimos (0.0-0.2): **41.7%** de transacciones
- En máximos (0.8-1.0): **13.5%** de transacciones


### Target Variables  (Alpha Market-Corrected)
| Columna | Tipo | Descripción | Cobertura | Fórmula |
|---------|------|-------------|-----------|---------|
| `alpha_1w` | Float | Alpha 1 semana | 89.9% | Stock Return - Benchmark Return |
| `alpha_1m` | Float | Alpha 1 mes (RECOMENDADO) | 89.4% | Stock Return - Benchmark Return |
| `alpha_3m` | Float | Alpha 3 meses | 87.0% | Stock Return - Benchmark Return |
| `benchmark_used` | String | Benchmark aplicado (SPY/IWM/IWV) | 100.0% | Metadata |
| `return_1w` | Float | Retorno absoluto 1 semana | 90.0% | (Price_t+7 - Price_t) / Price_t |
| `return_1m` | Float | Retorno absoluto 1 mes | 89.5% | (Price_t+30 - Price_t) / Price_t |
| `return_3m` | Float | Retorno absoluto 3 meses | 87.1% | (Price_t+90 - Price_t) / Price_t |

**Lógica de Benchmark Híbrido:**
```python
if market_cap >= $10B → SPY (S&P 500 - Large Caps)
elif market_cap < $10B → IWM (Russell 2000 - Small/Mid Caps)
else → IWV (Russell 3000 - Fallback)
```

**Distribución de benchmarks:**
- **IWM** (Small/Mid): 62.5% (28,290 transacciones)
- **SPY** (Large): 26.2% (11,845 transacciones)
- **IWV** (Fallback): 11.3% (5,107 transacciones)

**Estadísticas Alpha vs Retornos Absolutos:**
| Métrica | return_1m | alpha_1m | Diferencia |
|---------|-----------|----------|------------|
| Media | +1.95% | +0.94% | 1.01% (beta removido) |
| Mediana | +0.32% | -0.62% | - |

**Interpretación:** El modelo con `alpha_1m` predice el **verdadero skill del insider**, eliminando el sesgo del mercado alcista.

## 📊 Resumen Ejecutivo

### ✅ Dataset Final (ML-Ready)
- **Archivo**: `insider_trades_ml_ready.parquet`
- **Registros**: 45,242 transacciones
- **Columnas**: 25 (optimizadas, sin redundancia)
- **Tamaño**: 4.29 MB

## 📚 Notebooks del Pipeline

### 1. **01_data_cleaning.ipynb**
   - Estandarización de fechas y valores numéricos
   - Cálculo de `delta_owned`, `reporting_lag`, `cluster_buy`, `cluster_size`
   - Identificación de roles C-Level
   - Filtrado de outliers (reporting_lag > 180 días, transaction_value < $50k)
   - **Output**: `insider_trades_processed.parquet`

### 2. **02_tiingo_integration.ipynb**
   - Sistema de caché persistente (531.74 MB, 7,398 tickers)
   - 45,242 transacciones procesadas
   - Retornos calculados (90% cobertura)
   - **Output**: `insider_trades_with_targets.parquet`

### 3. **03_feature_engineering.ipynb**
   - `insider_id`, `insider_trade_count`, `days_since_last_trade`
   - `trade_day_of_week`, `cluster_c_level_pct`
   - 12,399 insiders únicos identificados
   - **Output**: `insider_trades_final.parquet` (19 columnas)

### 4. **04_advanced_features.ipynb**
   - **Alpha Targets** (market-corrected): `alpha_1w`, `alpha_1m`, `alpha_3m`
   - **Fundamentales**: `sector` (73% cov), `log_market_cap`
   - **Técnicas**: `price_range_position`, `volatility_30d`
   - **Refinados**: `role_bucket`, `log_transaction_value`
   - **Eliminadas**: 7 columnas redundantes
   - **Output**: `insider_trades_ml_ready.parquet` (**25 columnas**)
