import os
import random
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

load_dotenv()


def get_traffic_level(hour, day_of_week, base_duration, duration_in_traffic):
    ratio = duration_in_traffic / base_duration

    if ratio >= 1.5:
        return "HIGH"
    elif ratio >= 1.2:
        return "MEDIUM"
    else:
        return "LOW"


def generate_duration(hour, day_of_week, base_km):
    """Simula duração realista baseada em hora e dia"""
    speed = 60.0

    if day_of_week < 5 and 7 <= hour <= 9:
        speed *= random.uniform(0.4, 0.6)
    elif day_of_week < 5 and 17 <= hour <= 19:
        speed *= random.uniform(0.35, 0.55)
    elif day_of_week < 5 and 10 <= hour <= 16:
        speed *= random.uniform(0.65, 0.85)
    elif hour < 6 or hour > 22:
        speed *= random.uniform(0.9, 1.0)
    elif day_of_week >= 5:
        speed *= random.uniform(0.75, 0.95)
    else:
        speed *= random.uniform(0.7, 0.9)

    base_duration = (base_km / 60) * 3600
    duration_in_traffic = (base_km / speed) * 3600
    average_speed = speed

    return base_duration, duration_in_traffic, average_speed


def generate_synthetic_data(route_ids: list, days: int = 180):
    """Gera N dias de dados históricos para cada rota"""
    records = []
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    route_distances = {rid: random.uniform(3, 25) for rid in route_ids}

    current = start_date
    while current <= end_date:
        for route_id in route_ids:
            for hour in range(0, 24):
                if random.random() < 0.3:
                    continue

                timestamp = current.replace(
                    hour=hour,
                    minute=random.randint(0, 59),
                    second=random.randint(0, 59),
                    microsecond=0
                )

                base_km = route_distances[route_id]

                base_dur, dur_traffic, avg_speed = generate_duration(
                    hour, current.weekday(), base_km
                )

                level = get_traffic_level(
                    hour, current.weekday(), base_dur, dur_traffic
                )

                records.append({
                    "route_id": route_id,
                    "timestamp": timestamp,
                    "duration": round(base_dur, 2),
                    "duration_in_traffic": round(dur_traffic, 2),
                    "average_speed": round(avg_speed, 2),
                    "traffic_level": level
                })

        current += timedelta(days=1)

    return pd.DataFrame(records)


def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        database=os.getenv("DB_NAME", "traffic"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "123"),
        port=os.getenv("DB_PORT", "5432")
    )


def get_route_ids() -> list:
    """Busca os IDs de todas as rotas ativas do banco"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id FROM route WHERE active = true")
        ids = [row[0] for row in cursor.fetchall()]
        return ids
    finally:
        cursor.close()
        conn.close()


def insert_into_db(df: pd.DataFrame):
    """Insere os dados gerados na tabela traffic_data"""
    if df.empty:
        print("⚠️ Nenhum dado para inserir.")
        return

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        values = [
            (
                int(row.route_id),
                row.timestamp,
                float(row.duration),
                float(row.duration_in_traffic),
                float(row.average_speed),
                row.traffic_level
            )
            for row in df.itertuples(index=False)
        ]

        query = """
            INSERT INTO traffic_data (
                route_id,
                timestamp,
                duration,
                duration_in_traffic,
                average_speed,
                traffic_level
            ) VALUES %s
        """

        execute_values(cursor, query, values)
        conn.commit()

        print(f"✅ {len(values)} registros inseridos com sucesso na tabela traffic_data.")

    except Exception as e:
        conn.rollback()
        print(f"❌ Erro ao inserir dados no banco: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    ROUTE_IDS = get_route_ids()
    print(f"🛣️ Rotas encontradas: {ROUTE_IDS}")

    if not ROUTE_IDS:
        print("⚠️ Nenhuma rota ativa encontrada na tabela route.")
    else:
        df = generate_synthetic_data(ROUTE_IDS, days=180)

        print(df["traffic_level"].value_counts())
        print(f"📊 Total de registros gerados: {len(df)}")

        insert_into_db(df)