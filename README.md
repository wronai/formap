# 🧠 FORMAP - Form Mapper & Auto-Filler

[English below] Automatyczne mapowanie i wypełnianie formularzy internetowych przy użyciu Playwright.

## ✨ Funkcje

- 🔍 Mapowanie pól formularza poprzez przechodzenie między nimi klawiszem Tab
- 💾 Zapis mapowania pól do pliku JSON
- 🚀 Automatyczne wypełnianie formularzy na podstawie zapisanego mapowania
- 🔒 Obsługa wszystkich standardowych pól formularza (tekst, wybór, radio, checkbox, itp.)
- 🐍 Prosty interfejs w języku Python

---

# 🧠 FORMAP - Form Mapper & Auto-Filler

Automatically map and fill web forms with ease using Playwright.

## ✨ Features

- 🔍 Map HTML form fields by tabbing through them
- 💾 Save field mappings to a JSON file
- 🚀 Automatically fill forms using saved mappings
- 🔒 Supports all standard form fields (text, select, radio, checkbox, etc.)
- 🐍 Simple Python API

## 🚀 Szybki start / Quick Start

### Wymagania / Prerequisites

- Python 3.8+
- Git (do sklonowania repozytorium / for cloning the repository)

### Instalacja / Installation

1. **Sklonuj repozytorium / Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/formap.git
   cd formap
   ```

2. **Skonfiguruj środowisko / Set up the environment**:
   ```bash
   # Utwórz i aktywuj środowisko wirtualne
   # Create and activate virtual environment
   python -m venv venv
   source venv/bin/activate  # Na Windows: venv\Scripts\activate
   
   # Zainstaluj zależności
   # Install dependencies
   pip install -r form-mapper/requirements.txt
   
   # Zainstaluj przeglądarki Playwright
   # Install Playwright browsers
   python -m playwright install
   ```

## 🛠️ Użycie / Usage

### 1. Mapowanie pól formularza / Map Form Fields

Aby zmapować pola formularza / To map the fields of a form:

```bash
# Aktywuj środowisko wirtualne jeśli nieaktywne
# Activate virtual environment if not already activated
source venv/bin/activate

# Uruchom mapowanie
# Run the mapper
python form-mapper/map_fields.py https://przykladowa-strona.pl/logowanie
```

```
python form-mapper/auto_map_form.py https://bewerbung.jobs/325696/buchhalter-m-w-d
python form-mapper/auto_fill_form.py https://bewerbung.jobs/325696/buchhalter-m-w-d
```


Postępuj zgodnie z instrukcjami na ekranie, przechodząc przez pola formularza klawiszem Tab. Naciśnij 's' aby zapisać lub 'q' aby wyjść bez zapisywania.

### 2. Wypełnianie formularza / Fill a Form

Aby wypełnić formularz używając zapisanego mapowania / To fill a form using a saved mapping:

```bash
# Aktywuj środowisko wirtualne jeśli nieaktywne
# Activate virtual environment if not already activated
source venv/bin/activate

# Uruchom wypełnianie
# Run the filler
python form-mapper/fill_form.py form_map.json
```

## 📋 Przykłady użycia / Usage Examples

### Przykład 1: Logowanie / Example 1: Login Form

```bash
# Mapowanie formularza logowania
# Mapping a login form
python form-mapper/map_fields.py https://przykladowa-strona.pl/logowanie
# Po zapisaniu mapowania, wypełnij formularz
# After saving the mapping, fill the form
python form-mapper/fill_form.py form_map.json
```

### Przykład 2: Rejestracja / Example 2: Registration Form

```bash
# Mapowanie formularza rejestracji
# Mapping a registration form
python form-mapper/map_fields.py https://przykladowa-strona.pl/rejestracja
# Wypełnij formularz danymi
# Fill the form with data
python form-mapper/fill_form.py form_map.json
```

### Przykład 3: Formularz kontaktowy / Example 3: Contact Form

```bash
# Mapowanie formularza kontaktowego
# Mapping a contact form
python form-mapper/map_fields.py https://przykladowa-strona.pl/kontakt
# Wypełnij i wyślij formularz
# Fill and submit the form
python form-mapper/fill_form.py form_map.json
```

## 🐳 Uruchamianie w Dockerze / Docker Support

Możesz również uruchomić FORMAP używając Dockera / You can also run FORMAP using Docker:

```bash
# Zbuduj obraz Dockera / Build the Docker image
docker build -t formap .

