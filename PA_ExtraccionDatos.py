#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 15 19:13:18 2025

@author: ricardoortiz
"""

# pip install wbgapi
import wbgapi as wb
import pandas as pd
import requests
import pandas as pd
from io import StringIO
from datetime import datetime



wb.source.info()
wb.economy.info(db=75)


# Lista de variables seleccionadas del Banco Mundial
SEvar = ['GB.XPD.RSDV.GD.ZS','IP.JRN.ARTC.SC', 'SP.POP.SCIE.RD.P6', 'SP.POP.TECH.RD.P6', 'NY.GDP.PCAP.CD', 'SE.XPD.TOTL.GD.ZS', 'SE.XPD.TOTL.GB.ZS', 'SE.PRM.ENRR', 'SE.SEC.ENRR','SE.TER.ENRR', 'ER.PTD.TOTL.ZS', 'AG.LND.FRST.K2', 'AG.SRF.TOTL.K2', 'GE.EST' , 'IT.NET.USER.ZS']


# Países participantes en GBIF
GBIF_countries = ['AND', 'AGO', 'ARG', 'ARM', 'AUS', 'BEL', 'BEN', 'BRA', 'BDI', 'KHM', 'CMR', 'CAN', 'CAF',
 'CHL', 'COL', 'CRI', 'HRV', 'DNK', 'ECU', 'EST', 'FIN', 'FRA', 'GEO', 'DEU', 'GTM', 'GIN',
 'ISL', 'IRL', 'LBR', 'LUX', 'MDG', 'MWI', 'MRT', 'MEX', 'MNG', 'NAM', 'NLD', 'NZL', 'NOR',
 'PAN', 'PER', 'POL', 'PRT', 'SLE', 'SVK', 'SVN', 'ZAF', 'SSD', 'ESP', 'SUR', 'SWE', 'CHE',
 'TJK', 'TGO', 'TON', 'GBR', 'USA', 'URY', 'UZB', 'ZWE']

#Carga de datos con el API del Banco Mundial para los países seleccionados. 
#SE_Col_data= wb.data.DataFrame(SEvar, 'COL', time=range(2000, 2025), labels=True).reset_index()
SEdata= wb.data.DataFrame(SEvar, GBIF_countries, time=range(2000, 2025), labels=True).reset_index()

SEdata.head(5)


# Pivotear y organizar la tabla en un formato legible para el análisis.

# Cargar los datos
SEdata = SEdata.drop(columns=['Series'])

# Aplicar la función Melt para convertir los años de columnas a filas
SEdata_long = SEdata.melt(
    id_vars=["economy", "series", "Country"],
    var_name="Year",
    value_name="Value"
)

# Limpiar el campo Year: eliminar 'YR' y convertir a datetime
SEdata_long["Year"] = SEdata_long["Year"].str.replace("YR", "", regex=False)
SEdata_long["Year"] = pd.to_datetime(SEdata_long["Year"], format="%Y")
SEdata_long["Year"] = SEdata_long["Year"].dt.year  # Extrae solo el año como número

#Pivotear usando los valores de 'Series' como nombres de columna
SEdata_pivot = SEdata_long.pivot_table(
    index=["economy", "Country", "Year"],
    columns="series",
    values="Value",
    aggfunc="first"  # por si hay duplicados
).reset_index()

#  limpiar nombre de columnas si queda jerarquía
SEdata_pivot.columns.name = None



#Countries metadata


# URL de la API para obtener información de países
url = "https://api.worldbank.org/v2/country?format=json&per_page=300"

# Realizar la solicitud GET
response = requests.get(url)
data = response.json()

# Extraer los datos de los países
countries = data[1]  # La segunda parte del JSON contiene la lista de países

# Crear un DataFrame con la información relevante
countries_meta = pd.DataFrame([{
    "id": country["id"],
    "iso2Code": country["iso2Code"],
    "region": country["region"]["value"],
    "incomeLevel": country["incomeLevel"]["value"],
    "lendingType": country["lendingType"]["value"],
   
} for country in countries])

# Mostrar las primeras filas del DataFrame
print(countries_meta.head())



BM_Data = pd.merge(SEdata_pivot, countries_meta, left_on="economy", right_on="id", how="left")
##### Transformaciones

BM_Data  = BM_Data.rename(columns={'Year': 'year'})
BM_Data  = BM_Data.rename(columns={'Country': 'country'})
BM_Data  = BM_Data.rename(columns={'iso2Code': 'countryCode'})
dropcolumns = ['economy','id']
BM_Data = BM_Data.drop(dropcolumns, axis=1)



###############################
#DATOS GBIF
###############################


############################################

# Descargar los datos y generar subset por año y país

############################################



# Parámetros
BASE_URL = "https://analytics-files.gbif.org/global/csv/"
GBIF_FILES = [
    "occ_country.csv",
    "occ_publisherCountry.csv",
    "spe_country.csv",
    "spe_publisherCountry.csv"
]
DIAS_UMBRAL = 60  # días alrededor del 31 de diciembre a considerar

# Función para cargar archivos CSV desde URL
def load_csv(filename):
    url = BASE_URL + filename
    try:
        print(f"📥 Cargando {filename} desde: {url}")
        response = requests.get(url)
        response.raise_for_status()
        df = pd.read_csv(StringIO(response.text))
        print(f"✅ {filename} cargado con éxito.")
        return df
    except Exception as e:
        print(f"❌ Error al cargar {filename}: {e}")
        return pd.DataFrame()

# Función para ajustar el año según cercanía a diciembre 31
def ajustar_anio(snapshot, max_dias=DIAS_UMBRAL):
    d31_prev = datetime(snapshot.year - 1, 12, 31)
    d31_curr = datetime(snapshot.year, 12, 31)
    diff_prev = abs((snapshot - d31_prev).days)
    diff_curr = abs((snapshot - d31_curr).days)
    
    if diff_prev <= max_dias and snapshot < d31_curr:
        return snapshot.year - 1
    elif diff_curr <= max_dias:
        return snapshot.year
    else:
        return None

# Función para obtener solo la fecha más cercana a 31 dic por año
def extraer_snapshot_mas_cercano(df, dias_umbral=DIAS_UMBRAL):
    df = df.copy()
    df["snapshot"] = pd.to_datetime(df["snapshot"])
    df["year"] = df["snapshot"].apply(lambda x: ajustar_anio(x, dias_umbral))
    df = df.dropna(subset=["year"])
    
    df["dist_to_d31"] = df.apply(
        lambda row: abs((row["snapshot"] - datetime(int(row["year"]), 12, 31)).days),
        axis=1
    )
    
    df_sorted = df.sort_values(by=["year", "dist_to_d31"])
    fechas_cercanas = df_sorted.groupby("year")["snapshot"].first().reset_index()
    
    df_final = df.merge(fechas_cercanas, on=["year", "snapshot"], how="inner")
    return df_final.drop(columns=["dist_to_d31"])

# Cargar y procesar todos los archivos
dataframes = {}
for filename in GBIF_FILES:
    key = filename.replace(".csv", "")
    df_raw = load_csv(filename)
    if not df_raw.empty:
        dataframes[key] = extraer_snapshot_mas_cercano(df_raw)

globals().update(dataframes)

# Ejemplo: visualizar resultado para 'occ_country'
print(dataframes["occ_country"].head())



#########################3
#JOIN
########################

# Renombrar columnas
spe_publisherCountry.rename(columns={
    'publisherCountry': 'countryCode',
    'speciesCount': 'speciesCount_publisher'
}, inplace=True)

occ_publisherCountry.rename(columns={
    'publisherCountry': 'countryCode',
    'occurrenceCount': 'occurrenceCount_publisher'
}, inplace=True)

occ_country.rename(columns={'country': 'countryCode'}, inplace=True)
spe_country.rename(columns={'country': 'countryCode'}, inplace=True)

# Lista de datasets
datasets = [spe_country, spe_publisherCountry, occ_country, occ_publisherCountry]

# Limpieza: eliminar snapshot y filtrar NaNs en countryCode
for i in range(len(datasets)):
    datasets[i] = datasets[i].drop(columns=["snapshot"], errors="ignore")
    datasets[i] = datasets[i].dropna(subset=["countryCode"])

# Merge usando year y countryCode como claves
from functools import reduce
df_merged = reduce(lambda left, right: pd.merge(left, right, on=["year", "countryCode"], how="outer"), datasets)

# Mostrar una vista previa
print(df_merged.head())


Data = pd.merge(BM_Data, df_merged, on=["year", "countryCode"], how="left")







