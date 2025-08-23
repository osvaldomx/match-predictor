# src/data/scrape.py
import argparse
import os
import time
import re
from datetime import datetime

import pandas as pd
import requests
from bs4 import BeautifulSoup

# URL base para los resultados de la Liga MX en FBref.
# El primer '{year}' es para la temporada (ej. 2023-2024), el segundo para el ID de la tabla.
BASE_URL = "https://fbref.com/en/comps/31/{year}/schedule/{year}-Liga-MX-Scores-and-Fixtures"

def scrape_season_data(season: str) -> pd.DataFrame:
    """
    Extrae los datos de la tabla de resultados de una temporada de la Liga MX.

    Args:
        season: La temporada a extraer, en formato 'YYYY-YYYY' (ej. '2023-2024').

    Returns:
        Un DataFrame de pandas con los datos de los partidos.
    """
    url = BASE_URL.format(year=season)
    print(f"Obteniendo datos para la temporada {season} desde {url}...")
    
    # Es una buena práctica usar un User-Agent para simular un navegador
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener la página: {e}")
        return pd.DataFrame()

    # Usamos BeautifulSoup para parsear el HTML
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # La tabla de resultados suele tener un ID que podemos usar como selector
    #table_id = f"sched_{season}_31_1"
    table_id = f"sched_all"
    table = soup.find('table', {'id': table_id})

    if not table:
        print(f"No se encontró la tabla con el ID '{table_id}'.")
        return pd.DataFrame()

    # Extraemos los datos de la tabla
    rows = table.find('tbody').find_all('tr')

    season_type_global = None
    season_year_global = None
    
    match_data = []
    for row in rows:
        # Saltamos las filas que son cabeceras intermedias en la tabla
        if row.find_all(['th', 'tr'], {'class': 'thead'}):
            continue

        cells = row.find_all(['th', 'td'])
        # Si la fila no tiene suficientes celdas, la ignoramos
        if len(cells) < 10 or cells[1].text.strip() == 'Wk':
            continue

        # Saltamos filas intermedias vacias
        if not cells[4].text.strip():
            continue

        # Extraemos tipo de temporada
        ptr = r"(Apertura|Clausura)\s\d{4}"
        match_season = re.search(ptr, cells[0].text.strip(), re.IGNORECASE)

        season_type = match_season.group().split(' ')[0] if match_season else None
        season_year = match_season.group().split(' ')[1] if match_season else None

        season_type_global = season_type if season_type else season_type_global
        season_year_global = season_year if season_year else season_year_global

        if "Regular Season" in cells[0].text.strip():
            season_phase = "Regular Season"
        else:
            season_phase = "Liguilla"

        # Extraemos fases de liguilla
        week = None
        if "Quarter" in cells[0].text.strip():
            if 'Leg 1' in cells[14].text.strip():
                week = "Cuartos Ida"
            else:
                week = "Cuartos Vuelta"
        elif "Semi" in cells[0].text.strip():
            if 'Leg 1' in cells[14].text.strip():
                week = "Semifinal Ida"
            else:
                week = "Semifinal Vuelta"
        elif "Finals" in cells[0].text.strip():
            if 'Leg 1' in cells[14].text.strip():
                week = "Final Ida"
            else:
                week = "Final Vuelta"

        # Checa el marcador por si hay penales, por el momento se eliminan
        ptr = r'\d+–\d+'
        fix_score = re.search(ptr, cells[7].text.strip())
            
        match_info = {
            'week': cells[1].text.strip() or week,
            'day': cells[2].text.strip(),
            'date': cells[3].text.strip(),
            'time': cells[4].text.strip(),
            'home_team': cells[5].text.strip(),
            'xgh': cells[6].text.strip(),
            'score': fix_score.group() if fix_score else cells[7].text.strip(),
            'xga': cells[8].text.strip(),
            'away_team': cells[9].text.strip(),
            'attendance': cells[10].text.strip(),
            'venue': cells[11].text.strip().replace('...', '').strip(),
            'referee': cells[12].text.strip(),
            'match_report_url': cells[13].find('a')['href'] if cells[13].find('a') else None,
            'season_type': season_type_global,
            'season_year': season_year_global,
            'seeason_phase': season_phase 
        }
        match_data.append(match_info)

    return pd.DataFrame(match_data)


if __name__ == '__main__':
    # Usamos argparse para manejar los argumentos de la línea de comandos
    # Esto hace que el script sea compatible con nuestro dvc.yaml
    parser = argparse.ArgumentParser(
        description="Web scraper para datos de la Liga MX desde FBref."
    )
    parser.add_argument(
        "--output", 
        type=str, 
        required=True, 
        help="Ruta del archivo CSV de salida."
    )
    args = parser.parse_args()

    # Vamos a obtener datos de las últimas 5 temporadas completas
    current_year = datetime.now().year
    seasons = [
        f"{year}-{year+1}" for year in range(current_year - 6, current_year - 1)
    ]

    all_seasons_df = []
    for s in seasons:
        season_df = scrape_season_data(s)
        if not season_df.empty:
            season_df['calendar'] = s
            all_seasons_df.append(season_df)
        time.sleep(3)  # Pausa de 3 segundos para ser respetuosos con el servidor

    # Concatenamos los datos de todas las temporadas y los guardamos
    final_df = pd.concat(all_seasons_df, ignore_index=True)
    
    # Aseguramos que el directorio de salida exista
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    final_df.to_csv(args.output, index=False)
    
    print(f"\n[SUCCESS] Datos guardados exitosamente en '{args.output}'.")
    print(f"Total de partidos extraídos: {len(final_df)}")