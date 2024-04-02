FROM python:3.11.4

WORKDIR /app

COPY requirements.txt .
COPY main.py .
COPY data .
RUN pip install -r requirements.txt
COPY data/ data/

EXPOSE 8501

CMD ["streamlit", "run", "main.py"]