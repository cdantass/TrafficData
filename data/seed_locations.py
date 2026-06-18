import os
import psycopg2
from dotenv import load_dotenv
from aracaju_config import LOCATIONS, ROUTES

load_dotenv()


def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        database=os.getenv("DB_NAME", "traffic"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "123"),
    )


def seed():
    conn = get_connection()
    cursor = conn.cursor()

    print("=" * 60)
    print("SEED — LOCALIZAÇÕES E ROTAS DE ARACAJU")
    print("=" * 60)

    # Limpa na ordem correta (respeita FKs)
    print("\n🧹 Limpando dados anteriores...")
    cursor.execute("DELETE FROM traffic_data")
    cursor.execute("DELETE FROM traffic_analysis")
    cursor.execute("DELETE FROM route")
    cursor.execute("DELETE FROM location")
    print("   ✅ Tabelas limpas")

    # Insere localizações
    print(f"\n📍 Inserindo {len(LOCATIONS)} localizações...")
    location_ids = []
    for name, lat, lng, tipo in LOCATIONS:
        cursor.execute(
            """
            INSERT INTO location (name, latitude, longitude, active)
            VALUES (%s, %s, %s, true)
            RETURNING id
            """,
            (name, lat, lng),
        )
        loc_id = cursor.fetchone()[0]
        location_ids.append(loc_id)
        print(f"   [{loc_id:02d}] {name} ({tipo})")

    # Insere rotas com distância real
    print(f"\n🛣️  Inserindo {len(ROUTES)} rotas...")
    route_ids = []
    for origin_idx, dest_idx, dist_km in ROUTES:
        origin_id   = location_ids[origin_idx]
        dest_id     = location_ids[dest_idx]
        origin_name = LOCATIONS[origin_idx][0]
        dest_name   = LOCATIONS[dest_idx][0]
        route_name  = f"{origin_name} → {dest_name}"

        cursor.execute(
            """
            INSERT INTO route (origin_id, destination_id, name, active)
            VALUES (%s, %s, %s, true)
            RETURNING id
            """,
            (origin_id, dest_id, route_name),
        )
        route_id = cursor.fetchone()[0]
        route_ids.append((route_id, dist_km))
        print(f"   [{route_id:02d}] {route_name}  ({dist_km} km)")

    conn.commit()
    cursor.close()
    conn.close()

    print("\n" + "=" * 60)
    print(f"✅ SEED CONCLUÍDO")
    print(f"   📍 {len(location_ids)} localizações criadas")
    print(f"   🛣️  {len(route_ids)} rotas criadas")
    print("=" * 60)
    print("\n▶️  Próximo passo: python data/generate_data.py")

    return route_ids


if __name__ == "__main__":
    seed()