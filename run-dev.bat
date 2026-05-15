@echo off
chcp 65001 >nul
echo =====================================
echo Mirae Mobility - Eagle Taxi Dev Server
echo =====================================
echo.

echo [1] 현재 PC의 IPv4 주소 확인
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /i "IPv4"') do (
   set IP=%%a
)
set IP=%IP: =%

echo.
echo 접속 주소:
echo Frontend Local: http://localhost:5173
echo Backend Local : http://localhost:8000
echo API Docs      : http://localhost:8000/docs
echo Network URL   : http://%IP%:5173
echo.

echo [2] Backend 서버 실행
start "Eagle Taxi Backend" cmd /k "cd backend && .venv\Scripts\activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

echo [3] Frontend 서버 실행
start "Eagle Taxi Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo 서버 실행 명령을 보냈습니다.
echo 브라우저에서 http://localhost:5173 으로 접속하세요.
echo 같은 Wi-Fi 접속자는 http://%IP%:5173 으로 접속하세요.
pause
