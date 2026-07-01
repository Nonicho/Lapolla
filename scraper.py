name: Scrapear resultados quiniela

on:
  schedule:
    - cron: '30 13 * * *'
    - cron: '15 15 * * *'
    - cron: '15 18 * * *'
    - cron: '15 21 * * *'
    - cron: '15 0 * * *'
  workflow_dispatch: {}

permissions:
  contents: write

jobs:
  scrape:
    runs-on: ubuntu-latest
    steps:
      - name: Clonar repo
        uses: actions/checkout@v4

      - name: Configurar Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Instalar dependencias
        run: pip install -r requirements.txt

      - name: Correr scraper
        run: python scraper.py

      - name: Commitear resultados si cambiaron
        run: |
          git config user.name "quiniela-bot"
          git config user.email "actions@github.com"
          git add resultados.json
          git diff --quiet --cached || git commit -m "Actualiza resultados quiniela"
          git push
