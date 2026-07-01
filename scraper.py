#!/usr/bin/env python3
import json
import re
import sys
from datetime import datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup

URL = "https://loteria.gba.gob.ar/resultados"
OUTPUT_FILE = Path(__file__).parent / "resultados.json"
SORTEOS = ["La Previa", "El Primero", "Matutina", "Vespertina", "Nocturna"]
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"}


def fetch_html() -> str:
    resp = requests.get(URL, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    return resp.text


def extract_sorteo(texto: str, nombre_sorteo: str):
    patron_inicio = re.escape(f"Quiniela {nombre_sorteo}")
    match_inicio = re.search(patron_inicio, texto)
    if not match_inicio:
        return None
    resto = texto[match_inicio.end():]
    for otro in SORTEOS:
        if otro == nombre_sorteo:
            continue
        corte = re.search(re.escape(f"Quiniela {otro}"), resto)
        if corte:
            resto = resto[: corte.start()]
    fecha_match = re.search(r"(\d{2}/\d{2}/\d{4})", resto)
    fecha = fecha_match.group(1) if fecha_match else None
    sorteo_match = re.search(r"Sorteo N°\s*(\d+)", resto)
    numero_sorteo = sorteo_match.group(1) if sorteo_match else None
    pares = re.findall(r"\b(\d{2})\s+(\d{3,4})\b", resto)
    extracto = {posicion: numero for posicion, numero in pares}
    if not fecha and not numero_sorteo and not extracto:
        return None
    return {"sorteo": nombre_sorteo, "fecha": fecha, "numero_sorteo": numero_sorteo, "extracto": extracto}


def scrape():
    html = fetch_html()
    soup = BeautifulSoup(html, "html.parser")
    texto = soup.get_text(separator=" ")
    texto = re.sub(r"\s+", " ", texto)
    resultados = {}
    for nombre in SORTEOS:
        datos = extract_sorteo(texto, nombre)
        if datos:
            resultados[nombre] = datos
    return {"fuente": URL, "actualizado": datetime.utcnow().isoformat() + "Z", "sorteos": resultados}


def main():
    try:
        data = scrape()
    except requests.RequestException as e:
        print(f"Error al conectar con la fuente: {e}", file=sys.stderr)
        sys.exit(1)
    if not data["sorteos"]:
        print("Advertencia: no se pudo extraer ningún sorteo.", file=sys.stderr)
        sys.exit(2)
    OUTPUT_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OK - resultados guardados en {OUTPUT_FILE}")
    print(json.dumps(data, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
