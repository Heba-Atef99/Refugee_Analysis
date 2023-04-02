from dash import html, dcc, Dash, dash_table
import dash_bootstrap_components as dbc

import plotly.express as px
import plotly.graph_objects as go

import importlib
import pandas as pd

import functions.transform_data as td
importlib.reload(td);

plots_theme = 'simple_white'
idp_color = '#9B1D20'
ref_color = '#235755'
asylm_color = '#E19A00'
gray = '#b3b3b3'

global iso_loc, isos_original

def get_isos(df1, df2):
    global iso_loc, isos_original
    iso_loc = df1
    isos_original = df2

def get_ban(head, body, color, is_multi=False):
    if is_multi:
        ban = dbc.Col([
            body[2],
            html.Br(),
            html.Span([head], className='ban_head', style={'color':color}),
            html.Br(),
            body[0],
            body[1],
        ], className='col-4 ban_desc')

    else:
        ban = dbc.Col([
            html.Span([head], className='ban_body', style={'color':color}),
            html.Br(),
            body[0],
            html.Br(),
            body[1],
            html.Br(),
            body[2],
        ], className='col-4 ban_desc')

    return ban

def prepare_ban_body(type, ban_body, color, year, is_multi=False):
    if is_multi:
            body = [
                html.Span(['Since ']),
                html.Span([str(ban_body)], style={'color':color}),
                html.Span(['The number of ' + type + ' has grown by ']),
                ]
            return body

    proposition = ' In '

    if type == "Asylum-seekers":
        proposition = ' From '

    # body = [html.Span([type + proposition]),
    #         html.Span([ban_body], className='ban_body', style={'color':color}),
    #         html.Span([' In '+ str(year)]),
    #         ]
    body = [html.Span(["Top Country With "]),
            html.Span([ban_body], className='ban_head', style={'color':color}),
            html.Span([' ' + type + ' In '+ str(year)]),
            ]
    return body

def generate_ban(year, type1, type2, country, color, is_multi=False):
    ban_body_country, ban_head = td.get_type_ban(year, type1, country, is_multi)
    # ban_body = prepare_ban_body(type2, ban_body, color, year, is_multi)
    if is_multi:
        ban_head = str(ban_head) + ' Times'
    else:
        if ban_head < 0.5:
            ban_head *= 1000
            ban_head = str(ban_head)+'K'
        else:
            ban_head = str(ban_head)+'M'
                
    if is_multi:
        ban_body = prepare_ban_body(type2, ban_body_country, color, year, is_multi)
        ban = get_ban(ban_head, ban_body, color, is_multi)
    
    else:
        ban_body = prepare_ban_body(type2, ban_head, color, year, is_multi)
        ban = get_ban(ban_body_country, ban_body, color)
    # ban = get_ban(ban_body, ban_head, color)
    return ban

def get_all_bans(year):
    ban1 = generate_ban(year, 'Refugees under UNHCR\'s mandate', 'Refugees', 'Country of asylum', ref_color)
    ban2 = generate_ban(year, 'IDPs of concern to UNHCR', 'IDPs', 'Country of origin', idp_color)
    ban3 = generate_ban(year, 'Asylum-seekers', 'Asylum-seekers', 'Country of origin', asylm_color)
    ban4 = generate_ban(year, 'IDPs of concern to UNHCR', 'IDPs', 'Country of origin', idp_color, True)
    ban5 = generate_ban(year, 'Asylum-seekers', 'Asylum-seekers', 'Country of origin', asylm_color, True)
    return ban1, ban2, ban3, ban4, ban5

def plot_fig1(df_new):
    fig = px.bar(df_new.iloc[-10:],
             y="Country of origin",
             x= ["Refugees under UNHCR's mandate","Asylum-seekers","IDPs of concern to UNHCR"],
             barmode='group',
             orientation='h',text_auto='.1s', color_discrete_sequence=[ref_color, asylm_color, idp_color], template=plots_theme)
    
    fig.update_layout(legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    ), legend_title="Population Type")
    return fig

