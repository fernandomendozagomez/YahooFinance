import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import io
from datetime import datetime

# === PALETAS DE COLORES PERSONALIZADAS ===
# Colores para gráficos - tema oscuro
DARK_COLORS = ['#194AFE', '#D43260', '#B1F5F1', '#6921B5', '#EA375D', '#55D9FB', '#B349D1']

# Colores para gráficos - tema claro
LIGHT_COLORS = ['#3B82F6', '#EF4444', '#FBBF24', '#10B981', '#8B5CF6', '#60A5FA', '#10B981']

# Colores para texto y etiquetas
TEXT_COLORS = {
    'primary': '#111827',
    'secondary': '#6B7280',
    'success': '#10B981',
    'error': '#EF4444',
    'info': '#2563EB',
    'accent': '#22C55E',
    'muted': '#9CA3AF'
}

# Configuración de la página
st.set_page_config(
    page_title="Análisis Financiero con Yahoo Finanzas",
    page_icon="📈",
    layout="wide"
)

# Encabezado con logo a la derecha
col1, col2 = st.columns([4, 1])
with col1:
    st.title("📊 Análisis Financiero Interactivo")
    st.markdown("Obtén datos de Yahoo Finanzas o carga tus propios archivos para analizar.")
with col2:
    st.image(
        "https://st.mextudia.com/wp-content/uploads/2023/06/Logo-Global-Open-University.jpg",
        width=150,
        caption="Global Open University"
    )

# --- Empresas populares ---
POPULAR_STOCKS = {
    "Apple (AAPL)": "AAPL",
    "Microsoft (MSFT)": "MSFT",
    "Amazon (AMZN)": "AMZN",
    "Google (GOOGL)": "GOOGL",
    "Tesla (TSLA)": "TSLA",
    "Meta (META)": "META",
    "NVIDIA (NVDA)": "NVDA",
    "Berkshire Hathaway (BRK-B)": "BRK-B",
    "JPMorgan Chase (JPM)": "JPM",
    "Visa (V)": "V",
}

# --- Barra lateral ---
st.sidebar.header("Opciones")

# Selector de tema
st.sidebar.markdown("---")
theme = st.sidebar.radio("🎨 Tema de colores", ["Claro", "Oscuro"], index=0)
COLOR_PALETTE = LIGHT_COLORS if theme == "Claro" else DARK_COLORS
st.sidebar.markdown("---")

# Selección de fuente de datos
data_source = st.sidebar.radio(
    "Fuente de datos",
    ("Yahoo Finanzas", "Cargar archivo local")
)

df = None

