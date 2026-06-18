import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        database=os.getenv("DB_NAME", "traffic"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "123")
    )

# Localizações reais de Aracaju
LOCATIONS = [
    ("RioMar Aracaju",                          -10.94545, -37.04805),
    ("Universidade Tiradentes - Farolândia",    -10.97030, -37.10370),
    ("Shopping Jardins",                         -10.93790, -37.05500),
    ("Terminal Rodoviário de Aracaju",           -10.91580, -37.05780),
    ("Mercado Municipal de Aracaju",             -10.91420, -37.05100),
    ("Praça Fausto Cardoso - Centro",            -10.91180, -37.04820),
    ("Hospital de Urgência de Sergipe - HUSE",  -10.94380, -37.07150),
    ("Universidade Federal de Sergipe - UFS",   -10.92380, -37.10610),
    ("Aeroporto de Aracaju",                    -10.98440, -37.07030),
    ("Farol de Aracaju - Atalaia",              -11.00900, -37.04420),
]

# Rotas entre os pontos (origin_index, destination_index)
# Índices baseados na lista acima (começa em 0)
ROUTES = [
    (0, 1),   # RioMar → Unit Farolândia
    (0, 2),   # RioMar → Shopping Jardins
    (0, 7),   # RioMar → UFS
    (2, 3),   # Shopping Jardins → Rodoviária
    (3, 4),   # Rodoviária → Mercado Municipal
    (4, 5),   # Mercado → Praça Fausto Cardoso
    (5, 6),   # Centro → HUSE
    (6, 7),   # HUSE → UFS
    (7, 8),   # UFS → Aeroporto
    (8, 9),   # Aeroporto → Atalaia
    (1, 0),   # Unit Farolândia → RioMar (volta)
    (7, 0),   # UFS → RioMar (volta)
]

def seed():
    conn = get_connection()
    cursor = conn.cursor()

    # Limpa dados existentes na ordem correta (respeita FK)
    print("🧹 Limpando dados anteriores...")
    cursor.execute("DELETE FROM traffic_data")
    cursor.execute("DELETE FROM route")
    cursor.execute("DELETE FROM location")

    # Insere locations
    print("📍 Inserindo locations...")
    location_ids = []
    for name, lat, lng in LOCATIONS:
        cursor.execute("""
            INSERT INTO location (name, latitude, longitude, active)
            VALUES (%s, %s, %s, true)
            RETURNING id
        """, (name, lat, lng))
        loc_id = cursor.fetchone()[0]
        location_ids.append(loc_id)
        print(f"   ✅ [{loc_id}] {name}")

    # Insere routes
    print("\n🛣️  Inserindo rotas...")
    route_ids = []
    for origin_idx, dest_idx in ROUTES:
        origin_id   = location_ids[origin_idx]
        dest_id     = location_ids[dest_idx]
        origin_name = LOCATIONS[origin_idx][0]
        dest_name   = LOCATIONS[dest_idx][0]
        route_name  = f"{origin_name} → {dest_name}"

        cursor.execute("""
            INSERT INTO route (origin_id, destination_id, name, active)
            VALUES (%s, %s, %s, true)
            RETURNING id
        """, (origin_id, dest_id, route_name))
        route_id = cursor.fetchone()[0]
        route_ids.append(route_id)
        print(f"   ✅ [{route_id}] {route_name}")

    conn.commit()
    cursor.close()
    conn.close()

    print(f"\n✅ Seed concluído!")
    print(f"   📍 {len(location_ids)} locations criadas")
    print(f"   🛣️  {len(route_ids)} rotas criadas")
    print(f"\n   IDs das rotas para o generate_data.py:")
    print(f"   ROUTE_IDS = {route_ids}")
    return route_ids

if __name__ == "__main__":
    route_ids = seed()