"""
Vercel Python 함수 진입점.
ASGI 앱은 `app` 이름으로 노출 (Vercel 런타임이 로드).
"""
import sys
from pathlib import Path

_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from app.main import app  # noqa: E402,F401
