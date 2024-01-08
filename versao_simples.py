import pandas as pd
import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd
import streamlit as st
import sqlite3
from datetime import datetime
import streamlit as st
import requests
import sqlite3
from time import sleep
import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import sqlite3



st.set_page_config(
    page_title="Dona sorte",
    page_icon=":robot_face:",
    layout="wide",
    initial_sidebar_state="expanded"
)


paginas_disponiveis = ["Consultas", "Inserir dados", "Dash", "TJ4","Coordenadas"]
pagina_selecionada = st.multiselect("Selecione a página", paginas_disponiveis)



# Função para a página 1
def pagina1():



    # Dados de login das empresas
    dados_login_empresas = {
        'atual': {
            'cnpj': '07117654000149',
            'senhas': ['FOTUS23','JEO@397'," ","FOTUS@","07117654",],
        },
    }

    # Lista de transportadoras para a seleção
    transportadoras_disponiveis = [ "CT DISTRIBUICAO E LOGISTICA LTDA", "FITLOG TRANSPORTES E LOGISTICA",
                                    "ATUAL CARGAS TRANSPORTES LTDA", "JEONCEL TRANSPORTES LTDA", "DIREÇÃO TRANSPORTES", "M V G TRANSPORTES LTDA"]

    with st.expander(f"Marque as transportadoras a serem selecionadas."):
        # Seleção da transportadora
        transportadoras_selecionadas = [st.checkbox(transportadora, key=transportadora) for transportadora in transportadoras_disponiveis]

    class SSW_Consulta:
        def __init__(self):
            self.headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'pt-BR,pt;q=0.5',
                'Cache-Control': 'max-age=0',
                'Connection': 'keep-alive',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Origin': 'https://ssw.inf.br',
                'Referer': 'https://ssw.inf.br/2/rastreamento?',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-User': '?1',
                'Sec-GPC': '1',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
                'sec-ch-ua': '"Brave";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
            }

        def extrair_data_especifica(self, soup):
            elementos_tdb = soup.find_all('p', {'class': 'tdb'})
            for elemento in elementos_tdb:
                match = re.search(r'\b\d{2}/\d{2}/\d{2}\b', elemento.get_text())
                if match:
                    data_formatada = datetime.strptime(match.group(), '%d/%m/%y').strftime('%d/%m/%Y')
                    return data_formatada
            return "Data não encontrada"

        def extrair_previsao_entrega(self, url):
            try:
                response_detalhes = requests.get(url)
                response_detalhes.raise_for_status()
                soup_detalhes = BeautifulSoup(response_detalhes.text, 'html.parser')
                dados_detalhes = soup_detalhes.find_all(class_='tdb')

                if dados_detalhes:
                    sexto_dado = dados_detalhes[7].text.strip()
                    data_match = re.search(r'\d{2}/\d{2}/\d{2}', sexto_dado)

                    if data_match:
                        previsao_entrega = data_match.group()

                        # Adicione o ano completo (se o ano for menor que 100, assume-se que é do século passado)
                        previsao_entrega = datetime.strptime(previsao_entrega, '%d/%m/%y').strftime('%d/%m/%Y')

                        return previsao_entrega
                    else:
                        return None
                else:
                    return None
            except requests.RequestException as e:
                return None

        def realizar_consulta(self, data_login, numero_nota):
            for senha in data_login['senhas']:
                data = {
                    'cnpj': data_login['cnpj'],
                    'NR': numero_nota,
                    'chave': senha,
                }

                try:
                    response = requests.post('https://ssw.inf.br/2/resultSSW', headers=self.headers, data=data)
                    response.raise_for_status()
                    soup = BeautifulSoup(response.text, 'html.parser')
                    info_block = soup.find('tr', {'style': 'background-color:#FFFFFF;cursor:pointer;'})

                    if info_block:
                        situacao_element = info_block.find('p', {'class': 'titulo'})
                        nf_element = info_block.find('p', {'class': 'tdb'})

                        url_completa = None
                        url_detalhes_element = info_block.find('a', {'class': 'email'})
                        if url_detalhes_element and 'onclick' in url_detalhes_element.attrs:
                            match = re.search(r"opx\('(.*?)'\)", url_detalhes_element['onclick'])
                            if match:
                                url_detalhes = match.group(1)
                                url_completa = f'https://ssw.inf.br{url_detalhes}'

                        if situacao_element and nf_element:
                            situacao_text = situacao_element.get_text(strip=True)
                            situacao_text = re.sub(r'\([^)]*\)', '', situacao_text)
                            nf_text = nf_element.get_text(strip=True)
                            data_situacao = self.extrair_data_especifica(soup)
                            Data_Status = data_situacao

                            # Se o status não indicar entrega, definir data_situacao como None
                            if situacao_text not in ["MERCADORIA ENTREGUE", "ENTREGA REALIZADA COM RESSALVA"]:
                                data_situacao = None

                            # Extrair a previsão de entrega independentemente da situação
                            previsao_entrega = self.extrair_previsao_entrega(url_completa)

                            # Imprimir resultados diretamente
                            #st.toast(f'Número da Nota: {numero_nota}')
            
                            # Atualizar o banco de dados com os novos dados
                            self.atualizar_banco_dados(numero_nota, situacao_text, data_situacao, previsao_entrega,
                                                    url_completa, Data_Status)

                            # Se a mercadoria foi entregue, interrompa as consultas
                            if situacao_text == "MERCADORIA ENTREGUE":
                                #st.write(f'Nota {numero_nota}: Mercadoria entregue. Interrupção das consultas.')
                                break

                except requests.RequestException as e:
                    print(f"Erro na requisição: {e}")

        def atualizar_banco_dados(self, numero_nota, situacao, data_situacao, previsao_entrega, url_completa, Data_Status):
            # Adicione a lógica para atualizar o banco de dados aqui
            try:
                formatted_data_status = (Data_Status.strftime('%d/%m/%Y') if isinstance(Data_Status, datetime) else Data_Status)

                cursor.execute('UPDATE consultas SET Data_Status=? WHERE Numero_Nota=?',
                            (formatted_data_status if Data_Status != "Data não encontrada" else None, numero_nota))
                conn.commit()  # Certifique-se de cometer a transação após a atualização

                cursor.execute('SELECT Data_Saida FROM consultas WHERE Numero_Nota=?', (numero_nota,))
                data_saida = cursor.fetchone()[0]

                if data_saida and isinstance(data_situacao, str) and data_situacao != "Data não encontrada":
                    # Converter as datas para objetos datetime
                    data_saida = datetime.strptime(data_saida, '%d/%m/%Y')
                    data_situacao = datetime.strptime(data_situacao, '%d/%m/%Y')

                    # Calcular o Leadtime em dias
                    leadtime = (data_situacao - data_saida).days

                    # Atualizar o banco de dados com os novos dados, incluindo o Leadtime
                    cursor.execute('UPDATE consultas SET Status=?, Data_Entrega=?, Previsao_Entrega=?, Leadtime=?, Situacao_Entrega=? WHERE Numero_Nota=?',
                                (situacao, data_situacao.strftime('%d/%m/%Y'), previsao_entrega, leadtime, url_completa, numero_nota))
                else:
                    # Atualizar o banco de dados com os novos dados, sem calcular o Leadtime
                    cursor.execute('UPDATE consultas SET Status=?, Data_Entrega=?, Previsao_Entrega=?, Leadtime=?,Situacao_Entrega=? WHERE Numero_Nota=?',
                                (situacao, data_situacao, previsao_entrega, None, url_completa, numero_nota))

                conn.commit()
            except sqlite3.Error as e:
                st.toast(f"Erro ao atualizar o banco de dados: {e}")



    # Conectar ao banco de dados
    conn = sqlite3.connect('consultas.db')
    cursor = conn.cursor()


    def main():
        # DataFrame vazio para armazenar os resultados
        colunas = ['id', 'Nro_Fotus', 'Data_Saida', 'MES', 'UF', 'Regiao', 'Numero_Nota', 'Valor_Total',
                'Valor_Frete', 'Peso', 'Perc_Frete', 'Transportadora', 'Dt_Faturamento', 'PLATAFORMA',
                'Previsao_Entrega', 'Data_Entrega', 'Data_Status', 'STATUS', 'Situacao_Entrega', 'Leadtime',
                'Integrador', 'CEP', 'Latitude', 'Longitude', 'Vendedor', 'Nome_cliente', 'Coordenador',
                'Cidade_Carga_Atual', 'Classificacao', 'km', 'Nome_Cidade', 'Vazio3', 'Vazio4', 'Vazio5']
        df_resultados = pd.DataFrame(columns=colunas)

        # Criar a interface do Streamlit
        st.title("Consulta de Notas")

        # Adicionar um botão para iniciar a consulta
        if st.button("Iniciar Consulta"):
            consulta_concluida = True  # Adicionado para verificar se todas as consultas foram concluídas
            for i, transportadora in enumerate(transportadoras_disponiveis):
                if transportadoras_selecionadas[i]:
                    cursor.execute(
                        f'SELECT Numero_Nota, Status FROM consultas WHERE '
                        f'(Status NOT IN ("MERCADORIA ENTREGUE", "ENTREGA REALIZADA COM RESSALVA") OR Status IS NULL) AND '
                        f'Transportadora = "{transportadora}"'
                    )
                    dados_notas = cursor.fetchall()

                    with st.expander(f"Dados Atualizados - {transportadora}"):
                        # Criar um espaço reservado para o DataFrame
                        dataframe_placeholder = st.empty()


                        col1, col2, col3, col4 = st.columns(4)
                        dica1 = col1.empty()  # Indicação
                        contagem_01 = col2.empty()  # Derrotas
                        contagem_11 = col3.empty()  # Vitórias
                        resultado1 = col4.empty()  # Resultado da aposta anterior

                    for dado_nota in dados_notas:
                        consulta_concluida = False  # Atualizado para False se houver pelo menos uma consulta
                        numero_nota, status_atual = dado_nota

                        # Loop através dos dados de login das empresas
                        for empresa, dados_login in dados_login_empresas.items():
                            consulta_ssw = SSW_Consulta()
                            consulta_ssw.realizar_consulta(dados_login, numero_nota)

                            # Adicionar resultados ao DataFrame
                            cursor.execute('SELECT * FROM consultas WHERE Numero_Nota=?', (numero_nota,))
                            resultado_consulta = cursor.fetchone()
                            df_resultado = pd.DataFrame([resultado_consulta], columns=colunas)
                            df_resultados = pd.concat([df_resultados, df_resultado], ignore_index=True)

                            # Contar o total de dados com 'MERCADORIA ENTREGUE'
                            total_entregues = df_resultados[df_resultados['STATUS'] == 'MERCADORIA ENTREGUE'].shape[0]
                            total_numero_nota = df_resultados['Numero_Nota'].nunique()
                            dica1.metric("'Notas consultadas:", total_numero_nota)
                            contagem_01.metric("Entregues", total_entregues)
                            # Exibir o DataFrame resultante até o momento no Streamlit
                            dataframe_placeholder.dataframe(df_resultados.tail(1000))

            # Verificar se todas as consultas foram concluídas
            if consulta_concluida:
                st.success("Todas as consultas foram concluídas com sucesso!")

            # Verificar se não houve retorno em nenhuma consulta
            if df_resultados.empty:
                st.warning("Nenhuma consulta retornou resultados. Verifique os parâmetros e tente novamente.")

        # Fechar a conexão com o banco de dados
        conn.close()


    # Executar o aplicativo
    if __name__ == '__main__':
        main()



