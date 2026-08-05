# VoiceMatch Backend

API construída com **FastAPI** para a plataforma de recrutamento com entrevista por IA, integrada ao **PostgreSQL** (via Docker) para banco de dados, utilizando **Alembic** para migrações do banco.

## 🚀 Como Rodar Localmente

1. Clone o repositório:
```bash
git clone https://github.com/Ron4ld0/voicematch-back.git
cd voicematch-back
```

2. Crie e ative um ambiente virtual:
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
# source .venv/bin/activate
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Variáveis de ambiente:
Copie o arquivo `.env.example` para `.env` e preencha com as credenciais do seu banco de dados PostgreSQL. Para rodar o banco de dados via Docker, você pode usar o `docker-compose.yml` já incluído no projeto:
```bash
docker-compose up -d
```

5. Execute as migrações:
```bash
alembic upgrade head
```

6. Inicie o servidor:
```bash
uvicorn app.main:app --reload --port 8000
```
A documentação da API (Swagger) estará disponível em `http://localhost:8000/docs`.

---

# Modelo de Dados — Plataforma de Recrutamento com Entrevista por IA

Este documento descreve o modelo de dados atualizado da plataforma, implementado em PostgreSQL via Docker.

## Visão geral do fluxo

```
Usuario
 └── Recrutador ──> Vaga (score_minimo_triagem)

Candidato ──> Candidatura ──[Triagem IA (score & feedback)]──> Entrevista ──> PerguntaEntrevista ──> RespostaEntrevista
                  │                                                  │
              (vaga_id)                                         (score_geral,
                                                                 feedbacks)
```

1. Um `Usuario` se cadastra (com email e senha). O sistema o classifica como `Recrutador` (tabela vinculada 1:1).
2. O `Recrutador` cria uma `Vaga`, podendo definir um `score_minimo_triagem` para ativação do gate por IA.
3. Um `Candidato` (que é uma entidade independente de `Usuario`) se candidata a uma vaga, gerando uma `Candidatura` (status inicial `pendente_triagem`).
4. A IA analisa o currículo do candidato contra a vaga. Se o score obtido atingir ou superar o threshold, o status passa para `aprovada_triagem`, liberando a criação da `Entrevista` de voz. Caso contrário, assume `reprovada_triagem`.
5. A `Candidatura` aprovada origina uma `Entrevista`.
6. A `Entrevista` contém várias `PerguntaEntrevista`, geradas pela IA a partir dos dados da vaga.
7. Cada pergunta recebe uma `RespostaEntrevista` em áudio, com transcrição e métricas comportamentais.
8. Ao final, a `Entrevista` é atualizada com `score_geral` e os feedbacks (candidato e recrutador).

---

## Tabelas

### `usuario`
Tabela base para autenticação (email e senha_hash).

| Campo | Tipo | Observação |
|---|---|---|
| `id` | uuid (PK) | |
| `nome_completo` | varchar | |
| `email` | varchar, único | Usado para login |
| `senha_hash` | varchar | Senha criptografada |
| `telefone` | varchar | |
| `tipo_usuario` | enum (`recrutador`) | Define o perfil do usuário |
| `data_criacao` | timestamptz | |

### `recrutador` (especialização 1:1 de `usuario`)
Guarda dados exclusivos de quem publica vagas.

| Campo | Tipo | Observação |
|---|---|---|
| `id` | uuid (PK, FK → `usuario.id`) | Mesmo id do usuário |
| `empresa` | varchar | |
| `cnpj` | varchar(14) | Apenas dígitos; validado pelos dígitos verificadores. Não é único — vários recrutadores podem ser da mesma empresa |
| `cargo` | varchar | |

### `candidato` (entidade independente)
Guarda dados dos candidatos às vagas. Diferente do recrutador, no momento o candidato não tem vínculo direto com a tabela `usuario`.

| Campo | Tipo | Observação |
|---|---|---|
| `id` | uuid (PK) | |
| `nome` | varchar | |
| `email` | varchar, único | |
| `telefone` | varchar | |
| `curriculo_url` | text | Link para o currículo |
| `resumo_profissional` | text | |
| `experiencias` | jsonb | Lista de experiências |
| `tecnologias` | jsonb | Lista de tecnologias/skills |

### `vaga`
Vaga de emprego publicada por um recrutador.

| Campo | Tipo | Observação |
|---|---|---|
| `id` | uuid (PK) | |
| `recrutador_id` | uuid (FK → `recrutador.id`) | |
| `titulo` | varchar | |
| `descricao` | text | |
| `descricao_candidato_ideal` | text | Contexto extra para a IA gerar perguntas |
| `requisitos_hard` | jsonb | |
| `requisitos_soft` | jsonb | |
| `score_minimo_triagem` | numeric(4,2) | Score mínimo (threshold) para aprovação na triagem de currículo por IA (null = sem gate ativo) |
| `status` | enum (`ativa`, `pausada`, `encerrada`) | |
| `data_criacao` | timestamptz | |

