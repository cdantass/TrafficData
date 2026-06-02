# 🚦 SmartTraffic Aracaju

Sistema backend para coleta, análise e previsão de dados de trânsito em Aracaju, utilizando **Java + Spring Boot + PostgreSQL**, com integração futura com **IA em Python**.

---

## 📌 Objetivo

O objetivo do projeto é analisar o comportamento do trânsito ao longo do tempo, permitindo:

* Consultar histórico de tráfego por rota
* Identificar horários de pico
* Comparar dias da semana
* Prever condições futuras de trânsito (com IA)

---

## 🧠 Arquitetura

O sistema segue uma arquitetura baseada em microserviços:

```
[ Spring Boot API ] → [ PostgreSQL ]
         ↓
[ Python IA Service ]
```

---

## ⚙️ Tecnologias utilizadas

### Backend

* Java 21
* Spring Boot
* Spring Data JPA
* Spring Web
* Jakarta Validation
* Lombok

### Banco de dados

* PostgreSQL

### IA (em desenvolvimento)

* Python
* FastAPI
* Pandas
* Scikit-learn

---

## 🧱 Estrutura do projeto

```
com.traffic.aracaju
 ├── controller
 ├── service
 ├── repository
 ├── entity
 ├── dto
 ├── exception
```

---

## 📊 Modelagem de dados

### 📍 Location

Representa um ponto geográfico.

* id
* name
* latitude
* longitude

---

### 🛣️ Route

Define uma rota entre dois pontos.

* id
* origin (Location)
* destination (Location)
* name

---

### 🚦 TrafficData

Armazena dados históricos de trânsito.

* id
* route
* timestamp
* duration
* durationInTraffic
* averageSpeed
* trafficLevel (LOW, MEDIUM, HIGH)

---

## 🔌 Endpoints principais

### 📍 Locations

```
POST   /locations
GET    /locations
GET    /locations/{id}
```

---

### 🛣️ Routes

```
POST   /routes
GET    /routes
GET    /routes/{id}
DELETE /routes/{id}
```

Exemplo de criação:

```json
{
  "originId": 1,
  "destinationId": 2
}
```

---

### 🚦 Traffic Data (em desenvolvimento)

```
POST   /traffic-data
GET    /traffic-data
GET    /traffic-data/route/{id}
```

---

## 🧠 Lógica de análise de trânsito

O nível de trânsito é calculado com base na relação entre tempo normal e tempo com trânsito:

```
ratio = durationInTraffic / duration
```

Classificação:

* LOW → ratio < 1.2
* MEDIUM → ratio < 1.5
* HIGH → ratio ≥ 1.5

---

## 🔄 Coleta de dados (planejado)

Os dados serão coletados automaticamente via:

* Google Distance Matrix API

Com execução periódica (scheduler):

* a cada 10–15 minutos
* armazenando histórico para análise futura

---

## 🚀 Roadmap

### ✅ Fase 1

* CRUD completo (Location, Route, TrafficData)

### 🔄 Fase 2

* Cálculo de métricas de trânsito
* Filtros por horário e dia

### 🔜 Fase 3

* Integração com serviço de IA (Python)
* Previsão de trânsito

### 🔮 Fase 4

* Dashboard / visualização
* Alertas inteligentes

---

## ⚠️ Boas práticas adotadas

* Separação de camadas (Controller, Service, Repository)
* Uso de DTOs (evita exposição de entidades)
* Tratamento de exceções customizado
* Uso de paginação (Pageable)
* Enum para controle de estado (`TrafficLevel`)

---

## 📌 Melhorias futuras

* Autenticação com Spring Security
* Cache de consultas
* Integração com APIs externas (Waze, Google)
* Machine Learning para previsão de tráfego

---
