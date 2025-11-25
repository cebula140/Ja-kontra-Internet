Jaś kontra Internet - Podróż w głąb sieci
Opis projektu

"Jaś kontra Internet" to edukacyjna gra zręcznościowa stworzona w języku Python z wykorzystaniem biblioteki Pygame. Projekt łączy elementy rozgrywki typu "bullet hell" z edukacją na temat cyberbezpieczeństwa, tworząc unikalne doświadczenie gamifikacji nauki.

Gra została opracowana jako zgłoszenie konkursowe w ramach Hack Heroes 2025, odpowiadając na potrzebę edukacji młodych użytkowników internetu w zakresie bezpieczeństwa cyfrowego.
Cel i przydatność społeczna

Głównym celem projektu jest edukacja młodzieży w zakresie:

    Podstawowych zasad bezpieczeństwa w internecie

    Rozpoznawania zagrożeń takich jak phishing

    Znaczenia szyfrowania danych (HTTPS)

    Korzystania z VPN i zapór sieciowych

    Tworzenia silnych haseł

Projekt odpowiada na realną potrzebę społeczną - wzrost świadomości cyberbezpieczeństwa wśród młodych użytkowników internetu, którzy są szczególnie narażeni na cyberzagrożenia.
Wymagania systemowe
Minimalne wymagania:

    System operacyjny: Windows 7/8/10/11, macOS 10.14+, Linux z Python 3.6+

    Python 3.6 lub nowszy

    Biblioteka Pygame

Instalacja i uruchomienie
Krok 1: Instalacja Pythona

Pobierz i zainstaluj Python z oficjalnej strony: https://www.python.org/downloads/
Krok 2: Instalacja Pygame

Otwórz wiersz poleceń (cmd) lub terminal i wykonaj:
bash

pip install pygame

Krok 3: Uruchomienie gry

Pobierz pliki projektu i uruchom:
bash

python main.py

Kontrole w grze
Podstawowe sterowanie:

    W, A, S, D - poruszanie się postacią

    Spacja - użycie bomby (jeśli dostępna)

    Shift - zwolnienie tempa poruszania (chodzenie)

    Escape - pauza/menu

Tryb edukacyjny:

    Spacja - przejście z tekstu edukacyjnego do quizu

    1, 2, 3 - wybór odpowiedzi w quizie

    Escape - powrót do menu głównego

Menu:

    Kliknięcie myszą - interakcja z przyciskami

Dodatkowo, w ustawieniach można zmienić rozdzielczość, włączyć/wyłączyć efekt CRT, pokazywanie FPS oraz dostosować głośność.
Struktura projektu
text

jas-kontra-internet/
├── main.py              # Główny plik gry
├── library.py           # Moduł pomocniczy do zarządzania danymi
├── assets/              # Katalog z zasobami
│   ├── music.mp3        # Muzyka tła (opcjonalnie)
│   ├── jas.png          # Sprite głównego bohatera (opcjonalnie)
│   ├── bomb.wav         # Dźwięk bomby (opcjonalnie)
│   ├── sfx_hit.wav      # Dźwięk trafienia (opcjonalnie)
│   └── pixel_font.ttf   # Czcionka pixelowa (opcjonalnie)
├── settings.json        # Plik konfiguracyjny ustawień
├── scores.json         # Plik z wynikami graczy
├── progress.json       # Plik z postępem edukacyjnym
└── README.md           # Ten plik

Opis mechaniki gry
Tryb główny (Game)

Gracz steruje postacią Jasia, który musi unikać różnych typów pocisków reprezentujących zagrożenia internetowe. Każdy typ pocisku symbolizuje inne niebezpieczeństwo występujące w sieci.
System edukacyjny (Edu)

Tryb nauki składa się z dwóch części:

    Lekcja - prezentacja wiedzy o cyberbezpieczeństwie

    Quiz - sprawdzenie zrozumienia materiału

Nagrody i postęp

Za poprawne odpowiedzi w quizach gracz otrzymuje:

    Dodatkowe bomby (maksymalnie 3)

    Dodatkowe życia (maksymalnie 5)

    Punkty wiedzy - wpływają na poziom trudności

Jak dodać nowe pytania i teksty edukacyjne
Dodawanie nowych tekstów edukacyjnych

Aby dodać nowy tekst edukacyjny, należy go dopisać do listy edu_readings w pliku main.py:
python

edu_readings = [
    "Twój nowy tekst edukacyjny tutaj.",
    ...
]

Dodawanie nowych pytań quizowych

Aby dodać nowe pytanie, należy rozszerzyć listę edu_quiz w pliku main.py:
python

edu_quiz = [
    {
        "q": "Twoje pytanie?",
        "a": ["Odpowiedź A", "Odpowiedź B", "Odpowiedź C"],
        "correct": 0  # Indeks poprawnej odpowiedzi (0, 1 lub 2)
    },
    ...
]

Ważne uwagi:

    Zachowaj formatowanie i strukturę list

    Upewnij się, że liczba tekstów edukacyjnych i pytań jest taka sama

    Używaj tylko znaków ASCII i polskich znaków (ą, ć, ę, ł, ń, ó, ś, ź, ż)

    Pytania powinny dotyczyć cyberbezpieczeństwa i być zgodne z celami edukacyjnymi projektu

Technologie wykorzystane
Główne technologie:

    Python 3.8+ - język programowania

    Pygame - biblioteka do tworzenia gier

    JSON - format przechowywania danych

Zaawansowane funkcjonalności:

    System zarządzania assetami

    Dynamiczna generacja poziomu trudności

    System zapisu i wczytywania postępu

    Interfejs użytkownika z przyciskami

    Efekty wizualne (CRT shader)

    Sterowanie dźwiękiem i muzyką

Funkcjonalności
Podstawowe:

    Sterowanie postacią za pomocą klawiszy WASD

    Używanie bomb do oczyszczenia obszaru (Spacja)

    System żyć i punktów

    Różne typy wrogich pocisków

Zaawansowane:

    Tryb edukacyjny z quizami

    System nagród za postępy w nauce

    Dostosowywanie trudności do umiejętności gracza

    Zapisywanie wyników i postępu

    Konfigurowalne ustawienia graficzne i dźwiękowe

Wyzwania i rozwiązania
Wyzwania techniczne:

    Optymalizacja wydajności - implementacja systemu czyszczenia nieużywanych obiektów

    Zarządzanie stanem gry - system trybów (title, game, pause, edu)

    Przechowywanie danych - wykorzystanie JSON do zapisu ustawień i postępu

Rozwiązania edukacyjne:

    Gamifikacja nauki - połączenie rozgrywki z quizami

    Progresywna trudność - dostosowanie do poziomu wiedzy gracza

    Natychmiastowa informacja zwrotna - system nagród za poprawne odpowiedzi

Projekt "Jaś kontra Internet" został stworzony z myślą o edukacji młodego pokolenia w erze cyfrowej. Łącząc rozrywkę z nauką, dążymy do budowania świadomego i bezpiecznego społeczeństwa informacyjnego.