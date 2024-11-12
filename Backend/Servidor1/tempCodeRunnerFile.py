import socket
import time
import pickle
from flask import Flask, request, jsonify
from collections import deque
from threading import Thread
import requests
from flask_cors import CORS


app = Flask(__name__)

CORS(app)

# Definição de rotas (simulação das rotas no servidor)
routes_server1 = {
    'Recife->Fortaleza->Salvador->Brasilia': {'passagens': 10},
    'Recife->Brasilia->Fortaleza->Manaus': {'passagens': 3},
    'Recife->Salvador->Brasilia->Uberlandia': {'passagens': 4},
}

# Estado do token e fila de pendentes
token = 1  # O token começa com o servidor 1
pending_requests = deque()  # Fila para armazenar as requisições pendentes

host = socket.gethostname()
other_port = 8086
my_port = 8080
my_port_socket = 8083  # Porta do socket para comunicação
my_port_socket2 = 8084  # Porta do socket para comunicação

# Socket para escutar mensagens
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Configura o socket para escutar na porta 8090 (não a mesma do Flask)
try:
    s.bind((host, my_port_socket))
    s.listen(5)
    print(f"Socket bindado na porta {my_port_socket} com sucesso!")
    print("MEU PISCA")
except OSError as e:
    print(f"Erro ao tentar bind na porta {my_port_socket}: {e}")

# Função que processa a compra da passagem
def process_purchase(route):
    """Função que processa a compra da passagem"""
    if route in routes_server1 and routes_server1[route]['passagens'] > 0:
        routes_server1[route]['passagens'] -= 1
        return {"success": True, "remaining": routes_server1[route]['passagens']}  # Retorna as passagens restantes
    else:
        return {"success": False, "message": "Passagem indisponível ou rota inválida."}

# Rota para verificar se o servidor tem o token
@app.route('/api/verificar_token', methods=['GET'])
def verificar_token():
    return jsonify({'has_token': token == 1})

# Rota para receber requisições de compra de passagens
@app.route('/api/comprar', methods=['POST'])
def comprar_passagem():
    data = request.json
    rota = data.get('rota')
    
    if rota:
        if token == 1:  # Verifica se o servidor possui o token
            print(f"Servidor 1: Processando compra para a rota: {rota}")
            resultado = process_purchase(rota)
            if resultado['success']:
                print(f"Compra realizada para a rota: {rota}")
                return jsonify({"success": True, "remaining": resultado['remaining']})
            else:
                print(f"Falha na compra: {resultado['message']}")
                return jsonify({"success": False, "message": resultado['message']})
        else:
            # Adiciona a solicitação à fila de pendências
            pending_requests.append(rota)
            print(f"Servidor 1: Solicitação para a rota {rota} adicionada à fila.")
            return jsonify({"success": False, "message": "Solicitação adicionada à fila."})
    else:
        return jsonify({"error": "Rota não especificada"}), 400

# Rota para passar o token para o próximo nó
@app.route('/api/passar_token', methods=['POST'])
def passar_token():
    time.sleep(5)  # Atraso simulado (se necessário)

    global token
    token = 2  # Passa o token para o próximo servidor

    # Comunicação com o Node 2 via socket em uma thread separada
    def send_token():
        try:
            with socket.socket() as ss:
                print(f"Node 1 está tentando enviar o token {token} para o Node 2...")
                ss.connect((host, other_port))  # Conecta no Node 2
                ss.send(pickle.dumps(token))  # Envia o token
                print(f"Token {token} enviado para o Node 2.")

        except Exception as e:
            print(f"Erro ao enviar o token para o Node 2: {e}")

    # Função que escuta pela chegada do token em uma thread
    def escutar_token():
        global token
        print("PRINT CAIO: ESPERANDO TOKEN")
        try:
            
            with socket.socket() as s:
                s.bind((host, my_port_socket2))  # Porta de escuta
                s.listen(5)
                print("Esperando pelo token...")

                while True:
                    c, addr = s.accept()  # Aceita a conexão
                    print(f"Conexão recebida de {addr}")
                    data = pickle.loads(c.recv(1024))  # Recebe os dados do socket

                    if data == 1:  # Verifica se o token recebido é o esperado
                        print("Token recebido!")
                        token = 1  # Atualiza o token
                        c.close()

                        # Após receber o token, chama a rota para passar o token
                        # Aqui, estamos chamando a função diretamente, mas você também poderia usar o Flask diretamente.
                        with app.test_client() as client:
                            client.post('http://localhost:8080/api/passar_token')

                    else:
                        print(f"Token inesperado recebido: {data}")
        except Exception as e:
            print(f"Erro ao escutar token: {e}")
    
    
    # Cria uma thread para enviar o token
    thread = Thread(target=send_token)
    thread.start()

    # Inicia a thread que escuta o token
    token_thread = Thread(target=escutar_token)
    token_thread.daemon = True  # A thread será finalizada quando o processo principal terminar
    token_thread.start()

    # Processa as requisições pendentes quando o token for passado
    while pending_requests:
        req_rota = pending_requests.popleft()  # Pega a primeira solicitação da fila
        print(f"Processando solicitação pendente para a rota: {req_rota}")
        resultado = process_purchase(req_rota)
        if resultado['success']:
            print(f"Compra realizada para a rota: {req_rota}")
        else:
            print(f"Falha na compra: {resultado['message']}")
        
        print("-"*30)
        for rota, dados in routes_server1.items():
            passagens = dados['passagens']  # Acessando o número de passagens restantes
            print(f"Rota: {rota}, Passagens restantes: {passagens}")
        print("-"*30)

    return jsonify({'success': True, 'message': 'Token passado e pendências processadas.'})

# Servidor de rotas - apenas para exibição das rotas disponíveis
@app.route('/api/rota', methods=['POST'])
def descobrir_rotas():
    data = request.json
    origem = data.get('origem')
    destino = data.get('destino')
    
    rotas_disponiveis = {}

    # Filtra as rotas de acordo com origem e destino
    for rota, passagens in routes_server1.items():
        if rota.startswith(origem) and rota.endswith(destino):
            rotas_disponiveis[rota] = {"passagens": passagens['passagens']}

    return jsonify({"rotas": rotas_disponiveis})

# Função que faz a requisição para passar o token a cada alguns segundos
def pass_token_periodicamente():
    try:
        url = 'http://localhost:8080/api/passar_token'
        response = requests.post(url)
        if response.status_code == 200:
            print("Token passado com sucesso!")
        else:
            print(f"Erro ao passar o token: {response.status_code}")
    except Exception as e:
        print(f"Erro ao fazer a requisição para passar o token: {e}")

if __name__ == '__main__':
    # Inicia a thread que passa o token periodicamente
    token_periodico_thread = Thread(target=pass_token_periodicamente)
    token_periodico_thread.daemon = True
    token_periodico_thread.start()

    # Inicia o servidor Flask
    app.run(host="0.0.0.0", port=my_port)
    
