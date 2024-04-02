# Predição de Churn

Este repositório contém um modelo de predição de churn desenvolvido em Python, utilizando aprendizado de máquina, para identificar clientes em risco de cancelamento de assinatura ou abandono de serviço.

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

## Organização das pastas

- case_data_scientist/
  - notebook_analise_dados.ipynb: Este notebook contém o código utilizado para análise dos dados, treinamento do modelo de previsão de churn e qualquer outra análise realizada durante o processo de ciência de dados.

- online_app_kpis/
  - data/: Esta pasta contém os dados utilizados pela aplicação online, como planilhas CSV e imagens necessárias para a execução do código.
  - main.py: Este arquivo contém o código-fonte principal da aplicação online. Utilizando a biblioteca Streamlit, ele cria uma interface web interativa onde os usuários podem visualizar análises de churn e fazer previsões de churn para clientes específicos.
  - Dockerfile: Este arquivo contém as instruções para a criação da imagem Docker que será usada para executar a aplicação online.
  - requirements.txt: Este arquivo contém as dependências Python necessárias para executar a aplicação online, como bibliotecas Streamlit, Pandas, Matplotlib, etc.

## Contribuição
Contribuições são bem-vindas! Sinta-se à vontade para enviar pull requests.

