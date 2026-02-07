# Diseño del Schema del Dataset

Este documento describe el esquema del dataset final ML-ready que se utilizará para entrenar el modelo de predicción de acciones.

## Objetivo
Predecir el movimiento del precio de una acción (subida/bajada) en un horizonte temporal determinado (e.g., 1 mes, 3 meses) basándose en transacciones de insiders.

## Schema Final (data/processed/insider_trades_ml_ready.parquet)

**Dataset:** 42,015 transacciones × 23 columnas (optimizado para ML)  
**Periodo:** 2018-2026  
**Tamaño:** 3.95 MB

---

### Features de Identificación
| Columna | Tipo | Descripción | Cobertura |
|---------|------|-------------|-----------|
| `ticker` | String | Símbolo de la empresa | 100.0% |
| `filing_date` | Datetime | Fecha en que la SEC publicó la transacción | 100.0% |
| `insider_id` | String | Identificador único: ticker + role | 100.0% |

---

### Features del Insider (Señal)
| Columna | Tipo | Descripción | Cobertura |
|---------|------|-------------|-----------|
| `role_bucket` | Integer | **Jerarquía numérica del insider (1-4)** | 100.0% |
| `log_transaction_value` | Float | **Log del valor de transacción (normalizado)** | 100.0% |
| `delta_owned` | Float | Qty / Owned_After (importancia relativa) | 100.0% |
| `owned_pct_change` | Float | Cambio % en tenencia del insider | 100.0% |
| `insider_trade_count` | Integer | Track record del insider (# operaciones previas) | 100.0% |
| `days_since_last_trade` | Float | Frecuencia de trading | 72.7% |

**Jerarquía `role_bucket`:**
- **4** = Top (CEO, CFO, COO, Chairman, Board)
- **3** = High (President, EVP, SVP, VP)
- **2** = Director (Non-executive)
- **1** = Other (Officer, 10% Owner)

### Features del Evento
| Columna | Tipo | Descripción | Cobertura |
|---------|------|-------------|-----------|
| `reporting_lag` | Integer | Días entre trade_date y filing_date | 100.0% |
| `cluster_buy` | Integer | # insiders operando el mismo día | 100.0% |
| `cluster_c_level_pct` | Float | % de C-levels en el cluster | 100.0% |

**Nota sobre clustering:**
- `cluster_size` captura compras coordinadas (ventana 7 días)
- 52.2% de transacciones ocurren en clusters
- Valores típicos: 1 (individual), 2-5 (pequeño), 6-20 (grande), 20+ (masivo)

### Features Fundamentales 
| Columna | Tipo | Descripción | Cobertura | Fuente |
|---------|------|-------------|-----------|--------|
| `log_market_cap`| Float | Log de capitalización bursátil (normalizado) | 100.0% | yfinance |
| `sector` | String | Sector industrial (categórico) | 78.5% | yfinance |

** Feature Eliminada:** `market_cap` (outliers masivos, reemplazado por `log_market_cap`)

**Nota:** 66.3% de tickers tienen `market_cap` en yfinance. Los faltantes usan `log_market_cap = 0`.

### Features Técnicas 
| Columna | Tipo | Descripción | Cobertura | Fuente |
|---------|------|-------------|-----------|--------|
| `price_range_position` | Float | (Price - Low52) / (High52 - Low52) | 97.1% | Tiingo |
| `volatility_30d` | Float | Volatilidad 30d anualizada (Std × √252) | 94.1% | Tiingo |

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
| `alpha_1w` | Float | Alpha 1 semana | 96.8% | Stock Return - Benchmark Return |
| `alpha_1m` | Float | Alpha 1 mes (RECOMENDADO) | 96.3% | Stock Return - Benchmark Return |
| `alpha_3m` | Float | Alpha 3 meses | 93.8% | Stock Return - Benchmark Return |
| `benchmark_used` | String | Benchmark aplicado (SPY/IWM/IWV) | 100.0% | Metadata |
| `return_1w` | Float | Retorno absoluto 1 semana | 96.8% | (Price_t+7 - Price_t) / Price_t |
| `return_1m` | Float | Retorno absoluto 1 mes | 96.3% | (Price_t+30 - Price_t) / Price_t |
| `return_3m` | Float | Retorno absoluto 3 meses | 93.8% | (Price_t+90 - Price_t) / Price_t |

**Lógica de Benchmark Híbrido:**
```python
if market_cap >= $10B → SPY (S&P 500 - Large Caps)
elif market_cap < $10B → IWM (Russell 2000 - Small/Mid Caps)
else → IWV (Russell 3000 - Fallback)
```

**Distribución de benchmarks:**
- **IWM** (Small/Mid): 67.0% (28,167 transacciones)
- **IWV** (Fallback): 21.3% (8,955 transacciones)
- **SPY** (Large): 11.6% (4,893 transacciones)

**Estadísticas Alpha vs Retornos Absolutos:**
| Métrica | return_1m | alpha_1m | Diferencia |
|---------|-----------|----------|------------|
| Media | +1.95% | +0.94% | 1.01% (beta removido) |
| Mediana | +0.32% | -0.62% | - |

**Interpretación:** El modelo con `alpha_1m` predice el **verdadero skill del insider**, eliminando el sesgo del mercado alcista.

### Outlier Treatment
Los retornos y alphas se han **capeado** a límites financieramente razonables:

| Métrica | Rango Válido | Justificación |
|---------|--------------|---------------|
| **Retornos** | -100% a +300% | Stock no puede perder >100%; triplicar en 1-3 meses es raro pero posible |
| **Alpha** | -150% a +300% | Alpha puede ser < -100% si benchmark sube mientras stock colapsa |

---

## 📊 Resumen Ejecutivo

### ✅ Dataset Final (ML-Ready)
- **Archivo**: `insider_trades_ml_ready.parquet`
- **Registros**: 42,015 transacciones
- **Columnas**: 23 (optimizadas, sin redundancia)
- **Tamaño**: 3.95 MB
- **Tickers únicos**: 5,060

## 📚 Notebooks del Pipeline

### 1. **01_data_cleaning.ipynb**
   - Estandarización de fechas y valores numéricos
   - Cálculo de `delta_owned`, `reporting_lag`, `cluster_buy`
   - Identificación de roles C-Level
   - Filtrado de outliers (reporting_lag > 180 días, transaction_value < $50k)
   - **Output**: `insider_trades_processed.parquet`

### 2. **02_tiingo_integration.ipynb**
   - Sistema de caché persistente (530 MB, 5,063 tickers)
   - Diagnóstico de datos: 3,855 activos, 1,086 delistados, 456 sin datos
   - Eliminación de tickers sin datos (3,211 transacciones, 7.1%)
   - 42,015 transacciones procesadas
   - Retornos calculados (96%+ cobertura)
   - **Output**: `insider_trades_with_targets.parquet`

### 3. **03_feature_engineering.ipynb**
   - **Parte 1 - Features Básicas**: `insider_id`, `insider_trade_count`, `days_since_last_trade`, `cluster_c_level_pct`
   - **Parte 2 - Features Avanzadas**:
     - **Alpha Targets** (market-corrected): `alpha_1w`, `alpha_1m`, `alpha_3m`
     - **Fundamentales**: `sector` (78.5% cov), `log_market_cap`
     - **Técnicas**: `price_range_position` (97.1%), `volatility_30d` (94.1%)
     - **Refinados**: `role_bucket`, `log_transaction_value`
   - **Outlier Capping**: Retornos -100%/+300%, Alpha -150%/+300%
   - **Eliminadas**: columnas redundantes
   - **Output**: `insider_trades_ml_ready.parquet` (**23 columnas**)
