# ShiroAI

Shiro is an AI presentation generator by Noah Youngs, developed under Aldeo Innovations beginning in June 2024. It guides a presentation through **ideate → research → outline → slides**, combining a conversational interface with source-backed content generation and editable slides.

This repository contains the application source and a separate video-rendering Lambda. It is a historical prototype: the latest application commit before this documentation update is from September 2024. Running it requires configuring external services and adapting deployment-specific settings; this README does not imply that the original hosted service is available.

## What it does

1. **Ideate:** discuss the topic, audience, purpose, and presentation requirements with an AI assistant.
2. **Research:** search the web, add URLs or upload source files, and extract and summarize their content.
3. **Outline:** embed and cluster source passages into topics, then build and refine a presentation outline.
4. **Slides:** generate and edit slide content, layouts, icons, images, Mermaid diagrams, and narration scripts.

The backend uses OpenAI-compatible function calling for interactive workflows, with model access routed through Portkey. Research processing uses LangChain/LlamaIndex, OpenAI embeddings, BERTopic/HDBSCAN topic clustering, and Cohere reranking to select relevant source passages for slide generation (retrieval-augmented generation, or RAG). Stage updates and generation progress reach the browser through Socket.IO over WebSockets/polling; presentation data and stage state are persisted in DynamoDB and S3.

Implemented export paths include PDF, slide JPGs, and narrated MP4. MP4 generation combines rendered slide images, Amazon Polly narration, and an AWS Lambda using MoviePy/FFmpeg. JPG rendering also supports the video pipeline; it is not a promise of a separate JPG download control in the UI. PPTX export, sharing, speaker notes, and export source/reference switches are disabled or marked “Coming Soon” in the current UI.

## Architecture

| Directory | Responsibility |
| --- | --- |
| [`frontend/`](frontend/) | Next.js 14 / React 18 application, Auth.js with Cognito, slide editor, uploads, and server actions that call the renderer. |
| [`backend/`](backend/) | Python FastAPI services: Socket.IO orchestration on port 8000 and REST endpoints for icon search/image generation on port 8001. |
| [`headless-api/`](headless-api/) | TypeScript / Express HTTPS service on port 3003; Puppeteer rendering, Mermaid utilities, PDF/JPG output, Polly audio, and video Lambda invocation. |
| [`shared_ts/`](shared_ts/) | Shared TypeScript data types and DynamoDB access code. |
| [`sam-lambda/generate-video/`](sam-lambda/generate-video/) | AWS SAM template and Python 3.10 video-rendering function. This is not a complete infrastructure definition for the application. |
| [`notes/dynamodb_schema.md`](notes/dynamodb_schema.md) | Historical database design notes; compare with the current access code before provisioning indexes. |

The browser connects to the frontend and both Python services. The frontend and Python backend call the internal headless API. All services rely on provisioned AWS resources; there is no bundled offline mode or local database emulator configuration.

## Prerequisites

- Node.js and npm with workspace support. Node 20 is a reasonable starting point based on the repository's Node 20 type declarations; no Node runtime version is pinned.
- Python 3.11 and Poetry for the main backend (`pyproject.toml` permits Python 3.11 through 3.x; compatibility with newer releases is not established).
- Browser binaries and operating-system libraries for Puppeteer and Python Playwright.
- Locally trusted HTTPS certificates, for example generated with `mkcert`.
- AWS access to a DynamoDB table, S3 bucket, Cognito user pool/app client, and CloudFront distribution with signing configuration. Image upload also calls Rekognition. Video export additionally needs Polly and an existing video-rendering Lambda with FFmpeg.
- Configured model/search providers, including Portkey, OpenAI, Brave Search, and the providers used by the selected generation paths. Stability AI is used for applicable image-generation modes.

These services may incur charges. No complete provisioning script, environment template, or credential-free demo is included.

## Local setup

### 1. Install dependencies

From the repository root:

```bash
npm ci
cd backend
poetry install
poetry run playwright install chromium
cd ..
```

Use the Poetry manifest and lockfile for Python dependencies. `backend/requirements.txt` is an older environment snapshot containing machine-specific `file:///AppleInternal/...` references and is not a portable installation path. The Poetry manifest also references a Git dependency, `noahyoungs/main_content_extractor`; its availability is required.

### 2. Configure services

Create untracked `frontend/.env.local`, `backend/.env`, and `headless-api/.env` files for the corresponding services. The frontend loads its Next.js environment files; Python modules use `python-dotenv`, and the headless entry point imports `dotenv/config`. Never put private values in `NEXT_PUBLIC_*` variables: those are exposed to the browser.

The following variable names are read directly by application code. Set the relevant group in each process that uses it.

