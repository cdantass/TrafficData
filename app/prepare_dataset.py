"""
prepare_dataset.py

Transforma o dataset UCI Metro Interstate Traffic Volume
em dados compatíveis com o banco do projeto Aracaju.

Dataset: https://archive.ics.uci.edu/dataset/492/metro+interstate+traffic+volume
Arquivo: Metro_Interstate_Traffic_Volume.csv
"""

import os

import holidays
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()


def get_engine():
    url = (
        f"postgresql+psycopg2://{os.getenv('DB_USER', 'postgres')}"
        f":{os.getenv('DB_PASSWORD', '123')}"
        f"@{os.getenv('DB_HOST', 'localhost')}"
        f":{os.getenv('DB_PORT', '5432')}"
        f"/{os.getenv('DB_NAME', 'traffic')}"
    )
    return create_engine(url)


def get_route_ids() -> list:
    """Busca todos os IDs de rotas ativas do banco."""
    engine = get_engine()
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT id FROM route WHERE active = true"))
            ids = [row[0] for row in result]
        print(f"🛣️  Rotas encontradas no banco: {ids}")
        return ids
    finally:
        engine.dispose()


def load_uci_dataset(csv_path: str) -> pd.DataFrame:
    """Carrega e valida o dataset UCI."""
    print(f"📂 Carregando dataset: {csv_path}")

    if not os.path.exists(csv_path):
        raise FileNotFoundError(
            f"\n❌ Arquivo não encontrado: {csv_path}"
            f"\n\n👉 Siga os passos:"
            f"\n   1. Acesse: https://archive.ics.uci.edu/dataset/492/metro+interstate+traffic+volume"
            f"\n   2. Clique em 'Download' para baixar o ZIP"
            f"\n   3. Extraia o arquivo 'Metro_Interstate_Traffic_Volume.csv'"
            f"\n   4. Coloque-o na pasta: traffic-ai/data/"
        )

    df = pd.read_csv(csv_path)
    print(f"✅ {len(df)} registros carregados do dataset UCI")
    print(f"   Colunas: {list(df.columns)}")
    return df


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transforma o dataset UCI para o formato do projeto.

    Colunas originais do UCI:
    - holiday, temp, rain_1h, snow_1h, clouds_all, weather_main,
      weather_description, date_time, traffic_volume
    """
    print("⚙️  Processando features...")

    df = df.copy()

    df["date_time"] = pd.to_datetime(df["date_time"])

    df["hour"] = df["date_time"].dt.hour
    df["day_of_week"] = df["date_time"].dt.dayofweek
    df["month"] = df["date_time"].dt.month
    df["is_weekend"] = (df["day_of_week"] >= 5).astype(int)

    df["is_rush_hour"] = (
        ((df["hour"] >= 7) & (df["hour"] <= 9)) |
        ((df["hour"] >= 17) & (df["hour"] <= 19))
    ).astype(int)

    br_holidays = holidays.Brazil(
        state="SE",
        years=df["date_time"].dt.year.unique().tolist()
    )
    df["is_holiday"] = df["date_time"].dt.date.apply(
        lambda d: 1 if d in br_holidays else 0
    )

    df["temp_celsius"] = df["temp"] - 273.15
    df["is_raining"] = (df["rain_1h"] > 0).astype(int)

    low_threshold = df["traffic_volume"].quantile(0.33)
    high_threshold = df["traffic_volume"].quantile(0.66)

    def classify_traffic(volume):
        if volume <= low_threshold:
            return "LOW"
        elif volume <= high_threshold:
            return "MEDIUM"
        return "HIGH"

    df["traffic_level"] = df["traffic_volume"].apply(classify_traffic)

    speed_map = {"LOW": 60, "MEDIUM": 40, "HIGH": 25}
    df["average_speed"] = df["traffic_level"].map(speed_map).astype(float)
    df["average_speed"] += np.random.uniform(-5, 5, len(df))
    df["average_speed"] = df["average_speed"].clip(lower=5)

    df["duration"] = np.random.uniform(600, 2400, len(df))
    df["duration_in_traffic"] = df.apply(
        lambda r: r["duration"] * (
            1.5 if r["traffic_level"] == "HIGH"
            else 1.2 if r["traffic_level"] == "MEDIUM"
            else 1.0
        ),
        axis=1
    )

    print("   Distribuição de tráfego:")
    print(df["traffic_level"].value_counts().to_string())

    return df


def insert_into_db(df: pd.DataFrame, route_ids: list):
    """
    Insere os dados processados no banco usando SQLAlchemy,
    distribuindo entre as rotas disponíveis.
    """
    engine = get_engine()

    cols = [
        "hour", "day_of_week", "month", "is_weekend", "is_rush_hour",
        "is_holiday", "temp_celsius", "is_raining", "average_speed",
        "traffic_level", "duration", "duration_in_traffic", "date_time"
    ]
    df_clean = df[cols].drop_duplicates(subset=["date_time"]).copy()

    insert_sql = text("""
        INSERT INTO traffic_data
            (route_id, timestamp, duration, duration_in_traffic, average_speed, traffic_level)
        VALUES
            (:route_id, :timestamp, :duration, :duration_in_traffic, :average_speed, :traffic_level)
        ON CONFLICT DO NOTHING
    """)

    total = 0

    try:
        with engine.begin() as conn:
            for route_id in route_ids:
                print(f"\n💾 Inserindo dados para rota {route_id}...")

                route_factor = np.random.uniform(0.7, 1.3)

                records = []
                for _, row in df_clean.iterrows():
                    records.append({
                        "route_id": route_id,
                        "timestamp": row["date_time"].to_pydatetime(),
                        "duration": round(float(row["duration"]) * route_factor, 2),
                        "duration_in_traffic": round(float(row["duration_in_traffic"]) * route_factor, 2),
                        "average_speed": round(float(row["average_speed"]), 2),
                        "traffic_level": row["traffic_level"]
                    })

                conn.execute(insert_sql, records)
                inserted = len(records)
                total += inserted

                print(f"   ✅ {inserted} registros processados")
    finally:
        engine.dispose()

    print(f"\n🎉 Total processado: {total} registros em {len(route_ids)} rotas")


def main():
    csv_path = "data/Metro_Interstate_Traffic_Volume.csv"

    df = load_uci_dataset(csv_path)
    df = engineer_features(df)

    route_ids = get_route_ids()
    if not route_ids:
        print("❌ Nenhuma rota encontrada no banco. Execute seed_locations.py primeiro.")
        return

    insert_into_db(df, route_ids)

    print("\n✅ Dataset pronto! Agora execute POST /train para retreinar o modelo.")


if __name__ == "__main__":
    main()