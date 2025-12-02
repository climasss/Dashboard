# import streamlit as st
# import serial
# import pandas as pd
# import serial.tools.list_ports
# import time

# # Configuração da página
# st.set_page_config(page_title="Monitor Serial", layout="wide")
# col1, col2 = st.columns([1, 4])
# with col1:
#     st.image("baja.webp", width=100)
# with col2:
#     st.title("📡 Monitoramento dos dados via LoRa CABIPAJA")

# # Cabeçalhos esperados
# colunas = [
#     "⛽Nivel de combustivel",
#     "💨Velocidade",
#     "🌡️Temperatura motor",
#     "🌡️Temperatura CVT",
#     "🛰️Odometro",
#     "🪫Bateria",
#     "🚨Farol",
#     "🛰️Sinal LoRa",
#     "⏱️Intervalo (s)"
# ]

# # Inicializa estados
# if "serial_conexao" not in st.session_state:
#     st.session_state.serial_conexao = None
# if "dados_recebidos" not in st.session_state:
#     st.session_state.dados_recebidos = []
# if "csv_dados" not in st.session_state:
#     st.session_state.csv_dados = b""  # CSV em bytes
# if "tempo_inicial" not in st.session_state:
#     st.session_state.tempo_inicial = time.time()

# # Entrada da porta
# porta_usuario = st.text_input("Informe a porta serial (ex: COM3, COM5):", value="COM7")
# if st.button("Conectar"):
#     try:
#         ser = serial.Serial(porta_usuario, 9600, timeout=None)
#         st.session_state.serial_conexao = ser
#         st.success(f"Conectado à {porta_usuario}")
#     except Exception as e:
#         st.error(f"Erro ao conectar: {e}")

# # Containers fixos
# tabela_area = st.empty()

# # Botão fixo fora do loop
# st.download_button(
#     label="📥 Baixar CSV atualizado",
#     data=st.session_state.csv_dados,
#     file_name="dados_lora.csv",
#     mime="text/csv",
#     key="botao_download_csv_fixo"
# )

# # Leitura automática após conexão
# if st.session_state.serial_conexao:
#     ser = st.session_state.serial_conexao
#     buffer = ""
#     tempo_inicial = st.session_state.tempo_inicial

#     for _ in range(10000000000000):
#         if ser.in_waiting > 0:
#             dados = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
#             buffer += dados

#             while '\r\n' in buffer:
#                 linha_completa, buffer = buffer.split('\r\n', 1)
#                 partes = linha_completa.strip().split(',')

#                 if len(partes) == 8:
#                     try:
#                         valores = [float(p.strip()) for p in partes]

#                         tempo_atual = time.time()
#                         tempo_total = round(tempo_atual - tempo_inicial, 2)

#                         # Adiciona o tempo como última coluna
#                         valores.append(tempo_total)
#                         st.session_state.dados_recebidos.append(valores)
#                     except ValueError:
#                         st.warning("Erro ao converter dados.")

#         # Atualiza tabela
#         df_temp = pd.DataFrame(st.session_state.dados_recebidos, columns=colunas)
#         tabela_area.dataframe(df_temp.tail(10), use_container_width=True)

#         # Atualiza CSV no session_state
#         if not df_temp.empty:
#             st.session_state.csv_dados = df_temp.to_csv(index=False).encode('utf-8')

#         time.sleep(1)

import streamlit as st
import serial
import pandas as pd
import serial.tools.list_ports
import time

# --- Configuração da Página ---
st.set_page_config(page_title="Monitor Serial Capibaja", layout="wide")

col1, col2 = st.columns([1, 4])
with col1:
    # Use uma imagem local ou um link de imagem online
    st.image("baja.webp", width=120)
with col2:
    st.title("📡 Monitoramento dos Dados via LoRa - CAPIBaja")