# === Opción 1: Yahoo Finanzas ===
if data_source == "Yahoo Finanzas":
    st.sidebar.subheader("Parámetros de Yahoo Finanzas")
    
    # Selección múltiple de empresas
    selected_stocks = st.sidebar.multiselect(
        "Selecciona una o más empresas",
        options=list(POPULAR_STOCKS.keys()),
        default=["Apple (AAPL)"]  # Apple por defecto
    )
    
    if not selected_stocks:
        st.sidebar.warning("⚠️ Por favor selecciona al menos una empresa.")
    
    # Períodos predefinidos
    PERIODS = {
        "1 día": "1d",
        "5 días": "5d",
        "1 mes": "1mo",
        "3 meses": "3mo",
        "6 meses": "6mo",
        "1 año": "1y",
        "2 años": "2y",
        "5 años": "5y",
        "10 años": "10y",
        "Año a la fecha (YTD)": "ytd",
        "Máximo histórico": "max"
    }
    
    period_label = st.sidebar.selectbox(
        "Período de datos",
        options=list(PERIODS.keys()),
        index=5  # 1 año por defecto
    )
    period = PERIODS[period_label]
    
    # Intervalos
    INTERVALS = {
        "1 minuto": "1m",
        "2 minutos": "2m",
        "5 minutos": "5m",
        "15 minutos": "15m",
        "30 minutos": "30m",
        "60 minutos": "60m",
        "90 minutos": "90m",
        "1 hora": "1h",
        "1 día": "1d",
        "5 días": "5d",
        "1 semana": "1wk",
        "1 mes": "1mo",
        "3 meses": "3mo"
    }
    
    interval_label = st.sidebar.selectbox(
        "Intervalo de datos",
        options=list(INTERVALS.keys()),
        index=8  # 1 día por defecto
    )
    interval = INTERVALS[interval_label]
    
    # Validación: intervalos intradía solo para períodos cortos
    if period in ["1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"] and interval in ["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h"]:
        st.sidebar.warning("⚠️ Los intervalos intradía (menos de 1 día) solo están disponibles para períodos ≤ 60 días. Se usará '1d' automáticamente.")
        interval = "1d"
    
    if st.sidebar.button("Obtener datos") and selected_stocks:
        try:
            with st.spinner(f"Descargando datos para {len(selected_stocks)} empresa(s)..."):
                # Descargar datos para múltiples empresas
                tickers = [POPULAR_STOCKS[stock] for stock in selected_stocks]
                
                if len(tickers) == 1:
                    # Una sola empresa
                    data = yf.download(tickers[0], period=period, interval=interval)
                    
                    if data.empty:
                        st.error("No se encontraron datos para este activo en el período seleccionado.")
                    else:
                        df = data.copy()
                        df.reset_index(inplace=True)
                        
                        # Aplanar columnas multiíndice a strings simples
                        df.columns = [
                            ' '.join(col).strip() if isinstance(col, tuple) else col
                            for col in df.columns
                        ]
                        
                        st.success(f"✅ Datos descargados para **{selected_stocks[0]}** ({period_label})")
                else:
                    # Múltiples empresas
                    data = yf.download(tickers, period=period, interval=interval, group_by='ticker')
                    
                    if data.empty:
                        st.error("No se encontraron datos para los activos seleccionados.")
                    else:
                        df = data.copy()
                        df.reset_index(inplace=True)
                        
                        # Aplanar columnas multiíndice
                        df.columns = [
                            ' '.join([str(c) for c in col]).strip() if isinstance(col, tuple) else str(col)
                            for col in df.columns
                        ]
                        
                        st.success(f"✅ Datos descargados para **{len(selected_stocks)}** empresas ({period_label})")
        except Exception as e:
            st.error(f"❌ Error al descargar datos: {e}")

# === Opción 2: Cargar archivo local ===
else:
    st.sidebar.subheader("Cargar archivo")
    uploaded_file = st.sidebar.file_uploader(
        "Elige un archivo (CSV, Excel)",
        type=["csv", "xlsx", "xls"]
    )
    
    if uploaded_file:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            st.success("✅ Archivo cargado exitosamente.")
        except Exception as e:
            st.error(f"❌ Error al leer el archivo: {e}")

