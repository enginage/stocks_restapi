# Stocks Rest API

Supabase(Postgres)를 데이터 소스로 하는 **국내 고배당 ETF 시뮬레이션용 REST API**를 Vercel에서 제공합니다. 경로는 EarlyRetireLab FastAPI와 동일하게 `/api/v1/...` 입니다.

## 엔드포인트

| 설명 | Method | Path |
|------|--------|------|
| ETF 목록 | GET | `/api/v1/domestic-etfs?etf_type=high_dividend` |
| 공통코드 마스터 | GET | `/api/v1/common-code-masters` |
| 공통코드 상세 | GET | `/api/v1/common-code-details?master_id={id}` |
| 일봉(기준일 근처) | GET | `/api/v1/domestic-etfs-daily-chart/etf/{etf_id}/period?months_ago=12` |
| 일봉(최신) | GET | `/api/v1/domestic-etfs-daily-chart/etf/{etf_id}/latest` |
| 배당(기간) | GET | `/api/v1/domestic-etfs-dividend/etf/{etf_id}/period?months_ago=12` |
| 헬스 | GET | `/api/v1/health` |

추가: `GET /api/v1/domestic-etfs/{etf_id}`, `GET /api/v1/domestic-etfs-dividend/etf/{etf_id}` (전체 배당, 최대 1000건).

## Supabase 설정

1. **스키마 노출 (필수)**: PostgREST는 기본이 `public`만 허용합니다. `stock` / `basic` 테이블을 쓰려면 반드시 추가하세요.  
   **Supabase Dashboard** → **Project Settings** → **Data API** (또는 **API**) → **Exposed schemas**에 `stock`, `basic`을 입력 후 저장.  
   이걸 안 하면 `PGRST106` / `The schema must be one of the following: public, graphql_public` 오류가 납니다.  
   대안: `public` 스키마에 동일 테이블/뷰를 두고 `SUPABASE_SCHEMA_STOCK=public` 등으로 맞추기.

2. **스키마 권한 (Exposed schemas 추가 후에도 `42501 permission denied for schema stock` / `basic` 이면 필수)**  
   API가 쓰는 DB 역할에 스키마 `USAGE`와 테이블 `SELECT`를 줘야 합니다. **SQL Editor**에서 한 번 실행 (Supabase [Custom schemas 가이드](https://supabase.com/docs/guides/api/using-custom-schemas)와 동일 취지):

   ```sql
   -- stock
   GRANT USAGE ON SCHEMA stock TO anon, authenticated, service_role;
   GRANT SELECT ON ALL TABLES IN SCHEMA stock TO anon, authenticated, service_role;
   GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA stock TO anon, authenticated, service_role;
   ALTER DEFAULT PRIVILEGES IN SCHEMA stock GRANT SELECT ON TABLES TO anon, authenticated, service_role;

   -- basic
   GRANT USAGE ON SCHEMA basic TO anon, authenticated, service_role;
   GRANT SELECT ON ALL TABLES IN SCHEMA basic TO anon, authenticated, service_role;
   GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA basic TO anon, authenticated, service_role;
   ALTER DEFAULT PRIVILEGES IN SCHEMA basic GRANT SELECT ON TABLES TO anon, authenticated, service_role;
   ```

   - RestAPI는 **`SUPABASE_SERVICE_ROLE_KEY`** 를 쓰므로 `service_role` 권한이 핵심입니다.  
   - 이후에도 막히면 **Table Editor**에서 해당 테이블 → **RLS**: 서버 전용이면 RLS를 끄거나, `service_role`은 보통 RLS를 우회하지만 **스키마/테이블 GRANT**는 별개이므로 위 GRANT를 먼저 확인하세요.

3. **테이블** (EarlyRetireLab DB와 동일 구조 권장):
   - `stock.domestic_etfs`
   - `stock.domestic_etfs_daily_chart`
   - `stock.domestic_etfs_dividend`
   - `basic.common_code_master`
   - `basic.common_code_detail`
4. **환경 변수** (Vercel / 로컬): `.env.example` 참고.
   - `SUPABASE_URL`은 **Dashboard → Settings → API의 Project URL** (`https://xxxxx.supabase.co`)만 사용합니다. `postgresql://` 풀러 주소는 PostgREST 클라이언트에 넣을 수 없습니다.
   - `SUPABASE_SERVICE_ROLE_KEY`는 **service_role** 키(비밀)를 넣어야 합니다. 비어 있으면 500이 납니다.
   - 로컬에서 `uvicorn` 실행 시 `app/main.py`가 프로젝트 루트의 `.env`를 자동 로드합니다.

## Supabase 클라이언트 재사용

`supabase_client.py`에서 모듈 전역 `_supabase_client`와 `asyncio.Lock`으로 **요청마다 `create_client`를 호출하지 않습니다**. Vercel 웜 인스턴스에서는 동일 프로세스가 재사용됩니다.

## 로컬 실행

**포트**: EarlyRetireLab `backend-fastapi`는 보통 **8000**을 씁니다. RestAPI 로컬은 **8080**으로 두면 동시에 띄워도 충돌하지 않습니다. 프론트 기본값(`VITE_STOCKS_REST_API_URL` 미설정)도 `http://127.0.0.1:8080` 입니다.

```bash
cd D:\MyPjt\Stocks\RestAPI
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
# .env 에 Supabase 키 설정
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

- API: `http://127.0.0.1:8080/api/v1/health`

## Vercel 배포

1. 이 디렉터리(`RestAPI`)를 Vercel 프로젝트 루트로 연결.
2. 환경 변수에 `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY` 설정.
3. `api/index.py`가 ASGI `app`을 노출하므로 별도 빌드 커맨드 없이 배포 가능한 경우가 많습니다.  
   - 경로가 맞지 않으면 Vercel 대시보드의 Functions 로그에서 실제 `path`를 확인하고, 필요 시 `vercel.json`의 `rewrites`를 조정하세요.

## 웹 / Expo 연동

- EarlyRetireLab 일반 API: `VITE_API_BASE_URL` (기본 8000 — `backend-fastapi`).
- 고배당 ETF 시뮬레이션만 RestAPI: `VITE_STOCKS_REST_API_URL` (로컬 미설정 시 8080, 배포 시 Vercel RestAPI URL).

---

참고 스펙 문서: `EarlyRetireLab/docs/EXPO_DOMESTIC_HIGH_DIVIDEND_SIMULATION.md`

## 이전 `Serverless` 폴더

폴더가 다른 프로그램에서 사용 중이면 이름만 바꿀 수 없을 수 있습니다. `RestAPI`로 코드를 옮긴 뒤, IDE·터미널을 닫고 `D:\MyPjt\Stocks\Serverless`를 삭제하세요. 가상환경은 `RestAPI`에서 `python -m venv .venv`로 다시 만듭니다.
