# file-management

현재 가상환경이 활성화되어 있는데도 (`(.venv)` 표시가 있음), 시스템의 전역 파이썬이 인식되고 있네요.

이 문제를 해결하기 위해 다음 단계들을 시도해보세요:

1. 먼저 현재 가상환경을 비활성화합니다:

```bash
deactivate
```

2. 기존 가상환경 폴더를 삭제합니다:

```bash
rm -r .venv
```

3. 새로운 가상환경을 생성할 때 파이썬 전체 경로를 지정해서 만듭니다:

```bash
C:\Python312\python.exe -m venv .venv
```

4. 가상환경을 다시 활성화합니다:

```bash
.venv\Scripts\activate
```

5. 다시 파이썬 경로를 확인합니다:

```bash
where python
```

이제 첫 번째 경로가 다음과 같이 나와야 합니다:

```
C:\Users\WEVEN_PC\Desktop\project\file-management\back-end\.venv\Scripts\python.exe
```

만약 여전히 문제가 있다면, 시스템 환경 변수의 PATH 설정을 확인해볼 필요가 있습니다. Windows 검색에서 "환경 변수"를 검색하여 PATH 변수에서 파이썬 관련 경로들의 우선순위를 확인해보세요.

아, Git Bash에서는 Windows 경로를 다르게 표현해야 합니다. Git Bash는 Unix 스타일 경로를 사용하기 때문입니다.

다음과 같이 시도해보세요:

1. Windows 경로를 Git Bash 스타일로 변경:

```bash
"/c/Python312/python.exe" -m venv .venv
```

또는:

```bash
python -m venv .venv
```

2. 가상환경 활성화 (Git Bash용):

```bash
source .venv/Scripts/activate
```

3. 확인:

```bash
which python
```

만약 여전히 문제가 있다면, cmd나 PowerShell을 사용하는 것이 더 안정적일 수 있습니다.

Windows PowerShell에서는:

```powershell
C:\Python312\python.exe -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Windows cmd에서는:

```cmd
C:\Python312\python.exe -m venv .venv
.\.venv\Scripts\activate
```

Git Bash를 계속 사용하고 싶으시다면, 경로에 공백이나 특수문자가 없는지 확인하고, 경로를 따옴표로 감싸서 사용하세요.

설치가 완료된 후 uvicorn 명령어가 정상적으로 실행될 것입니다. 만약 pip 명령어 자체가 인식되지 않는다면 다음과 같이 시도해보세요:

```bash
python -m pip install fastapi uvicorn
```
