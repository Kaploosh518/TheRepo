import streamlit as st
import pandas as pd
import altair as alt
import numpy as np

#streamlit run c:/Users/600318012/Coding/Github_v1/TheRepo/30daysst.py

import logging
import re
## For some reason I need to reinstall all the packages so this line worked 'python -m pip install pandas'
import pandas as pd
import os
import graphviz as gv
import streamlit as st
from math import floor
import textwrap
import polars as pl
#from streamlit_extras.dataframe_explorer import dataframe_explorer
from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)
from typing import Any, Dict

##FORMATTING PARAMETERS 
##-----------------------------------------------------------------------------------------------
display_limit = 4
business_name_limit = 35
##-----------------------------------------------------------------------------------------------


def wide_space_default():
    st.set_page_config(layout="wide", page_title="Hierarchy", initial_sidebar_state='collapsed')

wide_space_default()

##I imported the dataframe explorer function so I could tweak the language
def dataframe_explorer(df: pd.DataFrame, case: bool = True) -> pd.DataFrame:
    random_key_base = pd.util.hash_pandas_object(df)

    df = df.copy()

    # Try to convert datetimes into standard format (datetime, no timezone)
    for col in df.columns:
        if is_object_dtype(df[col]):
            try:
                df[col] = pd.to_datetime(df[col])
            except Exception:
                pass

        if is_datetime64_any_dtype(df[col]):
            df[col] = df[col].dt.tz_localize(None)

    modification_container = st.container()

    with modification_container:
        to_filter_columns = st.multiselect(
            "Select column(s) to filter by",
            df.columns,
            key=f"{random_key_base}_multiselect",
        )
        filters: Dict[str, Any] = dict()
        for column in to_filter_columns:
            left, right = st.columns((1, 20))
            # Treat columns with < 10 unique values as categorical
            if is_categorical_dtype(df[column]) or df[column].nunique() < 10:
                left.write("↳")
                filters[column] = right.multiselect(
                    f"Filter by {column}",
                    df[column].unique(),
                    default=list(df[column].unique()),
                    key=f"{random_key_base}_{column}",
                )
                df = df[df[column].isin(filters[column])]
            elif is_numeric_dtype(df[column]):
                left.write("↳")
                _min = float(df[column].min())
                _max = float(df[column].max())
                step = (_max - _min) / 100
                filters[column] = right.slider(
                    f"Values for {column}",
                    _min,
                    _max,
                    (_min, _max),
                    step=step,
                    key=f"{random_key_base}_{column}",
                )
                df = df[df[column].between(*filters[column])]
            elif is_datetime64_any_dtype(df[column]):
                left.write("↳")
                filters[column] = right.date_input(
                    f"Values for {column}",
                    value=(
                        df[column].min(),
                        df[column].max(),
                    ),
                    key=f"{random_key_base}_{column}",
                )
                if len(filters[column]) == 2:
                    filters[column] = tuple(map(pd.to_datetime, filters[column]))
                    start_date, end_date = filters[column]
                    df = df.loc[df[column].between(start_date, end_date)]
            else:
                left.write("↳")
                filters[column] = right.text_input(
                    f"Search by {column}",
                    key=f"{random_key_base}_{column}",
                )
                if filters[column]:
                    df[column] = df[column].fillna("")
                    df = df[df[column].str.contains(filters[column], case=case)]

    return df


if "user_duns" not in st.session_state:
    st.warning("Please enter a DUNS number to view the hierarchy.")

if "user_duns" not in st.session_state:
    st.session_state.user_duns = ""


input_temp_2 = st.text_input("Enter a duns number", placeholder="Type DUNS number here...", on_change=lambda: new_duns_input(), key="input_temp_2", value=st.session_state.user_duns)
st.session_state.user_duns = input_temp_2

def new_duns_input():
    new_value = st.session_state.input_temp_2
    if "user_duns" not in st.session_state or st.session_state.user_duns != new_value:
        st.session_state.user_duns = [new_value]
    st.rerun()

