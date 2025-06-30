# MariaDB Flask API 서버

이 API 서버는 MariaDB와 연동하여 GitHub Pages에서 데이터를 표시할 수 있도록 합니다.

## 설치 및 설정

### 1. 필요한 패키지 설치
```bash
pip install -r requirements.txt
```

### 2. MariaDB 연결 설정
`app.py` 파일에서 DB_CONFIG 부분을 수정하세요:

```python
DB_CONFIG = {
    'host': 'your_mariadb_host',      # MariaDB 서버 주소
    'port': 3306,                     # MariaDB 포트 (기본값: 3306)
    'user': 'your_username',          # DB 사용자명
    'password': 'your_password',      # DB 비밀번호
    'database': 'your_database',      # DB 이름
    'charset': 'utf8mb4'
}
```

### 3. API 서버 실행
```bash
python app.py
```

서버가 `http://localhost:5000`에서 실행됩니다.

## API 엔드포인트

### 1. 서버 상태 확인
- **URL:** `GET /api/health`
- **설명:** API 서버가 정상 작동하는지 확인

### 2. 매출 통계
- **URL:** `GET /api/stats/sales`
- **설명:** 최근 30일간의 매출 및 주문 통계
- **필요 테이블:** `sales` (created_at, amount 컬럼 필요)

### 3. 사용자 통계
- **URL:** `GET /api/stats/users`
- **설명:** 전체 사용자, 활성 사용자, 신규 사용자 수
- **필요 테이블:** `users` (status, created_at 컬럼 필요)

### 4. 사용자 정의 쿼리
- **URL:** `POST /api/custom-query`
- **설명:** 원하는 SQL 쿼리를 실행
- **요청 본문:**
```json
{
    "query": "SELECT * FROM your_table LIMIT 10"
}
```

## 필요한 데이터베이스 테이블

### sales 테이블 (매출 통계용)
```sql
CREATE TABLE sales (
    id INT AUTO_INCREMENT PRIMARY KEY,
    amount DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### users 테이블 (사용자 통계용)
```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    status ENUM('active', 'inactive') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 배포 옵션

### 1. 로컬 개발용
- `python app.py`로 실행
- `http://localhost:5000`에서 접근

### 2. 무료 호스팅 서비스
- **Heroku:** `Procfile`과 `runtime.txt` 추가 필요
- **Railway:** GitHub 연동으로 자동 배포
- **Render:** 무료 티어로 배포 가능

### 3. VPS/클라우드 서버
- Ubuntu/CentOS 등에 Python 환경 구축
- nginx + gunicorn으로 프로덕션 배포

## 보안 주의사항

1. **데이터베이스 접속 정보 보호**
   - 환경 변수 사용 권장
   - `.env` 파일로 관리

2. **SQL 인젝션 방지**
   - 사용자 정의 쿼리는 개발/테스트 환경에서만 사용
   - 프로덕션에서는 미리 정의된 쿼리만 사용

3. **CORS 설정**
   - 필요한 도메인만 허용하도록 설정

## 문제 해결

### 연결 오류
- MariaDB 서버가 실행 중인지 확인
- 방화벽 설정 확인
- 사용자 권한 확인

### 쿼리 오류
- 테이블명과 컬럼명 확인
- SQL 문법 확인
- 데이터베이스 권한 확인 