def plot_idp(idps):
    color_seq = [idp_color] + [gray]*(len(idps)-1)
    idb_plot = px.bar(data_frame=idps, x = 'Country of origin', y="IDPs of concern to UNHCR", color = 'Country of origin', color_discrete_sequence=color_seq, template=plots_theme)
    idb_plot.update_layout(showlegend=False)
    return idb_plot

def create_map(source_iso='SYR'):
  isos_customized = isos_original[isos_original['Country of origin (ISO)'] == source_iso].drop_duplicates()
  df_cd = pd.merge(isos_customized, iso_loc, how='left', left_on = 'Country of asylum (ISO)', right_on = 'Alpha-3 code')

  mig_fig = go.Figure()

  dest = zip(df_cd["Latitude (average)"], df_cd["Longitude (average)"])
  source_lat_long = iso_loc[iso_loc['Alpha-3 code'] == source_iso]
  slat, slon =source_lat_long.iloc[0, 1:3]

  ## Loop thorugh each flight entry to add line between source and destination
  for dlat, dlon in dest:
      mig_fig.add_trace(go.Scattergeo(
                          lat = [slat,dlat],
                          lon = [slon, dlon],
                          mode = 'lines',
                          line = dict(width = 1, color="red")
                          ))

  ## Loop thorugh each flight entry to plot source and destination as points.
  mig_fig.add_trace(
      go.Scattergeo(
                  lon =  df_cd["Longitude (average)"].values.tolist(),
                  lat =  df_cd["Latitude (average)"].values.tolist(),
                  hoverinfo = 'text',
                  text = df_cd['Country'],
                  mode = 'markers',
                  marker = dict(size = 5, color = 'black', opacity=0.6))
      )

  ## Update graph layout to improve graph styling.
  mig_fig.update_layout(
                    # title_text= country_name + " Refuegees' Destination",
                    margin={"t":10,"b":0,"l":10, "r":10, "pad":0},
                    showlegend=False,
                    title_x=0.5
                    )

  mig_fig.update_geos(projection_type="natural earth", landcolor='lightgray')

  return mig_fig

def plot_asylm_ref(ref_year):
    fig = px.choropleth(ref_year, locations='Country of asylum (ISO)',
                    color="Refugees under UNHCR's mandate",
                    hover_name="Country of asylum",
                    color_continuous_scale=px.colors.sequential.Greens)
 
    fig["layout"].pop("updatemenus")
    fig.update_geos(projection_type="natural earth", landcolor='lightgray')
    fig.update_layout(
        margin={"t":40,"b":85,"l":0, "r":0, "pad":30},
        coloraxis_colorbar=dict(
            orientation="h",
            yanchor="bottom",
            xanchor="right",
            x=1.07
            )
    )
    return fig

def plot_seekers(seekers):
    color_seq = [asylm_color] + [gray]*(len(seekers)-1)
    # print(color_seq)
    seekers_plot = px.bar(seekers, y="Asylum-seekers", x='Country of origin',color = 'Country of origin',  color_discrete_sequence=color_seq, template=plots_theme)
    seekers_plot.update_layout(showlegend=False)

    return seekers_plot

def create_events_table(events, month):
    events['day'] = events['day'].apply(lambda x: month+'-'+x.strip()[:2])
    events.rename(columns = {'day': 'Day', 'event': 'Event'}, inplace=True)
    table_events = dash_table.DataTable(
                    events.to_dict('records'), 

                    columns=[{'id': c, 'name': c} for c in events.columns],
                    style_header={
                        'fontWeight': 'bold',
                        'textAlign': 'center',
                        'font-family': 'var(--bs-body-font-family)'
                    },
                    style_data={
                        'white-space': 'inherit',
                        'textAlign': 'left',
                        'font-family': 'var(--bs-body-font-family)'
                    },
                    style_table={'overflowY': 'scroll', 'max-height': 400},
                    style_cell_conditional=[{'if': {'column_id': 'Day'}, 'width': '15%'}]
                    )
    return table_events