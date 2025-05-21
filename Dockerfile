FROM python:3.12-slim-bookworm

WORKDIR /app

COPY requirements.txt .

RUN apt-get update && apt-get install -y sqlite3 curl bsdmainutils util-linux gawk bash \
  && curl -Ls https://git.io/trans -o /usr/local/bin/trans \
  && chmod +x /usr/local/bin/trans

RUN pip install -r requirements.txt

RUN curl -fsSL https://ollama.com/install.sh | sh

COPY . .

RUN touch /app/database/database.db

EXPOSE 8000

COPY entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

CMD ["/entrypoint.sh"]
