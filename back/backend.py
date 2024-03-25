import os
import sys

import uvicorn
from fastapi import FastAPI, Request, Response, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

sys.path.append("./")
sys.path.append("./front")
sys.path.append("./back")

from back.config import *
from back.kakao import router as kakao_router  # 카카오 로그인 라우터 불러오기
from back.mongodb import router as mongo_router  # MongoDB 라우터 불러오기

MY_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "front", "jobits"
)  # 필요한 값에 접근하기 위해 경로 설정
ACCESS_TOKEN = None  # 토큰 저장
ID_TOKEN = None  # ID 토큰 : 로그인 여부 확인용

# redirect URI 자동 설정
app = FastAPI(docs_url="/documentation", redoc_url=None)
app.include_router(kakao_router, prefix="/kakao")
app.include_router(mongo_router, prefix="/users")
templates = Jinja2Templates(directory="front/templates")  # 템플릿 폴더 지정(HTML 파일 저장 폴더)

origins = [
    f"http://{INSIDE_IP}:{PORT}",
    f"http://{OUTSIDE_IP}:{PORT}" f"http://{OUTSIDE_IP}:{STREAMLIT_PORT}" f"http://localhost:{PORT}",
]
app.add_middleware(
    CORSMiddleware,
    # allow_origins=origins,
    allow_origins=["*"],  # 모든 출처 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# WebSocket
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_json("FAST API")
    # return


# 미들웨어 : 모든 Path 에서 동작
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    response = await call_next(request)
    return response


# 첫 시작 페이지
@app.get("/")
def read_root():
    return RedirectResponse(url=f"http://{OUTSIDE_IP}:{STREAMLIT_PORT}")


class AccessToken(BaseModel):
    access_token: str


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)  # 8000은 모두에게 배포로 설정

    # # HTTPS 연결용 - 구현 예정
    # uvicorn.run(app, host=INSIDE_IP, port=PORT, ssl_keyfile=KEY_FILE, ssl_certfile=CERT_FILE)
