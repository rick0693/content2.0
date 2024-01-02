

import requests
from datetime import datetime
import sqlite3

class ConsultaNotasFiscaisTecmar:
    def __init__(self, cookies, headers):
        self.cookies = cookies
        self.headers = headers

    def get_nfe_data(self, nf_fiscal, user_agent):
        params = {
            'dias': '15',
            'numero': nf_fiscal,
        }

        headers = self.headers.copy()
        headers['User-Agent'] = user_agent

        max_attempts = 10
        for attempt in range(1, max_attempts + 1):
            try:
                response = requests.get(
                    'https://smonet.tecmartransportes.com.br/smonet/rest/restricted/nfes',
                    params=params,
                    cookies=self.cookies,
                    headers=headers,
                    timeout=(1, 3)
                )
                
                # Verificar se a resposta HTTP foi bem-sucedida (código 200)
                if response.status_code == 200:
                    try:
                        # Tentar decodificar o JSON
                        return response.json()
                    except ValueError as e:
                        print(f"Erro ao decodificar JSON: {e}")
    
            except requests.exceptions.RequestException as e:
                if attempt == max_attempts:
                    return None

        return None
    
    def format_date(self, date_str):
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%f%z")
            return date_obj.strftime('%d/%m/%Y')
        except ValueError:
            print(f"Erro ao formatar a data: {date_str}. Formato inválido.")
            return "Indisponível"

    def process_nfe_data(self, nf_fiscal, user_agent):
        nfe_data = self.get_nfe_data(nf_fiscal, user_agent)

        # Verificar se nfe_data é um JSON válido
        if nfe_data is not None:
            for item in nfe_data:
                # Tratamento de erro para a data de previsão de entrega
                try:
                    print(f"Previsão de Entrega: {self.format_date(item['previsaoEntrega'])}")
                except KeyError:
                    print("Data de previsão de entrega indisponível.")

                # Tratamento de erro para a data de entrega
                try:
                    print(f"Data de Entrega: {self.format_date(item['dataEntrega'])}")
                except KeyError:
                    print("Data de entrega indisponível.")

                print(f"Status: {item['status']}")
                print("-----")

# Conectar ao banco de dados
conn = sqlite3.connect('consultas.db')
cursor = conn.cursor()

# Consultar todas as linhas da tabela com a condição desejada
cursor.execute('SELECT Numero_Nota FROM consultas WHERE Transportadora = "TECMAR TRANSPORTES LTDA"')
numeros_notas = cursor.fetchall()

# Utilizando a classe para percorrer todas as notas fiscais
nf_processor = ConsultaNotasFiscaisTecmar(
    cookies = {
    'usuario': '%7B%22usuario%22%3A%22fotusenergia%22%2C%22senha%22%3A%22Fotus1*%22%2C%22bloqueado%22%3A%22%22%2C%22idTipo%22%3A2%2C%22codigoImagemLogoCliente%22%3A%22%22%2C%22codParceiro%22%3A-1%2C%22codVendedor%22%3A-1%2C%22apiKey%22%3A%22%22%7D',
    'exibirDados': 'true',
    'acessoNota': 'true',
    'acessoTitulo': 'true',
    'acessoEntregas': 'true',
    'aprovaPedido': 'false',
    'mostraDtRom': 'false',
    'imagemGed': 'true',
    'showOcorren': 'true',
    'acessoBaixaCte': 'false',
    'acessoBaixaNfe': 'true',
    'acessoSimulaFrete': 'false',
    'acessoWms': 'false',
    'exibirValorFrete': 'true',
    'acessoPedido': 'false',
    'fotoProd': 'false',
    'abaStatusMf': 'true',
    'showStatusNf': 'true',
    'showCampoEvento': 'true',
    'acessoColeta': 'false',
    'f5_cspm': '1234',
    'sessionId': '%22c0b8a3c8-1d4f-4d72-a56d-88fab9381721%22',
    '_ga': 'GA1.4.1780150315.1703556073',
    '_gid': 'GA1.4.1495214896.1703556073',
    'TS01f169a9': '01714172ae82425bb76129c530782762c353589e7919574c688f5eb393cc9634da44b8da360fc7db890f91559fdcdf68fd433d99fa',
    '_gat': '1',
    },


    headers = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
    'Authorization': 'c0b8a3c8-1d4f-4d72-a56d-88fab9381721',
    'Connection': 'keep-alive',
    # 'Cookie': 'usuario=%7B%22usuario%22%3A%22fotusenergia%22%2C%22senha%22%3A%22Fotus1*%22%2C%22bloqueado%22%3A%22%22%2C%22idTipo%22%3A2%2C%22codigoImagemLogoCliente%22%3A%22%22%2C%22codParceiro%22%3A-1%2C%22codVendedor%22%3A-1%2C%22apiKey%22%3A%22%22%7D; exibirDados=true; acessoNota=true; acessoTitulo=true; acessoEntregas=true; aprovaPedido=false; mostraDtRom=false; imagemGed=true; showOcorren=true; acessoBaixaCte=false; acessoBaixaNfe=true; acessoSimulaFrete=false; acessoWms=false; exibirValorFrete=true; acessoPedido=false; fotoProd=false; abaStatusMf=true; showStatusNf=true; showCampoEvento=true; acessoColeta=false; f5_cspm=1234; sessionId=%22c0b8a3c8-1d4f-4d72-a56d-88fab9381721%22; _ga=GA1.4.1780150315.1703556073; _gid=GA1.4.1495214896.1703556073; TS01f169a9=01714172ae387ba2bf4899f2b1dc4763c15136f2b4a7e1655a3d741120b887adcce8510aae6acfc6590aea71ada890015458867068; _gat=1; f5avr1140254715aaaaaaaaaaaaaaaa_cspm_=JGKJPOKEEKDOBBMEDEBBOCKLJKPHFMAAIFJDFCOCJOEAAONNIJJEPNDKGLPLFAOJEIKCJPHFFCJOEFNLKPDACEKMAMEBAFIEFDNIGMAJHBLKIJPIIMOKEPIHEEOJIPMO',
    'Referer': 'https://smonet.tecmartransportes.com.br/smonet/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-GPC': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Brave";v="120"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    }
)

for numero_nota in numeros_notas:
    numero_nota = numero_nota[0]  # Extrair o valor do tuplo
    
    # Consultar o status da nota no banco de dados
    cursor.execute('SELECT Status FROM consultas WHERE Numero_Nota = ?', (numero_nota,))
    status = cursor.fetchone()

    # Verificar se o status é 'ENTREGUE'
    if status and status[0] == 'Entregue':
        print(f"Nota Fiscal {numero_nota} já está entregue. Pulando para a próxima.")
        continue

    # Se o status não for 'ENTREGUE', prosseguir com a consulta no site
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
    print(f"\nConsultando Nota Fiscal: {numero_nota}")

    nfe_data = nf_processor.get_nfe_data(numero_nota, user_agent)

    # Verificar se nfe_data é um JSON válido
    if nfe_data is not None and nfe_data:
        # Atualizar o status para o valor fornecido pelo site após a consulta bem-sucedida
        novo_status = nfe_data[0].get('status', 'Indisponível')
        cursor.execute('UPDATE consultas SET Status = ? WHERE Numero_Nota = ?', (novo_status, numero_nota))
        conn.commit()

        # Imprimir as informações da nota
        nf_processor.process_nfe_data(numero_nota, user_agent)
    else:
        print(f"Não foi possível obter dados para a Nota Fiscal: {numero_nota}")

# Fechar a conexão com o banco de dados
conn.close()






