FROM python:3.12-slim

# Instala dependências do sistema (obrigatório para pandas_ta + TA-Lib)
RUN apt-get update && apt-get install -y \
    build-essential \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Instala TA-Lib (biblioteca C que o pandas_ta precisa)
RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
    tar -xzf ta-lib-0.4.0-src.tar.gz && \
    cd ta-lib && \
    ./configure --prefix=/usr && \
    make && \
    make install && \
    cd .. && \
    rm -rf ta-lib*

# Copia requirements e instala Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código da app
COPY streamlit_app.py .

EXPOSE 8501

CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
