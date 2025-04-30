
##streamlit run c:/Users/600318012/Coding/hierarchy/vscode_pk/streamlitv8.py
import logging
import re
## For some reason I need to reinstall all the packages so this line worked 'python -m pip install pandas'
import pandas as pd
import os
import graphviz as gv
os.environ["PATH"] += r";C:\Users\600318012\AppData\Roaming\Python\Python312\Scripts"
import streamlit as st
from math import floor
import textwrap
import polars as pl

##THIS IS GOING TO BE NEXT STEPS FOR DEVELOPMENT
##I am going to need to make multiple python files and coordinate how I am going to initialize each page and retain the data that I want to keep in between runs
##For now I am going to stick with the current generation of streamlitv7, and work on getting buy in from leadership





##FORMATTING PARAMETERS 
##-----------------------------------------------------------------------------------------------
display_limit = 4
business_name_limit = 35
##-----------------------------------------------------------------------------------------------


def wide_space_default():
    st.set_page_config(layout="wide")

wide_space_default()


if "page" not in st.session_state:
    st.session_state.page = "landing"

if "selected_value" not in st.session_state:
    st.session_state.selected_value = None
    

if st.session_state.page == "landing" and not st.session_state.selected_value:
    st.title("Welcome to the Hierarchy Viewer App")
    st.write("This app allows you to visualize hierarchical data interactively.")
    duns_number = st.text_input("Enter the DUNS Number:")
    if st.button("Proceed"):
        st.session_state.selected_value = duns_number
        st.session_state.page = "main"
    
    
    

