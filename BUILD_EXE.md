# EXE 파일 생성 가이드

## 📦 Windows에서 EXE 파일 만들기

### 방법 1: 자동 빌드 (권장)

```bash
# 1. 의존성 설치
pip install -r requirements.txt

# 2. build.bat 실행
build.bat
```

그러면 `dist\Strange-TicTacToe.exe` 파일이 생성됩니다!

### 방법 2: 수동 빌드

```bash
# 1. PyInstaller 설치
pip install PyInstaller

# 2. exe 파일 생성
pyinstaller --onefile --windowed --name "Strange-TicTacToe" game.py
```

## 🐧 Linux/Mac에서 EXE 파일 만들기

```bash
# 1. 의존성 설치
pip install -r requirements.txt

# 2. build.sh 실행
chmod +x build.sh
./build.sh
```

## ✨ 생성된 파일

- **dist/Strange-TicTacToe.exe** - 독립 실행형 exe 파일
- 다른 파일 설치 필요 없음!
- 어디든 복사해서 실행 가능

## 🚀 EXE 파일 실행

```bash
# 생성된 exe 파일을 더블클릭하거나
dist\Strange-TicTacToe.exe

# 또는 명령줄에서
.\dist\Strange-TicTacToe.exe
```

## ⚠️ Windows Defender 경고

PyInstaller로 생성한 exe 파일을 처음 실행할 때 Windows Defender에서 경고할 수 있습니다.
이는 정상적인 현상이며, "추가 정보" → "어쨌든 실행"을 클릭하면 됩니다.

## 🗑️ 빌드 파일 정리

생성 후 불필요한 파일들을 삭제할 수 있습니다:

```bash
rmdir /s build
del Strange-TicTacToe.spec
```

이렇게 하면 `dist` 폴더의 exe 파일만 남습니다!
