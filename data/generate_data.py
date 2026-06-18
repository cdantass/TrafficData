"""
generate_data.py
Gerador de dados sintéticos REALISTAS para Aracaju/SE.

Simula:
- Picos de trânsito reais (7h-9h e 17h-19h nos dias úteis)
- Padrões de sábado e domingo distintos
- Feriados nacionais e sergipanos
- Carnaval e Semana Santa
- Impacto da chuva (chuvas tropicais intensas — mais fortes à tarde)
- Eventos especiais (São João, férias escolares, Black Friday)
- Perfil de congestionamento por tipo de via (Av. Tancredo, Centro, etc.)
- 1 ano de dados históricos para todas as rotas
"""

import os
import random
import math
from datetime import date, datetime, timedelta

import numpy as np
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

from aracaju_config import (
    LOCATIONS,
    ROUTES,
    WEEKDAY_SPEED_FACTORS,
    SATURDAY_SPEED_FACTORS,
    SUNDAY_SPEED_FACTORS,
    NATIONAL_HOLIDAYS,
    SERGIPE_HOLIDAYS,
    SPECIAL_EVENTS,
    RAIN_PROBABILITY,
    RAIN_SPEED_PENALTY,
    RAIN_HOUR_PROBABILITY_BOOST,
    ROUTE_CONGESTION_PROFILE,
    GENERATION_CONFIG,
)

load_dotenv()

random.seed(42)
np.random.seed(42)


# ---------------------------------------------------------------------------
# BANCO
# ---------------------------------------------------------------------------

def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        database=os.getenv("DB_NAME", "traffic"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "123"),
    )


def get_routes_from_db():
    """
    Retorna lista de (route_id, origin_name, dest_name, dist_km).
    Tenta reconstruir a distância real a partir do nome da rota.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT r.id, lo.name, ld.name
        FROM route r
        JOIN location lo ON lo.id = r.origin_id
        JOIN location ld ON ld.id = r.destination_id
        WHERE r.active = true
        ORDER BY r.id
    """)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    # Mapeia nome da origin+dest para distância real definida em ROUTES
    # Usa índice de LOCATIONS para encontrar a distância
    location_name_to_idx = {loc[0]: i for i, loc in enumerate(LOCATIONS)}

    result = []
    for route_id, origin_name, dest_name in rows:
        origin_idx = location_name_to_idx.get(origin_name)
        dest_idx   = location_name_to_idx.get(dest_name)

        dist_km = 5.0  # padrão se não achar
        if origin_idx is not None and dest_idx is not None:
            for o, d, km in ROUTES:
                if o == origin_idx and d == dest_idx:
                    dist_km = km
                    break

        result.append((route_id, origin_name, dest_name, dist_km))

    print(f"🛣️  {len(result)} rotas carregadas do banco")
    return result


# ---------------------------------------------------------------------------
# FERIADOS
# ---------------------------------------------------------------------------

def _easter_date(year: int) -> date:
    """Algoritmo de Butcher para calcular a Páscoa."""
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day   = ((h + l - 7 * m + 114) % 31) + 1
    return date(year, month, day)


def build_holiday_set(year: int) -> set:
    holidays = set()

    for month, day in NATIONAL_HOLIDAYS:
        holidays.add(date(year, month, day))

    for month, day in SERGIPE_HOLIDAYS:
        try:
            holidays.add(date(year, month, day))
        except ValueError:
            pass

    # Carnaval: 47 dias antes da Páscoa (segunda e terça)
    easter  = _easter_date(year)
    carnival_tue = easter - timedelta(days=47)
    carnival_mon = carnival_tue - timedelta(days=1)
    carnival_sat = carnival_tue - timedelta(days=3)
    carnival_sun = carnival_tue - timedelta(days=2)
    holidays.update([carnival_sat, carnival_sun, carnival_mon, carnival_tue])

    # Semana Santa: Quinta e Sexta Santa
    holy_thursday = easter - timedelta(days=3)
    good_friday   = easter - timedelta(days=2)
    holidays.update([holy_thursday, good_friday, easter])

    # Corpus Christi: 60 dias após Páscoa
    holidays.add(easter + timedelta(days=60))

    return holidays