# Uruchom mapowanie / Run the mapper
docker run -it --rm -v $(pwd):/app formap python map_fields.py https://przykladowa-strona.pl/formularz

# Uruchom wypełnianie / Run the filler
docker run -it --rm -v $(pwd):/app formap python fill_form.py form_map.json
```

## 📁 Project Structure

```
form-mapper/
├── Dockerfile           # Docker configuration
├── Makefile            # Common commands
├── README.md           # This file
├── requirements.txt     # Python dependencies
├── map_fields.py       # Form field mapping script
└── fill_form.py        # Form filling script
```

## 💡 Wskazówki / Tips

- Upewnij się, że wszystkie wymagane pola są wypełnione przed zapisaniem mapowania.
- Możesz edytować plik `form_map.json` ręcznie, aby dostosować mapowanie.
- Użyj opcji `--headless` aby uruchomić przeglądarkę w trybie bezokienkowym.

## 🤝 Współtworzenie / Contributing

Wkład jest mile widziany! Zapraszamy do przesyłania Pull Requestów. / Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 Licencja / License

Ten projekt jest dostępny na licencji MIT - zobacz plik [LICENSE](LICENSE) aby uzyskać więcej informacji. / This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.





Oto pełna struktura projektu do **mapowania i wypełniania formularzy za pomocą Playwright**, w stylu **MVP z Mistral 7B**, z kompletem:

* `Makefile` do uruchamiania zadań
* `Dockerfile` do konteneryzacji
* `docker-compose.yml` do lokalnego uruchamiania
* `README.md` z instrukcją

---

## 📁 Struktura projektu:

```
form-mapper/
├── Dockerfile
├── Makefile
├── README.md
├── docker-compose.yml
├── map_fields.py
├── fill_form.py
├── requirements.txt
└── example.env
```

---

## 📄 `map_fields.py` i `fill_form.py`

*(Już masz je wcześniej — kopiujesz z poprzedniej wiadomości.)*

---

## 📄 `requirements.txt`

```txt
playwright==1.44.0
```

---

## 📄 `Dockerfile`

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    playwright install --with-deps

COPY . .

CMD ["bash"]
```

---

## 📄 `docker-compose.yml`

```yaml
version: '3.8'

services:
  formmapper:
    build: .
    container_name: formmapper
    environment:
      - PYTHONUNBUFFERED=1
    volumes:
      - .:/app
    entrypoint: ["tail", "-f", "/dev/null"]  # Do debugowania interaktywnego
```

*(możesz zmienić `entrypoint`, by odpalało konkretne polecenie, np. `python map_fields.py`)*

---

## 📄 `Makefile`

```makefile
.PHONY: map fill up build shell

map:
	python map_fields.py

fill:
	python fill_form.py

build:
	docker-compose build

up:
	docker-compose up -d

shell:
	docker-compose exec formmapper bash
```

---

## 📄 `example.env`

```env
URL=https://example.com
EMAIL=test@example.com
USERNAME=jan.kowalski
PASSWORD=tajne123
```

(Można potem podciągać zmienne do `fill_form.py` z `os.getenv`.)

---

## 📄 `README.md`

````markdown
# 🧠 Form Mapper & Auto-Filler (Playwright + Mistral 7B-style)

Ten projekt automatycznie:
1. Mapuje formularze HTML przez klawisz `Tab`
2. Tworzy plik JSON z XPath i typami pól
3. Na podstawie mapy automatycznie wypełnia formularze

## 🔧 Wymagania

- Python 3.11+
- Docker (opcjonalnie)

## 🐍 Lokalne uruchomienie

### Instalacja
```bash
pip install -r requirements.txt
playwright install
````

### Mapowanie pól

```bash
make map
```

### Wypełnianie formularza

```bash
make fill
```

## 🐳 Uruchomienie w Dockerze

### Budowanie kontenera

```bash
make build
```

### Włączenie środowiska

```bash
make up
make shell  # potem np. python map_fields.py
```

## 📂 Pliki

* `map_fields.py` – mapa formularzy przez `Tab`
* `fill_form.py` – wypełnianie pól wg JSON
* `form_map.json` – wynik mapowania
* `example.env` – przykładowe dane

## 📌 Autor

Projekt edukacyjny inspirowany użyciem LLM (np. Mistral 7B) do automatyzacji formularzy.

```

---