| Area | Variables and requirements |
| --- | --- |
| Browser endpoints (`frontend`) | `NEXT_PUBLIC_BASE_URL`, `NEXT_PUBLIC_BACKEND_URL`, `NEXT_PUBLIC_REST_API_URL`, `NEXT_PUBLIC_CLOUDFRONT_DOMAIN`, `NEXT_PUBLIC_COGNITO_ID`. For local services, use your configured HTTPS origins on ports 3000, 8000, and 8001; CloudFront values are hostnames without a scheme. |
| Session auth (`frontend`) | `NEXTAUTH_SECRET`, `AUTH_COGNITO_ISSUER`, `AUTH_COGNITO_SECRET`. The latter two are read by the installed Auth.js provider configuration; the client ID is supplied explicitly through `NEXT_PUBLIC_COGNITO_ID`. Configure allowed callback/logout URLs for your own Cognito app. |
| Session auth (`backend`) | `AUTHJS_SECRET`, `AUTHJS_SALT`, `SESSION_TOKEN_NAME`. The secret must match the frontend session secret. The frontend's configured cookie name is `__Secure-next-auth.session-token`; align both the backend cookie lookup and Auth.js derivation salt with that configuration. |
| AWS / persistence (all three services) | `AWS_REGION`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `DYNAMODB_TABLE_NAME`, `SOURCES_BUCKET_NAME`. Configure credentials for your own resources; some paths explicitly read access-key variables rather than relying only on the AWS default credential chain. |
| Internal renderer (`frontend`, `backend`) | `HEADLESS_API_URL`, `HEADLESS_API_INTERNAL_KEY`. Use the headless HTTPS origin (port 3003 by default), with the same internal key configured in the renderer. |
| Renderer (`headless-api`) | `HEADLESS_API_INTERNAL_KEY`, `NEXT_PUBLIC_BASE_URL` (CORS origin), `PORT` (optional; defaults to 3003), `CLOUDFRONT_DOMAIN`, `CLOUDFRONT_PRIVATE_KEY`, `CLOUDFRONT_KEY_PAIR_ID`, `INTER_TTF_URL`, `EXPORT_MP4_LAMBDA_NAME`. The Lambda name is checked at import time, so it is required for service startup even if you only intend to use PDF export. |
| Frontend asset signing | `CLOUDFRONT_PRIVATE_KEY`, `CLOUDFRONT_KEY_PAIR_ID`, together with `NEXT_PUBLIC_CLOUDFRONT_DOMAIN`. |
| Backend models | `PORTKEY_API_KEY`, `OPENAI_API_KEY`, `CHAT_MODEL_OPENAI_ID`, `SLIDES_CHAT_MODEL_OPENAI_ID`. `SAI_API_KEY` and optional `API_HOST` select/configure Stability AI image generation. |
| Optional diagnostics | `DISABLE_SSL_VERIFY` is read by frontend/backend outbound requests; prefer trusted local certificates and leave verification enabled. `SAVE_PAYLOAD_FOR_DEBUGGING=true` makes the renderer save its video Lambda payload locally. |

Additional provider setup is required: Brave Search is instantiated through `AsyncBrave()` without explicit credentials in the application, so configure it according to the installed SDK. Several Portkey virtual-key identifiers and model names are hard-coded in `backend/llm_clients.py`, `backend/research/summarize.py`, `backend/outline/label_documents_and_extract_topics.py`, and `backend/slides/`. Adapt those references to your own provider configuration; setting an API key alone does not recreate the original gateway setup. They are not additional environment variables.

Provision DynamoDB keys/indexes against [`shared_ts/utils/dynamodb-interface.ts`](shared_ts/utils/dynamodb-interface.ts) and [`backend/dynamodb_interface.py`](backend/dynamodb_interface.py). Configure S3/CloudFront access and signing for your own bucket and domain. The SAM template includes original resource names that must be adapted before any separate infrastructure deployment.

### 3. Prepare HTTPS and origins

The frontend development command enables experimental HTTPS. Both Python commands below expect `backend/server.key` and `backend/server.crt`; the headless server expects `headless-api/localhost+2-key.pem` and `headless-api/localhost+2.pem`. Generate your own trusted certificates for the hostnames you will use. For example, with `mkcert` already installed:

```bash
mkcert -install
mkcert -key-file backend/server.key -cert-file backend/server.crt localhost 127.0.0.1 ::1
mkcert -key-file headless-api/localhost+2-key.pem -cert-file headless-api/localhost+2.pem localhost 127.0.0.1 ::1
```

`backend/server.crt` is tracked; generating a local certificate replaces that public certificate in your working tree. Keep local certificate changes out of commits. Private key files are ignored by Git.

