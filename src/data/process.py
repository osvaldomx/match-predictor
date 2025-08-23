# src/data/process.py
import argparse
import os
import pandas as pd
import numpy as np

def calculate_rolling_features(group: pd.DataFrame, window_size: int = 5) -> pd.DataFrame:
    """Calcula características rodantes para un equipo."""
    group = group.sort_values('date')
    
    # Goles y Puntos
    rolling_stats = group[['goals_scored', 'goals_conceded', 'points']].rolling(window=window_size, closed='left').mean()
    group['avg_goals_scored'] = rolling_stats['goals_scored']
    group['avg_goals_conceded'] = rolling_stats['goals_conceded']
    group['avg_points'] = rolling_stats['points']
    
    return group

def process_data(input_path: str, output_path: str):
    """
    Limpia los datos crudos y genera características para el modelo.
    """
    print(f"Cargando datos crudos desde {input_path}...")
    df = pd.read_csv(input_path)

    # --- 1. Limpieza de Datos ---
    # Convertir a datetime para poder ordenar
    df['date'] = pd.to_datetime(df['date'])
    # Eliminar partidos futuros que no tienen marcador
    df = df[df['score'].notna()].copy()
    
    # Extraer goles del marcador (ej. '2–1')
    score_split = df['score'].str.split('–', expand=True)
    df['home_goals'] = pd.to_numeric(score_split[0])
    df['away_goals'] = pd.to_numeric(score_split[1])
    
    # Definir el resultado (nuestra variable objetivo)
    # H: Home Win, D: Draw, A: Away Win
    df.loc[df['home_goals'] > df['away_goals'], 'result'] = 'H'
    df.loc[df['home_goals'] == df['away_goals'], 'result'] = 'D'
    df.loc[df['home_goals'] < df['away_goals'], 'result'] = 'A'

    # --- 2. Preparar datos para Feature Engineering ---
    # Creamos una vista de los datos por equipo para calcular sus estadísticas por partido
    home_df = df[['date', 'home_team', 'home_goals', 'away_goals', 'result']].rename(
        columns={'home_team': 'team', 'home_goals': 'goals_scored', 'away_goals': 'goals_conceded'}
    )
    home_df['location'] = 'H'
    
    away_df = df[['date', 'away_team', 'away_goals', 'home_goals', 'result']].rename(
        columns={'away_team': 'team', 'away_goals': 'goals_scored', 'home_goals': 'goals_conceded'}
    )
    away_df['location'] = 'A'
    
    # Unimos todo en un solo DataFrame
    team_stats_df = pd.concat([home_df, away_df]).sort_values('date')
    
    # Definimos las condiciones lógicas para cada resultado posible
    conditions = [
        # Condición 1: El equipo era local (H) Y el resultado fue victoria local (H)
        (team_stats_df['location'] == 'H') & (team_stats_df['result'] == 'H'),
        # Condición 2: El equipo era visitante (A) Y el resultado fue victoria visitante (A)
        (team_stats_df['location'] == 'A') & (team_stats_df['result'] == 'A'),
        # Condición 3: El resultado fue un empate (D)
        (team_stats_df['result'] == 'D')
    ]

    # Definimos los valores (puntos) correspondientes a cada condición
    choices = [3, 3, 1]

    # Usamos np.select para crear la columna de puntos.
    # Si ninguna condición se cumple (es decir, una derrota), el valor por defecto es 0.
    team_stats_df['points'] = np.select(conditions, choices, default=0)
    
    # --- 3. Calcular Features Rodantes ---
    # Agrupamos por equipo y aplicamos la función de cálculo de features
    print("Calculando características rodantes (forma del equipo)...")
    processed_df = team_stats_df.groupby('team', group_keys=False).apply(calculate_rolling_features)
    
    # --- 4. Unir Features al Dataset Original ---
    # Renombramos columnas para distinguir entre local y visitante
    home_features = processed_df[processed_df['location'] == 'H'].rename(columns=lambda x: f"home_{x}" if x not in ['date', 'team'] else x)
    away_features = processed_df[processed_df['location'] == 'A'].rename(columns=lambda x: f"away_{x}" if x not in ['date', 'team'] else x)
    
    # Unimos de vuelta al dataframe original
    final_df = df.merge(home_features[['date', 'team', 'home_avg_goals_scored', 'home_avg_goals_conceded', 'home_avg_points']], 
                        left_on=['date', 'home_team'], right_on=['date', 'team'])
    final_df = final_df.merge(away_features[['date', 'team', 'away_avg_goals_scored', 'away_avg_goals_conceded', 'away_avg_points']],
                          left_on=['date', 'away_team'], right_on=['date', 'team'])

    # Limpiamos columnas redundantes y filas sin datos de promedios (las primeras de cada temporada)
    final_df = final_df.drop(columns=['team_x', 'team_y']).dropna()

    # --- 5. Guardar el resultado ---
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    final_df.to_csv(output_path, index=False)
    print(f"\n[SUCCESS] Datos procesados y guardados en '{output_path}'.")
    print(f"Dataset final con {len(final_df)} partidos y {len(final_df.columns)} columnas.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Procesa datos crudos de partidos y genera features."
    )
    parser.add_argument(
        "--input", 
        type=str, 
        required=True, 
        help="Ruta del archivo CSV de entrada (datos crudos)."
    )
    parser.add_argument(
        "--output", 
        type=str, 
        required=True, 
        help="Ruta del archivo CSV de salida (datos procesados)."
    )
    args = parser.parse_args()
    process_data(args.input, args.output)