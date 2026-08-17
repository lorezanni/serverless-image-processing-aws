# Serverless Image Processing Pipeline

Pipeline per l'elaborazione e l'ottimizzazione automatica di immagini su AWS.
Il sistema adotta un'architettura event-driven ed e implementato con Serverless Framework su runtime Python 3.11.

## Architettura del sistema

Il flusso di esecuzione e stateless e asincrono:

- **Amazon S3 (input bucket):** riceve le immagini originali caricate dal client.
- **AWS Lambda (Python 3.11 + Pillow):** viene invocata da evento S3, esegue ridimensionamento e compressione JPEG.
- **Amazon S3 (output bucket):** salva in modo persistente i file ottimizzati.
- **Amazon DynamoDB:** registra i metadati di esecuzione (tempi, dimensioni, percentuali di compressione).

## Struttura del progetto

```text
.
├── benchmark_samples/            # Dataset di test per le misurazioni
├── package/                      # Dipendenze Linux x86_64 per runtime Lambda
├── handler.py                    # Funzione di elaborazione immagine
├── serverless.yml                # Configurazione infrastruttura cloud
├── generate-benchmarks-images.py # Script di generazione immagini benchmark
├── requirements.txt              # Dipendenze Python del progetto
└── results.csv                   # Risultati benchmark
```

## Installazione e configurazione

1. Scarica le dipendenze Pillow compatibili con Amazon Linux:

```bash
pip install --platform manylinux2014_x86_64 --target ./package --only-binary=:all: --python-version 3.11 Pillow
```

2. Esegui il deploy dell'infrastruttura con Serverless Framework:

```bash
serverless deploy
```

## Esecuzione test

Per generare il dataset immagini a diverse risoluzioni:

```bash
python generate-benchmarks-images.py
```

I file generati possono essere caricati nel bucket S3 di input per avviare l'elaborazione e analizzare le metriche salvate su DynamoDB.

## Risultati benchmark

Dati sperimentali ottenuti con allocazione memoria Lambda a 1024 MB:

| Risoluzione | Dimensione In | Dimensione Out | Compressione | Tempo Elaborazione | Durata Totale | Stato Container |
| --- | --- | --- | --- | --- | --- | --- |
| 800x600 | 240.23 KB | 86.85 KB | 63.85% | 358 ms | 959 ms | Cold Start |
| 800x600 | 240.23 KB | 86.85 KB | 63.85% | 338 ms | 464 ms | Warm Start |
| 1920x1080 | 1029.07 KB | 100.82 KB | 90.20% | 1290 ms | 1486 ms | Warm Start |
| 2560x1440 | 1827.60 KB | 100.88 KB | 94.48% | 2244 ms | 2577 ms | Warm Start |
| 3840x2160 | 4108.57 KB | 100.91 KB | 97.54% | 5064 ms | 5787 ms | Warm Start |