if st.session_state.page == "main":
    chosen_hierarchy = st.session_state.selected_value
    if chosen_hierarchy:
    ##Initializing dataset
        df = pl.read_csv(
            r"C:\Users\600318012\Coding\hierarchy\outputs\dnb_export.csv",
            dtypes={col: pl.Utf8 for col in pl.read_csv(r"C:\Users\600318012\Coding\hierarchy\outputs\dnb_export.csv", n_rows=1).columns}
        )
        global_ultimate_duns = df.filter(df['duns_number'] == chosen_hierarchy)['global_ultimate_duns_number'].to_list()
        if global_ultimate_duns:
            df = df.filter(df['global_ultimate_duns_number'] == global_ultimate_duns[0])
        else:
            st.error("The entered DUNS number does not exist in the dataset.")
        linkage_data_polars = df.select([
            'duns_number',
            'duns_linkage',
            'business_name',
            'tradestyle_name',
            'hierarchy_level',
            'site_indicator'
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
        st.image(r"C:\Users\600318012\Coding\hierarchy\vscode_pk\1490x100_Market-Universe-Banner_3.png", use_container_width=True)
        st.markdown("""
            <h1 style='text-align: center; font-size: 48px; color: black; margin-top: 0;'>
                Hierarchy Viewer
            </h1>
        """, unsafe_allow_html=True)

        ##Logic to handle the duns number in the URL
        params = st.query_params
        duns_from_url = params.get("URL_DUNS")

        if "new_duns_number" not in st.session_state:
            if duns_from_url:
                st.session_state.new_duns_number = duns_from_url
            else:
                st.session_state.new_duns_number = None

        if "recently_searched" not in st.session_state:
            st.session_state.recently_searched = []
            if duns_from_url:
                st.session_state.recently_searched.append(duns_from_url)

        specified_duns = st.session_state.new_duns_number or linkage_2[(linkage_2['site_indicator'] == 'Global Ultimate') | (linkage_2['site_indicator'] == 'Target and Global Ultimate')]['duns_number'].iloc[0]

        def handle_input_change():
            new_value = st.session_state.input_temp
            st.session_state.new_duns_number = new_value
            if new_value not in st.session_state.recently_searched:
                st.session_state.recently_searched.append(new_value)

        st.markdown(
            "<h3 style='color: #002496;'>Enter Duns Number:</h3>", 
            unsafe_allow_html=True
        )
        st.text_input(
            "",
            key="input_temp",
            value=specified_duns,
            on_change=handle_input_change,
            placeholder="Type DUNS number here..."
        )



        ##Initializing hierarchy data of duns
        temp3 = linkage_2.loc[linkage_2['duns_number'] == specified_duns, 'duns_linkage'].values[0]
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
        dot.node(str(specified_row['duns_number']), node_label, color='#FECB00', style='filled', URL = f"http://localhost:8501/?URL_DUNS={specified_row['duns_number']}")
        children = linkage_2[linkage_2['parent_id'] == specified_duns]

        hidden_nodes_count_children = len(children) - display_limit

        ##Children Nodes - Not Formatted (Future)
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
                if child_row['site_indicator'] == 'Target and Global Ultimate' or child_row['site_indicator'] == 'Target Ultimate' or child_row['site_indicator'] == 'Global Ultimate':
                    dot.node(str(child_row['duns_number']), child_label, color = '#FECB00', fontcolor = '#0073CF', style = 'bold', URL = f"http://localhost:8501/?URL_DUNS={child_row['duns_number']}")
                else:
                    dot.node(str(child_row['duns_number']), child_label, color = '#0073CF', fontcolor = '#0073CF', style = 'bold', URL = f"http://localhost:8501/?URL_DUNS={child_row['duns_number']}")
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
                if str(parent_data.iloc[0]['site_indicator']) == 'Target and Global Ultimate' or str(parent_data.iloc[0]['site_indicator']) == 'Target Ultimate' or str(parent_data.iloc[0]['site_indicator']) == 'Global Ultimate':
                    dot.node(str(parent_data.iloc[0]['duns_number']), parent_label, color = '#FECB00', fontcolor = '#0073CF', style = 'bold', URL = f"http://localhost:8501/?URL_DUNS={parent_data.iloc[0]['duns_number']}")
                else:
                    dot.node(str(parent_data.iloc[0]['duns_number']), parent_label, color = '#0073CF', fontcolor = '#0073CF', style = 'bold', URL = f"http://localhost:8501/?URL_DUNS={parent_data.iloc[0]['duns_number']}")
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
                    dot.node(str(duns_id), sibling_label, color = '#FECB00', fontcolor = '#0073CF', style = 'bold', URL = f"http://localhost:8501/?URL_DUNS={sibling_row['duns_number']}")
                else:
                    dot.node(str(duns_id), sibling_label, color = '#0073CF', fontcolor = '#0073CF', style = 'bold', URL = f"http://localhost:8501/?URL_DUNS={sibling_row['duns_number']}")
                dot.edge(str(specified_row['parent_id']), str(duns_id))

        #Formatting purposes
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


        st.graphviz_chart(dot)


        if 'recently_searched' not in st.session_state:
            st.session_state.recently_searched = []

        if specified_duns and specified_duns not in st.session_state.recently_searched:
            st.session_state.recently_searched.append(specified_duns)

        st.markdown(
            "<h3 style='color: teal;'>Recently Searched Duns Numbers:</h3>", 
            unsafe_allow_html=True
        )


        if specified_duns and specified_duns not in st.session_state.recently_searched:
            st.session_state.recently_searched.append(specified_duns)

        st.dataframe(linkage_2[linkage_2['duns_number'].isin(st.session_state.recently_searched)][['duns_number', 'business_name', 'tradestyle_name', 'hierarchy_level', 'site_indicator', 'children_count', 'duns_linkage']], use_container_width=True)


        col1, col2 = st.columns(2)

        if hidden_nodes_count_siblings > 0:
            col1.markdown(
            "<h3 style='color: teal;'>Other Siblings:</h3>", 
            unsafe_allow_html=True
        )
            col1.dataframe(siblings.iloc[display_limit:][['duns_number', 'business_name', 'tradestyle_name', 'hierarchy_level', 'site_indicator', 'children_count', 'duns_linkage']])

        if hidden_nodes_count_children > 0:
            col2.markdown(
            "<h3 style='color: teal;'>Other Children:</h3>", 
            unsafe_allow_html=True
        )
            col2.dataframe(children.iloc[display_limit:][['duns_number', 'business_name', 'tradestyle_name', 'hierarchy_level', 'site_indicator', 'children_count', 'duns_linkage']])

        st.markdown(
            "<h3 style='color: teal;'>Full Family Tree: </h3>", 
            unsafe_allow_html=True
        )

        st.dataframe(linkage_2[['duns_number', 'business_name', 'tradestyle_name', 'hierarchy_level', 'site_indicator', 'children_count', 'duns_linkage']])