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

1. **스키마 노출**: Dashboard → Project Settings → API → `Exposed schemas`에 `stock`, `basic` 추가 (또는 `public`에 뷰 생성).
2. **테이블** (EarlyRetireLab DB와 동일 구조 권장):
   - `stock.domestic_etfs`
   - `stock.domestic_etfs_daily_chart`
   - `stock.domestic_etfs_dividend`
   - `basic.common_code_master`
   - `basic.common_code_detail`
3. **환경 변수** (Vercel / 로컬): `.env.example` 참고. 서버에서는 `SUPABASE_SERVICE_ROLE_KEY` 권장.

## Supabase 클라이언트 재사용

`supabase_client.py`에서 모듈 전역 `_supabase_client`와 `asyncio.Lock`으로 **요청마다 `create_client`를 호출하지 않습니다**. Vercel 웜 인스턴스에서는 동일 프로세스가 재사용됩니다.

## 로컬 실행

```bash
cd D:\MyPjt\Stocks\RestAPI
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env   # 값 채우기
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- API: `http://127.0.0.1:8000/api/v1/health`

## Vercel 배포

1. 이 디렉터리(`RestAPI`)를 Vercel 프로젝트 루트로 연결.
2. 환경 변수에 `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY` 설정.
3. `api/index.py`가 ASGI `app`을 노출하므로 별도 빌드 커맨드 없이 배포 가능한 경우가 많습니다.  
   - 경로가 맞지 않으면 Vercel 대시보드의 Functions 로그에서 실제 `path`를 확인하고, 필요 시 `vercel.json`의 `rewrites`를 조정하세요.

## 웹 / Expo 연동

EarlyRetireLab `VITE_API_BASE_URL` 또는 Expo `EXPO_PUBLIC_API_BASE_URL`을 배포 도메인으로 설정합니다 (예: `https://your-project.vercel.app`).

---

참고 스펙 문서: `EarlyRetireLab/docs/EXPO_DOMESTIC_HIGH_DIVIDEND_SIMULATION.md`

## 이전 `Serverless` 폴더

폴더가 다른 프로그램에서 사용 중이면 이름만 바꿀 수 없을 수 있습니다. `RestAPI`로 코드를 옮긴 뒤, IDE·터미널을 닫고 `D:\MyPjt\Stocks\Serverless`를 삭제하세요. 가상환경은 `RestAPI`에서 `python -m venv .venv`로 다시 만듭니다.
