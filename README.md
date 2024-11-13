# Relatório do Projeto - Sistema de Venda de Passagens

## Arquitetura da Solução

A solução desenvolvida para o sistema de venda de passagens é baseada em uma **arquitetura distribuída**, onde os componentes principais são:

1. **Frontend (Cliente)**:
   - O frontend é responsável pela interface com o usuário, onde o cliente seleciona a origem e destino das passagens, descobre as rotas disponíveis e efetua a compra.
   - Foi implementado utilizando HTML, CSS e JavaScript. O frontend se comunica com o backend por meio de **APIs RESTful**.

2. **Backend (Servidor)**:
   - O backend é implementado com o framework **Flask** e oferece uma API REST para o gerenciamento das passagens.
   - O servidor manipula as requisições de compra, consulta de rotas, e a lógica de concorrência entre os clientes.

3. **Servidores de Companhias**:
   - Cada companhia de transporte tem seu próprio servidor, que é responsável por manter o controle das passagens disponíveis e interagir com o servidor principal para garantir que o estoque de passagens esteja sempre atualizado.

### Classificação da Arquitetura

A arquitetura é **cliente-servidor distribuída**, com múltiplos servidores que oferecem acesso a diferentes rotas e passagens. O modelo de comunicação entre os servidores e o cliente é baseado em APIs RESTful, garantindo a escalabilidade e a manutenção de estados consistentes durante as interações.

---

## Protocolo de Comunicação

O sistema usa **APIs RESTful** para a comunicação entre os componentes desenvolvidos. Abaixo estão descritos os principais métodos remotos, parâmetros e retornos envolvidos no processo de compra de passagens:

### Endpoints

1. **Verificar Passagens Disponíveis**
   - **Método**: `POST /api/rota`
   - **Descrição**: Este endpoint é utilizado para consultar as rotas disponíveis entre uma cidade de origem e um destino.
   - **Parâmetros**:
     - `origem`: Nome da cidade de origem (ex.: "Barreiras").
     - `destino`: Nome da cidade de destino (ex.: "Salvador").
   - **Exemplo de Requisição**:
     ```json
     {
       "origem": "Barreiras",
       "destino": "Salvador"
     }
     ```
   - **Retorno**:
     - `rotas`: Lista de rotas disponíveis com as respectivas passagens.
     - **Exemplo de Resposta**:
     ```json
     {
       "rotas": [
         {
           "id": 1,
           "origem": "Barreiras",
           "destino": "Salvador",
           "quantidade_disponivel": 5
         },
         {
           "id": 2,
           "origem": "Barreiras",
           "destino": "Salvador",
           "quantidade_disponivel": 3
         }
       ]
     }
     ```

2. **Comprar Passagem**
   - **Método**: `POST /api/comprar`
   - **Descrição**: Este endpoint permite a compra de uma passagem, realizando o bloqueio da passagem e atualizando a quantidade de passagens disponíveis.
   - **Parâmetros**:
     - `rota_id`: ID da rota que o cliente deseja comprar.
   - **Exemplo de Requisição**:
     ```json
     {
       "rota_id": 1
     }
     ```
   - **Retorno**:
     - `success`: Booleano indicando se a compra foi bem-sucedida.
     - `remaining`: Número de passagens restantes para a rota.
     - **Exemplo de Resposta**:
     ```json
     {
       "success": true,
       "remaining": 4
     }
     ```

3. **Verificação de Token**
   - **Método**: `GET /api/verificar_token`
   - **Descrição**: Este endpoint verifica se o cliente possui um token válido para realizar a compra. O token é utilizado para garantir que o cliente não tente comprar passagens em uma rota já ocupada por outro cliente.
   - **Exemplo de Requisição**:
     Não há parâmetros, pois o sistema verifica o token automaticamente para cada cliente.
   - **Retorno**:
     - `has_token`: Booleano que indica se o cliente possui um token válido para realizar a compra.
     - **Exemplo de Resposta**:
     ```json
     {
       "has_token": true
     }
     ```

---

## Roteamento

O cálculo das rotas é feito de forma distribuída, considerando as informações de passagens e rotas fornecidas pelos servidores das companhias. A lógica de roteamento considera todos os trechos disponíveis nos servidores de todas as companhias, permitindo que o sistema mostre ao usuário todas as rotas possíveis entre a origem e o destino escolhido.

A interação entre os servidores é feita por meio de requisições de consulta de rotas, e cada servidor responde com as passagens disponíveis para suas respectivas rotas. O sistema então agrega essas informações e apresenta ao usuário as opções de viagem.

---

## Concorrência Distribuída

Para garantir que não haja vendas duplicadas ou a venda de passagens além da quantidade disponível, o sistema emprega uma estratégia de controle de concorrência distribuída. A lógica de concorrência é implementada da seguinte forma:

1. **Verificação de Passagens Disponíveis**:  
   Antes de permitir a compra de uma passagem, o sistema verifica, no servidor, a quantidade de passagens restantes para a rota desejada.

2. **Bloqueio de Passagens**:  
   Quando uma passagem é comprada, o sistema realiza uma operação de bloqueio na quantidade de passagens disponíveis para evitar que o mesmo assento seja vendido para dois clientes distintos.

3. **Fila de Espera**:  
   A implementação de uma fila de espera também pode ser usada, garantindo que, caso uma compra não seja concluída, o sistema retorne as passagens ao estoque, permitindo que outros clientes possam adquiri-las.

Além disso, o sistema utiliza um **algoritmo de Token Ring** para coordenar o acesso concorrente aos recursos distribuídos. O Token Ring garante que apenas um servidor por vez possa processar uma compra de passagem, evitando condições de corrida entre servidores e assegurando a consistência dos dados no sistema distribuído.

---

## Confiabilidade da Solução

A solução foi projetada para garantir confiabilidade mesmo diante de falhas de rede ou desconexões temporárias. Ao desconectar e reconectar os servidores das companhias, o sistema continua garantindo a concorrência distribuída e a finalização das compras anteriormente iniciadas por um cliente.

A comunicação entre os servidores e o cliente é robusta, e o sistema é capaz de manter os dados de transações consistentes, mesmo durante falhas intermitentes.

---

## Documentação do Código

O código do projeto é bem documentado com comentários explicativos nas principais classes e funções. Cada função possui uma descrição clara sobre seu propósito, parâmetros e o retorno esperado, facilitando a manutenção e compreensão do código.

---

## Emprego do Docker

A tecnologia **Docker** foi empregada para contêinerizar os serviços e testes implementados. O uso do Docker permite que o sistema seja facilmente implantado e testado em diferentes ambientes, garantindo que a solução seja escalável e portátil.

- **Serviços Dockerizados**: Todos os componentes do sistema, incluindo o frontend, o backend e os servidores das companhias, estão contêinerizados. Isso facilita o gerenciamento e a orquestração dos serviços.
- **Testes em Ambiente Isolado**: Os testes de integração e desempenho também foram realizados em containers Docker, garantindo que a solução seja testada em um ambiente isolado e controlado.

---

## Como Executar o Projeto

1. **Pré-requisitos**:
   - Docker instalado.
   - Acesso ao repositório no GitHub.

2. **Iniciar o Docker Compose**:
   Para rodar o projeto, basta usar o Docker Compose para orquestrar os containers. Execute o seguinte comando na raiz do projeto:

   ```bash
   docker-compose up --build
