# System-akwizycji-danych-V2
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org/)

Druga wersja systemu akwizycji danych, oparta na REST API, służąca do rejestrowania węzłów pomiarowych, z których dane są na bieżąco odczytywane i analizowane w celu utrzymania optymalnych warunków środowiskowych (np. dla upraw szklarniowych). System działa w pełni asynchronicznie i posiada kompletną architekturę: dedykowany panel administratora, panel użytkownika, oddzielny moduł do obsługi komunikacji MQTT oraz zintegrowany system logów (serwerowych i audytowych). Projekt został zbudowany z naciskiem na najlepsze praktyki backendowe: bezpieczeństwo (JWT, Rate Limiting), separację warstw dostępu (UUID dla klientów publicznych, Integer dla relacji wewnętrznych) oraz wysoką wydajność.

## Główne funkcjonalność 
* **Autoryzacja i Bezpieczeństwo:** Rejestracja, logowanie oraz ochrona endpointów przy użyciu tokenów JWT.
* **Zarządzanie z Poziomu Administratora:** Panel administratora do zarządzania: kontem użytkownika, zarejestrowanymi urządzeniami, przepływem informacji i analizą dostarczonych danych.
* **Zarządzanie przepływem danych:** Z panelu admina można w całość zobaczyć jakie akcje zostały podjęte na koncie użytkownika.
* **Dodawanie Urządzeni i Analiza Danych:** Użytkownik może w każdej chwili dodać nowe urządzenie i rozpocząć analizę konkretnej uprawy, którą w każdym momencie może zatrzymać i zmienić.
* **Kontrola Konta Przez Użytkownika** Użytkownik może zmienić swoje dane w tym hasło a w przypadku zapomnienia hasła może je zresetować podczas logowania (admin również może zresetować hasło użytkownika).
* **Analizy:** Przeglądanie analizy w danym urządzeniu z procentową wartością jaki czas były poprawne warunki dla rozwoju uprawy
* ""Odczyt Danych** Można zobaczyć dane z całego okresu działania urządzenia 
* **Ochrona przed nadużyciami:** Wdrożony `SlowAPI` chroniący krytyczne endpointy przed atakami Brute Force i DDoS.
* **Harmonogram:** Funkcje wywoływane automatycznie co 10 min w celu sprawdzenia czy urządzenia poprawnie wysyłają informacje (jeżeli nie urządzeni ustawiane jest na offline)

## Użyte Technologie 
* **Backend Framework: ** FastAPI, SQLAlchemy 2.0, Alembic
* **Baza Danych: ** PostgreSQL
* **Zarządzanie Środowiskiem: ** Pydantic Settings
* **Bezpieczeństwo: ** Passlib(argon2), PyJWT, SlowAPI
* **Testowanie:** Pytest, Pytest-Asyncio, HTTPX

## Instalacja i Uruchomienie Backendu
### 1. Pobierz biblioteki i skonfiguruj zmienne środowiskowe
Zainstaluj wymagane pakiety: `pip install -r requirements.txt` Utwórz plik `.env` w głównym katalogu projektu, bazując na pliku przykładowym: `.env.example .env`

### 2. Utwórz bazę danych
Wykonaj migrację Alembic, aby zbudować strukturę bazy danych w wierszu poleceni: `alembic revision --autogenerate -m "database"` następnie `alembic upgrade head`

### 3. Wgranie przykładowych danych dla upraw
W wierszu poleceni uruchom `python -m tools.loadcultivationstats` 

### 4. Utwórz konto admina 
W wierszu poleceni uruchom `python -m tools.createsuperuser` i podaj wymagane wartość

### 5. Uruchom serwer FastAPI
W wierszu poleceni `fastapi run src/main.py`

## Instalacja i Uruchomienie Frontendu
### 1. Zainstaluj Środowisko
W wierszu poleceni wejdź do pliku z frontendem `cd frontend`, następnie zainstaluj pakiet `npm install`

### 2. Wystartowanie frontendu
W wierszu poleceni `npm run dev`

## Zmiana w Backendzie ESP 32
### 1. Zmieni część kodu
Wyszukaj w `firmware_esp32/main.py` takiego fragmentu `client = MQTTClient("client", "IP URZĄDZENIA")` i zmieni IP URZĄDZENIA na takie jakie jest na twoim urządzeniu

## Uruchomienie testów
Projekt posiada pełne pokrycie testami dla głównych ścieżek autoryzacji, operacji CRUD i mechanizmów chroniących aplikację. Aby uruchomić testy integracyjne w wyizolowanym środowisku pamięci, wpisz w konsoli: `pytest test`

## Struktura projektu
```text
System-akwizycji-danych-v2/
├── alembic/                    # Skrypty migracji bazy danych (Alembic)
├── firmware_esp32/             # Oprogramowanie dla mikrokontrolerów ESP32
├── frontend/                   # Aplikacja webowa (Vue 3 + Vite + Tailwind CSS)
│   ├── node_modules/           # Zainstalowane zależności npm (ignorowane w Git)
│   ├── public/                 # Statyczne zasoby publiczne
│   ├── src/                    # Kod źródłowy interfejsu użytkownika
│   ├── .env / .env.example     # Zmienne środowiskowe dla frontendu
│   ├── package.json            # Konfiguracja projektu frontendowego i zależności
│   ├── tailwind.config.js      # Konfiguracja stylów Tailwind CSS
│   └── vite.config.js          # Konfiguracja bundlera Vite
├── src/                        # Główny kod źródłowy backendu (FastAPI)
│   ├── admin/                  # Logika panelu administratora
│   ├── auth/                   # Autoryzacja, uwierzytelnianie (JWT) i hashowanie
│   ├── core/                   # Konfiguracja główna (Settings, Logger)
│   ├── cultivation/            # Logika biznesowa zarządzania profilami upraw
│   ├── database/               # Sesja bazy danych i modele SQLAlchemy
│   ├── device/                 # Obsługa urządzeń pomiarowych (ESP32)
│   ├── telemetry/              # Odbiór i przetwarzanie pomiarów z sensorów
│   ├── users/                  # Endpointy do zarządzania kontami użytkowników
│   ├── worker/                 # Skrypty i zadania działające w tle
│   └── main.py                 # Punkt wejścia i inicjalizacja aplikacji FastAPI
├── test/                       # Testy jednostkowe i integracyjne (Pytest)
├── tools/                      # Pomocnicze skrypty narzędziowe i administracyjne
│   ├── createsuperuser.py      # Kreator konta administratora z poziomu CLI
│   └── loadcultivationstats.py # Narzędzie do ładowania/eksportu danych upraw
├── venv/                       # Wirtualne środowisko Pythona (ignorowane w Git)
├── .env / .env.example         # Zmienne środowiskowe backendu (hasła, klucze)
├── alembic.ini                 # Konfiguracja narzędzia do migracji bazy danych
├── pytest.ini                  # Konfiguracja frameworka testowego
└── requirements.txt            # Lista zależności systemowych backendu (pip)

```


