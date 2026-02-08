import streamlit as st
import serial
import pandas as pd
import serial.tools.list_ports
import time
from datetime import datetime
import plotly.express as px  # <--- IMPORTAÇÃO DO GRÁFICO NOVO

# Configuração da página
st.set_page_config(page_title="Monitor Serial", layout="wide")

# --- SIDEBAR ---
st.sidebar.title("Configurações")
porta_usuario = st.sidebar.text_input("Porta Serial (ex: COM6):", value="COM6")
btn_conectar = st.sidebar.button("Conectar Serial")

# Layout do Topo
col1, col2 = st.columns([1, 4])
with col1:
    try:
        st.image("baja.webp", width=100)
    except:
        st.write("🏎️")
with col2:
    st.title("📡 Monitoramento dos dados via LoRa CABIPAJA")

# --- DEFINIÇÃO DAS COLUNAS ---
colunas = [
    "🕒 Hora",              # 0
    "💨Velocidade",         # 1
    "🌡️Temperatura motor",  # 2
    "🌡️Temperatura CVT",    # 3
    "🛰️Odometro",           # 4
    "🚨Vibracao",           # 5
    "🛰️Sinal LoRa",         # 6
    "⏱️Intervalo (s)"      # 7
]

# Inicializa estados
if "serial_conexao" not in st.session_state:
    st.session_state.serial_conexao = None
if "dados_recebidos" not in st.session_state:
    st.session_state.dados_recebidos = []
if "csv_dados" not in st.session_state:
    st.session_state.csv_dados = b"" 
if "tempo_inicial" not in st.session_state:
    st.session_state.tempo_inicial = time.time()

# --- CONEXÃO ---
if btn_conectar:
    try:
        if st.session_state.serial_conexao:
            st.session_state.serial_conexao.close()
        ser = serial.Serial(porta_usuario, 9600, timeout=None)
        st.session_state.serial_conexao = ser
        st.sidebar.success(f"Conectado à {porta_usuario}")
        st.session_state.dados_recebidos = [] 
    except Exception as e:
        st.sidebar.error(f"Erro ao conectar: {e}")

# Seleção do Gráfico
opcoes_grafico = colunas[1:-1] 
variavel_selecionada = st.selectbox("📊 Selecione a variável para o gráfico:", options=opcoes_grafico)

# Placeholders
grafico_area = st.empty()
tabela_area = st.empty()

# Botão Download
st.download_button(
    label="📥 Baixar CSV atualizado",
    data=st.session_state.csv_dados,
    file_name="dados_lora.csv",
    mime="text/csv"
)

# --- LOOP DE LEITURA ---
if st.session_state.serial_conexao:
    ser = st.session_state.serial_conexao
    tempo_inicial = st.session_state.tempo_inicial
    buffer = ""

    while True:
        try:
            if ser.in_waiting > 0:
                dados = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
                buffer += dados

                while '\r\n' in buffer:
                    linha_completa, buffer = buffer.split('\r\n', 1)
                    linha_limpa = linha_completa.strip()

                    if not linha_limpa: continue
                    if linha_limpa.startswith(','): linha_limpa = linha_limpa[1:]
                    
                    partes = linha_limpa.split(',')

                    try:
                        valores = [float(p.strip()) for p in partes if p.strip()]
                    except ValueError:
                        continue 

                    # Aceita apenas pacotes com 6 valores exatos
                    if len(valores) == 6:
                        hora_atual = datetime.now().strftime("%H:%M:%S")
                        tempo_total = round(time.time() - tempo_inicial, 2)
                        
                        linha_tabela = [hora_atual] + valores + [tempo_total]
                        st.session_state.dados_recebidos.append(linha_tabela)

                # --- ATUALIZAÇÃO VISUAL ---
                df_temp = pd.DataFrame(st.session_state.dados_recebidos, columns=colunas)
                
                if not df_temp.empty:
                    # 1. Tabela
                    df_invertido = df_temp.iloc[::-1]
                    tabela_area.dataframe(df_invertido.head(10), use_container_width=True)
                    
                    # 2. GRÁFICO AVANÇADO (PLOTLY)
                    if variavel_selecionada and variavel_selecionada in df_temp.columns:
                        
                        # Cria o gráfico interativo
                        fig = px.line(
                            df_temp, 
                            x="⏱️Intervalo (s)", 
                            y=variavel_selecionada,
                            title=f"Evolução: {variavel_selecionada}",
                            markers=True, # Adiciona bolinhas nos pontos
                            template="plotly_dark" # Tema escuro para combinar
                        )
                        
                        # Personalização fina do visual
                        fig.update_traces(line_color='#00CC96', line_width=2) # Cor verde Bajan
                        fig.update_layout(
                            height=400, # Altura do gráfico
                            xaxis_title="Tempo decorrido (s)",
                            yaxis_title=variavel_selecionada,
                            margin=dict(l=20, r=20, t=40, b=20),
                            hovermode="x unified" # Mostra linha vertical ao passar mouse
                        )
                        
                        # Plota o gráfico no placeholder
                        grafico_area.plotly_chart(fig, use_container_width=True)

                    # 3. CSV
                    st.session_state.csv_dados = df_temp.to_csv(index=False).encode('utf-8')
            
            time.sleep(0.05)
            
        except Exception as e:
            st.error(f"Erro: {e}")
            break