# --- Procesamiento y visualización ---
if df is not None:
    with st.expander("🔍 Ver datos crudos"):
        st.dataframe(df)
    
    # Detectar columna de fecha de forma robusta
    date_col = None
    for col in df.columns:
        col_str = str(col).lower()
        if 'date' in col_str or 'time' in col_str:
            date_col = col
            break
    
    if date_col is None and 'Date' in df.columns:
        date_col = 'Date'
    elif date_col is None:
        df['Index'] = df.index
        date_col = 'Index'
    
    # Columnas numéricas
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    
    # Análisis exploratorio (tabla)
    st.subheader("📈 Estadísticas Descriptivas (Tabla)")
    st.write(df.describe())
    
    # --- SELECCIÓN MANUAL DE COLUMNAS ---
    st.subheader("🔧 Selección de Columnas")
    st.markdown("Selecciona manualmente qué columna usar para cada variable clave. Si no seleccionas nada, se intentará detectar automáticamente.")
    
    # Detectar columnas disponibles para cada tipo
    close_options = [col for col in numeric_cols if 'close' in str(col).lower()]
    high_options = [col for col in numeric_cols if 'high' in str(col).lower()]
    low_options = [col for col in numeric_cols if 'low' in str(col).lower()]
    open_options = [col for col in numeric_cols if 'open' in str(col).lower()]
    volume_options = [col for col in numeric_cols if 'volume' in str(col).lower()]
    
    # Selección manual
    selected_close = st.selectbox("Columna para Close", ["Auto-detectar"] + close_options, index=0)
    selected_high = st.selectbox("Columna para High", ["Auto-detectar"] + high_options, index=0)
    selected_low = st.selectbox("Columna para Low", ["Auto-detectar"] + low_options, index=0)
    selected_open = st.selectbox("Columna para Open", ["Auto-detectar"] + open_options, index=0)
    selected_volume = st.selectbox("Columna para Volume", ["Auto-detectar"] + volume_options, index=0)
    
    # Asignar columnas seleccionadas o detectadas
    close_col = selected_close if selected_close != "Auto-detectar" else close_options[0] if close_options else None
    high_col = selected_high if selected_high != "Auto-detectar" else high_options[0] if high_options else None
    low_col = selected_low if selected_low != "Auto-detectar" else low_options[0] if low_options else None
    open_col = selected_open if selected_open != "Auto-detectar" else open_options[0] if open_options else None
    volume_col = selected_volume if selected_volume != "Auto-detectar" else volume_options[0] if volume_options else None
    
    # Lista final de columnas disponibles para gráficos
    available_cols = [col for col in [close_col, high_col, low_col, open_col, volume_col] if col]
    
    if not available_cols:
        st.warning("❌ No se encontraron columnas clave para visualizar (Close, High, Low, Open, Volume).")
        st.info("💡 Revisa los nombres de las columnas o selecciona manualmente arriba.")
    else:
        st.success(f"✅ Seleccionadas: {available_cols}")
        
        # --- ESTADÍSTICOS Y GRÁFICAS ---
        st.subheader("📊 Estadísticos y Visualizaciones")
        
        if available_cols:
            # === Gráfico de barras con estadísticos ===
            stats_data = []
            for col in available_cols:
                stats = df[col].describe()
                stats_data.append({
                    "Columna": col,
                    "Mínimo": stats['min'],
                    "Q1": stats['25%'],
                    "Mediana": stats['50%'],
                    "Q3": stats['75%'],
                    "Máximo": stats['max']
                })
            
            stats_df = pd.DataFrame(stats_data)
            st.markdown("### 📊 Estadísticos Descriptivos (Min, Q1, Mediana, Q3, Max)")
            
            fig_bar = go.Figure()
            for i, row in stats_df.iterrows():
                fig_bar.add_trace(go.Bar(
                    x=['Mínimo', 'Q1', 'Mediana', 'Q3', 'Máximo'],
                    y=[row['Mínimo'], row['Q1'], row['Mediana'], row['Q3'], row['Máximo']],
                    name=row['Columna'],
                    marker_color=COLOR_PALETTE[i % len(COLOR_PALETTE)]
                ))
            
            fig_bar.update_layout(
                title="Estadísticos por Columna",
                xaxis_title="Estadístico",
                yaxis_title="Valor",
                barmode='group',
                legend_title="Columna",
                plot_bgcolor='#FFFFFF' if theme == "Claro" else '#1D1D3A',
                paper_bgcolor='#FFFFFF' if theme == "Claro" else '#070E0A',
                font=dict(color=TEXT_COLORS['primary'] if theme == "Claro" else '#B1F5F1')
            )
            st.plotly_chart(fig_bar, use_container_width=True)
            
            # === Gráfico de caja (boxplot) ===
            st.markdown("### 📦 Gráfico de Caja (Boxplot)")
            
            fig_box = go.Figure()
            for i, col in enumerate(available_cols):
                fig_box.add_trace(go.Box(
                    y=df[col],
                    name=col,
                    marker_color=COLOR_PALETTE[i % len(COLOR_PALETTE)],
                    line=dict(color=COLOR_PALETTE[i % len(COLOR_PALETTE)])
                ))
            
            fig_box.update_layout(
                title="Distribución de las variables clave",
                yaxis_title="Valor",
                xaxis_title="Variable",
                showlegend=False,
                plot_bgcolor='#FFFFFF' if theme == "Claro" else '#1D1D3A',
                paper_bgcolor='#FFFFFF' if theme == "Claro" else '#070E0A',
                font=dict(color=TEXT_COLORS['primary'] if theme == "Claro" else '#B1F5F1')
            )
            st.plotly_chart(fig_box, use_container_width=True)
            
            # === Gráficas de líneas ===
            st.markdown("### 📈 Gráficas de Línea")
            
            if volume_col:
                fig_lines = make_subplots(specs=[[{"secondary_y": True}]])
                
                for i, col in enumerate(available_cols):
                    if col == volume_col:
                        fig_lines.add_trace(
                            go.Scatter(
                                x=df[date_col],
                                y=df[col],
                                mode='lines',
                                name=col,
                                line=dict(color='#9CA3AF', dash='dot')
                            ),
                            secondary_y=True
                        )
                    else:
                        fig_lines.add_trace(
                            go.Scatter(
                                x=df[date_col],
                                y=df[col],
                                mode='lines',
                                name=col,
                                line=dict(color=COLOR_PALETTE[i % len(COLOR_PALETTE)], width=2)
                            ),
                            secondary_y=False
                        )
                
                fig_lines.update_layout(
                    title="Evolución de precios y volumen",
                    xaxis_title=str(date_col),
                    legend_title="Variables",
                    height=600,
                    plot_bgcolor='#FFFFFF' if theme == "Claro" else '#1D1D3A',
                    paper_bgcolor='#FFFFFF' if theme == "Claro" else '#070E0A',
                    font=dict(color=TEXT_COLORS['primary'] if theme == "Claro" else '#B1F5F1')
                )
                fig_lines.update_yaxes(title_text="Precio", secondary_y=False)
                fig_lines.update_yaxes(title_text="Volumen", secondary_y=True)
            else:
                fig_lines = go.Figure()
                
                for i, col in enumerate(available_cols):
                    fig_lines.add_trace(
                        go.Scatter(
                            x=df[date_col],
                            y=df[col],
                            mode='lines',
                            name=col,
                            line=dict(color=COLOR_PALETTE[i % len(COLOR_PALETTE)], width=2)
                        )
                    )
                
                fig_lines.update_layout(
                    title="Evolución de las variables disponibles",
                    xaxis_title=str(date_col),
                    yaxis_title="Valor",
                    legend_title="Variables",
                    height=600,
                    plot_bgcolor='#FFFFFF' if theme == "Claro" else '#1D1D3A',
                    paper_bgcolor='#FFFFFF' if theme == "Claro" else '#070E0A',
                    font=dict(color=TEXT_COLORS['primary'] if theme == "Claro" else '#B1F5F1')
                )
            
            st.plotly_chart(fig_lines, use_container_width=True)
    
    # --- Exportación de resultados ---
    st.subheader("📤 Exportar Resultados")
    
    col_export1, col_export2 = st.columns(2)
    
    with col_export1:
        st.markdown("#### Descargar como CSV")
        # Preparar CSV
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        csv_data = csv_buffer.getvalue()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        st.download_button(
            label="📥 Descargar CSV",
            data=csv_data,
            file_name=f"datos_financieros_{timestamp}.csv",
            mime="text/csv",
            help="Haz clic para descargar el archivo CSV"
        )
    
    with col_export2:
        st.markdown("#### Descargar como Excel")
        # Preparar Excel
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Datos Financieros')
        excel_data = excel_buffer.getvalue()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        st.download_button(
            label="📥 Descargar Excel",
            data=excel_data,
            file_name=f"datos_financieros_{timestamp}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            help="Haz clic para descargar el archivo Excel"
        )

else:
    st.info("👆 Selecciona una fuente de datos en la barra lateral para comenzar.")