### `candidatura`
Registra a intenção de um candidato em uma vaga. Existe **antes** da entrevista.

| Campo | Tipo | Observação |
|---|---|---|
| `id` | uuid (PK) | |
| `vaga_id` | uuid (FK → `vaga.id`) | |
| `candidato_id` | uuid (FK → `candidato.id`) | |
| `status` | enum (`pendente_triagem`, `aprovada_triagem`, `reprovada_triagem`, `em_entrevista`, `avaliada`, `aprovada`, `rejeitada`) | Estado da candidatura no fluxo de triagem e entrevista |
| `score_triagem` | numeric(4,2) | Nota da triagem de currículo calculada pela IA |
| `feedback_triagem` | jsonb | Feedback da triagem (pontos fortes, gaps, texto explicativo) |
| `data_triagem` | timestamptz | Data/hora em que a triagem da IA foi realizada |
| `data_candidatura` | timestamptz | |

Constraint `unique (vaga_id, candidato_id)` impede duplicidade.

### `entrevista`
Uma tentativa de entrevista associada a uma candidatura.

| Campo | Tipo | Observação |
|---|---|---|
| `id` | uuid (PK) | |
| `candidatura_id` | uuid (FK → `candidatura.id`) | Permite criação apenas se candidatura possuir `status = aprovada_triagem` |
| `status` | enum (`agendada`, `em_andamento`, `concluida`, `cancelada`) | |
| `data_inicio` | timestamptz | |
| `data_fim` | timestamptz | |
| `score_geral` | numeric(4,2) | Nota consolidada (0 a 10) |
| `feedback_candidato` | text | |
| `feedback_recrutador` | text | |
| `data_criacao` | timestamptz | |

### `pergunta_entrevista`
Pergunta gerada pela IA.

| Campo | Tipo | Observação |
|---|---|---|
| `id` | uuid (PK) | |
| `entrevista_id` | uuid (FK → `entrevista.id`) | |
| `pergunta_texto` | text | |
| `ordem` | int | Posição da pergunta |
| `data_criacao` | timestamptz | |

Constraint `unique (entrevista_id, ordem)` garante a não repetição de ordem.

### `resposta_entrevista`
A resposta em áudio, com transcrição e métricas.

| Campo | Tipo | Observação |
|---|---|---|
| `id` | uuid (PK) | |
| `pergunta_id` | uuid (FK → `pergunta_entrevista.id`), único | Uma por pergunta |
| `audio_url` | text | Link para o arquivo de áudio |
| `transcricao` | text | Texto via STT |
| `metricas` | jsonb | Sinais (confiança, nervosismo, etc) |
| `data_resposta` | timestamptz | |

---

## Diagrama de relacionamentos (resumo)

```
usuário
   │ 1:1
   ▼
recrutador ──1:N──> vaga (score_minimo_triagem)
                      │
                    1:N
                      ▼
candidato ──1:N──> candidatura ──[Triagem IA (aprovada_triagem)]──1:N──> entrevista ──1:N──> pergunta_entrevista ──1:1──> resposta_entrevista
```

---

## Enums definidos

| Enum | Valores |
|---|---|
| `tipo_usuario_enum` | `recrutador` |
| `status_vaga_enum` | `ativa`, `pausada`, `encerrada` |
| `status_candidatura_enum` | `pendente_triagem`, `aprovada_triagem`, `reprovada_triagem`, `em_entrevista`, `avaliada`, `aprovada`, `rejeitada` |
| `status_entrevista_enum` | `agendada`, `em_andamento`, `concluida`, `cancelada` |

---

## Pontos em aberto / próximos passos

- **Autenticação:** O sistema conta com registro nativo usando e-mail e hash de senha.
- **Integração Candidato/Usuário:** Avaliar se no futuro o candidato precisará logar via tabela `usuario` ou se o acesso será diferente.
- **Skills normalizadas:** Hoje `requisitos_hard`/`requisitos_soft` e `tecnologias` são `jsonb` livres.
- **CPF removido:** o campo era coletado do recrutador mas nunca lido por nenhuma regra de negócio, e o candidato — a pessoa de fato avaliada — não o possuía. Pelo princípio da necessidade (LGPD, Art. 6º, III), foi removido. Para identificar o recrutador bastam e-mail e o `cnpj` da empresa. Se um dia houver contratação efetiva, o CPF pertence a `candidato` e deve ser coletado só nesse momento.
