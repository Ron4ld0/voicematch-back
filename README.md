# Modelo de Dados — Plataforma de Recrutamento com Entrevista por IA

Este documento descreve o modelo de dados da plataforma, implementado em PostgreSQL via Supabase. O esquema cobre o fluxo completo: cadastro de usuários, publicação de vagas, candidaturas, entrevistas conduzidas por IA (com perguntas e respostas em áudio) e o feedback final gerado.

## Visão geral do fluxo

```
Pessoa (auth.users)
 ├── Recrutador ──> Vaga
 └── Candidato ──> Candidatura ──> Entrevista ──> PerguntaEntrevista ──> RespostaEntrevista
                       │                │
                    (vaga_id)      (score_geral,
                                    feedbacks)
```

1. Um usuário se cadastra (Supabase Auth) e vira `Pessoa`, especializado em `Recrutador` ou `Candidato`.
2. O `Recrutador` cria uma `Vaga`.
3. O `Candidato` se candidata, gerando uma `Candidatura`.
4. A `Candidatura` origina uma `Entrevista`.
5. A `Entrevista` contém várias `PerguntaEntrevista`, geradas pela IA a partir dos dados da vaga.
6. Cada pergunta recebe uma `RespostaEntrevista` em áudio, com transcrição e métricas comportamentais.
7. Ao final, a `Entrevista` é atualizada com `score_geral` e os feedbacks (candidato e recrutador).

---

## Tabelas

### `pessoa`
Tabela base de qualquer usuário da plataforma. O `id` é o mesmo `id` do Supabase Auth (`auth.users`), então não existe cadastro de senha/login separado — a autenticação é 100% delegada ao Supabase.

| Campo | Tipo | Observação |
|---|---|---|
| `id` | uuid (PK, FK → `auth.users.id`) | Vínculo direto com o usuário autenticado |
| `nome_completo` | varchar | |
| `email` | varchar, único | |
| `telefone` | varchar | |
| `cpf` | varchar, único | Dado sensível (LGPD) — considerar criptografia/mascaramento futuramente |
| `tipo_usuario` | enum (`recrutador`, `candidato`) | Define qual tabela de especialização consultar |
| `data_criacao` | timestamptz | |

### `recrutador` (especialização 1:1 de `pessoa`)
Guarda dados exclusivos de quem publica vagas.

| Campo | Tipo | Observação |
|---|---|---|
| `id` | uuid (PK, FK → `pessoa.id`) | Mesmo id da pessoa |
| `empresa` | varchar | |
| `cargo` | varchar | |

### `candidato` (especialização 1:1 de `pessoa`)
Guarda dados exclusivos de quem se candidata a vagas.

| Campo | Tipo | Observação |
|---|---|---|
| `id` | uuid (PK, FK → `pessoa.id`) | Mesmo id da pessoa |
| `curriculo_url` | text | Link para o currículo (ex: arquivo no Supabase Storage) |
| `resumo_profissional` | text | |
| `experiencias` | jsonb | Lista livre de experiências profissionais |
| `tecnologias` | jsonb | Lista livre de tecnologias/skills do candidato |

> **Por que herança em vez de uma tabela única `usuario`?** Porque recrutador e candidato têm atributos e regras de negócio bem diferentes. Separar evita colunas nulas em excesso e deixa claro, via FK, qual perfil o usuário possui.

### `vaga`
Vaga de emprego publicada por um recrutador.

| Campo | Tipo | Observação |
|---|---|---|
| `id` | uuid (PK) | |
| `recrutador_id` | uuid (FK → `recrutador.id`) | |
| `titulo` | varchar | |
| `descricao` | text | |
| `descricao_candidato_ideal` | text | Usado como contexto extra para a IA gerar perguntas mais direcionadas |
| `requisitos_hard` | jsonb | Lista de hard skills exigidas |
| `requisitos_soft` | jsonb | Lista de soft skills exigidas |
| `status` | enum (`ativa`, `pausada`, `encerrada`) | |
| `data_criacao` | timestamptz | |

> **Nota:** o contador `inscricoes` da versão anterior foi removido. O número de candidaturas agora é obtido via `COUNT()` sobre a tabela `candidatura`, evitando dessincronia entre um contador manual e a realidade do banco.

### `candidatura`
Registra o ato de um candidato se candidatar a uma vaga. É o elo entre `vaga` e `candidato`, e existe **antes** de qualquer entrevista acontecer.

| Campo | Tipo | Observação |
|---|---|---|
| `id` | uuid (PK) | |
| `vaga_id` | uuid (FK → `vaga.id`) | |
| `candidato_id` | uuid (FK → `candidato.id`) | |
| `status` | enum (`pendente`, `em_entrevista`, `avaliada`, `aprovada`, `rejeitada`) | Estado da candidatura no funil de contratação |
| `data_candidatura` | timestamptz | |

Constraint `unique (vaga_id, candidato_id)` impede que o mesmo candidato se candidate duas vezes à mesma vaga.