# ---------------------------------------------------------------------------
# IMPACTO DE CHUVA
# ---------------------------------------------------------------------------

def get_rain_event(month: int, hour: int) -> tuple[str | None, float]:
    """
    Retorna (tipo_chuva, fator_velocidade).
    Chuvas tropicais de Aracaju: intensas, concentradas à tarde.
    """
    base_prob = RAIN_PROBABILITY.get(month, 0.15)
    hour_boost = RAIN_HOUR_PROBABILITY_BOOST.get(hour, 1.0)
    effective_prob = min(base_prob * hour_boost, 0.90)

    if random.random() > effective_prob:
        return None, 1.0

    # Distribuição dos tipos de chuva em Aracaju
    rain_type = random.choices(
        ["light", "moderate", "heavy"],
        weights=[0.40, 0.35, 0.25]
    )[0]

    factor = RAIN_SPEED_PENALTY[rain_type]
    noise  = random.uniform(-0.03, 0.03)
    return rain_type, max(factor + noise, 0.30)


# ---------------------------------------------------------------------------
# FATOR DE CONGESTIONAMENTO POR ROTA
# ---------------------------------------------------------------------------

def get_route_congestion_factor(origin_name: str, dest_name: str) -> float:
    route_str = f"{origin_name} {dest_name}"
    factor = 1.0
    for keyword, congestion in ROUTE_CONGESTION_PROFILE.items():
        if keyword.lower() in route_str.lower():
            factor = max(factor, congestion)
    return factor


# ---------------------------------------------------------------------------
# CÁLCULO DE VELOCIDADE
# ---------------------------------------------------------------------------

def calculate_speed(
    hour: int,
    weekday: int,      # 0=seg, 6=dom
    month: int,
    day: date,
    is_holiday: bool,
    route_congestion: float,
    rain_factor: float,
    special_event_factor: float,
) -> float:
    base_speed = GENERATION_CONFIG["base_speed_kmh"]

    # Fator por hora e dia
    if is_holiday or weekday == 6:
        hour_factor = SUNDAY_SPEED_FACTORS.get(hour, 0.85)
    elif weekday == 5:
        hour_factor = SATURDAY_SPEED_FACTORS.get(hour, 0.80)
    else:
        hour_factor = WEEKDAY_SPEED_FACTORS.get(hour, 0.70)

    # Ruído realista (±6%)
    noise = random.uniform(
        1.0 - GENERATION_CONFIG["speed_noise"],
        1.0 + GENERATION_CONFIG["speed_noise"]
    )

    speed = base_speed * hour_factor * route_congestion * rain_factor * special_event_factor * noise
    return max(speed, 5.0)  # mínimo de 5 km/h


# ---------------------------------------------------------------------------
# CLASSIFICAÇÃO DO NÍVEL DE TRÁFEGO
# ---------------------------------------------------------------------------

def classify_traffic_level(speed: float, base_speed: float = 60.0) -> str:
    ratio = speed / base_speed
    if ratio >= 0.75:
        return "LOW"
    elif ratio >= 0.50:
        return "MEDIUM"
    else:
        return "HIGH"


# ---------------------------------------------------------------------------
# GERADOR PRINCIPAL
# ---------------------------------------------------------------------------

