"""
aracaju_config.py
Configurações baseadas na realidade de Aracaju/SE.
Centraliza todos os padrões usados pelo gerador e pelo modelo.
"""

# ---------------------------------------------------------------------------
# LOCALIZAÇÕES REAIS DE ARACAJU
# ---------------------------------------------------------------------------
LOCATIONS = [
    # (nome, latitude, longitude, tipo, distâncias_km_para_outras_rotas)
    ("RioMar Shopping Aracaju",                  -10.94545, -37.04805, "shopping"),
    ("Universidade Tiradentes - Farolândia",      -10.97030, -37.10370, "universidade"),
    ("Shopping Jardins",                          -10.93790, -37.05500, "shopping"),
    ("Terminal Rodoviário de Aracaju",            -10.91580, -37.05780, "terminal"),
    ("Mercado Municipal de Aracaju",              -10.91420, -37.05100, "comercio"),
    ("Praça Fausto Cardoso - Centro",             -10.91180, -37.04820, "centro"),
    ("Hospital de Urgência de Sergipe - HUSE",   -10.94380, -37.07150, "hospital"),
    ("Universidade Federal de Sergipe - UFS",     -10.92380, -37.10610, "universidade"),
    ("Aeroporto Santa Maria - Aracaju",           -10.98440, -37.07030, "aeroporto"),
    ("Orla de Atalaia",                           -11.00900, -37.04420, "lazer"),
    ("Bairro Salgado Filho",                      -10.93100, -37.07200, "residencial"),
    ("Bairro Farolândia",                         -10.96500, -37.08900, "residencial"),
    ("Bairro Jabotiana",                          -10.95800, -37.11200, "residencial"),
    ("Bairro São Conrado",                        -10.97800, -37.06100, "residencial"),
    ("Av. Tancredo Neves (trecho central)",       -10.94000, -37.06500, "via_principal"),
    ("Av. Hermes Fontes (trecho central)",        -10.92800, -37.05900, "via_principal"),
    ("Bairro Grageru",                            -10.93500, -37.06800, "residencial"),
    ("Conjunto Augusto Franco",                   -10.96200, -37.09100, "residencial"),
    ("Porto de Aracaju",                          -10.91000, -37.04200, "porto"),
    ("Parque da Sementeira",                      -10.93200, -37.05100, "lazer"),
]

# ---------------------------------------------------------------------------
# ROTAS REALISTAS ENTRE OS PONTOS
# (origin_idx, dest_idx, distancia_km_real)
# ---------------------------------------------------------------------------
ROUTES = [
    # Rotas de alto volume (centro-bairros)
    (5,  0,  8.2),   # Centro → RioMar
    (0,  5,  8.2),   # RioMar → Centro (volta)
    (5,  2,  4.1),   # Centro → Shopping Jardins
    (2,  5,  4.1),   # Shopping Jardins → Centro
    (5,  6,  5.3),   # Centro → HUSE
    (6,  5,  5.3),   # HUSE → Centro
    # Rotas universitárias (alto pico manhã/tarde)
    (5,  7,  9.7),   # Centro → UFS
    (7,  5,  9.7),   # UFS → Centro
    (1,  5,  9.1),   # Unit Farolândia → Centro
    (5,  1,  9.1),   # Centro → Unit Farolândia
    # Rotas aeroporto
    (8,  5,  9.3),   # Aeroporto → Centro
    (5,  8,  9.3),   # Centro → Aeroporto
    (8,  0,  3.8),   # Aeroporto → RioMar
    # Rotas orla/lazer
    (9,  0,  7.5),   # Atalaia → RioMar
    (0,  9,  7.5),   # RioMar → Atalaia
    (9,  5,  12.4),  # Atalaia → Centro
    # Rotas bairros residenciais
    (11, 5,  7.8),   # Farolândia → Centro
    (12, 5,  11.2),  # Jabotiana → Centro
    (13, 0,  4.9),   # São Conrado → RioMar
    (10, 5,  5.6),   # Salgado Filho → Centro
    # Rotas via principais (eixos de congestionamento)
    (14, 0,  2.1),   # Av. Tancredo → RioMar
    (15, 5,  1.8),   # Av. Hermes Fontes → Centro
    (16, 2,  2.3),   # Grageru → Shopping Jardins
    (17, 7,  3.1),   # Augusto Franco → UFS
]

# ---------------------------------------------------------------------------
# PADRÕES DE VELOCIDADE POR HORA E DIA — ARACAJU
# (fator multiplicador sobre velocidade base de 60 km/h)
# ---------------------------------------------------------------------------

# Seg-Sex (dias úteis)
WEEKDAY_SPEED_FACTORS = {
    0:  0.95,   # madrugada — quase livre
    1:  0.93,
    2:  0.90,
    3:  0.88,
    4:  0.85,
    5:  0.80,   # início do movimento
    6:  0.72,   # começa rush matinal
    7:  0.48,   # PICO MÁXIMO — entrada escolas/trabalho
    8:  0.42,   # PICO MÁXIMO
    9:  0.55,   # diminuindo
    10: 0.68,
    11: 0.70,
    12: 0.62,   # horário de almoço — movimento considerável
    13: 0.65,
    14: 0.72,
    15: 0.68,
    16: 0.55,   # começando rush noturno
    17: 0.40,   # PICO MÁXIMO — saída trabalho/escolas
    18: 0.38,   # PICO MÁXIMO
    19: 0.50,
    20: 0.65,
    21: 0.75,
    22: 0.82,
    23: 0.90,
}

