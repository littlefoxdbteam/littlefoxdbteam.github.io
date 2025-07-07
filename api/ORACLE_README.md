# Oracle DB Flask API 서버

이 API 서버는 Oracle DB와 연동하여 쿼리 결과를 GitHub Pages에서 표시할 수 있도록 합니다.

## 설치 및 설정

### 1. Oracle Instant Client 설치
Oracle DB 연결을 위해 Oracle Instant Client가 필요합니다.

#### Windows:
1. [Oracle Instant Client Downloads](https://www.oracle.com/database/technologies/instant-client/winx64-downloads.html)에서 다운로드
2. `instantclient-basic-windows.x64-21.x.x.x.x.zip` 다운로드
3. 압축 해제 후 `C:\oracle\instantclient_21_x` 폴더에 저장
4. 환경 변수 PATH에 `C:\oracle\instantclient_21_x` 추가

#### Linux:
```bash
# Ubuntu/Debian
sudo apt-get install libaio1
wget https://download.oracle.com/otn_software/linux/instantclient/instantclient-basic-linuxx64.zip
unzip instantclient-basic-linuxx64.zip
export LD_LIBRARY_PATH=/path/to/instantclient:$LD_LIBRARY_PATH
```

### 2. 필요한 패키지 설치
```bash
pip install -r oracle_requirements.txt
```

### 3. Oracle DB 연결 설정
`oracle_app.py` 파일에서 DB_CONFIG 부분을 수정하세요:

```python
DB_CONFIG = {
    'user': 'your_username',          # Oracle 사용자명
    'password': 'your_password',      # Oracle 비밀번호
    'dsn': 'your_host:1521/your_service_name',  # Oracle 연결 문자열
    'encoding': 'UTF-8'
}
```

#### DSN 형식 예시:
- **TNS 형식:** `host:port/service_name`
- **EZConnect 형식:** `host:port/service_name`
- **TNS 파일 사용:** `tns_alias`

### 4. API 서버 실행
```bash
python oracle_app.py
```

서버가 `http://localhost:5001`에서 실행됩니다.

## API 엔드포인트

### 1. 서버 상태 확인
- **URL:** `GET /api/health`
- **설명:** API 서버가 정상 작동하는지 확인

### 2. 쿼리 실행
- **URL:** `POST /api/query`
- **설명:** Oracle SQL 쿼리를 실행
- **요청 본문:**
```json
{
    "query": "SELECT * FROM your_table WHERE ROWNUM <= 100"
}
```

### 3. 테이블 목록 조회
- **URL:** `GET /api/tables`
- **설명:** 사용 가능한 테이블 목록 조회

### 4. 테이블 구조 정보
- **URL:** `GET /api/table-info/<table_name>`
- **설명:** 특정 테이블의 컬럼 정보 조회

### 5. 샘플 데이터 조회
- **URL:** `GET /api/sample-data/<table_name>`
- **설명:** 특정 테이블의 샘플 데이터 조회 (최대 10행)

## 보안 주의사항

1. **데이터베이스 접속 정보 보호**
   - 환경 변수 사용 권장
   - `.env` 파일로 관리

2. **SQL 인젝션 방지**
   - 사용자 정의 쿼리는 개발/테스트 환경에서만 사용
   - 프로덕션에서는 미리 정의된 쿼리만 사용

3. **권한 관리**
   - Oracle 사용자는 필요한 최소 권한만 부여
   - SELECT 권한만 있는 사용자 계정 사용 권장

## 문제 해결

### 연결 오류
- Oracle Instant Client가 올바르게 설치되었는지 확인
- 환경 변수 PATH 설정 확인
- 방화벽 설정 확인
- Oracle 서버가 실행 중인지 확인

### 쿼리 오류
- 테이블명과 컬럼명 확인
- SQL 문법 확인
- 데이터베이스 권한 확인

### 성능 이슈
- 대용량 데이터 조회 시 LIMIT/ROWNUM 사용
- 인덱스 활용 확인
- 쿼리 최적화 필요 