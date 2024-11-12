# Definir a imagem base
FROM python:3.9-slim

# Definir o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copiar o arquivo requirements.txt e instalar as dependências
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copiar o código do servidor
COPY . .

# Expôr a porta
EXPOSE 8082

# Comando para rodar o servidor Flask
CMD ["python", "token3.py"]
