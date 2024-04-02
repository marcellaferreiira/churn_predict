# Previsão de Churn

Este repositório contém um modelo de previsão de churn desenvolvido em Python, utilizando aprendizado de máquina, para identificar clientes em risco de cancelamento de assinatura ou abandono de serviço.

## Descrição

O modelo analisa o comportamento dos clientes e prevê a probabilidade de churn, permitindo que empresas implementem estratégias de retenção eficazes.

## Execução do Código

### Pré-requisitos

- Docker instalado: [Instruções de instalação](https://docs.docker.com/get-docker/)

### Passo a Passo

1. Clone o repositório:

    ```bash
    git clone https://github.com/seu-usuario/seu-repositorio.git
    cd seu-repositorio
    ```

2. Construa a imagem Docker:

    ```bash
    docker build -t previsao-churn .
    ```

3. Execute o contêiner Docker:

    ```bash
    docker run -p 8501:8501 previsao-churn
    ```

4. Acesse o aplicativo no navegador em [http://localhost:8501](http://localhost:8501)

## Dados

Os dados utilizados pelo modelo estão localizados na pasta `data`. Esta pasta contém uma planilha em CSV e imagens necessárias para a execução do código.

## Contribuição
Contribuições são bem-vindas! Sinta-se à vontade para enviar pull requests.

