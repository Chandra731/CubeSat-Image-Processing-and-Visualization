@echo off
setlocal EnableDelayedExpansion

:: Function to create a virtual environment and install dependencies
:setup_env
    set dir=%1
    set requirements_file=%2

    echo Setting up virtual environment for %dir%...
    cd %dir%
    python -m venv env
    call env\Scripts\activate
    pip install -r %requirements_file%
    call env\Scripts\deactivate
    cd ..
    goto :eof

:: Set up the frontend
call :setup_env "frontend" "requirements.txt"
echo Setting up frontend environment variables...
(
    echo FLASK_RUN_HOST=0.0.0.0
    echo FLASK_RUN_PORT=5000
) > frontend\.env

:: Set up the backend
call :setup_env "backend" "requirements.txt"
echo Setting up backend environment variables...
(
    echo FLASK_RUN_HOST=0.0.0.0
    echo FLASK_RUN_PORT=5001
    echo DATABASE_URL=postgresql://user:password@localhost/dbname
    echo CELERY_BROKER_URL=redis://localhost:6379/0
    echo CELERY_RESULT_BACKEND=redis://localhost:6379/0
) > backend\.env

:: Set up the AI model
call :setup_env "ai_model" "requirements.txt"
echo Setting up AI model environment variables...
(
    echo FLASK_RUN_HOST=0.0.0.0
    echo FLASK_RUN_PORT=8001
) > ai_model\.env

:: Instructions to run the applications
echo Setup complete! To run the applications, use the following commands:
echo.
echo Frontend:
echo cd frontend
echo call env\Scripts\activate
echo flask run
echo.
echo Backend:
echo cd backend
echo call env\Scripts\activate
echo flask run
echo.
echo AI Model:
echo cd ai_model
echo call env\Scripts\activate
echo flask run --port=8001

endlocal