if "user_duns" in st.session_state:

    specified_duns = st.session_state.user_duns if st.session_state.user_duns else None

    if specified_duns is None:
        st.warning("Please enter a DUNS number to view the hierarchy.")
        st.write(st.session_state['user_duns'])
        st.stop()

    ##Initializing dataset
    df = pl.read_csv(
                r"C:\Users\600318012\Coding\hierarchy\outputs\dnb_export.csv",
                dtypes={col: pl.Utf8 for col in pl.read_csv(r"C:\Users\600318012\Coding\hierarchy\outputs\dnb_export.csv", n_rows=1).columns}
            )

    # try:
    #     filtered_df = df.filter(pl.col('duns_number') == st.session_state.user_duns[0])
    #     if filtered_df.is_empty():
    #         raise ValueError("No matching DUNS number found in the dataset.")
    #     specified_global_ultimate = filtered_df.select('global_ultimate_duns_number').item()
    # except Exception as e:
    #     st.error(f"Incomplete Duns Hierarchy or invalid input: {e}. Please check and try again.")
    #     st.stop()
    specified_global_ultimate = '653713339'

    new_df = df.filter(pl.col('global_ultimate_duns_number') == specified_global_ultimate)
    linkage_data_polars = new_df.select([
                'duns_number',
                'duns_linkage',
                'business_name',
                'tradestyle_name',
                'hierarchy_level',
                'site_indicator',
                'global_ultimate_duns_number'
            ])

    linkage_data = linkage_data_polars.to_pandas()
    linkage_data = linkage_data.astype(str)

    linkage_data['parent_id'] = linkage_data['duns_linkage'].apply(
        lambda x: x[10:19] if pd.notnull(x) and len(x) >= 10 else ''
    )

    children_count = linkage_data.groupby('parent_id').size().reset_index(name='children_count')

    linkage_2 = pd.merge(
        linkage_data,
        children_count,
        left_on='duns_number',
        right_on='parent_id',
        how='left'
    ).drop(columns='parent_id_y')


    linkage_2 = linkage_2.rename(columns={'parent_id_x': 'parent_id'})
    linkage_2['children_count'] = linkage_2['children_count'].fillna(0).astype(int)
    st.image(r"C:\Users\600318012\market-universe\Streamlit\hierarchy_viewer_v1\1490x100_Market-Universe-Banner_3.png", use_container_width=True)
    st.markdown("""
        <h1 style='text-align: center; font-size: 48px; color: black; margin-top: 0;'>
            Hierarchy Viewer
        </h1>
    """, unsafe_allow_html=True)

    ##Logic to handle the duns number in the URL
    # params = st.query_params
    # duns_from_url = params.get("URL_DUNS")

    # if "new_duns_number" not in st.session_state:
    #     if duns_from_url:
    #         st.session_state.new_duns_number = duns_from_url
    #     else:
    #         st.session_state.new_duns_number = None

    # if "recently_searched" not in st.session_state:
    #     st.session_state.recently_searched = []
    #     if duns_from_url:
    #         st.session_state.recently_searched.append(duns_from_url)

    # specified_duns = st.session_state.new_duns_number or linkage_2[(linkage_2['site_indicator'] == 'Global Ultimate') | (linkage_2['site_indicator'] == 'Target and Global Ultimate')]['duns_number'].iloc[0]

    # def handle_input_change():
    #     new_value = st.session_state.input_temp
    #     st.session_state.new_duns_number = new_value
    #     if new_value not in st.session_state.recently_searched:
    #         st.session_state.recently_searched.append(new_value)



    st.markdown(
        "<h3 style='color: #002496;'>Enter Duns Number:</h3>", 
        unsafe_allow_html=True
    )

    def handle_input_change():
        new_value = st.session_state.input_temp
        if "user_duns" not in st.session_state or st.session_state.user_duns[0] != new_value:
            st.session_state.user_duns = [new_value]
        if new_value not in st.session_state.recently_searched:
            st.session_state.recently_searched.append(new_value)

    st.text_input(
        "",
        key="input_temp",
        value=specified_duns,
        on_change=handle_input_change,
        placeholder="Type DUNS number here..."
    )
    st.markdown(
        "<h3 style='color: #002496;'>Current Selection</h3>", 
        unsafe_allow_html=True
    )
    this_selection = df.filter(pl.col('duns_number') == specified_duns).select([
                'duns_number',
                'duns_linkage',
                'business_name',
                'tradestyle_name',
                'hierarchy_level',
                'site_indicator',
                'global_ultimate_duns_number'
            ]).to_pandas()
    st.table(this_selection)
    st.divider()



    ##Initializing hierarchy data of duns
    try:
        temp3 = linkage_2.loc[linkage_2['duns_number'] == specified_duns, 'duns_linkage'].values[0]
    except IndexError:
        st.error("Single Location Duns or Nulled Hierarchy Data")
        st.dataframe(df.head(10), use_container_width=True)
        st.stop()
    specified_duns_linkage = re.findall(r'\d{9}', temp3)

    parental_chain = linkage_2[
        (linkage_2['duns_linkage'].str.contains(specified_duns, na=False)) |
        (linkage_2['duns_number'].isin(specified_duns_linkage))
    ]

    dot = gv.Digraph(comment='Hierarchy', graph_attr={'rankdir': 'TB'}, node_attr={'shape': 'box'})
    dot.attr('node', fixedsize='false')



    def wrap_label(text, width=business_name_limit):
        return "\n".join(textwrap.wrap(text, width))


    # Add the specified DUNS node
    specified_row = parental_chain[parental_chain['duns_number'] == specified_duns].iloc[0]
    node_label = (
        wrap_label(str(specified_row['business_name'])) + "\n DUNS: " + str(specified_row['duns_number']) +
        ", " + str(specified_row['site_indicator']) + "\n Number of Direct Children: " +
        str(specified_row['children_count']) + "\n Hierachy Level: " +
        str(specified_row['hierarchy_level'])
    )
    if specified_row['site_indicator'] == 'Target and Global Ultimate' or specified_row['site_indicator'] == 'Global Ultimate':
        dot.node(str(specified_row['duns_number']), node_label, color='#0073CF', fontcolor='white', style='filled')
    else:
        dot.node(str(specified_row['duns_number']), node_label, color='#FECB00', style='filled')
    children = linkage_2[linkage_2['parent_id'] == specified_duns]

    hidden_nodes_count_children = len(children) - display_limit

    ##Children Nodes
    for i, (_, child_row) in enumerate(children.iterrows()):
        if i >= display_limit:
            break
        child_label = (
            wrap_label(str(child_row['business_name'])) + "\n DUNS: " + str(child_row['duns_number']) +
            ", " + str(child_row['site_indicator']) + "\n Number of Direct Children: " +
            str(child_row['children_count']) + "\n Hierachy Level: " +
            str(child_row['hierarchy_level'])
        )
        if specified_duns != child_row['duns_number']: ##Have to include this due to how children data is pulled
            if child_row['site_indicator'] == 'Target and Global Ultimate' or child_row['site_indicator'] == 'Global Ultimate':
                dot.node(str(child_row['duns_number']), child_label, color = '#0073CF', fontcolor = 'white', style = 'filled')
            elif child_row['site_indicator'] == 'Target Ultimate':
                dot.node(str(child_row['duns_number']), child_label, color = '#96BC28', fontcolor = '#0073CF', style = 'bold')
            else:
                dot.node(str(child_row['duns_number']), child_label, color = '#0073CF', fontcolor = '#0073CF', style = 'bold')
        dot.edge(specified_duns, str(child_row['duns_number']))

    if hidden_nodes_count_children > 0:
        dot.node("hidden_nodes_children", f"...and {hidden_nodes_count_children} more children", shape="ellipse", style="dashed, filled", fillcolor = 'gray83')
        dot.edge(specified_duns, "hidden_nodes_children")



    ##Complete Parental Chain
    current_duns = specified_duns
    while True:
        parent_row = parental_chain[parental_chain['duns_number'] == current_duns]
        if parent_row.empty or pd.isna(parent_row.iloc[0]['parent_id']) or parent_row.iloc[0]['parent_id'] == '':
            break
        parent_id = parent_row.iloc[0]['parent_id']
        parent_data = parental_chain[parental_chain['duns_number'] == parent_id]
        if parent_data.empty:
            break
        parent_label = (
            wrap_label(str(parent_data.iloc[0]['business_name'])) + "\n DUNS: " + str(parent_data.iloc[0]['duns_number']) +
            ", " + str(parent_data.iloc[0]['site_indicator']) + "\n Number of Direct Children: " +
            str(parent_data.iloc[0]['children_count']) + "\n Hierachy Level: " +
            str(parent_data.iloc[0]['hierarchy_level'])
        )
        if current_duns != parent_data.iloc[0]['duns_number']:
            if str(parent_data.iloc[0]['site_indicator']) == 'Target and Global Ultimate' or str(parent_data.iloc[0]['site_indicator']) == 'Global Ultimate':
                dot.node(str(parent_data.iloc[0]['duns_number']), parent_label, color = '#0073CF', fontcolor = 'white', style = 'filled')
                
                #, URL = f"http://localhost:8501/?URL_DUNS={parent_data.iloc[0]['duns_number']}"
            elif str(parent_data.iloc[0]['site_indicator']) == 'Target Ultimate':
                dot.node(str(parent_data.iloc[0]['duns_number']), parent_label, color = '#96BC28', fontcolor = '#0073CF', style = 'bold')
            
            else:
                dot.node(str(parent_data.iloc[0]['duns_number']), parent_label, color = '#0073CF', fontcolor = '#0073CF', style = 'bold')
    
                #, URL = f"http://localhost:8501/?URL_DUNS={parent_data.iloc[0]['duns_number']}"
            dot.edge(str(parent_data.iloc[0]['duns_number']), current_duns)
        current_duns = parent_id

    ##Siblings
    siblings = linkage_2[linkage_2['parent_id'] == specified_row['parent_id']]

    hidden_nodes_count_siblings = len(siblings) - display_limit

    displayed_siblings = siblings[siblings['duns_number'] != specified_duns].head(display_limit)
    sibling_ids = list(displayed_siblings['duns_number'])

    middle_index = floor(len(sibling_ids) / 2)
    sibling_ids.insert(middle_index, specified_duns)

    for duns_id in sibling_ids:
        if str(duns_id) != str(specified_duns):
            sibling_row = linkage_2[linkage_2['duns_number'] == duns_id].iloc[0]
            sibling_label = (
                wrap_label(str(sibling_row['business_name'])) + "\n DUNS: " + str(sibling_row['duns_number']) +
                ", " + str(sibling_row['site_indicator']) + "\n Number of Direct Children: " +
                str(sibling_row['children_count']) + "\n Hierachy Level: " +
                str(sibling_row['hierarchy_level'])
            )
            if sibling_row['site_indicator'] == 'Target and Global Ultimate' or sibling_row['site_indicator'] == 'Target Ultimate' or sibling_row['site_indicator'] == 'Global Ultimate':
                dot.node(str(duns_id), sibling_label, color = '#96BC28', fontcolor = '#0073CF', style = 'bold')
    
                #, URL = f"http://localhost:8501/?URL_DUNS={sibling_row['duns_number']}"
            else:
                dot.node(str(duns_id), sibling_label, color = '#0073CF', fontcolor = '#0073CF', style = 'bold')
    
                #, URL = f"http://localhost:8501/?URL_DUNS={sibling_row['duns_number']}"
            dot.edge(str(specified_row['parent_id']), str(duns_id))

    #Formatting purposes
    if len(sibling_ids) >= 2:
        with dot.subgraph() as same_rank:
            same_rank.attr(rank='same')
            for duns_id in sibling_ids:
                same_rank.node(str(duns_id))

        for i in range(len(sibling_ids) - 1):
            dot.edge(str(sibling_ids[i]), str(sibling_ids[i + 1]), style="invis")

        dot.node("dummy_left", style="invis", width='0.01')
        dot.node("dummy_right", style="invis", width='0.01')
        dot.edge("dummy_left", str(sibling_ids[0]), style="invis")
        dot.edge(str(sibling_ids[-1]), "dummy_right", style="invis")

    if hidden_nodes_count_siblings > 0:
        dot.node("hidden_nodes_siblings", f"...and {hidden_nodes_count_siblings} more siblings", shape="ellipse", style="dashed, filled", fillcolor = 'gray83')
        dot.edge(str(specified_row['parent_id']), "hidden_nodes_siblings")

    ##

    if len(sibling_ids) > 3 or len(children) > 3:
        st.graphviz_chart(dot, use_container_width=True)
    else:
        left, center, right = st.columns([4, 4, 3])
        with center:
            st.graphviz_chart(dot)

    st.divider()


    if 'recently_searched' not in st.session_state:
        st.session_state.recently_searched = []

    if specified_duns and specified_duns not in st.session_state.recently_searched:
        st.session_state.recently_searched.append(specified_duns)






    col1, col2 = st.columns(2)

    if len(siblings) > 1:
        col1.markdown(
        f"<h3 style='color: #002496;'>All {len(siblings)-1} Siblings:</h3>", 
        unsafe_allow_html=True
    )
        col1.dataframe(df.filter(pl.col('duns_number').is_in(siblings[siblings['duns_number'] != specified_duns]['duns_number'].tolist())).select([
            'duns_number',
            'business_name',
            'tradestyle_name',
            'street_address',
            'city_name',
            'state_province_name',
            'country_name',
            'site_indicator'
        ]).to_pandas())

    if len(children) > 0:
        col2.markdown(
        f"<h3 style='color: #002496;'>All {len(children)} Children:</h3>", 
        unsafe_allow_html=True
    )
        col2.dataframe(df.filter(pl.col('duns_number').is_in(children['duns_number'].tolist())).select([
            'duns_number',
            'business_name',
            'tradestyle_name',
            'street_address',
            'city_name',
            'state_province_name',
            'country_name',
            'site_indicator'
        ]).to_pandas())

    if len(siblings) > 1 and len(children) > 0:
        st.divider()

    st.markdown(
        f"<h3 style='color: #002496;'>All {str(len(linkage_2))} Total Family Members:</h3>", 
        unsafe_allow_html=True
    )

    filtered_family = dataframe_explorer(df.filter(pl.col('duns_number').is_in(linkage_2['duns_number'].tolist())).select([
        'duns_number',
        'business_name',
        'tradestyle_name',
        'street_address',
        'city_name',
        'state_province_name',
        'country_name',
        'site_indicator'
    ]).to_pandas(), case=False)
    st.dataframe(filtered_family, use_container_width=True)


    st.divider()

    st.markdown(
        "<h3 style='color: #002496;'>Recently Searched:</h3>", 
        unsafe_allow_html=True
    )


    if specified_duns and specified_duns not in st.session_state.recently_searched:
        st.session_state.recently_searched.append(specified_duns)

    st.dataframe(df.filter(pl.col('duns_number').is_in(st.session_state.recently_searched)).select([
        'duns_number',
        'business_name',
        'tradestyle_name',
        'street_address',
        'city_name',
        'state_province_name',
        'country_name',
        'site_indicator'
    ]).to_pandas(), use_container_width=True)

    st.divider()

    st.markdown(
        "<h3 style='color: #002496;'>Search for Other Businesses:</h3>", 
        unsafe_allow_html=True
    )

    if 'user_duns' not in st.session_state:
        st.session_state['user_duns'] = []

    search_term = st.text_input("", placeholder="Business Name")
    search_term = search_term.upper()
    if search_term:
        result_df = df.filter(
            pl.col("business_name").str.contains(search_term, literal=True)
        )
        result_df = result_df.select(
            pl.col("duns_number"),
            pl.col("business_name"),
            pl.col("tradestyle_name"),
            pl.col("street_address"),
            pl.col("city_name"),
            pl.col("state_province_name"),
            pl.col("country_name"),
            pl.col("site_indicator"),
            pl.col("hierarchy_level")

        )
        st.markdown(
            f"<h5 style='color: #002496;'>Found {len(result_df)} matches containing {search_term}</h5>",
            unsafe_allow_html=True
            )
        filtered_temp = dataframe_explorer(result_df.to_pandas(), case=False)
        st.dataframe(filtered_temp)







    
