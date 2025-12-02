import streamlit as st
import serial
import time
import pandas as pd

st.set_page_config(page_title="Monitor Serial", layout="wide")
col1, col2 = st.columns([1, 4])
with col1:
    st.image("baja.webp", width=100)
with col2:
    st.title("📡 Monitoramento dos dados via LoRa CABIPAJA")

# Entrada da porta
porta_usuario = st.text_input("Informe a porta serial (ex: COM3, COM5):")
iniciar = st.button("Conectar e iniciar leitura")

# Área para exibir os dados
tabela_area = st.empty()

# Cabeçalhos esperados
colunas = ["⛽Nivel de combustivel", "💨Velocidade", "🌡️Temperatura motor", "🌡️Temperatura CVT", "🛰️Odometro", "🪫Bateria", "🛰️Sinal LoRa"]

# Se iniciar e porta válida
if iniciar and porta_usuario:
    try:
        ser = serial.Serial(porta_usuario, 9600, timeout=1)
        buffer = ""

        while True:
            if ser.in_waiting > 0:
                dados = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
                buffer += dados

                while '\r\n' in buffer:
                    linha_completa, buffer = buffer.split('\r\n', 1)
                    partes = linha_completa.strip().split(',')

                    if len(partes) == 7:
                        try:
                            valores = [float(p.strip()) for p in partes]
                            df = pd.DataFrame([valores], columns=colunas)
                            tabela_area.dataframe(df, use_container_width=True)
                        except ValueError:
                            pass

            time.sleep(0.1)

    except serial.SerialException as e:
        st.error(f"Erro ao conectar: {e}")
