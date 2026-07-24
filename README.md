# HSK1 com Áudio — Flashcards de Mandarim com FSRS

App de flashcards para estudar o vocabulário do **HSK1** (nível básico de mandarim),
com áudio nativo e repetição espaçada baseada em **FSRS** — o mesmo algoritmo de
Machine Learning usado atualmente pelo Anki para agendar revisões.

🔗 **Demo ao vivo:** [hsk1.darkintelligence.com.br](https://hsk1.darkintelligence.com.br)
📄 **Case completo (contexto e decisões técnicas):** [darkintelligence.com.br/cases/hsk](https://darkintelligence.com.br/cases/hsk/)

---

## Por que esse projeto existe

Comecei estudando mandarim e queria uma forma de treinar vocabulário com áudio.
O que era um script simples rodando no Replit virou um exercício prático de
engenharia: separar frontend e backend, hospedar cada parte no lugar certo,
debugar um erro de rate limit em produção, e — a parte mais interessante —
implementar um algoritmo real de repetição espaçada em vez de sortear palavras
aleatoriamente.

## Arquitetura

```
frontend/   → HTML/CSS/JS estático (hospedado no Hostgator)
backend/    → API Flask (hospedado no Render)
```

O frontend nunca fala diretamente com nenhum banco de dados ou lógica de negócio —
ele só consome a API via `fetch()`. Isso permite hospedar cada parte no serviço
mais adequado: hospedagem compartilhada comum pro front (barato, sem hibernação),
e um serviço com suporte real a Python pro back.

```
Usuário → Frontend (Hostgator)
              │  fetch()
              ▼
         Backend Flask (Render)
              │
    ┌─────────┴─────────┐
    ▼                    ▼
/api/words          /api/audio/<hanzi>
(vocabulário)      (mp3 pré-gerado)
```

## Stack

| Camada     | Tecnologia                          |
|------------|--------------------------------------|
| Frontend   | HTML, CSS, JavaScript (vanilla)       |
| Backend    | Python, Flask, gunicorn               |
| Áudio      | gTTS (gerado offline, não em runtime) |
| ML         | FSRS (repetição espaçada), implementado em JS puro |
| Deploy     | Hostgator (frontend) + Render (backend) |

## Machine Learning: repetição espaçada com FSRS

Cada palavra do deck tem um estado individual — **estabilidade** (S, em dias) e
**dificuldade** (D) — recalculado a cada avaliação do usuário (Esqueci / Difícil /
Bom / Fácil). O algoritmo estima a probabilidade de o usuário ainda lembrar de
uma palavra num dado momento (*retrievability*) e prioriza mostrar primeiro as
palavras mais próximas de serem esquecidas, em vez de repetir aleatoriamente
palavras já dominadas.

A implementação (`frontend/fsrs.js`) usa os pesos padrão publicados pelo projeto
open-source FSRS — os mesmos parâmetros treinados em centenas de milhões de
revisões reais de usuários do Anki. O progresso de cada usuário é salvo no
`localStorage` do navegador.

### Por que FSRS em vez de um algoritmo simples tipo SM-2

FSRS modela três coisas que algoritmos mais antigos ignoram:
- **Retrievability real**, calculada com uma curva de decaimento em potência (não exponencial fixa).
- **Efeito de teste**: lembrar de algo que já estava quase esquecido fortalece a memória mais do que revisar algo óbvio.
- **Reaprendizado mais rápido**: uma palavra esquecida depois de várias revisões não volta "à estaca zero".

## Um bug real de produção (e a correção)

O áudio era originalmente gerado sob demanda via `gTTS` (que usa a API não-oficial
do Google Translate). Em produção, o IP compartilhado do Render — usado por
muitos outros projetos — já estava sendo limitado pelo Google com erro `429 Too
Many Requests`. A correção não foi tentar contornar o limite, e sim eliminar a
dependência dele em tempo real: os 113 áudios do deck são **pré-gerados uma
única vez** (`backend/gerar_audios.py`) e servidos como arquivos estáticos —
o backend em produção nunca mais chama o Google.

## Rodando localmente

**Backend:**
```bash
cd backend
pip install -r requirements.txt
python app.py
```

**Gerar os áudios (uma vez, antes do primeiro deploy):**
```bash
cd backend
pip install gtts
python gerar_audios.py
```

**Frontend:**
Edite `frontend/script.js` e ajuste `API_BASE` para `http://localhost:5000`
(ou a porta usada localmente), depois abra `frontend/index.html` no navegador.

## Deploy

Ver instruções detalhadas em [`DEPLOY.md`](./DEPLOY.md) — cobre deploy do backend
no Render e do frontend via cPanel (Hostgator), incluindo configuração de
subdomínio e CORS.

## Roadmap

- [ ] Persistência de progresso no backend (conta de usuário, sincronização multi-dispositivo)
- [ ] Feedback de pronúncia: gravação do usuário + análise de contorno tonal (pitch) via extração de F0
- [ ] Re-treino dos pesos do FSRS com dados reais de uso, comparando contra os pesos padrão

## Autor

**Ricardo Queiroz** — [LinkedIn](https://www.linkedin.com/in/queirozricardo/) · [darkintelligence.com.br](https://darkintelligence.com.br)
