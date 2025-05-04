FURIA Fans Bot - Telegram

Telegram chatbot para acompanhar tudo da line Counter‑Strike 2 da FURIA, criado para o Challenge #1 – Estágio FURIA Tech.

Como usar:
• Abra o bot no Telegram: https://t.me/ArthurFuriaBot

Funcionalidades

Comando / Botão    – Descrição
/start             – Boas‑vindas e menu inline
/help              – Lista rápida de comandos
/about  (ℹ️ Sobre) – História, conquistas e missão
/roster (📋)       – Elenco 2025 + coach e manager (links Liquipedia)
/results (✅)      – Últimas partidas (links HLTV)
/schedule (⏰)     – Próximos jogos com chance de vitória + link de transmissão
/news    (📰)      – Manchetes recentes (links externos)
/links   (🔗)      – Liquipedia, HLTV, Twitter, Instagram

Preview do menu principal

🐍 FURIA Fans Bot pronto para o clutch!
Acompanhe resultados, agenda, roster e notícias em tempo real.

Instalação local

Clone o repositório

Crie um ambiente virtual

Execute: pip install -r requirements.txt

Adicione o token do Bot (<BOT_TOKEN>) em um arquivo .env

Rode: python furia_telegram_bot.py

Docker

Executar: docker compose up --build -d

Requisitos

• Python 3.11+
• Dependências: aiogram>=3.7, httpx, beautifulsoup4, python-dotenv

Deploy sugerido

• Render  – Web Service Docker, variável BOT_TOKEN
• Railway – Deploy via Git, variável BOT_TOKEN
• Fly.io  – fly launch; depois fly secrets set BOT_TOKEN=...
• Cloudflare Workers – versão Python worker (não incluída)

Estrutura do projeto

furia_fans_bot/
furiaBot.py
README.txt (este arquivo)

Contribuição

Issues e pull requests são bem‑vindos.
