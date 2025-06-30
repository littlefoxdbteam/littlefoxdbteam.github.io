from flask import Flask, jsonify, request
from flask_cors import CORS
import pymysql
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)  # GitHub Pages에서 API 호출 허용

# MariaDB 연결 설정
DB_CONFIG = {
    'host': '10.1.123.213',  # MariaDB 서버 주소
    'port': 8306,         # MariaDB 포트
    'user': 'dba_python',  # DB 사용자명
    'password': 'P@ssw0rd1!',  # DB 비밀번호
    'database': 'littlefox',  # DB 이름
    'charset': 'utf8mb4'
}

def get_db_connection():
    """MariaDB 연결 함수"""
    try:
        connection = pymysql.connect(**DB_CONFIG)
        return connection
    except Exception as e:
        print(f"DB 연결 오류: {e}")
        return None

@app.route('/api/health')
def health_check():
    """API 상태 확인"""
    return jsonify({'status': 'healthy', 'message': 'API 서버가 정상 작동 중입니다.'})

@app.route('/api/stats/sales')
def get_sales_stats():
    """매출 통계 데이터 조회"""
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'DB 연결 실패'}), 500
        
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        
        # 예시 쿼리 - 실제 테이블명과 컬럼명으로 수정 필요
        query = """
        SELECT 
            DATE(created_at) as date,
            SUM(amount) as total_sales,
            COUNT(*) as order_count
        FROM sales 
        WHERE created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
        GROUP BY DATE(created_at)
        ORDER BY date DESC
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        return jsonify({
            'success': True,
            'data': results,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats/users')
def get_user_stats():
    """사용자 통계 데이터 조회"""
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'DB 연결 실패'}), 500
        
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        
        # 예시 쿼리 - 실제 테이블명과 컬럼명으로 수정 필요
        query = """
        SELECT 
            COUNT(*) as total_users,
            COUNT(CASE WHEN status = 'active' THEN 1 END) as active_users,
            COUNT(CASE WHEN created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY) THEN 1 END) as new_users_week
        FROM users
        """
        
        cursor.execute(query)
        results = cursor.fetchone()
        
        cursor.close()
        connection.close()
        
        return jsonify({
            'success': True,
            'data': results,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/custom-query', methods=['POST'])
def execute_custom_query():
    """사용자 정의 쿼리 실행"""
    try:
        data = request.get_json()
        query = data.get('query')
        
        if not query:
            return jsonify({'error': '쿼리가 제공되지 않았습니다.'}), 400
        
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'DB 연결 실패'}), 500
        
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(query)
        results = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        return jsonify({
            'success': True,
            'data': results,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Flask API 서버를 시작합니다...")
    print("API 엔드포인트:")
    print("- GET /api/health : 서버 상태 확인")
    print("- GET /api/stats/sales : 매출 통계")
    print("- GET /api/stats/users : 사용자 통계")
    print("- POST /api/custom-query : 사용자 정의 쿼리")
    app.run(debug=True, host='0.0.0.0', port=5000) 