Check [`backend/socketio_setup.py`](backend/socketio_setup.py): its origin allowlist includes HTTP localhost and the original domain, but not HTTPS localhost. Add your actual frontend HTTPS origin for local Socket.IO connections. Also inspect Cognito login/logout URLs in the frontend for references to the original authentication domain. These are required local adaptations, not settings handled entirely by the environment files.

### 4. Start the application

Run each command in a separate terminal, starting from the repository root:

```bash
# Frontend: https://localhost:3000
cd frontend
npm run dev
```

```bash
# Socket.IO backend: https://localhost:8000
cd backend
poetry run uvicorn main:app --reload --host 127.0.0.1 --port 8000 --ssl-keyfile server.key --ssl-certfile server.crt
```

```bash
# REST backend: https://localhost:8001
cd backend
poetry run uvicorn rest_api:app --host 127.0.0.1 --port 8001 --ssl-keyfile server.key --ssl-certfile server.crt
```

```bash
# Internal rendering API: https://localhost:3003
cd headless-api
npm run dev
```

Keep the backend working directory as `backend/`: icon data and other assets use relative paths. Icon embeddings are omitted from Git; the icon-search module generates them with model API calls when its local cache is missing, which can make initial startup slow and incur usage costs.

[`start.sh`](start.sh) is a tmux convenience launcher for these four processes, using externally reachable Python bind addresses. It terminates any existing tmux session named `shiroai` before starting another. The individual commands above make the processes easier to inspect.

The internal renderer requires `x-api-key` and `x-user-id` request headers, including for `/test-connection`. Its key is a server-side shared secret; browser clients should go through the authenticated frontend actions.

## Using Shiro

After configuring Cognito and signing in, create a presentation and work through the ideate, research, outline, and slides screens. Add research sources before generating the outline; refine the outline before generating slides. The slides screen supports editing and narration-script generation, with PDF and video export controls.

Presentation records, sources, topics, slides, and workflow state are stored in DynamoDB; extracted content, embeddings, images, rendered files, and audio use S3. Export actions return CloudFront links to generated files; asset access uses CloudFront signing and signed cookies. The video path builds a slide/audio manifest and invokes the configured Lambda to write the MP4 back to S3. See the [video function](sam-lambda/generate-video/generate_video/app.py) and its [SAM template](sam-lambda/generate-video/template.yaml) for that separate component.

## Development and checks

The repository defines these commands, run from the root after installing dependencies:

```bash
npm run build --workspace frontend
npm run lint --workspace frontend
npm run build --workspace headless-api
npm run build:css --workspace headless-api
```

Verification on Node 24.2.0 / npm 11.3.0: `npm ci --ignore-scripts` succeeded, and the headless JavaScript bundle built with warnings about CommonJS output and `import.meta`. The frontend build stops at a deprecated page-config export in `frontend/src/app/api/upload_image/route.ts`; frontend lint reports existing JSX and hook errors. Headless CSS generation fails because its CommonJS-style PostCSS config is loaded as an ES module. These application issues need repair before treating the build commands as a passing release gate. The headless bundle completing does not establish that its compiled startup path works. Browser downloads/install scripts and full service startup were not exercised during this documentation check.

Tests are not a self-contained offline suite. Frontend and backend DynamoDB tests perform real reads/writes/deletes; headless service tests target an original HTTPS domain and fixed test presentation/user identifiers in `headless-api/tests/service-tests/test-constants.ts`. Retarget integration tests to disposable resources before running them. There is no checked-in GitHub Actions CI workflow.

The declared JavaScript test entry points are `npm test --workspace frontend` and `npm test --workspace headless-api`. Backend tests live in `backend/tests/`; some imports/test assumptions may need repair before they run against the current models. The Lambda directory contains SAM starter tests that should be checked against the current non-API-Gateway video handler before reuse.

## Limitations and project status

- This is a service-dependent 2024 prototype, not a turnkey local application. Dependency installation, complete local startup, and end-to-end generation need verification in your own configured environment.
- Provider virtual keys, model identifiers, authentication URLs, origins, and some infrastructure names are deployment-specific. Their original availability is not established.
- Video export is labeled beta in the UI. PPTX, sharing, speaker notes, and reference inclusion are unfinished as described above.
- Model output, extracted research, source attribution, and generated visuals need human review before presenting or publishing.
- Bundled fonts, icon data, external dependencies, and generated/source media retain their applicable third-party terms; a repository license does not replace those terms.

## License

ShiroAI is licensed under the [ISC License](LICENSE). Copyright © 2024 Noah Youngs. Third-party dependencies and bundled assets remain subject to their own applicable terms and notices.
