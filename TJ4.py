import streamlit as st
import sqlite3
import requests
from datetime import datetime
import time
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import folium_static
from geopy.geocoders import Nominatim

class ConsultaNotasFiscais_TJ4:
    def __init__(self, db_path='consultas.db'):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.numeros_notas = self._consultar_numeros_notas()

        self.cookies = {
            'TS018608fa': '01a760ec21c50040e797b34e8debb9eed61e04a18d0575bcae881838cdc906e56e3b5a89fa8b7a15309c9c69c08e80dd16791b51df',
        }

        self.headers = {
            'authority': 'platform.senior.com.br',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'pt-BR,pt;q=0.7',
            'charset': 'UTF-8',
            'content-type': 'application/json',
            'externaluser': 'true',
            'origin': 'https://platform.senior.com.br',
            'referer': 'https://platform.senior.com.br/logistica-tck/tms/tck-frontend/',
            'sec-ch-ua': '"Brave";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'sec-gpc': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'x-tenant': 'frilog',
            'x-tenantdomain': 'frilog.com.br',
        }

        self.mymap = folium.Map(location=[-15.7801, -47.9292], zoom_start=4)
        self.marker_cluster = MarkerCluster().add_to(self.mymap)
        self.geolocator = Nominatim(user_agent="geoapiExercises")

    def _consultar_numeros_notas(self):
        self.cursor.execute('SELECT Numero_Nota FROM consultas WHERE Transportadora = "TJ4 TRANSPORTES EIRELI" AND (Status IS NULL OR Status != "MERCADORIA ENTREGUE")')
        return self.cursor.fetchall()

    def _obter_coordenadas(self, cidade, estado):
        endereco = f"{cidade}, {estado}, Brasil"
        location = self.geolocator.geocode(endereco)
        return (location.latitude, location.longitude) if location else None

    def _adicionar_marcador(self, coordenadas, cidade, estado):
        icon = folium.CustomIcon(icon_image='caminhão_entregue.png', icon_size=(30, 30))
        folium.Marker(
            location=coordenadas,
            popup=f"{cidade}, {estado}",
            icon=icon
        ).add_to(self.marker_cluster)

    def _consultar_nota_fiscal(self, numero_nota):
        st.write(f"\nConsultando Nota Fiscal: {numero_nota}")

        json_data = {
            'documento': numero_nota,
            'inscricaoFiscal': '07117654000149',
            'somenteFasesExecutadas': False,
            'pageRequest': {
                'offset': 0,
                'size': 10,
            },
        }

        response = requests.post(
            'https://platform.senior.com.br/t/senior.com.br/bridge/1.0/anonymous/rest/tms/tck/actions/externalTenantConsultaTracking',
            cookies=self.cookies,
            headers=self.headers,
            json=json_data,
        )

        if response.status_code == 200:
            data = response.json()
            lista_tracking = data.get("listaTracking", [])
            for tracking in lista_tracking:
                cidade = tracking.get("cidade")
                estado = tracking.get("estado")
                coordenadas = self._obter_coordenadas(cidade, estado)

                if coordenadas:
                    self._adicionar_marcador(coordenadas, cidade, estado)

                    # Atualiza o banco de dados com as coordenadas
                    self.cursor.execute("UPDATE consultas SET Latitude=?, Longitude=? WHERE Nome_Cidade=? AND UF=?", (coordenadas[0], coordenadas[1], cidade, estado))
                    self.conn.commit()

                    self._processar_dados_tracking(tracking, numero_nota)

                    # Adiciona um pequeno atraso para evitar problemas com a API de geocodificação
                    time.sleep(1)

    def _processar_dados_tracking(self, tracking, numero_nota):
        tracking_id = tracking.get("tracking", {}).get("id")
        codigo = tracking.get("tracking", {}).get("codigo")
        data_entrega = tracking.get("tracking", {}).get("dataEntrega")

        if data_entrega:
            try:
                data_entrega_formatada = datetime.strptime(data_entrega, '%Y-%m-%dT%H:%M:%S%z').strftime('%d/%m/%Y')
                st.write(f"Data de Entrega: {data_entrega_formatada}")
            except ValueError:
                st.write("Erro ao formatar a data de entrega.")
                data_entrega_formatada = None
        else:
            st.write("Data de Entrega: Não disponível")
            data_entrega_formatada = None

        lista_fases = tracking.get("listaTrackingFase", [])

        if lista_fases:
            lista_fases_ordenada = sorted(lista_fases, key=lambda x: x.get("dataExecucao"), reverse=True)
            ultima_fase = lista_fases_ordenada[0]

            sequencia = ultima_fase.get("sequencia")
            data_execucao = ultima_fase.get("dataExecucao")
            descricao_fase = ultima_fase.get("fase", {}).get("descricao")

            st.write(f"Status {descricao_fase}")
            conn = sqlite3.connect('consultas.db')
            cursor = conn.cursor()

            cursor.execute('SELECT * FROM consultas WHERE Numero_Nota=?', (numero_nota,))
            existing_record = cursor.fetchone()

            if existing_record:
                # Se o registro já existe, atualize as informações disponíveis
                if data_execucao:
                    # Converta data_execucao para um objeto datetime
                    data_execucao_datetime = datetime.strptime(data_execucao, '%Y-%m-%dT%H:%M:%S%z')
                    cursor.execute('UPDATE consultas SET STATUS=?, Data_Entrega=?, Previsao_Entrega=?, Situacao_Entrega=?, Data_Status=? WHERE Numero_Nota=?',
                                (descricao_fase, data_entrega_formatada, 'None', 'None', data_execucao_datetime.strftime('%d/%m/%Y'), numero_nota))
                else:
                    cursor.execute('UPDATE consultas SET STATUS=?, Data_Entrega=?, Previsao_Entrega=?, Situacao_Entrega=? WHERE Numero_Nota=?',
                                (descricao_fase, data_entrega_formatada, 'None', 'None', numero_nota))

                # Calcular Leadtime apenas se a descrição da fase for "MERCADORIA ENTREGUE"
                if descricao_fase == "MERCADORIA ENTREGUE":
                    cursor.execute('SELECT Data_Saida FROM consultas WHERE Numero_Nota=?', (numero_nota,))
                    data_saida_result = cursor.fetchone()

                    if data_saida_result:
                        data_saida = data_saida_result[0]

                        if data_saida:
                            try:
                                data_saida_datetime = datetime.strptime(data_saida, '%Y-%m-%d %H:%M:%S')
                            except ValueError:
                                data_saida_datetime = datetime.strptime(data_saida, '%d/%m/%Y')

                            if data_entrega_formatada:
                                data_entrega_datetime = datetime.strptime(data_entrega_formatada, '%d/%m/%Y')
                                leadtime = (data_entrega_datetime - data_saida_datetime).days
                                # Atualizar o registro no banco de dados
                                cursor.execute('UPDATE consultas SET Leadtime=? WHERE Numero_Nota=?', (leadtime, numero_nota))
                                # Commit para salvar as alterações
                                conn.commit()
            else:
                # Se o registro não existe, insira um novo registro
                if data_execucao:
                    # Converta data_execucao para um objeto datetime
                    data_execucao_datetime = datetime.strptime(data_execucao, '%Y-%m-%dT%H:%M:%S%z')
                    cursor.execute('INSERT INTO consultas (Numero_Nota, STATUS, Data_Entrega, Previsao_Entrega, Situacao_Entrega, Data_Status) VALUES (?, ?, ?, ?, ?, ?)',
                                (numero_nota, descricao_fase, data_entrega_formatada, 'None', 'None', data_execucao_datetime.strftime('%d/%m/%Y')))
                else:
                    cursor.execute('INSERT INTO consultas (Numero_Nota, STATUS, Data_Entrega, Previsao_Entrega, Situacao_Entrega, Data_Status) VALUES (?, ?, ?, ?, ?, ?)',
                                (numero_nota, descricao_fase, data_entrega_formatada, 'None', 'None', 'None'))

            conn.commit()
            conn.close()

    def realizar_consulta(self):
        for numero_nota in self.numeros_notas:
            numero_nota = numero_nota[0]
            self._consultar_nota_fiscal(numero_nota)

    def exibir_mapa(self):
        folium_static(self.mymap)

    def fechar_conexao(self):
        self.conn.close()

def main():
    st.title('Consulta de Notas Fiscais - TJ4 Transportes EIRELI')

    consulta = ConsultaNotasFiscais_TJ4()

    if st.button('Realizar Consulta'):
        consulta.realizar_consulta()

    st.subheader('Resultados da Consulta')

    for numero_nota in consulta.numeros_notas:
        numero_nota = numero_nota[0]
        st.write(f"Consulta para Nota Fiscal: {numero_nota}")
        # Adicione qualquer informação adicional que você queira exibir

    consulta.exibir_mapa()
    consulta.fechar_conexao()

if __name__ == '__main__':
    main()