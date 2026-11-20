FROM python:3.12-slim

# Runs on Render (render.yaml) or a Hugging Face Space. Both run the container as user 1000.
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    HTR_DATA=/home/user/data

WORKDIR $HOME/app
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt
COPY --chown=user . .

EXPOSE 7860
# Render sets $PORT; Hugging Face uses 7860.
CMD ["sh", "-c", "exec uvicorn server.main:app --host 0.0.0.0 --port ${PORT:-7860} --proxy-headers"]
