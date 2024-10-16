import requests
from datetime import datetime
from collections import defaultdict
from dotenv import load_dotenv
import os

def obter_previsao_tempo(cidade, api_key):
    url = "http://api.openweathermap.org/data/2.5/forecast"

    params = {
        'q': cidade,
        'appid': api_key,
        'lang': 'pt_br',
        'units': 'metric'
    }

    try:
        resposta = requests.get(url, params=params)
        resposta.raise_for_status()  
        dados = resposta.json()

        if dados['cod'] != "200":
            return f"Erro: {dados.get('message', 'Cidade não encontrada.')}"

        nome_cidade = dados['city']['name']
        pais = dados['city']['country']

        previsoes_por_dia = defaultdict(list)
        for previsao in dados['list']:
            data_hora = datetime.strptime(previsao['dt_txt'], "%Y-%m-%d %H:%M:%S")
            data = data_hora.date()
            previsoes_por_dia[data].append(previsao)

        previsao_dias = []
        for data, previsoes in previsoes_por_dia.items():
            temperaturas = [p['main']['temp'] for p in previsoes]
            descricoes = [p['weather'][0]['description'] for p in previsoes]
            umidades = [p['main']['humidity'] for p in previsoes]
            ventos = [p['wind']['speed'] for p in previsoes]

            temp_min = min(temperaturas)
            temp_max = max(temperaturas)
            descricao = max(set(descricoes), key=descricoes.count).capitalize()
            umidade_media = sum(umidades) / len(umidades)
            vento_medio = sum(ventos) / len(ventos)

            previsao_dias.append({
                'data': data.strftime("%d/%m/%Y"),
                'descricao': descricao,
                'temp_min': temp_min,
                'temp_max': temp_max,
                'umidade': umidade_media,
                'vento': vento_medio
            })

        return {
            'cidade': nome_cidade,
            'pais': pais,
            'previsao_dias': previsao_dias
        }

    except requests.exceptions.HTTPError as http_err:
        return f"Erro na requisição HTTP: {http_err}"
    except Exception as err:
        return f"Erro: {err}"

def main():
    
    load_dotenv()
    api_key = os.getenv('API_KEY')

    cidade = input("\nDigite o nome da cidade para obter a previsão do tempo: ")

    resultado = obter_previsao_tempo(cidade, api_key)

    if isinstance(resultado, dict):
        print(f"\nPrevisão do tempo para {resultado['cidade']}, {resultado['pais']}:")
        for dia in resultado['previsao_dias']:
            print(f"\nData: {dia['data']}")
            print(f"Descrição: {dia['descricao']}")
            print(f"Temperatura: Mín: {dia['temp_min']}°C | Máx: {dia['temp_max']}°C")
            print(f"Umidade: {dia['umidade']:.1f}%")
            print(f"Velocidade do Vento: {dia['vento']:.1f} m/s")
    else:
        print(resultado)

if __name__ == "__main__":
    main()
