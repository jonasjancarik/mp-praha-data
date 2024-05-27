# mp-praha-data

Skript pro konverzi otevřených dat "Měsíční zprávy o činnosti Městské policie hl. m. Prahy za rok 2024 podle útvarů" z JSON do CSV. Data z https://opendata.praha.eu/datasets/https%3A%2F%2Fapi.opendata.praha.eu%2Flod%2Fcatalog%2F2da23f23-c8fc-4edb-ad78-530f4b0228c4.

V současnosti bohužel data obsahují chyby - například nesmyslné částky, které možná vznikly sloučením různých čísel (celková částka a průměrná). Proto je nutné data pročistit a odstranit extrémní hodnoty.

## Instalace

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Použití

`python json_to_csv.py`

## Aktualizace
V adresáři data/output je CSV soubor s daty, ale pokud ho chcete aktualizovat, je potřeba spustit skript, který si stáhne nový zdrojový JSON soubor a převede ho na CSV.

Poslední aktualizace: 2024-05-27
