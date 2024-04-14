FROM python:3.8

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

# Install ngrok
RUN wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-stable-linux-amd64.zip && \
    unzip ngrok-stable-linux-amd64.zip && \
    mv ngrok /usr/local/bin/ngrok && \
    rm ngrok-stable-linux-amd64.zip

# Set Ngrok auth token
ARG NGROK_AUTH_TOKEN=""
RUN ngrok authtoken ${NGROK_AUTH_TOKEN}

# Expose Ngrok port
EXPOSE 4040

# Start ngrok tunnel
CMD ./ngrok authtoken ${NGROK_AUTH_TOKEN} ./ngrok http --domain=smart-insect-cleanly.ngrok-free.app 8000 &  uvicorn routes:app --host 0.0.0.0 --port 8000 
