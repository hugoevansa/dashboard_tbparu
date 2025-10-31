import streamlit as st
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import plotly.express as px
from matplotlib.colors import LinearSegmentedColormap
import json

st.set_page_config(layout='wide')

@st.cache_data
def load_data():
    return pd.read_excel('data.xlsx')

def format_number(x):
    return f'{x:,.0f}'
df = load_data()
d_map = gpd.read_file('gadm41_IDN_3.json')
d_map = d_map[d_map['NAME_1'] == 'JawaBarat']
d_map = d_map[d_map['NAME_2'] == 'KotaBandung']

with st.sidebar:
    # t = st.selectbox('Pilih Tahun', df['tahun'].unique().tolist().reverse())
    t = st.selectbox('Pilih Tahun', df['tahun'].unique().tolist()[::-1])


tab1, tab2, tab3 = st.tabs(['Main', 'Analisis Epidem', 'Coming soon'])
df = df[df['tahun'] == t]
df['kecamatan'] = df['kecamatan'].apply(lambda x: x.lower())
df['kecamatan'] = df['kecamatan'].astype(str).str.replace(' ', '', regex=False)

d_map['NAME_3'] = d_map['NAME_3'].apply(lambda x: x.lower())

merged = d_map.merge(df, left_on='NAME_3', right_on='kecamatan')

d_map = d_map[d_map['NAME_2'] == 'KotaBandung']

col = ['PASIEN DIOBATI (L)', 'PASIEN DIOBATI (P)', 'angka kematian']
jumlah_diobati_laki = df[col[0]].sum()
jumlah_diobati_perempuan = df[col[1]].sum()
jumlah_kematian = df[col[2]].sum()

piedf = pd.DataFrame({'Jenis Kelamin': ['Laki-laki', 'Perempuan'], 'Values': [jumlah_diobati_laki, jumlah_diobati_perempuan]})

with tab1:
    with st.container(border=True):
        # st.markdown('## Jumlah')
        with st.expander('Dataframe'):
            st.dataframe(df.set_index('kecamatan'))
        st.markdown("<h2 style='text-align:center;'>Jumlah</h2>", unsafe_allow_html=True)
        a1, a2, a3 = st.columns([1, 1, 1])
        with a1:
            with st.container(border=True):
                st.markdown('#### Pasien Diobati Laki')
                st.markdown(format_number(jumlah_diobati_laki))
        with a2:
            with st.container(border=True):
                st.markdown('#### Pasien Diobati Perempuan')
                st.markdown(format_number(jumlah_diobati_perempuan))
        with a3:
            with st.container(border=True):
                st.markdown('#### Kematian')
                st.markdown(format_number(jumlah_kematian))

        st.divider()
        # st.write(merged.iloc[:, -1].columns)
        merged_px = merged.copy()
        merged_px.set_index('NAME_3', inplace=True)
        geojson_data = json.loads(merged_px.to_json())
        for i, c in enumerate(st.columns([1, 1, 1])):
            with c:
                mer = merged_px.iloc[:, -3:]
                col_px = mer.columns[i]
                with st.container(border=True):
                    st.markdown(f'#### {col_px}')
                    fig = px.choropleth(
                        merged_px,
                        geojson=geojson_data,
                        locations=merged_px.index,
                        color=col_px,
                        hover_name=merged_px.index
                        )
                    fig.update_geos(fitbounds="locations", visible=False)
                    fig.update_layout(
                        margin=dict(l=0, r=0, t=0, b=0),
                        coloraxis_colorbar=dict(title='', thickness=10, len=0.6),
                        showlegend=True
                    )
                    # st.plotly_chart(fig, use_container_width=True, config={
                    #     'scrollZoom': False,
                    #     'displayModeBar': True
                    # })
                    # fig.update_layout(height=400, margin={"r":0,"t":0,"l":0,"b":0})
                    st.plotly_chart(fig, use_container_width=True)

        b1, b2 = st.columns([1, 1])
        with b1:
            with st.container(border=True):
                st.markdown("<h3 style='text-align:center;'>Proporsi Pasien Diobati</h3>", unsafe_allow_html=True)
                pie1 = px.pie(
                    piedf, values='Values', names="Jenis Kelamin",
                    color='Jenis Kelamin',
                    color_discrete_map={'Perempuan': "#ba2be6", 'Laki-laki': "#190aeb"},
                    hole=0.4
                )

                pie1.update_layout(height=500)
                st.plotly_chart(pie1, use_container_width=True)

        with b2:
            with st.container(border=True, vertical_alignment='center', height='stretch'):
                st.markdown("<h3 style='text-align:center;'>Bar Chart Pasien Diobati</h3>", unsafe_allow_html=True)
                st.bar_chart(df.set_index('kecamatan')[[col[0], col[1]]], stack=False)

