@echo off

:: Install pyenv if not already installed
if not exist %USERPROFILE%\.pyenv (
    echo Installing pyenv...
    git clone https://github.com/pyenv-win/pyenv-win.git %USERPROFILE%\.pyenv
)

:: Add pyenv to the PATH
set PATH=%USERPROFILE%\.pyenv\pyenv-win\bin;%PATH%

:: Check if pyenv-win is installed successfully
if not exist %USERPROFILE%\.pyenv\pyenv-win\bin\pyenv.bat (
    echo Error: pyenv-win installation failed.
    exit /b 1
)

:: Install required Python version
echo Installing Python version 3.11.3...
pyenv install -s 3.11.3
pyenv global 3.11.3

:: Echo the Python version being used
echo Using Python version %PYENV_VERSION%

:: Create virtual environment
echo Creating virtual environment...
python -m venv venv

:: Activate virtual environment
echo Activating virtual environment...
venv\Scripts\activate

:: Install project dependencies
echo Installing project dependencies...
pip install -r requirements.txt

echo Setup complete. You can now start using the project!