Chcesz, bym dodał możliwość odczytu danych z `.env`, automatyczne rozpoznawanie checkboxów, czy też interaktywny CLI do wprowadzania danych?
```


Oto prosty, **dwuczęściowy** skrypt w **Pythonie** używający **Playwright**, który:

1. **Symuluje przechodzenie przez pola formularza przy pomocy klawisza `Tab`**, zapisując kolejne **XPathy i typy pól** (np. input, button, select).
2. **Zapisuje mapę pól do pliku JSON**, która potem może być użyta do **automatycznego wypełniania formularza**.

⚠️ **Dostosowany do ograniczeń Mistral 7B**: nie robi analizy semantycznej strony, tylko czysto techniczne mapowanie po `Tab`.

---

## 📦 Wymagania:

Zainstaluj Playwright:

```bash
pip install playwright
playwright install
```

---

## 🧠 Część 1: Mapowanie pól przez `Tab` i zapis do JSON

```python
# map_fields.py
import json
import asyncio
from playwright.async_api import async_playwright

async def map_form_fields(url: str, output_json: str = "form_map.json"):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto(url)

        print(f"[INFO] Odwiedzono stronę: {url}")

        mapped_fields = []
        visited_elements = set()

        for i in range(50):  # maksymalnie 50 tabów
            await page.keyboard.press("Tab")
            await page.wait_for_timeout(200)

            active = await page.evaluate_handle("document.activeElement")
            tag = await active.evaluate("el => el.tagName.toLowerCase()")
            typ = await active.evaluate("el => el.type || ''")
            name = await active.evaluate("el => el.name || ''")
            id_attr = await active.evaluate("el => el.id || ''")

            xpath = await page.evaluate('''
                el => {
                    function getXPath(el) {
                        if (el.tagName === 'HTML')
                            return '/html';
                        if (el === document.body)
                            return '/html/body';
                        var ix = 0;
                        var siblings = el.parentNode.childNodes;
                        for (var i = 0; i < siblings.length; i++) {
                            var sibling = siblings[i];
                            if (sibling === el)
                                return getXPath(el.parentNode) + '/' + el.tagName.toLowerCase() + '[' + (ix+1) + ']';
                            if (sibling.nodeType === 1 && sibling.tagName === el.tagName)
                                ix++;
                        }
                    }
                    return getXPath(el);
                }
            ''', active)

            if xpath not in visited_elements:
                visited_elements.add(xpath)
                mapped_fields.append({
                    "tag": tag,
                    "type": typ,
                    "name": name,
                    "id": id_attr,
                    "xpath": xpath,
                })

        with open(output_json, "w") as f:
            json.dump(mapped_fields, f, indent=2)
            print(f"[INFO] Zapisano mapę formularza do: {output_json}")

        await browser.close()

if __name__ == "__main__":
    url = "https://przyklad.pl"  # <- PODAJ PRAWIDŁOWY ADRES STRONY
    asyncio.run(map_form_fields(url))
```

---

## 📝 Część 2: Wypełnianie formularza według mapy

```python
# fill_form.py
import json
import asyncio
from playwright.async_api import async_playwright

async def fill_form(url: str, json_map: str, values: dict):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto(url)

        with open(json_map, "r") as f:
            fields = json.load(f)

        for field in fields:
            xpath = field["xpath"]
            typ = field["type"]
            tag = field["tag"]

            if typ in ["text", "email", "password", "search", "tel", "url"] or tag == "textarea":
                value = values.get(field["name"] or field["id"] or xpath, "test")
                try:
                    el = await page.wait_for_selector(f"xpath={xpath}", timeout=1000)
                    await el.fill(value)
                except Exception as e:
                    print(f"[WARN] Nie udało się wypełnić pola {xpath}: {e}")

        await page.wait_for_timeout(3000)
        await browser.close()

if __name__ == "__main__":
    values = {
        "email": "test@example.com",
        "username": "jan.kowalski",
        "password": "tajne123"
        # dodaj klucze na podstawie mapy
    }
    url = "https://przyklad.pl"  # <- PODAJ TĘ SAMĄ STRONĘ
    asyncio.run(fill_form(url, "form_map.json", values))
```

---

## ✅ Jak tego używać?

1. **Krok 1**: Uruchom `map_fields.py`, by stworzyć mapę formularza.
2. **Krok 2**: Przejrzyj `form_map.json` i podaj odpowiednie wartości w `fill_form.py`.
3. **Krok 3**: Uruchom `fill_form.py`, by automatycznie wypełnić pola.




