from flask import Flask, jsonify, request
from flask_cors import CORS
import cx_Oracle
import json
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)  # GitHub Pages에서 API 호출 허용

# Oracle DB 연결 설정
DB_CONFIG = {
    'user': 'your_username',          # Oracle 사용자명
    'password': 'your_password',      # Oracle 비밀번호
    'dsn': 'your_host:1521/your_service_name',  # Oracle 연결 문자열
    'encoding': 'UTF-8'
}

def get_db_connection():
    """Oracle DB 연결 함수"""
    try:
        connection = cx_Oracle.connect(**DB_CONFIG)
        return connection
    except Exception as e:
        print(f"Oracle DB 연결 오류: {e}")
        return None

@app.route('/api/health')
def health_check():
    """API 상태 확인"""
    return jsonify({'status': 'healthy', 'message': 'Oracle API 서버가 정상 작동 중입니다.'})

@app.route('/api/query', methods=['POST'])
def execute_query():
    """Oracle 쿼리 실행"""
    try:
        data = request.get_json()
        query = data.get('query')
        
        if not query:
            return jsonify({'error': '쿼리가 제공되지 않았습니다.'}), 400
        
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Oracle DB 연결 실패'}), 500
        
        cursor = connection.cursor()
        
        # 쿼리 실행
        cursor.execute(query)
        
        # 컬럼명 가져오기
        columns = [col[0] for col in cursor.description]
        
        # 결과 데이터 가져오기
        results = []
        for row in cursor.fetchall():
            # datetime 객체를 문자열로 변환
            row_data = []
            for value in row:
                if isinstance(value, datetime):
                    row_data.append(value.strftime('%Y-%m-%d %H:%M:%S'))
                else:
                    row_data.append(str(value) if value is not None else '')
            results.append(dict(zip(columns, row_data)))
        
        cursor.close()
        connection.close()
        
        return jsonify({
            'success': True,
            'data': results,
            'columns': columns,
            'row_count': len(results),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tables')
def get_tables():
    """사용 가능한 테이블 목록 조회"""
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Oracle DB 연결 실패'}), 500
        
        cursor = connection.cursor()
        
        # 사용자 테이블 목록 조회
        query = """
        SELECT table_name 
        FROM user_tables 
        ORDER BY table_name
        """
        
        cursor.execute(query)
        tables = [row[0] for row in cursor.fetchall()]
        
        cursor.close()
        connection.close()
        
        return jsonify({
            'success': True,
            'tables': tables,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/table-info/<table_name>')
def get_table_info(table_name):
    """특정 테이블의 구조 정보 조회"""
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Oracle DB 연결 실패'}), 500
        
        cursor = connection.cursor()
        
        # 테이블 컬럼 정보 조회
        query = """
        SELECT column_name, data_type, data_length, nullable
        FROM user_tab_columns 
        WHERE table_name = :table_name
        ORDER BY column_id
        """
        
        cursor.execute(query, table_name=table_name.upper())
        columns = []
        for row in cursor.fetchall():
            columns.append({
                'name': row[0],
                'type': row[1],
                'length': row[2],
                'nullable': row[3]
            })
        
        cursor.close()
        connection.close()
        
        return jsonify({
            'success': True,
            'table_name': table_name,
            'columns': columns,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sample-data/<table_name>')
def get_sample_data(table_name):
    """특정 테이블의 샘플 데이터 조회 (최대 10행)"""
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Oracle DB 연결 실패'}), 500
        
        cursor = connection.cursor()
        
        # 샘플 데이터 조회
        query = f"SELECT * FROM {table_name} WHERE ROWNUM <= 10"
        
        cursor.execute(query)
        
        # 컬럼명 가져오기
        columns = [col[0] for col in cursor.description]
        
        # 결과 데이터 가져오기
        results = []
        for row in cursor.fetchall():
            row_data = []
            for value in row:
                if isinstance(value, datetime):
                    row_data.append(value.strftime('%Y-%m-%d %H:%M:%S'))
                else:
                    row_data.append(str(value) if value is not None else '')
            results.append(dict(zip(columns, row_data)))
        
        cursor.close()
        connection.close()
        
        return jsonify({
            'success': True,
            'table_name': table_name,
            'data': results,
            'columns': columns,
            'row_count': len(results),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Oracle Flask API 서버를 시작합니다...")
    print("API 엔드포인트:")
    print("- GET /api/health : 서버 상태 확인")
    print("- POST /api/query : Oracle 쿼리 실행")
    print("- GET /api/tables : 사용 가능한 테이블 목록")
    print("- GET /api/table-info/<table_name> : 테이블 구조 정보")
    print("- GET /api/sample-data/<table_name> : 테이블 샘플 데이터")
    app.run(debug=True, host='0.0.0.0', port=5001) 