# --- Cabeçalhos dos Dados ---
colunas = [
    "⛽Nivel de combustivel", "💨Velocidade", "🌡️Temperatura motor",
    "🌡️Temperatura CVT", "🛰️Odometro", "🪫Bateria", "🚨Farol",
    "🛰️Sinal LoRa", "⏱️Intervalo (s)"
]

# --- Inicialização do Estado da Sessão (Session State) ---
if "serial_conexao" not in st.session_state:
    st.session_state.serial_conexao = None
if "dados_recebidos" not in st.session_state:
    st.session_state.dados_recebidos = []
if "tempo_inicial" not in st.session_state:
    st.session_state.tempo_inicial = None

# --- Controles de Conexão na Barra Lateral ---
st.sidebar.header("Configurações de Conexão")

# Melhoria: Detectar portas seriais automaticamente
available_ports = [p.device for p in serial.tools.list_ports.comports()]
porta_selecionada = st.sidebar.selectbox("Selecione a Porta Serial:", available_ports)

if st.sidebar.button("Conectar", type="primary"):
    if not st.session_state.serial_conexao:
        try:
            ser = serial.Serial(porta_selecionada, 9600, timeout=1)
            st.session_state.serial_conexao = ser
            st.session_state.tempo_inicial = time.time()
            st.session_state.dados_recebidos = [] # Limpa dados antigos ao conectar
            st.sidebar.success(f"Conectado à {porta_selecionada}")
        except Exception as e:
            st.sidebar.error(f"Erro ao conectar: {e}")
    else:
        st.sidebar.warning("Já conectado.")

if st.sidebar.button("Desconectar"):
    if st.session_state.serial_conexao:
        st.session_state.serial_conexao.close()
        st.session_state.serial_conexao = None
        st.session_state.tempo_inicial = None
        st.sidebar.info("Desconectado.")

# --- Área Principal de Exibição dos Dados ---
st.header("Últimos Dados Recebidos")
tabela_area = st.empty()
st.header("Controles de Dados")
col_botoes1, col_botoes2 = st.columns(2)

# O DataFrame é criado uma vez por execução do script
df = pd.DataFrame(st.session_state.dados_recebidos, columns=colunas)

# Exibe a tabela com os últimos 10 registros
tabela_area.dataframe(df.tail(10), use_container_width=True)

# Botão de Download
if not df.empty:
    csv_data = df.to_csv(index=False).encode('utf-8')
    col_botoes1.download_button(
        label="📥 Baixar CSV completo",
        data=csv_data,
        file_name=f"dados_lora_capibaja_{time.strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )

# Botão para limpar os dados
if col_botoes2.button("🗑️ Limpar Dados da Sessão"):
    st.session_state.dados_recebidos = []
    st.rerun()


# --- Lógica de Leitura e Atualização Automática ---
if st.session_state.serial_conexao:
    ser = st.session_state.serial_conexao
    buffer = ""
    
    # Lê todos os dados que estão esperando no buffer da serial
    if ser.in_waiting > 0:
        try:
            dados = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
            buffer += dados

            # Processa cada linha completa que foi lida
            while '\r\n' in buffer:
                linha_completa, buffer = buffer.split('\r\n', 1)
                partes = linha_completa.strip().split(',')

                if len(partes) == 8: # Espera 8 colunas do LoRa
                    try:
                        valores = [float(p.strip()) for p in partes]
                        
                        # Calcula o tempo e adiciona como a 9ª coluna
                        tempo_atual = time.time()
                        tempo_decorrido = round(tempo_atual - st.session_state.tempo_inicial, 2)
                        valores.append(tempo_decorrido)
                        
                        st.session_state.dados_recebidos.append(valores)

                    except ValueError:
                        # Ignora linhas que não podem ser convertidas para float
                        pass # Pode adicionar um st.warning aqui se quiser depurar
        except Exception as e:
            st.error(f"Erro durante a leitura da serial: {e}")

    # Força o script a rodar novamente para criar o efeito de "loop"
    time.sleep(1) # Intervalo de atualização da tela
    st.rerun()
