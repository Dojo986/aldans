# Tea’s konfirmation – 16. maj 2026

En lille, moderne desktop-GUI app til at holde styr på planlægningen af Tea’s konfirmation. Appen bruger Python + Tkinter og gemmer data lokalt i en SQLite-database.

## Teknisk valg
**B) Python desktop (Tkinter + SQLite)** – hurtig at levere, kræver ingen ekstra frontend-frameworks og gemmer data lokalt i en fil.

## Funktioner
- **3 faner**: Overblik, Emner/To-do, Budget
- **Fast kategoriliste** (dropdowns) i både Emner/To-do og Budget
- **Emner/To-do**: tilføj, redigér, slet, markér som færdig, søg/filtrér og sortér
- **Overblik**: nedtælling, mini-dashboard for status og næste 5 deadlines
- **Budget**: budgetposter, betalt ja/nej og totalsummer
- **Seed-data** ved første opstart

## Sådan kører du projektet

### Krav
- Python 3.10+ (Tkinter følger typisk med i standardinstallationen)

### Start appen
```bash
python3 app.py
```

## Data og persistens
- Data gemmes lokalt i en SQLite-fil: `data/teas_konfirmation.db`.
- Databasen oprettes automatisk ved første kørsel sammen med seed-data.

## Projektstruktur
```
.
├── app.py
├── data/
│   └── teas_konfirmation.db
└── README.md
```