# Sábado
SATURDAY_SPEED_FACTORS = {
    0:  0.96, 1:  0.95, 2:  0.94, 3:  0.93, 4:  0.92, 5:  0.88,
    6:  0.82, 7:  0.75, 8:  0.70, 9:  0.68,
    10: 0.62,  # movimento shopping começa
    11: 0.58,
    12: 0.60,
    13: 0.62,
    14: 0.65,
    15: 0.68,
    16: 0.65,
    17: 0.62,  # saída do shopping
    18: 0.60,
    19: 0.65,
    20: 0.72,
    21: 0.78,
    22: 0.82,
    23: 0.88,
}

# Domingo
SUNDAY_SPEED_FACTORS = {
    0:  0.97, 1:  0.96, 2:  0.95, 3:  0.94, 4:  0.93, 5:  0.91,
    6:  0.88, 7:  0.85, 8:  0.82, 9:  0.80, 10: 0.78, 11: 0.75,
    12: 0.78, 13: 0.80, 14: 0.82, 15: 0.80, 16: 0.78, 17: 0.75,
    18: 0.72,  # orla movimentada
    19: 0.75,
    20: 0.78, 21: 0.82, 22: 0.85, 23: 0.90,
}

# ---------------------------------------------------------------------------
# FERIADOS SERGIPANOS E NACIONAIS
# ---------------------------------------------------------------------------
NATIONAL_HOLIDAYS = [
    (1,  1),   # Ano Novo
    (4,  21),  # Tiradentes
    (5,  1),   # Dia do Trabalho
    (9,  7),   # Independência
    (10, 12),  # N. Sra. Aparecida
    (11, 2),   # Finados
    (11, 15),  # Proclamação da República
    (12, 25),  # Natal
]

SERGIPE_HOLIDAYS = [
    (3,  8),   # Aniversário de Aracaju (8 de março — ponto facultativo comercial)
    (6,  24),  # São João (feriado estadual)
    (7,  8),   # Aniversário de Sergipe
    (10, 26),  # Nossa Sra. Aparecida (padroeira de Sergipe)
]

# Carnaval — dias variáveis (calculado dinamicamente no gerador)
# Semana Santa — dias variáveis

# ---------------------------------------------------------------------------
# EVENTOS ESPECIAIS QUE IMPACTAM O TRÂNSITO
# ---------------------------------------------------------------------------
SPECIAL_EVENTS = {
    # Mês: (descrição, fator_impacto, horas_afetadas)
    # fator > 1.0 = mais trânsito, < 1.0 = menos trânsito
    6:  ("Festa Junina/São João",         1.35, list(range(18, 24))),
    12: ("Natal/Festas fim de ano",       1.25, list(range(17, 23))),
    1:  ("Férias verão/Réveillon",        0.75, list(range(8, 22))),    # menos trânsito
    7:  ("Férias escolares julho",        0.80, list(range(7, 19))),    # menos trânsito
    3:  ("Carnaval",                      0.60, list(range(10, 24))),   # muito menos trânsito
    2:  ("Pré-carnaval",                  0.85, list(range(18, 24))),
    11: ("Black Friday/fim de semestre",  1.20, list(range(10, 22))),
}

# ---------------------------------------------------------------------------
# IMPACTO DA CHUVA
# (Aracaju tem chuvas intensas, especialmente abr-ago)
# ---------------------------------------------------------------------------
RAINY_MONTHS = [4, 5, 6, 7, 8]          # maior probabilidade de chuva
DRY_MONTHS   = [10, 11, 12, 1, 2, 3]    # menor probabilidade de chuva

RAIN_PROBABILITY = {
    month: 0.45 if month in RAINY_MONTHS else 0.12
    for month in range(1, 13)
}

RAIN_SPEED_PENALTY = {
    "light": 0.88,    # chuva leve — reduz 12% da velocidade
    "moderate": 0.72, # chuva moderada — reduz 28%
    "heavy": 0.52,    # chuva forte — reduz 48% (comum em Aracaju)
}

# Chuvas são mais frequentes à tarde em Aracaju (clima tropical)
RAIN_HOUR_PROBABILITY_BOOST = {
    h: 1.8 if 14 <= h <= 17 else 1.0
    for h in range(24)
}

# ---------------------------------------------------------------------------
# IMPACTO POR TIPO DE ROTA
# (algumas vias congestionam mais que outras)
# ---------------------------------------------------------------------------
ROUTE_CONGESTION_PROFILE = {
    # route_name_keyword: fator de congestionamento adicional
    "Tancredo":   1.25,   # Av. Tancredo Neves — uma das mais congestionadas
    "Hermes":     1.20,   # Av. Hermes Fontes — muito movimentada
    "Centro":     1.15,   # qualquer rota passando pelo centro
    "HUSE":       1.10,   # hospital — movimento constante
    "Aeroporto":  1.05,   # aeroporto — fluxo elevado em horários específicos
    "UFS":        1.12,   # UFS — pico na entrada/saída de aulas
    "Unit":       1.10,   # Universidade Tiradentes
    "RioMar":     1.08,   # shopping — fim de semana mais intenso
    "Atalaia":    1.15,   # orla — fim de semana/feriado muito movimentado
}

# ---------------------------------------------------------------------------
# CONFIGURAÇÕES DE GERAÇÃO
# ---------------------------------------------------------------------------
GENERATION_CONFIG = {
    "days":            365,    # 1 ano de dados
    "base_speed_kmh":  60.0,   # velocidade máxima em via urbana (Aracaju ~60km/h)
    "speed_noise":     0.06,   # variação aleatória de ±6%
    "skip_hour_prob":  0.08,   # 8% de chance de não ter coleta naquela hora
}