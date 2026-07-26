# 미션 5 — Docker / Jenkins CI·CD

미션 3(Backend) + 미션 4(Frontend)를 통합하고, nginx · Docker Compose · Jenkins로 로컬 배포합니다.

```
mission5/
├── backend/          # ← mission3
├── frontend/         # ← mission4
├── nginx/            # nginx.conf + Dockerfile (SPA + /api 프록시)
├── jenkins/          # 로컬 Jenkins (docker.sock)
├── docker-compose.yaml
├── Jenkinsfile
└── MISSION.md
```

| 항목 | URL |
|------|-----|
| UI | http://127.0.0.1:8005 |
| API health | http://127.0.0.1:8005/api/health |
| Swagger | http://127.0.0.1:8005/docs |
| Jenkins | http://127.0.0.1:8080 |

## 사전 준비

- Docker Desktop
- 모델 `final` (약 1.4GB) — GitHub에는 올리지 않음 (`model.safetensors` gitignore)

```bash
# 모델이 없으면 미션 3에서 동기화
for task in qa generation summary; do
  mkdir -p backend/outputs/$task
  cp -R ../mission3/outputs/$task/final backend/outputs/$task/final
done
```

## 로컬 Docker 배포

```bash
cd mission5
docker compose -f docker-compose.yaml up -d --build
docker compose ps
curl -s http://127.0.0.1:8005/api/health
```

중지:

```bash
docker compose -f docker-compose.yaml down
```

## GitHub + Jenkins CI/CD

### 1) GitHub 저장소

```bash
cd mission5
git init
git add .
git commit -m "feat: mission5 docker compose and jenkins pipeline"
# GitHub에서 빈 repo 생성 후
git branch -M main
git remote add origin https://github.com/<USER>/<REPO>.git
git push -u origin main
```

> `model.safetensors`는 용량 때문에 커밋되지 않습니다.  
> Jenkins 에이전트(또는 호스트)에 모델이 있어야 합니다. Pipeline `Ensure models` 단계가  
> `MODEL_SRC` 또는 `../mission3/outputs` 에서 자동 복사합니다.

### 2) 로컬 Jenkins 기동

```bash
cd mission5/jenkins
docker compose up -d --build

# 최초 비밀번호
docker compose exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
# → http://127.0.0.1:8080
```

플러그인: **Git**, **Pipeline**, **Docker Pipeline**(선택)

### 3) Pipeline Job

1. New Item → Pipeline
2. Pipeline → Definition: **Pipeline script from SCM**
3. SCM: Git → 저장소 URL
4. Script Path: `Jenkinsfile`
5. (선택) 환경변수 `MODEL_SRC=/models/mission3`  
   (`jenkins/docker-compose.yaml`이 mission3 outputs를 마운트함)
6. Build Now

성공 시: http://127.0.0.1:8005

## 구성 요약

| 서비스 | 역할 |
|--------|------|
| `backend` | FastAPI + 모델 (`:8000` 내부) |
| `nginx` | React 빌드 정적파일 + `/api` 프록시 (`:8005→80`) |

모델·소설 텍스트는 볼륨으로 마운트합니다.

```
./backend/outputs → /app/outputs
./backend/data/novels → /app/data/novels
```

## 개발 모드 (Docker 없이)

```bash
# backend
cd backend && uv sync && uv run python backend.py serve

# frontend
cd frontend && npm install && npm run dev
```
