import streamlit as st
import serial
import pandas as pd
import time
from datetime import datetime

# Configuração da página
st.set_page_config(page_title="Monitor Serial", layout="wide")

# --- SIDEBAR ---
st.sidebar.title("Configurações")
porta_usuario = st.sidebar.text_input("Porta Serial (ex: COM6):", value="COM6")
btn_conectar = st.sidebar.button("Conectar Serial")

col1, col2 = st.columns([1, 4])
with col1:
    try:
        st.image("baja.webp", width=100)
    except:
        st.write("🏎️")
with col2:
    st.title("📡 Monitoramento dos dados via LoRa CABIPAJA")

# --- DEFINIÇÃO DAS COLUNAS ---
# Hora + 6 Dados do Arduino + Intervalo = 8 Colunas
colunas = [
    "🕒Hora",              # 0 (Gerado aqui)
    "💨Velocidade",         # 1 (LoRa)
    "🌡️Temperatura motor",  # 2 (LoRa)
    "🌡️Temperatura CVT",    # 3 (LoRa)
    "🛰️Odometro",           # 4 (LoRa)
    "🚨Vibracao",           # 5 (LoRa)
    "🛰️Sinal LoRa",         # 6 (LoRa)
    "⏲RPM",                 # 7 (LoRa)
    "⏱️Intervalo (s)"      # 8 (Gerado aqui)
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

# --- LOOP DE LEITURA DIRETA ---
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

                    # Limpezas básicas
                    if not linha_limpa: continue
                    if linha_limpa.startswith(','): linha_limpa = linha_limpa[1:]
                    
                    partes = linha_limpa.split(',')

                    try:
                        valores = [float(p.strip()) for p in partes if p.strip()]
                    except ValueError:
                        continue 

                    # --- LÓGICA SIMPLIFICADA (SEM ZERO FILL) ---
                    # Esperamos EXATAMENTE 7 valores do Arduino:
                    # [Vel, TempM, TempC, Odo, RPM, Vibra, RSSI]
                    
                    if len(valores) == 7:
                        # Gera dados de tempo
                        hora_atual = datetime.now().strftime("%H:%M:%S")
                        tempo_total = round(time.time() - tempo_inicial, 2)

                        # Monta a linha direto: Hora + 7 Valores + Tempo
                        linha_tabela = [hora_atual] + valores + [tempo_total]
                        
                        st.session_state.dados_recebidos.append(linha_tabela)
                    
                    # Se vier incompleto (ex: 5 dados), ele simplesmente ignora e espera o próximo pacote correto.

                # --- ATUALIZAÇÃO VISUAL ---
                df_temp = pd.DataFrame(st.session_state.dados_recebidos, columns=colunas)
                
                if not df_temp.empty:
                    # Tabela Invertida (Mais recente no topo)
                    df_invertido = df_temp.iloc[::-1]
                    tabela_area.dataframe(df_invertido.head(10), use_container_width=True)
                    
                    # Gráfico Completo
                    if variavel_selecionada and variavel_selecionada in df_temp.columns:
                        df_grafico = df_temp.set_index("⏱️Intervalo (s)")[[variavel_selecionada]]
                        grafico_area.line_chart(df_grafico)

                    # CSV
                    st.session_state.csv_dados = df_temp.to_csv(
                        index=False,
                        sep=';',          # separador brasileiro
                        decimal=',',      # decimal brasileiro
                        encoding='utf-8-sig'  # evita problema de acento no Excel
                    ).encode('utf-8-sig')
            
            time.sleep(0.05)
            
        except Exception as e:
            st.error(f"Erro: {e}")
            break
