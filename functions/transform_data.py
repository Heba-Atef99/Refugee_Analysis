import numpy as np
import pandas as pd

global df_all_years

def get_df(df):
    global df_all_years
    df_all_years = df

def get_first_data(year):
    first_plot = df_all_years[df_all_years["Year"] == year].groupby("Country of origin")[["Refugees under UNHCR's mandate","Asylum-seekers","IDPs of concern to UNHCR"]].sum()
    first_plot = first_plot.sort_values(by="Refugees under UNHCR's mandate",ascending=True).reset_index()
    return first_plot

def get_idps(offset):
    # idps = df_all_years[df_all_years['Year'] > offset].groupby('Country of origin').agg({'IDPs of concern to UNHCR': 'sum'}).sort_values('IDPs of concern to UNHCR', ascending=False)
    idps = df_all_years[df_all_years['Year'] == offset].groupby('Country of origin').agg({'IDPs of concern to UNHCR': 'sum'}).sort_values('IDPs of concern to UNHCR', ascending=False)
    idps = idps.reset_index()

    idps['color_seq'] = '#b3b3b3'
    idps.loc[idps['Country of origin'] == 'Syrian Arab Rep.', 'color_seq'] = '#d62728'
    return idps.iloc[:10]

def get_type_ban(year, type, country, is_multi=False):
    if is_multi:
        t_1 = df_all_years[df_all_years['Year']==year][type].sum()
        t_2 = df_all_years[df_all_years['Year']==year-5][type].sum()
        past = year-5
        if t_2 == 0:
            t_2 = df_all_years[df_all_years['Year']==2000][type].sum()
            past = 2000

        return past, np.round(t_1 / t_2, 2)
    
    type_year = df_all_years[df_all_years['Year'] == year].groupby(country).agg({type: 'sum'}).sort_values(type, ascending=False)
    type_year = type_year.reset_index()
    return type_year.iloc[0, 0], round_bans(type_year.iloc[0, 1])

def round_bans(ban):
    return np.round(ban/1000000, 2)

def get_ref_data(year=2022):
    ref_year = df_all_years[df_all_years['Year'] == year].groupby("Country of asylum (ISO)").agg({"Refugees under UNHCR's mandate": 'sum'}).sort_values("Refugees under UNHCR's mandate", ascending=False)
    ref_year = ref_year.reset_index()
    ref_year = pd.merge(ref_year, df_all_years[df_all_years['Year'] == 2020][['Country of asylum (ISO)', 'Country of asylum']], how='left', on = 'Country of asylum (ISO)')
    return ref_year

def get_seekers(year=2022):
    seekers_year2 = df_all_years[df_all_years['Year'] == year].groupby('Country of origin').agg({'Asylum-seekers': 'sum'}).sort_values('Asylum-seekers', ascending=False)
    seekers_year2=seekers_year2.reset_index()
    seekers_year2 = seekers_year2[seekers_year2['Country of origin'].str.strip() !='Unknown']
    return seekers_year2.iloc[:10]