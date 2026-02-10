# CollegeHelper

Sistema web para auxiliar estudantes do ensino medio na escolha e organizacao de disciplinas, com recomendacoes por IA e geracao automatica de grade horaria.

---

## Sumario

- [Arquitetura](#arquitetura)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Configuracao e Instalacao](#configuracao-e-instalacao)
- [Variaveis de Ambiente](#variaveis-de-ambiente)
- [Backend (Flask)](#backend-flask)
  - [Models e Repositorios](#models-e-repositorios)
  - [Banco de Dados (SQLite)](#banco-de-dados-sqlite)
  - [Services](#services)
  - [Middleware](#middleware)
  - [Endpoints da API](#endpoints-da-api)
- [Frontend (Next.js)](#frontend-nextjs)
  - [Paginas](#paginas)
  - [Componentes](#componentes)
  - [Hooks](#hooks)
  - [Cliente API](#cliente-api)
- [Testes](#testes)
- [Dependencias](#dependencias)

---

## Arquitetura

| Camada   | Tecnologia       | Porta | Diretorio    |
|----------|------------------|-------|--------------|
| Frontend | Next.js 15 + React 19 | 3000  | `frontend/`  |
| Backend  | Flask 3.0        | 5000  | `backend/`   |
| Banco    | SQLite           | -     | `data/`      |
| Testes   | pytest           | -     | `tests/`     |

**Comunicacao:** O frontend consome a API REST do backend via `http://localhost:5000/api`. CORS esta configurado para aceitar requisicoes de `localhost:3000`.

**Autenticacao:** JWT (JSON Web Token) com 24h de expiracao. Senhas hasheadas com bcrypt.

---

## Estrutura do Projeto

```
CollegeHelper/
├── frontend/                  # Next.js (TypeScript)
│   ├── app/                   #   Paginas (App Router)
│   │   ├── layout.tsx         #     Layout raiz
│   │   ├── page.tsx           #     Home - renderiza login
│   │   ├── globals.css        #     Estilos globais (Tailwind)
│   │   └── main/
│   │       └── page.tsx       #     Dashboard principal
│   ├── components/            #   Componentes React
│   │   ├── main-form.tsx      #     Formulario de preferencias
│   │   ├── theme-provider.tsx #     Provider de tema (dark/light)
│   │   └── ui/                #     49 componentes shadcn/ui
│   ├── hooks/                 #   React Hooks customizados
│   │   ├── use-mobile.tsx     #     Deteccao de dispositivo movel
│   │   └── use-toast.ts       #     Sistema de notificacoes toast
│   ├── lib/                   #   Utilitarios e cliente API
│   │   ├── api.ts             #     Cliente HTTP para o backend
│   │   ├── scheduling-api.ts  #     API de agendamento (parcial)
│   │   └── utils.ts           #     Funcao cn() para classes CSS
│   ├── public/                #   Arquivos estaticos
│   ├── styles/                #   Estilos adicionais
│   ├── student-login.tsx      #   Componente de login
│   ├── package.json           #   Dependencias Node.js
│   ├── tsconfig.json          #   Configuracao TypeScript
│   ├── tailwind.config.ts     #   Configuracao Tailwind CSS
│   ├── next.config.mjs        #   Configuracao Next.js
│   └── postcss.config.mjs     #   Configuracao PostCSS
│
├── backend/                   # Flask (Python)
│   ├── app.py                 #   Factory create_app(), blueprints
│   ├── config.py              #   Classe Config (env vars)
│   ├── run.py                 #   Entrypoint do servidor
│   ├── models/                #   Camada de dados
│   │   ├── database.py        #     Conexao SQLite + init
│   │   ├── schema.sql         #     DDL completo do banco
│   │   ├── student.py         #     StudentRepository
│   │   ├── subject.py         #     SubjectRepository
│   │   └── preference.py      #     PreferenceRepository
│   ├── routes/                #   Endpoints da API
│   │   ├── health.py          #     GET /api/health
│   │   ├── auth.py            #     /api/auth/*
│   │   ├── students.py        #     /api/students/*
│   │   ├── subjects.py        #     /api/subjects/*
│   │   ├── preferences.py     #     /api/preferences/*
│   │   ├── ai.py              #     /api/ai/*
│   │   └── scheduling.py      #     /api/submit-preferences
│   ├── services/              #   Logica de negocio
│   │   ├── auth_service.py    #     Hashing + JWT
│   │   ├── ai_service.py      #     Integracao OpenAI
│   │   ├── scheduler_service.py #   Geracao de grade horaria
│   │   └── file_parser_service.py # Parse de CSV/JSON/TXT
│   └── middleware/            #   Middlewares
│       ├── auth_middleware.py  #     Decorator @require_auth
│       └── error_handlers.py  #     Handlers de erro JSON
│
├── tests/                     # Testes automatizados
│   ├── conftest.py            #   Fixtures (app, client, auth)
│   ├── test_auth.py           #   Testes de autenticacao
│   ├── test_students.py       #   Testes de perfil
│   └── test_subjects.py       #   Testes de disciplinas
│
├── data/                      # Banco de dados SQLite
│   └── student_subjects.db
│
├── requirements.txt           # Dependencias Python
├── .env.example               # Template de variaveis de ambiente
└── .gitignore
```

---

## Configuracao e Instalacao

### Pre-requisitos

- Python 3.10+
- Node.js 18+
- npm

### 1. Clonar e configurar ambiente

```bash
git clone <repo-url>
cd CollegeHelper

# Copiar variaveis de ambiente
cp .env.example .env
# Editar .env com suas chaves (ver secao abaixo)
```

### 2. Backend

```bash
# Instalar dependencias Python
pip install -r requirements.txt

# Iniciar servidor Flask (porta 5000)
python -m backend.run
```

### 3. Frontend

```bash
# Instalar dependencias Node.js
cd frontend
npm install

# Iniciar servidor Next.js (porta 3000)
npm run dev
```
### obs. Database

```bash
# Adicioanr as variaveis do db ao .env
# POSTGRESQL_PASSWORD=<senha>
vim postgresql.env

# Levantar container do banco de dados
docker-compose -f docker-compose.db.yml up -d 
```

### 4. Acessar

- **Frontend:** http://localhost:3000
- **API:** http://localhost:5000/api/health

---

## Variaveis de Ambiente

Arquivo `.env` na raiz do projeto:

| Variavel          | Descricao                              | Padrao                    | Obrigatoria |
|-------------------|----------------------------------------|---------------------------|-------------|
| `DATABASE_PATH`   | Caminho do banco SQLite                | `data/student_subjects.db`| Nao         |
| `FLASK_ENV`       | Ambiente Flask (`development`/`production`) | -                    | Nao         |
| `API_HOST`        | Host do servidor                       | `localhost`               | Nao         |
| `API_PORT`        | Porta do servidor                      | `5000`                    | Nao         |
| `SECRET_KEY`      | Chave secreta Flask (sessoes)          | chave de dev              | Sim (prod)  |
| `JWT_SECRET_KEY`  | Chave para assinar tokens JWT          | chave de dev              | Sim (prod)  |
| `OPENAI_API_KEY`  | Chave da API OpenAI (recursos de IA)   | -                         | Nao         |
| `FRONTEND_URL`    | URL do frontend para CORS              | `http://localhost:3000`   | Nao         |

---

## Backend (Flask)

### Models e Repositorios

Todos os models seguem o **padrao Repository** com metodos `@staticmethod`. Nenhum ORM e utilizado — queries SQL sao escritas diretamente com parametros `?` para prevenir SQL injection.

#### `StudentRepository` (`backend/models/student.py`)

Gerencia contas de estudantes (CRUD).

| Metodo | Parametros | Retorno | Descricao |
|--------|-----------|---------|-----------|
| `create()` | `email, password_hash, first_name, last_name, grade_level, **kwargs` | `int \| None` | Cria estudante. kwargs aceita: `date_of_birth`, `phone_number`, `guardian_email` |
| `find_by_email()` | `email` | `dict \| None` | Busca estudante ativo por email. Retorna id, email, password_hash, first_name, last_name, grade_level |
| `find_by_id()` | `student_id` | `dict \| None` | Busca perfil completo por ID (todas as colunas) |
| `update()` | `student_id, **kwargs` | `bool` | Atualiza campos permitidos. Seta `updated_at` automaticamente |

#### `SubjectRepository` (`backend/models/subject.py`)

Consulta de disciplinas disponiveis.

| Metodo | Parametros | Retorno | Descricao |
|--------|-----------|---------|-----------|
| `get_all()` | `active_only=True` | `list[dict]` | Lista disciplinas ordenadas por categoria e nome |
| `find_by_id()` | `subject_id` | `dict \| None` | Busca disciplina por ID |
| `get_categories()` | - | `list[str]` | Lista categorias distintas (apenas disciplinas ativas) |
| `get_by_category()` | `category, active_only=True` | `list[dict]` | Filtra disciplinas por categoria |

#### `PreferenceRepository` (`backend/models/preference.py`)

Gerencia preferencias de disciplinas dos estudantes.

| Metodo | Parametros | Retorno | Descricao |
|--------|-----------|---------|-----------|
| `get_by_student()` | `student_id` | `list[dict]` | Lista preferencias com JOIN em subjects (nome, codigo, categoria, dificuldade). Ordenado por prioridade ASC, interesse DESC |
| `add()` | `student_id, subject_id, interest_level, priority=None, notes=None, status='interested'` | `int \| None` | Adiciona preferencia (INSERT OR REPLACE). Constraint UNIQUE(student_id, subject_id) |
| `remove()` | `preference_id, student_id` | `bool` | Remove preferencia. Valida que pertence ao estudante |

#### `database.py` (`backend/models/database.py`)

Gerenciamento de conexao SQLite.

| Funcao | Descricao |
|--------|-----------|
| `get_db()` | Retorna conexao do request atual (armazenada em Flask `g`). Habilita foreign keys via PRAGMA. Suporta banco `:memory:` com singleton compartilhado para testes |
| `close_db()` | Fecha conexao no teardown do request. Nao fecha o singleton de memoria |
| `init_db(app)` | Executa `schema.sql` para criar tabelas no startup da aplicacao |

---

### Banco de Dados (SQLite)

#### Tabela `students`

Armazena contas e perfis dos estudantes.

| Coluna | Tipo | Constraints | Default |
|--------|------|-------------|---------|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | - |
| `email` | TEXT | UNIQUE NOT NULL | - |
| `password_hash` | TEXT | NOT NULL | - |
| `first_name` | TEXT | NOT NULL | - |
| `last_name` | TEXT | NOT NULL | - |
| `grade_level` | INTEGER | CHECK(9-12) | - |
| `date_of_birth` | DATE | - | - |
| `phone_number` | TEXT | - | - |
| `guardian_email` | TEXT | - | - |
| `is_active` | BOOLEAN | - | 1 |
| `created_at` | TIMESTAMP | - | CURRENT_TIMESTAMP |
| `updated_at` | TIMESTAMP | - | CURRENT_TIMESTAMP |

**Indices:** `idx_students_email` (email)

---

#### Tabela `subjects`

Catalogo de disciplinas/cursos disponiveis.

| Coluna | Tipo | Constraints | Default |
|--------|------|-------------|---------|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | - |
| `name` | TEXT | UNIQUE NOT NULL | - |
| `code` | TEXT | UNIQUE | - |
| `description` | TEXT | - | - |
| `category` | TEXT | NOT NULL | - |
| `difficulty_level` | INTEGER | CHECK(1-5) | - |
| `credits` | INTEGER | - | 1 |
| `prerequisites` | TEXT | - | - |
| `teacher_name` | TEXT | - | - |
| `max_students` | INTEGER | - | - |
| `semester` | TEXT | - | - |
| `schedule` | TEXT | - | - |
| `is_active` | BOOLEAN | - | 1 |
| `created_at` | TIMESTAMP | - | CURRENT_TIMESTAMP |

**Indices:** `idx_subjects_category` (category)

---

#### Tabela `student_preferences`

Relaciona estudantes com disciplinas de interesse.

| Coluna | Tipo | Constraints | Default |
|--------|------|-------------|---------|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | - |
| `student_id` | INTEGER | FK → students(id) ON DELETE CASCADE | - |
| `subject_id` | INTEGER | FK → subjects(id) ON DELETE CASCADE | - |
| `interest_level` | INTEGER | CHECK(1-5) | - |
| `priority` | INTEGER | - | - |
| `notes` | TEXT | - | - |
| `status` | TEXT | - | 'interested' |
| `created_at` | TIMESTAMP | - | CURRENT_TIMESTAMP |
| `updated_at` | TIMESTAMP | - | CURRENT_TIMESTAMP |

**Constraints:** UNIQUE(student_id, subject_id)
**Indices:** `idx_preferences_student` (student_id), `idx_preferences_subject` (subject_id)

---

#### Diagrama de Relacionamento

```
students (1) ──────< (N) student_preferences (N) >────── (1) subjects
   │                         │                                │
   │ id ←─── student_id ────┘                                │
   │                         └──── subject_id ───→ id         │
```

---

### Services

#### `AuthService` (`backend/services/auth_service.py`)

Autenticacao e autorizacao. Todos os metodos sao `@staticmethod`.

| Metodo | Descricao |
|--------|-----------|
| `hash_password(password)` | Gera hash bcrypt com salt aleatorio. Retorna string UTF-8 |
| `verify_password(password, hash)` | Compara senha plaintext com hash bcrypt. Retorna `bool` |
| `generate_token(student_id)` | Cria JWT com expiracao de 24h (algoritmo HS256). Payload: `student_id`, `exp`, `iat` |
| `verify_token(token)` | Decodifica JWT e retorna `student_id` ou `None` se expirado/invalido |

---

#### `AIService` (`backend/services/ai_service.py`)

Integracao com OpenAI GPT-4o-mini para recursos de IA academica. Requer `OPENAI_API_KEY` configurada. Retorna 503 se indisponivel.

| Metodo | Parametros | Descricao |
|--------|-----------|-----------|
| `is_available()` | - | Verifica se o cliente OpenAI foi inicializado |
| `get_subject_recommendations()` | `student_id, additional_context=''` | Analisa perfil e preferencias do estudante, sugere 5 disciplinas com justificativas |
| `analyze_subject_fit()` | `student_id, subject_name` | Avalia compatibilidade de uma disciplina com o perfil, retorna pros/contras e nota 1-10 |
| `get_career_advice()` | `student_id, career_interest` | Orienta sobre carreira com disciplinas relevantes e habilidades a desenvolver |
| `generate_study_plan()` | `student_id, selected_subjects, semester` | Gera plano de estudos semanal com alocacao de tempo e dicas |

**Configuracao do modelo:** `gpt-4o-mini`, temperature 0.7, max_tokens 1500. Todas as respostas sao solicitadas em formato JSON.

---

#### `SchedulerService` (`backend/services/scheduler_service.py`)

Gera grades horarias otimizadas baseadas em preferencias e disponibilidade.

**Estrategias de agendamento:**

| Estrategia | Descricao |
|------------|-----------|
| `MAXIMIZE_SUBJECTS` | Prioriza encaixar mais disciplinas (escolhe as mais curtas) |
| `CLEAR_DEPENDENCIES` | Prioriza disciplinas que sao pre-requisito de outras |
| `BALANCED_DIFFICULTY` | Distribui dificuldade uniformemente |
| `INTEREST_BASED` | Baseado em interesse do estudante |
| `HIGH_VALUE_CREDITS` | Maximiza creditos por periodo |

**Fluxo principal:**
1. Busca disciplinas disponiveis (banco + upload do usuario)
2. Filtra por compatibilidade com horarios do estudante
3. Aplica estrategia de priorizacao
4. Resolve conflitos de horario (algoritmo guloso)
5. Analisa resultado (total creditos, horas, dificuldade media, avisos)

**Data Classes:** `TimeSlot`, `Subject`, `StudentAvailability`, `SchedulingPreferences`

---

#### `FileParserService` (`backend/services/file_parser_service.py`)

Faz parse de arquivos de disciplinas para upload em massa.

| Formato | Descricao |
|---------|-----------|
| `.csv` | Colunas: name, schedule, credits, difficulty, category |
| `.json` | Objeto unico ou array de objetos |
| `.txt` | Blocos separados por `---` com pares chave:valor |

**Validacao:** Campo `name` e `schedule` obrigatorios. Credits limitado 1-10, difficulty 1-5.

---

### Middleware

#### `@require_auth` (`backend/middleware/auth_middleware.py`)

Decorator que protege endpoints autenticados:
1. Extrai token Bearer do header `Authorization`
2. Verifica token via `AuthService.verify_token()`
3. Armazena `student_id` em `g.current_student_id`
4. Retorna 401 se token ausente, invalido ou expirado

#### Error Handlers (`backend/middleware/error_handlers.py`)

Handlers registrados para respostas JSON consistentes:

| Codigo | Resposta |
|--------|----------|
| 400 | `{"error": "Bad Request", "message": "..."}` |
| 401 | `{"error": "Unauthorized", "message": "Authentication required"}` |
| 404 | `{"error": "Not Found", "message": "..."}` |
| 500 | `{"error": "Internal Server Error", "message": "..."}` (com log detalhado) |

---

### Endpoints da API

Base URL: `http://localhost:5000/api`

#### Health

| Metodo | Rota | Auth | Descricao |
|--------|------|------|-----------|
| GET | `/api/health` | Nao | Health check. Retorna `{"status": "healthy", "timestamp": "..."}` |

#### Autenticacao (`/api/auth`)

| Metodo | Rota | Auth | Body | Resposta |
|--------|------|------|------|----------|
| POST | `/api/auth/register` | Nao | `{"email", "password", "first_name", "last_name", "grade_level", "date_of_birth"?, "phone_number"?, "guardian_email"?}` | `201: {"success", "message", "student_id"}` |
| POST | `/api/auth/login` | Nao | `{"email", "password"}` | `200: {"success", "token", "student": {...}}` |
| POST | `/api/auth/logout` | Nao | - | `200: {"success", "message"}` |

**Validacoes:**
- `grade_level` deve ser entre 9 e 12
- Email deve ser unico (409 se duplicado)
- Senha verificada com bcrypt

---

#### Estudantes (`/api/students`)

| Metodo | Rota | Auth | Body | Resposta |
|--------|------|------|------|----------|
| GET | `/api/students/profile` | JWT | - | `200: {"success", "student": {...}}` |
| PUT | `/api/students/profile` | JWT | Campos a atualizar | `200: {"success", "message"}` |

---

#### Disciplinas (`/api/subjects`)

| Metodo | Rota | Auth | Params | Resposta |
|--------|------|------|--------|----------|
| GET | `/api/subjects` | Nao | `?category=` (opcional) | `200: {"success", "subjects": [...]}` |
| GET | `/api/subjects/<id>` | Nao | - | `200: {"success", "subject": {...}}` |
| GET | `/api/subjects/categories` | Nao | - | `200: {"success", "categories": [...]}` |

---

#### Preferencias (`/api/preferences`)

| Metodo | Rota | Auth | Body | Resposta |
|--------|------|------|------|----------|
| GET | `/api/preferences` | JWT | - | `200: {"success", "preferences": [...]}` |
| POST | `/api/preferences` | JWT | `{"subject_id", "interest_level" (1-5), "priority"?, "notes"?, "status"?}` | `201: {"success", "message", "preference_id"}` |
| DELETE | `/api/preferences/<id>` | JWT | - | `200: {"success", "message"}` |

---

#### IA (`/api/ai`)

Todos requerem JWT. Retornam 503 se `OPENAI_API_KEY` nao configurada.

| Metodo | Rota | Body | Descricao |
|--------|------|------|-----------|
| POST | `/api/ai/recommendations` | `{"additional_context"?}` | Sugestoes de disciplinas baseadas no perfil |
| POST | `/api/ai/subject-analysis` | `{"subject_name"}` | Analise de compatibilidade disciplina-estudante |
| POST | `/api/ai/career-advice` | `{"career_interest"}` | Orientacao de carreira |
| POST | `/api/ai/study-plan` | `{"selected_subjects", "semester"?}` | Plano de estudos semanal |

---

#### Agendamento (`/api/submit-preferences`)

| Metodo | Rota | Auth | Body |
|--------|------|------|------|
| POST | `/api/submit-preferences` | Nao | Ver abaixo |

**Corpo da requisicao:**
```json
{
  "weeklySchedule": [
    {
      "day": "Monday",
      "available": true,
      "timeSlots": [{"start": "08:00", "end": "12:00"}]
    }
  ],
  "subjectCount": 6,
  "preferenceStrategy": "balanced_difficulty",
  "prioritizeDependencies": true,
  "includeSaturday": false,
  "additionalNotes": "...",
  "uploadedSubjects": [...]
}
```

**Estrategias validas:** `maximize_subjects`, `clear_dependencies`, `balanced_difficulty`, `interest_based`, `high_value_credits`

---

## Frontend (Next.js)

### Paginas

| Rota | Arquivo | Descricao |
|------|---------|-----------|
| `/` | `app/page.tsx` | Pagina inicial — renderiza formulario de login |
| `/main` | `app/main/page.tsx` | Dashboard principal — formulario de preferencias, selecao de disciplinas, upload de PDF, construtor de grade horaria |

### Componentes

| Componente | Arquivo | Descricao |
|------------|---------|-----------|
| `StudentLogin` | `student-login.tsx` | Formulario de login com email e senha |
| `MainForm` | `components/main-form.tsx` | Formulario de preferencias: selecao de disciplinas (1-12), estrategia, horarios semanais com time slots, upload de arquivo |
| `ThemeProvider` | `components/theme-provider.tsx` | Wrapper para suporte a tema claro/escuro (next-themes) |
| **UI Library** | `components/ui/` | 49 componentes shadcn/ui (button, card, dialog, form, input, select, tabs, etc.) |

### Hooks

| Hook | Arquivo | Descricao |
|------|---------|-----------|
| `useIsMobile()` | `hooks/use-mobile.tsx` | Retorna `true` se largura < 768px. Usa MediaQuery listener |
| `useToast()` | `hooks/use-toast.ts` | Gerenciamento de notificacoes toast com reducer (add, update, dismiss, remove) |

### Cliente API

**Arquivo:** `frontend/lib/api.ts` (373 linhas)

Classe `ApiClient` singleton (`apiClient`) com:

- **Gerenciamento de token:** `setToken()`, `getToken()`, `clearToken()`, `isAuthenticated()` (localStorage)
- **Interceptors:** Headers automaticos (`Content-Type`, `Authorization: Bearer`)

**Metodos disponiveis:**

| Grupo | Metodos |
|-------|---------|
| Auth | `login()`, `register()`, `logout()` |
| Perfil | `getProfile()`, `updateProfile()` |
| Disciplinas | `getSubjects(category?)`, `getSubject(id)`, `getCategories()` |
| Preferencias | `getPreferences()`, `addPreference()`, `removePreference(id)` |
| IA | `getAIRecommendations()`, `analyzeSubjectFit()`, `getCareerAdvice()`, `generateStudyPlan()` |
| Sistema | `healthCheck()` |

**Interfaces TypeScript:** `Student`, `Subject`, `StudentPreference`, `LoginRequest`, `RegisterRequest`, `PreferenceRequest`, `AIRecommendationRequest`, `AISubjectAnalysisRequest`, `AICareerAdviceRequest`, `AIStudyPlanRequest`

---

## Testes

```bash
# Rodar todos os 15 testes
python -m pytest tests/ -v
```

| Arquivo | Testes | Cobertura |
|---------|--------|-----------|
| `test_auth.py` | 7 | Health check, registro, registro duplicado, campos faltantes, login, senha errada, logout |
| `test_students.py` | 3 | Buscar perfil, perfil sem auth, atualizar perfil |
| `test_subjects.py` | 5 | Listar disciplinas, listar categorias, disciplina nao encontrada, CRUD de preferencias, preferencias sem auth |

**Configuracao de testes:** Banco SQLite em memoria (`:memory:`) com singleton compartilhado para isolamento entre testes. `conftest.py` reseta `_memory_db` entre cada teste.

---

## Dependencias

### Backend (Python)

| Pacote | Versao | Uso |
|--------|--------|-----|
| flask | 3.0.0 | Framework web |
| flask-cors | 4.0.0 | Cross-Origin Resource Sharing |
| PyJWT | 2.8.0 | Tokens JWT |
| bcrypt | 4.1.2 | Hash de senhas |
| openai | >=1.0.0 | API OpenAI (GPT-4o-mini) |
| python-dotenv | 1.0.0 | Carregar .env |
| pytest | 7.4.3 | Framework de testes |

### Frontend (Node.js)

| Pacote | Uso |
|--------|-----|
| next 15.2.4 | Framework React com SSR |
| react 19.1.1 | Biblioteca UI |
| @radix-ui/* | Componentes headless acessiveis |
| tailwindcss 3.4.17 | CSS utilitario |
| lucide-react | Biblioteca de icones |
| react-hook-form | Gerenciamento de formularios |
| zod | Validacao de schemas |
| recharts | Graficos e visualizacoes |
| pdfjs-dist | Parse de arquivos PDF |
| next-themes | Suporte a tema claro/escuro |
| sonner | Notificacoes toast |
| class-variance-authority | Construtor de variantes CSS |
| date-fns | Manipulacao de datas |

---

## Comandos Rapidos

```bash
# Backend
python -m backend.run                    # Iniciar Flask (porta 5000)
python -m pytest tests/ -v               # Rodar testes

# Frontend
cd frontend && npm run dev               # Iniciar Next.js (porta 3000)
cd frontend && npm run build             # Build de producao
cd frontend && npm run lint              # Linter
```
