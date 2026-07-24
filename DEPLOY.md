# HSK1 Flashcards — Deploy separado (backend + frontend)

## Estrutura
```
backend/    -> API Flask, hospedar no Render (ou Railway/Fly.io)
frontend/   -> HTML/CSS/JS estático, hospedar no Hostgator (cPanel)
```

## 1. Deploy do backend (Render)

1. Crie um repositório no GitHub e suba só a pasta `backend/` (ou o repo inteiro, mas aponte o Render pra essa subpasta).
2. Em https://render.com → New → Web Service → conecte o repositório.
3. Configurações:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app` (já está no Procfile, o Render detecta sozinho)
   - **Runtime**: Python 3
4. Depois do deploy, o Render te dá uma URL tipo `https://hsk1-backend.onrender.com`.
5. Teste: acesse `https://SEU-BACKEND.onrender.com/api/health` — deve retornar `{"status": "ok", "total_palavras": 113}`.

**Nota sobre CORS:** no `app.py`, troque `origins: "*"` pelo domínio real do seu site no Hostgator quando for pra produção (ex: `https://ricardoqueiroz.com.br`), pra evitar que qualquer site chame sua API.

## 2. Deploy do frontend (Hostgator / cPanel)

1. Abra o `script.js` e troque a linha:
   ```js
   const API_BASE = "https://SEU-BACKEND.onrender.com";
   ```
   pela URL real que o Render te deu.
2. No cPanel, vá em **Gerenciador de Arquivos** → `public_html` (ou crie uma subpasta/subdomínio tipo `mandarim.seudominio.com.br`).
3. Faça upload dos 3 arquivos: `index.html`, `style.css`, `script.js`.
4. Acesse seu domínio — o site deve carregar e buscar as palavras da API no Render.

## 3. Sobre a hibernação do Render (free tier)

O free tier do Render também hiberna após ~15 min de inatividade, mas ele acorda **sozinho** na próxima requisição (leva uns 30-50s pra "esquentar" na primeira vez, depois fica normal). Diferente do Replit, você não precisa clicar em nada — só o primeiro acesso do dia é mais lento.

Se quiser eliminar até essa espera, dá pra configurar um serviço gratuito tipo UptimeRobot pra pingar `/api/health` a cada 10 min e manter o backend sempre acordado.

## Próximos passos (evoluções de ML)

- **FSRS (repetição espaçada)**: adicionar rota `/api/review` que recebe rating do usuário e retorna a próxima data de revisão.
- **Análise de tom**: rota `/api/check-pronunciation` que recebe áudio gravado do usuário e compara com o tom esperado.
