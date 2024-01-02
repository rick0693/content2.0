import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import sqlite3

# Dados de login das empresas
dados_login_empresas = {
    'atual': {
        'cnpj': '07117654000149',
        'senhas': [' ', ' ', 'FOTUS23', 'FOTUS@'],
    },
}

import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import sqlite3

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
        data = {
            'cnpj': data_login['cnpj'],
            'NR': numero_nota,
            'chave': data_login['senhas'][0],
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
                    print(f'Número da Nota: {numero_nota}')
                    print(f'Status: {situacao_text}')
                    print(f'Data de Entrega: {data_situacao}')
                    print(f'Previsão de Entrega: {previsao_entrega}')
                    print(f'Link: {url_completa}')
                    print(f'Dado: {Data_Status}')
                    # Atualizar o banco de dados com os novos dados
                    self.atualizar_banco_dados(numero_nota, situacao_text, data_situacao, previsao_entrega, url_completa, Data_Status)

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
            print(f"Erro ao atualizar o banco de dados: {e}")

# Conectar ao banco de dados
conn = sqlite3.connect('consultas.db')
cursor = conn.cursor()

def main():
    
    # Consultar todas as linhas da tabela com status não indicando entrega
    cursor.execute('SELECT Numero_Nota, Status FROM consultas WHERE (Status NOT IN ("MERCADORIA ENTREGUE", "ENTREGA REALIZADA COM RESSALVA") OR Status IS NULL) AND Transportadora IN ("CT DISTRIBUICAO E LOGISTICA LTDA", "FITLOG TRANSPORTES E LOGISTICA", "ATUAL CARGAS TRANSPORTES LTDA", "JEONCEL TRANSPORTES LTDA","DIREÇÃO TRANSPORTES")')
    dados_notas = cursor.fetchall()

    # Loop através dos dados de nota
    for dado_nota in dados_notas:
        numero_nota, status_atual = dado_nota

        # Loop através dos dados de login das empresas
        for empresa, dados_login in dados_login_empresas.items():
            consulta_ssw = SSW_Consulta()
            consulta_ssw.realizar_consulta(dados_login, numero_nota)

            # Atualizar o status atual após a consulta
            cursor.execute('SELECT Status FROM consultas WHERE Numero_Nota=?', (numero_nota,))
            novo_status = cursor.fetchone()[0]

            # Verificar se a mercadoria foi entregue após a consulta
            if novo_status == "MERCADORIA ENTREGUE":
                print(f'Nota {numero_nota}: Mercadoria entregue. Interrupção das consultas.')
                break

    # Fechar a conexão com o banco de dados
    conn.close()

# Executar o aplicativo
if __name__ == '__main__':
    main()