with tab2:
    df = pd.read_excel("penduduk.xlsx")

    df['Prevalensi tb paru per 1000'] = (df['total_kasus'] / df['penduduk_2']) * 1000

    df['CFR tb paru (%)'] = (df['kematian'] / df['total_kasus']) * 100

    df['CMR tb paru'] = (df['kematian'] / df['penduduk_1']) * 1000

    final_df = df[['kecamatan','Prevalensi tb paru per 1000','CFR tb paru (%)','CMR tb paru']]

    # Nilai ekstrem
    prev_max = df.loc[df["Prevalensi tb paru per 1000"].idxmax()]
    prev_min = df.loc[df["Prevalensi tb paru per 1000"].idxmin()]
    cfr_max = df.loc[df["CFR tb paru (%)"].idxmax()]
    cfr_min = df.loc[df["CFR tb paru (%)"].idxmin()]
    cmr_max = df.loc[df["CMR tb paru"].idxmax()]
    cmr_min = df.loc[df["CMR tb paru"].idxmin()]

    st.markdown(f"""
    <h2 style="text-align:center; font-weight:800; margin-top:10px; margin-bottom:25px;">
    Analisis Epidemiologi Kota Bandung 2024 penyakit TB Paru
    </h2>

    <style>
    /* ===== GRID UTAMA ===== */
    .metric-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
    gap: 18px;
    justify-items: stretch;
    align-items: stretch;
    max-width: 1200px;
    margin: 0 auto 25px auto;
    padding: 0 15px;
    }}

    /* ===== BOX ===== */
    .metric-box {{
    border-radius: 9px;
    background-color: rgba(255, 255, 255, 0.05);
    box-shadow: 0 6px 15px rgba(0,0,0,0.10);
    padding: 18px 20px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    transition: all 0.25s ease;
    text-align: center;
    }}
    .metric-box:hover {{
    transform: translateY(-3px);
    box-shadow: 0 8px 20px rgba(0,0,0,0.18);
    }}

    /* ===== TEKS ===== */
    .metric-title {{
    font-size: 17px;
    font-weight: 700;
    color: #1E90FF;
    margin-bottom: 6px;
    }}
    .metric-value {{
    font-size: 34px;
    font-weight: 1000;
    color: #1E90FF;
    margin-bottom: 4px;
    }}
    .metric-sub {{
    color: #1E90FF;
    font-size: 14px;
    }}

    /* ===== SUBDATA ===== */
    .subrow {{
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-top: 8px;
    }}
    .subcol-left, .subcol-right {{
    width: 48%;
    }}
    .subtitle {{
    font-size: 12px;
    font-weight: 700;
    color: #1E90FF;
    margin-bottom: 2px;
    }}
    .subname {{
    font-size: 12px;
    font-weight: 400;
    color: #1E90FF;
    }}
    .subvalue {{
    font-size: 13px;
    font-weight: 700;
    color: #1E90FF;
    }}

    /* ===== DARK MODE OVERRIDE ===== */
    @media (prefers-color-scheme: dark) {{
    .metric-box {{
        background-color: #ffffff !important;
        border: 1px solid rgba(0,0,0,0.15) !important;
        box-shadow: 0 6px 18px rgba(255,255,255,0.15) !important;
    }}
    .metric-title,
    .metric-value,
    .metric-sub,
    .subtitle,
    .subname,
    .subvalue {{
        color: #0000FF !important;
    }}
    .metric-value {{
        color: #1E90FF !important;
    }}
    }}

    /* ===== RESPONSIVE ===== */
    @media (max-width: 1100px) {{
    .metric-grid {{
        grid-template-columns: repeat(2, 1fr);
    }}
    }}
    @media (max-width: 700px) {{
    .metric-grid {{
        grid-template-columns: 1fr;
    }}
    .metric-value {{
        font-size: 28px;
    }}
    }}
    </style>

    <!-- ===== KONTEN KOTAK ===== -->
    <div class="metric-grid">

    <div class="metric-box">
        <div class="metric-title">Prevalensi TB Paru per 1000 Penduduk</div>
        <div class="subrow">
        <div class="subcol-left" style="text-align:left;">
            <div class="subtitle">Tertinggi</div>
            <div class="subname">{prev_max['kecamatan']}</div>
            <div class="subvalue">{prev_max['Prevalensi tb paru per 1000']:.2f}</div>
        </div>
        <div class="subcol-right" style="text-align:right;">
            <div class="subtitle">Terendah</div>
            <div class="subname">{prev_min['kecamatan']}</div>
            <div class="subvalue">{prev_min['Prevalensi tb paru per 1000']:.2f}</div>
        </div>
        </div>
    </div>

    <div class="metric-box">
        <div class="metric-title">Case Fatality Rate (CFR)</div>
        <div class="subrow">
        <div class="subcol-left" style="text-align:left;">
            <div class="subtitle">Tertinggi</div>
            <div class="subname">{cfr_max['kecamatan']}</div>
            <div class="subvalue">{cfr_max['CFR tb paru (%)']:.2f}%</div>
        </div>
        <div class="subcol-right" style="text-align:right;">
            <div class="subtitle">Terendah</div>
            <div class="subname">{cfr_min['kecamatan']}</div>
            <div class="subvalue">{cfr_min['CFR tb paru (%)']:.2f}%</div>
        </div>
        </div>
    </div>

    <div class="metric-box">
        <div class="metric-title">Crude Mortality Rate</div>
        <div class="subrow">
        <div class="subcol-left" style="text-align:left;">
            <div class="subtitle">Tertinggi</div>
            <div class="subname">{cmr_max['kecamatan']}</div>
            <div class="subvalue">{cmr_max['CMR tb paru']:.2f}</div>
        </div>
        <div class="subcol-right" style="text-align:right;">
            <div class="subtitle">Terendah</div>
            <div class="subname">{cmr_min['kecamatan']}</div>
            <div class="subvalue">{cmr_min['CMR tb paru']:.2f}</div>
        </div>
        </div>
    </div>

    </div>
    """, unsafe_allow_html=True)

    st.write(final_df)