> **Por que essa tabela existe separada de `entrevista`?** No modelo anterior, `entrevista` fazia o papel de candidatura *e* de entrevista ao mesmo tempo. Isso é problemático porque: (1) nem toda candidatura vira entrevista de imediato — pode ficar numa fila; (2) uma candidatura pode gerar mais de uma tentativa de entrevista (reagendamento); (3) o status de "funil de contratação" (pendente → aprovada/rejeitada) é conceitualmente diferente do status de execução da entrevista (agendada → concluída).

### `entrevista`
Uma tentativa de entrevista associada a uma candidatura.

| Campo | Tipo | Observação |
|---|---|---|
| `id` | uuid (PK) | |
| `candidatura_id` | uuid (FK → `candidatura.id`) | Não referencia vaga/candidato diretamente — passa sempre pela candidatura |
| `status` | enum (`agendada`, `em_andamento`, `concluida`, `cancelada`) | |
| `data_inicio` | timestamptz | |
| `data_fim` | timestamptz | |
| `score_geral` | numeric(4,2) | Nota consolidada, ex: `8.75`, escala 0–10 |
| `feedback_candidato` | text | Texto de retorno/melhoria voltado ao candidato |
| `feedback_recrutador` | text | Texto de justificativa voltado ao recrutador |
| `data_criacao` | timestamptz | |

### `pergunta_entrevista`
Cada pergunta que a IA gerou para aquela entrevista específica, a partir dos dados da vaga.

| Campo | Tipo | Observação |
|---|---|---|
| `id` | uuid (PK) | |
| `entrevista_id` | uuid (FK → `entrevista.id`) | |
| `pergunta_texto` | text | Texto da pergunta exibido no chat |
| `ordem` | int | Posição da pergunta na sequência da entrevista |
| `data_criacao` | timestamptz | |

Constraint `unique (entrevista_id, ordem)` garante que não haja duas perguntas na mesma posição dentro da mesma entrevista.

### `resposta_entrevista`
A resposta em áudio do candidato para uma pergunta específica, junto com a transcrição e as métricas comportamentais extraídas.

| Campo | Tipo | Observação |
|---|---|---|
| `id` | uuid (PK) | |
| `pergunta_id` | uuid (FK → `pergunta_entrevista.id`), único | Uma resposta por pergunta |
| `audio_url` | text | Link para o arquivo de áudio (ex: Supabase Storage) |
| `transcricao` | text | Texto transcrito do áudio (via STT) |
| `metricas` | jsonb | Sinais extraídos: confiança, nervosismo, vícios de linguagem, uso de palavrão, etc. |
| `data_resposta` | timestamptz | |

> **Por que granularizar pergunta e resposta em vez de guardar tudo dentro de `entrevista`?** Sem essa granularidade, o `score_geral` da entrevista vira uma "caixa-preta": não dá pra mostrar ao recrutador (ou auditar) *por que* aquela nota foi dada. Com `pergunta_entrevista` + `resposta_entrevista`, cada resposta carrega suas próprias métricas, e o score final pode ser calculado/explicado a partir delas — importante tanto para transparência quanto para eventuais questionamentos de viés na avaliação.

---

## Diagrama de relacionamentos (resumo)

```
auth.users (Supabase)
   │ 1:1
   ▼
pessoa
   │
   ├── 1:1 ──> recrutador ──1:N──> vaga
   │                                  │
   │                                1:N
   │                                  ▼
   └── 1:1 ──> candidato ──1:N──> candidatura ──1:N──> entrevista ──1:N──> pergunta_entrevista ──1:1──> resposta_entrevista
```

---

## Enums definidos

| Enum | Valores |
|---|---|
| `tipo_usuario_enum` | `recrutador`, `candidato` |
| `status_vaga_enum` | `ativa`, `pausada`, `encerrada` |
| `status_candidatura_enum` | `pendente`, `em_entrevista`, `avaliada`, `aprovada`, `rejeitada` |
| `status_entrevista_enum` | `agendada`, `em_andamento`, `concluida`, `cancelada` |

---

## Pontos em aberto / próximos passos

- **RLS (Row Level Security):** ainda não definido. Depende de quem acessa o Supabase diretamente (só o back-end FastAPI via service role, ou também o Next.js direto).
- **Trigger de criação de `pessoa`:** falta decidir se a linha em `pessoa` é criada via trigger no `auth.users` ou manualmente pelo back-end no momento do signup.
- **Skills normalizadas:** hoje `requisitos_hard`/`requisitos_soft` (em `vaga`) e `tecnologias` (em `candidato`) são `jsonb` livres. Se no futuro for necessário buscar/filtrar vagas por skill específica de forma estruturada, considerar normalizar em uma tabela `skill` + tabela associativa.
- **CPF:** avaliar criptografia em repouso ou mascaramento em logs, por ser dado sensível sob a LGPD.
