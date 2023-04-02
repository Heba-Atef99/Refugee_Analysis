import pandas as pd

def prepare_lons_lats(lons_lats):
    for col in lons_lats.columns:
        lons_lats[col] = lons_lats[col].str.replace('"', '').str.strip()

    lons_lats['Latitude (average)'] = lons_lats['Latitude (average)'].astype(float)
    lons_lats['Longitude (average)'] = lons_lats['Longitude (average)'].astype(float)
    return lons_lats

def prepare_df_all_years(df_all_years):
    df_all_years['Country of origin'] = df_all_years['Country of origin'].apply(lambda x: x.split('(')[0]).apply(lambda x: x.split(':')[0]).str.replace('Dem. Rep. of the', "").str.replace('United Rep. of', '').str.strip()
    df_all_years = df_all_years[df_all_years['Country of origin'] != 'Unknown']
    df_all_years = df_all_years[df_all_years['Country of asylum'] != 'Unknown']
    return df_all_years

def prepare_second_plot_data(second_plot):
    second_plot.columns = ["date","country","event","link"]
    second_plot['event'] = second_plot['event'].str.replace('Source:', 'Source ') #, ',
    second_plot[['day', 'event']] = second_plot['event'].str.split(':', 1, expand=True)
    second_plot['day'] = second_plot['day'].str.replace('As reported on',  '').str.replace('Around',  '').str.replace('On',  '') #, 'As reported on': '', 'Around': '', 'On':'',
    return second_plot

def prepare_data():
    df_all_years = pd.read_csv('data/all_years_population.csv')
    lons_lats = pd.read_csv('data/countries_codes_and_coordinates.csv',  sep=',', engine='python')
    second_plot = pd.read_excel("data/2022-protection-in-danger-monthly-news-brief-dataset.xlsx")

    df_all_years = prepare_df_all_years(df_all_years)
    second_plot = prepare_second_plot_data(second_plot)
    lons_lats = prepare_lons_lats(lons_lats)
    return df_all_years, second_plot, lons_lats
