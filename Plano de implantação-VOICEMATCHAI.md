- [ ] Criar Repositórios Git: Inicializar os repositórios separados para voicematch-front, voicematch-back e voicematch-services.

- [ ] Configurar Docker Local: Criar o arquivo docker-compose.yml na raiz do voicematch-back para rodar a imagem do PostgreSQL.

- [ ] Mapear Volumes: Configurar no Docker um volume local persistente para armazenar os arquivos de áudio estáticos.

- [ ] Provisionar Nuvem: Criar e configurar o ambiente Cloud (ex: AWS EC2) com Docker e Docker Compose instalados para o deploy futuro.

Esta é a fase de maior esforço técnico, onde a inteligência e a persistência de dados ganham

vida.

- [ ] Conexão com o Banco: Configurar a variável DATABASE_URL no voicematch-back utilizando as bibliotecas asyncpg ou psycopg2 para conectar ao Postgres.

- [ ] Modelagem de Dados: Criar os modelos em SQLAlchemy para as entidades centrais: Vagas, Candidatos e Entrevistas.

- [ ] Configuração do Alembic: Inicializar o Alembic no backend e gerar as migrations iniciais para criar as tabelas no PostgreSQL.

- [ ] Endpoints do Motor de IA: Implementar os contratos da API no voicematch-services (/ai/transcribe, /ai/generate-question e /ai/evaluate).

- [ ] Fluxo de Recepção de Áudio: Criar a rota no voicematch-back que recebe o arquivo do frontend e o salva fisicamente no volume local mapeado no Docker.

- [ ] Orquestração Síncrona: Programar o voicematch-back para, após salvar o áudio, disparar a requisição ao serviço de transcrição, atualizar o Postgres e solicitar a próxima etapa de IA.

O foco aqui é garantir a qualidade da interação do candidato com o MVP.

- [ ] Validação de UI/Acessibilidade: Validar a harmonia da paleta de cores e o uso correto de componentes acessíveis e semânticos (inputs, selects) no voicematch-front.

- [ ] Integração do Player de Áudio: Garantir que o player no frontend funcione consumindo e reproduzindo corretamente os arquivos de áudio estáticos expostos pelo voicematch-back.

- [ ] Testes de Fluxo Ponta a Ponta (E2E): Testar o caminho feliz completo (inscrição -> gravação -> avaliação final) para garantir a estabilidade do fluxo entre o Front, Gateway e Serviços de IA.

- [ ] Validação UX de Conclusão: Assegurar que, ao finalizar a entrevista, o sistema
