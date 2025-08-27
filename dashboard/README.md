# 📊 Fantacalcio Dashboard

Dashboard interattiva per l'analisi dei dati di fantacalcio generati dal progetto fantacalcio-py.

## 🚀 Avvio

Per avviare la dashboard:

```bash
# Dalla root del progetto
poetry run python run_dashboard.py
```

La dashboard sarà disponibile su: http://127.0.0.1:8050

## 📋 Prerequisiti

1. **Dati generati**: Prima di usare la dashboard, assicurati di aver eseguito l'analisi principale:
   ```bash
   poetry run python main.py
   ```
   Questo genererà i file Excel in `data/output/`:
   - `fpedia_analysis.xlsx`
   - `FSTATS_analysis.xlsx`

2. **Dipendenze**: Le dipendenze sono già installate quando hai eseguito `poetry install`

## 🎯 Funzionalità

### 📈 Overview
- Statistiche generali dei dataset
- Distribuzione per ruoli e squadre  
- Top giocatori per convenienza
- Grafici di distribuzione

### 🆚 Comparison
- Confronto tra dati FPEDIA e FSTATS
- Scatter plot interattivi
- Analisi di correlazione
- Statistiche comparative

### 👤 Players
- Tabella interattiva con tutti i giocatori
- Filtri avanzati per ruolo, squadra, convenienza
- Ordinamento e ricerca
- Export dei dati filtrati

## 🛠️ Tecnologie

- **Dash** - Framework web per Python
- **Plotly** - Grafici interattivi
- **Dash Bootstrap Components** - Styling
- **Dash AG Grid** - Tabelle avanzate
- **Pandas** - Manipolazione dati

## 📁 Struttura

```
dashboard/
├── app.py                  # App principale
├── components/
│   └── data_loader.py     # Caricamento dati
├── pages/
│   ├── overview.py        # Pagina overview
│   ├── comparison.py      # Pagina confronto
│   └── players.py         # Pagina giocatori
├── utils/
│   └── data_processing.py # Utilities per dati
└── assets/
    └── style.css          # Stili personalizzati
```

## 🔧 Troubleshooting

### Dashboard non si avvia
- Verifica che i file Excel esistano in `data/output/`
- Controlla che le dipendenze siano installate: `poetry install`

### Dati non visualizzati
- Esegui prima l'analisi principale: `poetry run python main.py`
- Usa il pulsante "Refresh Data" nella navbar

### Errori di importazione
- Assicurati di essere nella directory root del progetto
- Usa sempre `poetry run` per eseguire i comandi

## 📊 Dataset Info

- **FPEDIA**: Dati stagione corrente (513 giocatori, 30 colonne)
- **FSTATS**: Dati stagione precedente (499 giocatori, 70 colonne)  
- **Overlap**: Circa 400+ giocatori in comune

## 🎨 Personalizzazione

Puoi modificare gli stili in `dashboard/assets/style.css` per personalizzare l'aspetto della dashboard.