# Função para a página 2
def pagina2():

    class ConsultaNotas:
        def __init__(self, db_filename='consultas.db'):
            self.db_filename = db_filename

            # Criar a tabela no banco de dados se não existir
            self._criar_tabela_consultas()

        def _criar_tabela_consultas(self):
            conn = sqlite3.connect(self.db_filename)
            cursor = conn.cursor()

        def _criar_tabela_consultas(self):
            with sqlite3.connect(self.db_filename) as conn:
                cursor = conn.cursor()

                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS consultas (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        Nro_Fotus TEXT,
                        Data_Saida TEXT,
                        MES TEXT,
                        UF TEXT,
                        Regiao TEXT,
                        Numero_Nota TEXT,
                        Valor_Total TEXT,
                        Valor_Frete TEXT,
                        Peso TEXT,
                        Perc_Frete TEXT,
                        Transportadora TEXT,
                        Dt_Faturamento TEXT,
                        PLATAFORMA TEXT,
                        Previsao_Entrega TEXT,
                        Data_Entrega TEXT,
                        Data_Status TEXT,
                        STATUS TEXT,
                        Situacao_Entrega TEXT,
                        Leadtime TEXT,
                        Integrador TEXT,
                        CEP TEXT,
                        Latitude TEXT,
                        Longitude TEXT,
                        Vendedor TEXT,
                        Nome_cliente TEXT,
                        Coordenador TEXT,
                        Cidade_Carga_Atual TEXT,
                        Classificacao TEXT,
                        km TEXT,
                        Nome_Cidade TEXT,
                        Vazio3 TEXT,
                        Vazio4 TEXT,
                        Vazio5 TEXT
                    )
                ''')

            conn.commit()
            conn.close()

        def salvar_resultados_consulta(self, df):
            conn = sqlite3.connect(self.db_filename)
            cursor = conn.cursor()

            for _, row in df.iterrows():
                # Verificar se o número da nota já existe no banco de dados
                cursor.execute('SELECT * FROM consultas WHERE Numero_Nota=?', (row['Numero_Nota'],))
                existing_row = cursor.fetchone()

                if not existing_row:
                    # Inserir o novo registro apenas se o número da nota não existir
                    cursor.execute('''
                        INSERT INTO consultas (
                            Nro_Fotus, Data_Saida, MES, UF, Regiao, Numero_Nota, Valor_Total,
                            Valor_Frete, Peso, Perc_Frete, Transportadora, Dt_Faturamento,
                            PLATAFORMA, Previsao_Entrega, Data_Entrega, Data_Status, STATUS,
                            Situacao_Entrega, Leadtime, Nome_Cidade
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?)
                    ''', (
                        row['Nro_Fotus'], row['Data_Saida'], row['MES'], row['UF'],
                        row['Regiao'], row['Numero_Nota'], row['Valor_Total'],
                        row['Valor_Frete'], row['Peso'], row['Perc_Frete'],
                        row['Transportadora'], row['Dt_Faturamento'],
                        row['PLATAFORMA'], row['Previsao_Entrega'], row['Data_Entrega'],
                        row['Data_Status'], row['STATUS'], row['Situacao_Entrega'], row['Leadtime'], row['Nome_Cidade']
                    ))
                else:
                    # Se o número da nota já existir, atualizar os campos necessários
                    cursor.execute('''
                        UPDATE consultas SET
                            STATUS=?, Situacao_Entrega=?, Leadtime=?
                        WHERE Numero_Nota=?
                    ''', (
                        row['STATUS'], row['Situacao_Entrega'], row['Leadtime'], row['Numero_Nota']
                    ))

            conn.commit()
            conn.close()

    # Instância da classe de consulta
    consulta_notas = ConsultaNotas()

    # Função para carregar os dados e realizar consultas
    @st.cache_data
    def load_and_process_data(uploaded_file):
        df = pd.read_excel(uploaded_file)

        # Ajustando o formato da coluna "Nro_Fotus" conforme sua expressão
        df['Nro_Fotus'] = df['Nro_Fotus'].apply(lambda x: f"0{str(int(x))[:-2]}-{str(int(x))[-2:]}" if not pd.isna(x) else "")

        # Corrigindo o nome da coluna após renomeação
        df['Numero_Nota'] = df['Numero_Nota'].astype(str).str.split('.').str[0].str.zfill(6)

    

        # Formatando as colunas de datas
        df['Data_Saida'] = pd.to_datetime(df['Data_Saida'], errors='coerce').dt.strftime('%d/%m/%Y')
        df['Previsao_Entrega'] = pd.to_datetime(df['Previsao_Entrega'], errors='coerce').dt.strftime('%d/%m/%Y')
        df['Data_Entrega'] = pd.to_datetime(df['Data_Entrega'], errors='coerce').dt.strftime('%d/%m/%Y')
        df['Data_Status'] = pd.to_datetime(df['Data_Status'], errors='coerce').dt.strftime('%d/%m/%Y')
        df['Dt_Faturamento'] = pd.to_datetime(df['Dt_Faturamento'], errors='coerce').dt.strftime('%d/%m/%Y')

        # Salvar resultados no banco de dados
        consulta_notas.salvar_resultados_consulta(df)

        return df


    # Upload da planilha
    uploaded_file = st.file_uploader("Escolha um arquivo XLSX", type="xlsx")

    # Botão para realizar as consultas após o upload
    if uploaded_file is not None:
        df = load_and_process_data(uploaded_file)

        # Exibir o DataFrame atualizado após o upload
        st.write(df)


def pagina3():


    import streamlit as st
    import sqlite3
    import pandas as pd
    import folium
    from folium.plugins import MarkerCluster
    from streamlit_folium import folium_static
    from geopy.geocoders import Nominatim

    # Função para obter coordenadas a partir do nome da cidade, estado e país
    def obter_coordenadas_por_cidade_estado(cidade, estado, pais, geolocator, max_retries=3):
        for _ in range(max_retries):
            try:
                endereco = f"{cidade}, {estado}, {pais}"
                location = geolocator.geocode(endereco)
                if location:
                    return location.latitude, location.longitude
            except Exception as e:
                st.warning(f"Erro ao obter coordenadas para {cidade}, {estado}: {str(e)}")
                st.warning(f"Tentando novamente em breve...")

        st.error(f"Não foi possível obter coordenadas para {cidade}, {estado} após {max_retries} tentativas.")
        return None

    # Interface do Streamlit
    st.title("Dashboard Logístico")

    # Conecta ao banco de dados SQLite
    conn = sqlite3.connect('consultas.db')
    cursor = conn.cursor()

    # Executa a consulta SQL para obter os dados da tabela consultas
    consulta_sql = "SELECT * FROM consultas;"
    resultados = pd.read_sql_query(consulta_sql, conn)

    # Filtra os resultados com base nos controles
    filtro_status = st.multiselect("Filtrar por Status:", ["Todas"] + resultados['STATUS'].unique().tolist())
    filtro_transportadora = st.multiselect("Filtrar por Transportadora:", resultados['Transportadora'].unique())

    if "Todas" in filtro_status:
        filtro_status = resultados['STATUS'].unique().tolist()

    if filtro_status:
        resultados = resultados[resultados['STATUS'].isin(filtro_status)]

    if filtro_transportadora:
        resultados = resultados[resultados['Transportadora'].isin(filtro_transportadora)]

    # Cria um mapa usando folium
    mymap = folium.Map(location=[-15.7801, -47.9292], zoom_start=4)

    # Adiciona um cluster de marcadores para agrupar pontos próximos
    marker_cluster = MarkerCluster().add_to(mymap)

    # Inicializa o geolocator
    geolocator = Nominatim(user_agent="geoapiExercises")

    # Exibe os marcadores para os resultados filtrados
    for index, row in resultados.iterrows():
        if row['Latitude'] is not None and row['Longitude'] is not None:
            coordenadas = (row['Latitude'], row['Longitude'])

            # Define o ícone com base no status
            icon_color = 'green' if row['STATUS'] == 'MERCADORIA ENTREGUE' else 'red'

            # Adiciona o marcador ao cluster
            folium.Marker(
                location=coordenadas,
                popup=f"{row['Nome_Cidade']}, {row['UF']} - {row['STATUS']}",
                icon=folium.Icon(color=icon_color)
            ).add_to(marker_cluster)

    # Exibe o mapa no Streamlit
    folium_static(mymap)

    # Adiciona métricas
    st.subheader("Métricas")
    total_registros = len(resultados)
    st.metric("Total de Registros", total_registros)

    # Adiciona gráficos no corpo principal
    st.subheader("Contagem por Status e Transportadora")

    # Divide a tela em duas colunas
    col1, col2 = st.columns(2)

    # Gráfico de barras para contagem por Status
    contagem_status = resultados['STATUS'].value_counts()
    col1.bar_chart(contagem_status)

    # Gráfico de barras para contagem por Transportadora
    contagem_transportadora = resultados['Transportadora'].value_counts()
    col2.bar_chart(contagem_transportadora)

    # Fecha a conexão com o banco de dados
    conn.close()



def pagina4():



    dataframe_placeholder = st.empty()

    class ConsultaNotasFiscais_TJ4:
        def __init__(self, db_path='consultas.db'):
            self.conn = sqlite3.connect(db_path)
            self.cursor = self.conn.cursor()
            self.numeros_notas = self._consultar_numeros_notas()
            self.results_df = pd.DataFrame()  # Inicializar um DataFrame vazio

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

        def _consultar_numeros_notas(self):
            self.cursor.execute('SELECT Numero_Nota FROM consultas WHERE Transportadora = "TJ4 TRANSPORTES EIRELI" AND (Status IS NULL OR Status != "MERCADORIA ENTREGUE")')
            return self.cursor.fetchall()

        def _consultar_nota_fiscal(self, numero_nota):
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
                    self._processar_dados_tracking(tracking, numero_nota)
            else:
                st.write(f"Erro na solicitação. Código de status: {response.status_code}")

        def _processar_dados_tracking(self, tracking, numero_nota):
            tracking_id = tracking.get("tracking", {}).get("id")
            codigo = tracking.get("tracking", {}).get("codigo")
            data_entrega = tracking.get("tracking", {}).get("dataEntrega")

            if data_entrega:
                try:
                    data_entrega_formatada = datetime.strptime(data_entrega, '%Y-%m-%dT%H:%M:%S%z').strftime('%d/%m/%Y')
                except ValueError:
                    data_entrega_formatada = None
            else:
                data_entrega_formatada = None

            lista_fases = tracking.get("listaTrackingFase", [])

            if lista_fases:
                lista_fases_ordenada = sorted(lista_fases, key=lambda x: x.get("dataExecucao"), reverse=True)
                ultima_fase = lista_fases_ordenada[0]

                sequencia = ultima_fase.get("sequencia")
                data_execucao = ultima_fase.get("dataExecucao")
                descricao_fase = ultima_fase.get("fase", {}).get("descricao")

                # Convert the date to the desired format
                data_execucao_formatada = datetime.strptime(data_execucao, '%Y-%m-%dT%H:%M:%S%z').strftime('%d/%m/%Y %H:%M:%S')

                results_dict = {
                    "Numero_Nota": numero_nota,
                    "Tracking_ID": tracking_id,
                    "Codigo": codigo,
                    "Data_Entrega": data_entrega_formatada,
                    "Sequencia": sequencia,
                    "Data_Execucao": data_execucao_formatada,
                    "Descricao_Fase": descricao_fase,
                }

                results_df_row = pd.DataFrame.from_dict(results_dict, orient='index').T
                self.results_df = pd.concat([self.results_df, results_df_row], ignore_index=True)

                # Display the information in a DataFrame
                dataframe_placeholder.dataframe(self.results_df)

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

                    # Calcular Leadtime
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

        def fechar_conexao(self):
            self.conn.close()

    def main():
        st.title('Consulta de Notas Fiscais - TJ4 Transportes EIRELI')

        consulta = ConsultaNotasFiscais_TJ4()

        if st.button('Realizar Consulta'):
            consulta.realizar_consulta()

        consulta.fechar_conexao()

    if __name__ == '__main__':
        main()
def pagina5():
    import sqlite3
    from geopy.geocoders import Nominatim
    import streamlit as st

    def obter_coordenadas_cidade(geolocator, cidade_nome, uf):
        try:
            location = geolocator.geocode(f"{cidade_nome}, {uf}")
            if location:
                return location.latitude, location.longitude
            else:
                return None
        except Exception as e:
            st.error(f"Erro ao obter coordenadas para {cidade_nome}, {uf}: {e}")
            return None

    def atualizar_coordenadas_banco():
        db_filename = 'consultas.db'
        geolocator = Nominatim(user_agent="consulta_notas")

        conn = sqlite3.connect(db_filename)
        cursor = conn.cursor()

        # Seleciona todas as linhas onde Latitude e Longitude são nulas
        cursor.execute('SELECT * FROM consultas WHERE Latitude IS NULL OR Longitude IS NULL')
        rows = cursor.fetchall()

        for row in rows:
            cidade_nome = row['Nome_Cidade']
            uf = row['UF']

            # Obter coordenadas da cidade
            coordenadas = obter_coordenadas_cidade(geolocator, cidade_nome, uf)

            if coordenadas:
                latitude, longitude = coordenadas
                # Atualizar as coordenadas no banco de dados
                cursor.execute('''
                    UPDATE consultas SET
                        Latitude=?, Longitude=?
                    WHERE Numero_Nota=?
                ''', (latitude, longitude, row['Numero_Nota']))

                st.success(f"Coordenadas atualizadas para {cidade_nome}, {uf}")

        conn.commit()
        conn.close()

    if __name__ == "__main__":
        st.title("Atualizar Coordenadas do Banco de Dados")
        st.text("Este script atualiza as coordenadas (Latitude e Longitude) do banco de dados.")

        if st.button("Atualizar Coordenadas"):
            atualizar_coordenadas_banco()


# Verifique a página selecionada e exiba o conteúdo correspondente
if "Consultas" in pagina_selecionada:
    pagina1()
if "Inserir dados" in pagina_selecionada:
    pagina2()

# Verifique a página selecionada e exiba o conteúdo correspondente
if "Dash" in pagina_selecionada:
    pagina3()
if "TJ4" in pagina_selecionada:
    pagina4()
if "Coordenadas" in pagina_selecionada:
    pagina5()
