import sqlite3
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

class MiraTracking:

    def __init__(self):
        self.session = requests.Session()
        self.cookies = {}
        self.headers = {
            'authority': 'web.mira.com.br',
            'accept': '*/*',
            'accept-language': 'pt-BR,pt;q=0.5',
            'cache-control': 'no-cache',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'origin': 'https://web.mira.com.br',
            'referer': 'https://web.mira.com.br/',
            'sec-ch-ua': '"Brave";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'sec-gpc': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'x-microsoftajax': 'Delta=true',
            'x-requested-with': 'XMLHttpRequest',
        }

        self.conhecimento_selector = '#RadGridNF_ctl00__0 > td:nth-child(4)'
        self.previsao_selector = '#RadGridNF_ctl00__0 > td:nth-child(6)'

    def obter_dynamic_value(self):
        url = "https://web.mira.com.br/webmira/portalmira/login.aspx"
        params = {'usrId': 'tracking'}
        cookies = {}

        headers = {
            'authority': 'web.mira.com.br',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'accept-language': 'pt-BR,pt;q=0.6',
            'referer': 'https://www.mira.com.br/',
            'sec-ch-ua': '"Brave";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-site',
            'sec-fetch-user': '?1',
            'sec-gpc': '1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        }

        response = self.session.get(url, params=params, cookies=cookies, headers=headers)

        if response.status_code == 200:
            match = re.search(r'\(S\((.*?)\)\)', response.url)
            if match:
                dynamic_value = match.group(1)
                return dynamic_value
            else:
                print(f"Valor dinâmico não encontrado na URL {dynamic_value}.")
        else:
            print(f"A solicitação falhou com o código de status: {response.status_code}")

    def connect_to_database(self):
        conn = sqlite3.connect('consultas.db')
        cursor = conn.cursor()

        # Modifique a consulta para incluir a condição WHERE Transportadora = "MIRA OTM TRANSPORTES LTDA"
# Modifique a consulta para incluir a condição WHERE Transportadora = "MIRA OTM TRANSPORTES LTDA" e Status não é "MERCADORIA ENTREGUE"
        cursor.execute('SELECT Numero_Nota FROM consultas WHERE Transportadora = "MIRA OTM TRANSPORTES LTDA" AND (Status IS NULL OR Status != "MERCADORIA ENTREGUE")')


        resultados = cursor.fetchall()
        conn.close()
        return resultados


    def make_request(self, numero_nota):
        dynamic_value = self.obter_dynamic_value()
        data = {

            'RadScriptManager1': 'RadButtonAtualizarPanel|RadButtonAtualizar',
            'RadStyleSheetManager1_TSSM': ';Telerik.Web.UI, Version=2014.1.225.40, Culture=neutral, PublicKeyToken=121fae78165ba3d4:pt-BR:fe3df733-ee56-4563-8789-bc399360084a:ef4a543:aac1aeb7:fe53831e:8cee9284:ed057d30:9e1572d6:ed2942d4:92753c09:bc8339f7:45085116;Telerik.Web.UI.Skins, Version=2014.1.225.40, Culture=neutral, PublicKeyToken=121fae78165ba3d4:pt-BR:3dd8b356-632d-4a0a-b084-a130ce99deae:187c7316:c3a512b8:deef128f:f7cd01a9:d041fe4f:bcb61928:c5e84dda',
            'RadScriptManager1_TSM': ';;System.Web.Extensions, Version=4.0.0.0, Culture=neutral, PublicKeyToken=31bf3856ad364e35:pt-BR:f838b76e-3cda-4840-9a98-b7a7d0caf9ab:ea597d4b:b25378d2;Telerik.Web.UI, Version=2014.1.225.40, Culture=neutral, PublicKeyToken=121fae78165ba3d4:pt-BR:fe3df733-ee56-4563-8789-bc399360084a:16e4e7cd:86526ba7:874f8ea2:ed16cbdc:b7778d6c:f7645509:24ee1bba:7165f74:e330518b:1e771326:88144a7a:8e6f0d33:58366029:2003d0b8:c128760b:c8618e41:e4f8f289:1a73651d:333f8d94:92fe8ea0:fa31b949:19620875:f46195d3:490a9d4e:bd8f85e4;',
            'QsfFromDecorator_ClientState': '',
            'RadTextBoxCnpjCpf': '07117654000149',
            'RadTextBoxCnpjCpf_ClientState': '{"enabled":true,"emptyMessage":"Entre com CNPJ ou CPF","validationText":"07117654000149","valueAsString":"07117654000149","lastSetTextBoxValue":"07117654000149"}',
            'RadTextBoxNF': numero_nota,
            'RadTextBoxNF_ClientState': '{"enabled":true,"emptyMessage":"Nota Fiscal","validationText":"134076","valueAsString":"134076","lastSetTextBoxValue":"134076"}',
            'RadTextBoxControle': 'Nr.Controle Cliente',
            'RadTextBoxControle_ClientState': '{"enabled":true,"emptyMessage":"Nr.Controle Cliente","validationText":"","valueAsString":"","lastSetTextBoxValue":"Nr.Controle Cliente"}',
            'RadButtonAtualizar_ClientState': '',
            'RadTabStrip1_ClientState': '{"selectedIndexes":["0"],"logEntries":[],"scrollState":{}}',
            'RadGridNF$ctl00$ctl02$ctl03$FilterTextBox_DataEmissao': '',
            'RadGridNF$ctl00$ctl02$ctl03$FilterTextBox_Destinatario': '',
            'RadGridNF$ctl00$ctl02$ctl03$FilterTextBox_Conhecimento': '',
            'RadGridNF$ctl00$ctl02$ctl03$FilterTextBox_controle': '',
            'RadGridNF$ctl00$ctl02$ctl03$FilterTextBox_DT6_PRZENT': '',
            'RadGridNF$ctl00$ctl02$ctl03$FilterTextBox_TemplateColumn1': '',
            'RadGridNF_rfltMenu_ClientState': '',
            'RadGridNF_ClientState': '',
            'RadWindowComprovante_C_CancelButton_ClientState': '',
            'RadWindowComprovante_ClientState': '',
            'RadWindowDacte_C_RadButton2_ClientState': '',
            'RadWindowDacte_ClientState': '',
            'RadWindowFile_ClientState': '',
            'RadWindowDetalheNF_ClientState': '',
            'RadWindowManager1_ClientState': '',
            'RadWindowDetalheCTE_C_RadButton1_ClientState': '',
            'RadWindowDetalheCTE_ClientState': '',
            'RadWindowDetalheEDI_C_RadButton3_ClientState': '',
            'RadWindowDetalheEDI_ClientState': '',
            '__EVENTTARGET': 'RadButtonAtualizar',
            '__EVENTARGUMENT': '',
            '__VIEWSTATE': '/wEPDwUJMzIxMzM4MzY3D2QWAgIBD2QWOAIDD2QWAmYPFCsAAg8WBh4EVGV4dAUEU2lsax4TY2FjaGVkU2VsZWN0ZWRWYWx1ZWQeB1Zpc2libGVoZBAWFGYCAQICAgMCBAIFAgYCBwIIAgkCCgILAgwCDQIOAg8CEAIRAhICExYUFCsAAg8WBh8ABQVCbGFjax4FVmFsdWUFBUJsYWNrHghTZWxlY3RlZGhkZBQrAAIPFgYfAAUPQmxhY2tNZXRyb1RvdWNoHwMFD0JsYWNrTWV0cm9Ub3VjaB8EaGRkFCsAAg8WBh8ABQdEZWZhdWx0HwMFB0RlZmF1bHQfBGhkZBQrAAIPFgYfAAUER2xvdx8DBQRHbG93HwRoZGQUKwACDxYGHwAFBU1ldHJvHwMFBU1ldHJvHwRoZGQUKwACDxYGHwAFCk1ldHJvVG91Y2gfAwUKTWV0cm9Ub3VjaB8EaGRkFCsAAg8WBh8ABQpPZmZpY2UyMDA3HwMFCk9mZmljZTIwMDcfBGhkZBQrAAIPFgYfAAUPT2ZmaWNlMjAxMEJsYWNrHwMFD09mZmljZTIwMTBCbGFjax8EaGRkFCsAAg8WBh8ABQ5PZmZpY2UyMDEwQmx1ZR8DBQ5PZmZpY2UyMDEwQmx1ZR8EaGRkFCsAAg8WBh8ABRBPZmZpY2UyMDEwU2lsdmVyHwMFEE9mZmljZTIwMTBTaWx2ZXIfBGhkZBQrAAIPFgYfAAUHT3V0bG9vax8DBQdPdXRsb29rHwRoZGQUKwACDxYGHwAFBFNpbGsfAwUEU2lsax8EZ2RkFCsAAg8WBh8ABQZTaW1wbGUfAwUGU2ltcGxlHwRoZGQUKwACDxYGHwAFFVNpdGVmaW5pdHkgKE9ic29sZXRlKR8DBQpTaXRlZmluaXR5HwRoZGQUKwACDxYGHwAFBlN1bnNldB8DBQZTdW5zZXQfBGhkZBQrAAIPFgYfAAUHVGVsZXJpax8DBQdUZWxlcmlrHwRoZGQUKwACDxYGHwAFBVZpc3RhHwMFBVZpc3RhHwRoZGQUKwACDxYGHwAFBVdlYjIwHwMFBVdlYjIwHwRoZGQUKwACDxYGHwAFB1dlYkJsdWUfAwUHV2ViQmx1ZR8EaGRkFCsAAg8WBh8ABQhXaW5kb3dzNx8DBQhXaW5kb3dzNx8EaGRkDxYUZmZmZmZmZmZmZmZmZmZmZmZmZmYWAQV3VGVsZXJpay5XZWIuVUkuUmFkQ29tYm9Cb3hJdGVtLCBUZWxlcmlrLldlYi5VSSwgVmVyc2lvbj0yMDE0LjEuMjI1LjQwLCBDdWx0dXJlPW5ldXRyYWwsIFB1YmxpY0tleVRva2VuPTEyMWZhZTc4MTY1YmEzZDQWLGYPDxYEHghDc3NDbGFzcwUJcmNiSGVhZGVyHgRfIVNCAgJkZAIBDw8WBB8FBQlyY2JGb290ZXIfBgICZGQCAg8PFgYfAAUFQmxhY2sfAwUFQmxhY2sfBGhkZAIDDw8WBh8ABQ9CbGFja01ldHJvVG91Y2gfAwUPQmxhY2tNZXRyb1RvdWNoHwRoZGQCBA8PFgYfAAUHRGVmYXVsdB8DBQdEZWZhdWx0HwRoZGQCBQ8PFgYfAAUER2xvdx8DBQRHbG93HwRoZGQCBg8PFgYfAAUFTWV0cm8fAwUFTWV0cm8fBGhkZAIHDw8WBh8ABQpNZXRyb1RvdWNoHwMFCk1ldHJvVG91Y2gfBGhkZAIIDw8WBh8ABQpPZmZpY2UyMDA3HwMFCk9mZmljZTIwMDcfBGhkZAIJDw8WBh8ABQ9PZmZpY2UyMDEwQmxhY2sfAwUPT2ZmaWNlMjAxMEJsYWNrHwRoZGQCCg8PFgYfAAUOT2ZmaWNlMjAxMEJsdWUfAwUOT2ZmaWNlMjAxMEJsdWUfBGhkZAILDw8WBh8ABRBPZmZpY2UyMDEwU2lsdmVyHwMFEE9mZmljZTIwMTBTaWx2ZXIfBGhkZAIMDw8WBh8ABQdPdXRsb29rHwMFB091dGxvb2sfBGhkZAINDw8WBh8ABQRTaWxrHwMFBFNpbGsfBGdkZAIODw8WBh8ABQZTaW1wbGUfAwUGU2ltcGxlHwRoZGQCDw8PFgYfAAUVU2l0ZWZpbml0eSAoT2Jzb2xldGUpHwMFClNpdGVmaW5pdHkfBGhkZAIQDw8WBh8ABQZTdW5zZXQfAwUGU3Vuc2V0HwRoZGQCEQ8PFgYfAAUHVGVsZXJpax8DBQdUZWxlcmlrHwRoZGQCEg8PFgYfAAUFVmlzdGEfAwUFVmlzdGEfBGhkZAITDw8WBh8ABQVXZWIyMB8DBQVXZWIyMB8EaGRkAhQPDxYGHwAFB1dlYkJsdWUfAwUHV2ViQmx1ZR8EaGRkAhUPDxYGHwAFCFdpbmRvd3M3HwMFCFdpbmRvd3M3HwRoZGQCBQ8PFgIeElJlc29sdmVkUmVuZGVyTW9kZQspclRlbGVyaWsuV2ViLlVJLlJlbmRlck1vZGUsIFRlbGVyaWsuV2ViLlVJLCBWZXJzaW9uPTIwMTQuMS4yMjUuNDAsIEN1bHR1cmU9bmV1dHJhbCwgUHVibGljS2V5VG9rZW49MTIxZmFlNzgxNjViYTNkNAEWAh4Fc3R5bGUFDWRpc3BsYXk6bm9uZTtkAgsPZBYCZg9kFgICAQ8PFgQfBQUbcmZkVmFsaWRhdGlvblN1bW1hcnlDb250cm9sHwYCAmRkAg8PEA8WAh8CaGRkFgFmZAIRDxAPFgIfAmhkZGRkAhMPZBYCAgEPFCsAAg8WBh8ABQdDbGllbnRlHgtfIURhdGFCb3VuZGcfAmhkEBYDZgIBAgIWAxQrAAIPFgQfAAUHQ2xpZW50ZR8DBQExZGQUKwACDxYEHwAFCVJlbWV0ZW50ZR8DBQEyZGQUKwACDxYEHwAFDERlc3RpbmF0YXJpbx8DBQEzZGQPFgNmZmYWAQV3VGVsZXJpay5XZWIuVUkuUmFkQ29tYm9Cb3hJdGVtLCBUZWxlcmlrLldlYi5VSSwgVmVyc2lvbj0yMDE0LjEuMjI1LjQwLCBDdWx0dXJlPW5ldXRyYWwsIFB1YmxpY0tleVRva2VuPTEyMWZhZTc4MTY1YmEzZDQWCmYPDxYEHwUFCXJjYkhlYWRlch8GAgJkZAIBDw8WBB8FBQlyY2JGb290ZXIfBgICZGQCAg8PFgQfAAUHQ2xpZW50ZR8DBQExZGQCAw8PFgQfAAUJUmVtZXRlbnRlHwMFATJkZAIEDw8WBB8ABQxEZXN0aW5hdGFyaW8fAwUBM2RkAhcPFCsACA8WCB4MRW1wdHlNZXNzYWdlBRVFbnRyZSBjb20gQ05QSiBvdSBDUEYfBwsrBAEeDUxhYmVsQ3NzQ2xhc3MFB3JpTGFiZWwfAAUOMDcxMTc2NTQwMDAxNDlkFggeBVdpZHRoGwAAAAAAwGxAAQAAAB4KUmVzaXplTW9kZQspclRlbGVyaWsuV2ViLlVJLlJlc2l6ZU1vZGUsIFRlbGVyaWsuV2ViLlVJLCBWZXJzaW9uPTIwMTQuMS4yMjUuNDAsIEN1bHR1cmU9bmV1dHJhbCwgUHVibGljS2V5VG9rZW49MTIx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BQtEYXRhRW1pc3NhbxQrAAUWBB8QAgQeCERhdGFUeXBlGSsCZGRkBQxEZXN0aW5hdGFyaW8UKwAFFgQfEAIFHxEZKwJkZGQFDENvbmhlY2ltZW50bxQrAAUWBB8QAgYfERkrAmRkZAUIY29udHJvbGUUKwAFFgQfEAIHHxEZKwJkZGQFCkRUNl9QUlpFTlQUKwAFFgIfEAIIZGRkBQ9UZW1wbGF0ZUNvbHVtbjEUKwAFFgQfEAIJHwJoZGRkBQtDb2x1bW5EYWN0ZRQrAAUWBB8QAgofAmhkZGQFCUNvbHVtblhtbBQrAAUWBB8QAgsfAmhkZGQFEUNvbHVtbkNvbXByb3ZhbnRlFCsABRYEHxACDB8CaGRkZAUJQ29sdW1uRWRpZGUUKwAACyl5VGVsZXJpay5XZWIuVUkuR3JpZENoaWxkTG9hZE1vZGUsIFRlbGVyaWsuV2ViLlVJLCBWZXJzaW9uPTIwMTQuMS4yMjUuNDAsIEN1bHR1cmU9bmV1dHJhbCwgUHVibGljS2V5VG9rZW49MTIxZmFlNzgxNjViYTNkNAE8KwAHAAspdFRlbGVyaWsuV2ViLlVJLkdyaWRFZGl0TW9kZSwgVGVsZXJpay5XZWIuVUksIFZlcnNpb249MjAxNC4xLjIyNS40MCwgQ3VsdHVyZT1uZXV0cmFsLCBQdWJsaWNLZXlUb2tlbj0xMjFmYWU3ODE2NWJhM2Q0ARYCHgRfZWZzZGQWEh4MX2lzZmx0cml0bWV4aB4IRGF0YUtleXMWAB4EX2hsbQsrBgEfDwIBHgVfIUNJUxcAHgpEYXRhTWVtYmVyZR8JZx4USXNCb3VuZFRvRm9yd2FyZE9ubHloHgVfcWVsdBkpZ1N5c3RlbS5EYXRhLkRhdGFSb3dWaWV3LCBTeXN0ZW0uRGF0YSwgVmVyc2lvbj00LjAuMC4wLCBDdWx0dXJlPW5ldXRyYWwsIFB1YmxpY0tleVRva2VuPWI3N2E1YzU2MTkzNGUwODkUKwAEDwIDAgMUKwACZGQUKwACZGQUKwACZGRmFgZmDxQrAAMPZBYCHwgFC3dpZHRoOjEwMCU7ZGRkAgEPFgUUKwACDxYSHxNoHxQWAB8VCysGAR8PAgEfFhcAHxdlHwlnHxhoHxkZKwhkFwQFCF8hUENvdW50AgEFBl8hRFNJQwIBBRBDdXJyZW50UGFnZUluZGV4ZgULXyFJdGVtQ291bnQCARYCHgNfc2UWAh4CX2NmZBYLZGRkZGRkZGRkZGQWAmdnFgJmD2QWCGYPZBYIZg8PFgYfBQUIIHJnUGFnZXIfBgICHwJoZBYCZg8PFgIeCkNvbHVtblNwYW4CB2QWAmYPZBYCAgEPZBYCZg9kFghmD2QWBGYPDxYCHhFVc2VTdWJtaXRCZWhhdmlvcmhkZAICDw8WAh8daGRkAgEPZBYCZg8PFgQfBQUNcmdDdXJyZW50UGFnZR8GAgJkZAICD2QWBGYPDxYCHx1oZGQCAw8PFgIfHWhkZAIDDw8WBB8FBRByZ1dyYXAgcmdBZHZQYXJ0HwYCAmQWAgIBDxQrAAIPFhoeEUVuYWJsZUFyaWFTdXBwb3J0aB4TRW5hYmxlRW1iZWRkZWRTa2luc2ceGVJlZ2lzdGVyV2l0aFNjcmlwdE1hbmFnZXJnHwlnHhVFbmFibGVFbWJlZGRlZFNjcmlwdHNnHgxUYWJsZVN1bW1hcnllHwYCgAIfAWQfDBsAAAAAAABHQAEAAAAeHEVuYWJsZUVtYmVkZGVkQmFzZVN0eWxlc2hlZXRnHgpJbnB1dFRpdGxlZR4cT25DbGllbnRTZWxlY3RlZEluZGV4Q2hhbmdlZAUuVGVsZXJpay5XZWIuVUkuR3JpZC5DaGFuZ2VQYWdlU2l6ZUNvbWJvSGFuZGxlch4MVGFibGVDYXB0aW9uBRBQYWdlU2l6ZUNvbWJvQm94ZA8UKwABFCsAAg8WBh8ABQIxMB8DBQIxMB8EZxYCHhBvd25lclRhYmxlVmlld0lkBQ9SYWRHcmlkTkZfY3RsMDBkDxQrAQFmFgEFd1RlbGVyaWsuV2ViLlVJLlJhZENvbWJvQm94SXRlbSwgVGVsZXJpay5XZWIuVUksIFZlcnNpb249MjAxNC4xLjIyNS40MCwgQ3VsdHVyZT1uZXV0cmFsLCBQdWJsaWNLZXlUb2tlbj0xMjFmYWU3ODE2NWJhM2Q0FgZmDw8WBB8FBQlyY2JIZWFkZXIfBgICZGQCAQ8PFgQfBQUJcmNiRm9vdGVyHwYCAmRkAgIPDxYGHwAFAjEwHwMFAjEwHwRnFgIfJwUPUmFkR3JpZE5GX2N0bDAwZAIBD2QWCmYPDxYGHgdSb3dTcGFuAgIfAAUGJm5ic3A7HwJoZGQCAQ8P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Hy5lHy9lZAIMDw9kFgQfLmUfL2VkAg0PD2QWBB8uZR8vZWQCOQ8UKwADDxYCHwcLKwQBZGRkFgJmD2QWAgIBD2QWAgIBDzwrAAQBAA8WAh8HCysEAWRkAjsPFCsAAw8WAh8HCysEAWRkZBYCZg9kFgICAQ9kFgICAQ88KwAEAQAPFgIfBwsrBAFkZAJBDxQrAAIUKwADDxYCHwcLKwQBZGRkEBYCZgIBFgIUKwADDxYEHglCZWhhdmlvcnMLKXdUZWxlcmlrLldlYi5VSS5XaW5kb3dCZWhhdmlvcnMsIFRlbGVyaWsuV2ViLlVJLCBWZXJzaW9uPTIwMTQuMS4yMjUuNDAsIEN1bHR1cmU9bmV1dHJhbCwgUHVibGljS2V5VG9rZW49MTIxZmFlNzgxNjViYTNkND8fBwsrBAFkZGQUKwADDxYEHzALKwk/HwcLKwQBZGRkDxYCZmYWAQVxVGVsZXJpay5XZWIuVUkuUmFkV2luZG93LCBUZWxlcmlrLldlYi5VSSwgVmVyc2lvbj0yMDE0LjEuMjI1LjQwLCBDdWx0dXJlPW5ldXRyYWwsIFB1YmxpY0tleVRva2VuPTEyMWZhZTc4MTY1YmEzZDQWBGYPFCsAAw8WBB8wCysJPx8HCysEAWRkZGQCAQ8UKwADDxYEHzALKwk/HwcLKwQBZGRkZAJDDxQrAAMPFgIfBwsrBAFkZGQWAmYPZBYCAgEPZBYCAgEPPCsABAEADxYCHwcLKwQBZGQCRQ8UKwADDxYEHzALKwk/HwcLKwQBZGRkFgJmD2QWAgIBD2QWAgIBDzwrAAQBAA8WAh8HCysEAWRkGAYFC1NraW5DaG9vc2VyDxQrAAIFBFNpbGsFBFNpbGtkBSxSYWRHcmlkTkYkY3RsMDAkY3RsMDIkY3RsMDAkUGFnZVNpemVDb21ib0JveA8UKwACZQUCMTBkBR5fX0NvbnRyb2xzUmVxdWlyZVBvc3RCYWNrS2V5X18WEAUQUXNmRnJvbURlY29yYXRvcgUSUmFkQnV0dG9uQXR1YWxpemFyBQxSYWRUYWJTdHJpcDEFCVJhZEdyaWRORgUSUmFkR3JpZE5GJHJmbHRNZW51BRRSYWRXaW5kb3dDb21wcm92YW50ZQUjUmFkV2luZG93Q29tcHJvdmFudGUkQyRDYW5jZWxCdXR0b24FDlJhZFdpbmRvd0RhY3RlBRtSYWRXaW5kb3dEYWN0ZSRDJFJhZEJ1dHRvbjIFEVJhZFdpbmRvd01hbmFnZXIxBQ1SYWRXaW5kb3dGaWxlBRJSYWRXaW5kb3dEZXRhbGhlTkYFE1JhZFdpbmRvd0RldGFsaGVDVEUFIFJhZFdpbmRvd0RldGFsaGVDVEUkQyRSYWRCdXR0b24xBRNSYWRXaW5kb3dEZXRhbGhlRURJBSBSYWRXaW5kb3dEZXRhbGhlRURJJEMkUmFkQnV0dG9uMwUsUmFkR3JpZE5GJGN0bDAwJGN0bDAzJGN0bDAyJFBhZ2VTaXplQ29tYm9Cb3gPFCsAAmUFAjEwZAUWUmFkQ29tYm9Cb3hUaXBvQ2xpZW50ZQ8UKwACBQdDbGllbnRlZWQFF1JhZENvbWJvQm94TGlzdGFDbGllbnRlDxQrAAJlZWSKlcWbaKVBS65VFEB0N6syNIw3yVd2HRQ5sCeV2vovaw==',
            '__VIEWSTATEGENERATOR': '49D04743',
            '__EVENTVALIDATION': '/wEdACBBj/Zg8d0tfR28ZyJMnL1WjqOc4AVwnB17eZSKUJ+oFtkaKbtVeiKwwgPBNGfjaMPkkxdDnpSVG/9fLIyC5hjDUI3qRTyz4bYIC44w+nd3zZoVPgoK0LQe7SWXkEQKqgw8uK8iw10HXA/GI/FdNm6iDetirnDLRBilzzQgR0v+5qc3McsmjCsYvqHv2P/MJtkXVmhre0s7WCPciNDhMyjqXHoAryf9nKQsjUvxSpgNehSy1jAFuKNxe8htLNJSMsRGqyfl2W9+U5XLUlJLEaz9XIfPxIRjZz3fqvQpq+5qKHXNhAmruIlFRkHyV+8s7hdn0+XeSZVTQXKoAJAjZ2nR45M+HtB2DhiZbM4XUzq7aKtXq3YgmPtfbU/WHEqBoOUFgRZnnh3jl8FFY8z9U74UW02bst9p9h37ic2pLDN+WC512Yr4lQuqVNpVNUSo7Pbes4gJ/4QsyxJAhuCcnzHeyF5J2MdYk/8TjoyTIl+JoCzjVxFNfB/RC1seFPNDnkh8UwdfQf3UyZIIA9URpTA+mBmQKQozdHBrDX95YEoDN40Cbpeq9hMXVrjNJE66yx/A2jWVueBhEQ51mjdTwbUZGdkSZCMhlIZeTmfwcfvHhGejKe5k3jg2d5ahAd/oZ5B6tnUPUuHJTwlCkHlMW7KujBKmOwrzSakUt7It2SkUMNmozBGPXA8M+E+IBixzXA2P3ZpBJ3Mk+6NJEVXL7Eq2',
            '__ASYNCPOST': 'true',
            'RadAJAXControlID': 'RadAjaxManager1'

        }

        url = f'https://web.mira.com.br/webmira/portalmira/(S({dynamic_value}))/Tracking/TrackingNf.aspx'

        response = self.session.post(
            url,
            cookies=self.cookies,
            headers=self.headers,
            data=data,
        )

        self.cookies.update(response.cookies.get_dict())

        return response.text

    def extract_delivery_info(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        target_element = soup.find('td', class_='teamNames')

        if target_element:
            delivery_info = target_element.get_text(strip=True)
            match = re.search(r'(\d{2}/\d{2}/\d{4})', delivery_info)
            print(delivery_info)
            if match:
                data_entrega = match.group(1)
                status_match = re.search(r'Entregue', delivery_info)
                status = status_match.group() if status_match else delivery_info
                return status, data_entrega
            else:
                # Se não houver correspondência para a data, use delivery_info como status
                return delivery_info, "N/A"
        else:
            return "Elemento não encontrado.", "N/A"

    def extract_additional_info(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        conhecimento_element = soup.select_one(self.conhecimento_selector)
        previsao_element = soup.select_one(self.previsao_selector)

        conhecimento = conhecimento_element.get_text(strip=True) if conhecimento_element else "Não encontrado"
        previsao = previsao_element.get_text(strip=True) if previsao_element else "Não encontrado"

        return conhecimento, previsao

    def is_session_expired(self, html):
        return "Sua sessão expirou" in html

    def reauthenticate(self):
        pass

    def is_already_delivered(self, numero_nota):
        conn = sqlite3.connect('consultas.db')
        cursor = conn.cursor()

        cursor.execute('SELECT Status FROM consultas WHERE Numero_Nota = ?', (numero_nota,))
        status = cursor.fetchone()

        conn.close()

        return status and status[0] and status[0].lower() == "Entregue" if status else False





    def process_data(self):
        resultados = self.connect_to_database()

        for resultado in resultados:
            numero_nota = resultado[0]

            if not self.is_already_delivered(numero_nota):
                html_response = self.make_request(numero_nota)

                if self.is_session_expired(html_response):
                    self.reauthenticate()
                    html_response = self.make_request(numero_nota)

                delivery_info, data_entrega = self.extract_delivery_info(html_response)
                conhecimento, previsao = self.extract_additional_info(html_response)

                # Armazena as informações no banco de dados
                self.store_in_database(numero_nota, delivery_info, data_entrega, previsao)

                print(f"Status {delivery_info}")
                print(f"Data de Entrega: {data_entrega}")
                print(f"Conhecimento: {conhecimento}")
                print(f"Previsão: {previsao}")

    def store_in_database(self, numero_nota, status, data_entrega, previsao_entrega):
        conn = sqlite3.connect('consultas.db')
        cursor = conn.cursor()

        # Verifica se já existe um registro com o mesmo número de nota
        cursor.execute('SELECT * FROM consultas WHERE Numero_Nota = ?', (numero_nota,))
        existing_record = cursor.fetchone()

        if existing_record:
            # Atualiza o registro existente
            if status == "Entregue":
                status = "MERCADORIA ENTREGUE"
            cursor.execute('UPDATE consultas SET Status = ?, Data_Entrega = ?, Previsao_Entrega = ? WHERE Numero_Nota = ?',
                        (status, data_entrega, previsao_entrega, numero_nota))
        else:
            # Insere um novo registro
            if status == "Entregue":
                status = "MERCADORIA ENTREGUE"
            cursor.execute('INSERT INTO consultas (Numero_Nota, Status, Data_Entrega, Previsao_Entrega) VALUES (?, ?, ?, ?)',
                        (numero_nota, status, data_entrega, previsao_entrega))

        conn.commit()
        conn.close()


# Utilizando a classe
tracker = MiraTracking()
tracker.process_data()