def generate_data(routes: list, days: int = 365) -> list:
    """
    Gera dados sintéticos realistas para todas as rotas.
    Retorna lista de dicts prontos para inserção.
    """
    records = []
    end_date   = datetime.now().date()
    start_date = end_date - timedelta(days=days)

    # Pré-computa feriados para os anos necessários
    years = set(range(start_date.year, end_date.year + 1))
    all_holidays = set()
    for year in years:
        all_holidays.update(build_holiday_set(year))

    total_days = (end_date - start_date).days + 1
    print(f"\n📅 Gerando {total_days} dias × {len(routes)} rotas...")
    print(f"   Período: {start_date} → {end_date}")
    print(f"   Feriados encontrados: {len(all_holidays)}")

    current = start_date
    day_count = 0

    while current <= end_date:
        weekday    = current.weekday()  # 0=seg, 6=dom
        month      = current.month
        is_holiday = current in all_holidays

        # Fator do evento especial do mês
        special_factor = 1.0
        if month in SPECIAL_EVENTS:
            _, factor, affected_hours = SPECIAL_EVENTS[month]
            # Aplica apenas para horas afetadas (verificado por hora)
            special_factor_full = factor
        else:
            special_factor_full = 1.0
            affected_hours = []

        for route_id, origin_name, dest_name, dist_km in routes:
            route_congestion = get_route_congestion_factor(origin_name, dest_name)

            for hour in range(24):
                # Skip aleatório (simula falha de coleta)
                if random.random() < GENERATION_CONFIG["skip_hour_prob"]:
                    continue

                # Chuva (calculada por hora)
                rain_type, rain_factor = get_rain_event(month, hour)

                # Evento especial se hora afetada
                special_factor = special_factor_full if hour in affected_hours else 1.0

                speed = calculate_speed(
                    hour, weekday, month, current,
                    is_holiday, route_congestion, rain_factor, special_factor
                )

                # Duração base (sem trânsito) e com trânsito
                base_duration    = (dist_km / 60.0) * 3600       # segundos a 60 km/h
                traffic_duration = (dist_km / speed) * 3600       # segundos na velocidade real

                level = classify_traffic_level(speed)

                # Timestamp com minutos aleatórios
                timestamp = datetime.combine(
                    current,
                    datetime.min.time()
                ).replace(
                    hour=hour,
                    minute=random.randint(0, 59),
                    second=random.randint(0, 59),
                )

                records.append({
                    "route_id":            route_id,
                    "timestamp":           timestamp,
                    "duration":            round(base_duration, 2),
                    "duration_in_traffic": round(traffic_duration, 2),
                    "average_speed":       round(speed, 2),
                    "traffic_level":       level,
                })

        day_count += 1
        if day_count % 30 == 0:
            pct = (day_count / total_days) * 100
            print(f"   ⏳ {day_count}/{total_days} dias processados ({pct:.0f}%)")

        current += timedelta(days=1)

    return records


def insert_into_db(records: list):
    if not records:
        print("⚠️  Nenhum registro para inserir.")
        return

    conn = get_connection()
    cursor = conn.cursor()

    print(f"\n💾 Inserindo {len(records):,} registros no banco...")

    batch_size = 5000
    total_inserted = 0

    query = """
        INSERT INTO traffic_data
            (route_id, timestamp, duration, duration_in_traffic, average_speed, traffic_level)
        VALUES %s
        ON CONFLICT DO NOTHING
    """

    try:
        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]
            values = [
                (
                    r["route_id"],
                    r["timestamp"],
                    r["duration"],
                    r["duration_in_traffic"],
                    r["average_speed"],
                    r["traffic_level"],
                )
                for r in batch
            ]
            execute_values(cursor, query, values)
            conn.commit()
            total_inserted += len(batch)
            print(f"   ✅ Lote {i // batch_size + 1}: {total_inserted:,}/{len(records):,} inseridos")

    except Exception as e:
        conn.rollback()
        print(f"❌ Erro ao inserir: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

    return total_inserted


def print_summary(records: list):
    from collections import Counter
    levels = Counter(r["traffic_level"] for r in records)
    total  = len(records)

    print("\n" + "=" * 60)
    print("RESUMO DOS DADOS GERADOS")
    print("=" * 60)
    print(f"  Total de registros : {total:,}")
    for level in ["LOW", "MEDIUM", "HIGH"]:
        count = levels.get(level, 0)
        pct   = (count / total) * 100 if total else 0
        bar   = "█" * int(pct / 2)
        print(f"  {level:<8}: {count:>8,} ({pct:5.1f}%)  {bar}")
    print("=" * 60)


if __name__ == "__main__":
    print("=" * 60)
    print("GERADOR DE DADOS — ARACAJU/SE")
    print("=" * 60)

    routes = get_routes_from_db()

    if not routes:
        print("\n❌ Nenhuma rota encontrada.")
        print("   Execute primeiro: python data/seed_locations.py")
        exit(1)

    days = GENERATION_CONFIG["days"]
    records = generate_data(routes, days=days)

    print_summary(records)
    insert_into_db(records)

    print("\n✅ Geração concluída!")