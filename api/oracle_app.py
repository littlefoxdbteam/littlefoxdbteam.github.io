from flask import Flask, jsonify, request, session
from flask_cors import CORS
import cx_Oracle
import json
from datetime import datetime
import os
import hashlib

app = Flask(__name__)
CORS(app)  # GitHub Pages에서 API 호출 허용
app.secret_key = 'your-secret-key-here'  # 세션을 위한 시크릿 키

# 기본 Oracle DB 연결 설정 (선택사항)
DEFAULT_DB_CONFIG = {
    'host': 'localhost',
    'port': 1521,
    'service_name': 'XE'
}

# 연결 풀 (세션별로 저장)
connections = {}

def get_db_connection(connection_id=None):
    """Oracle DB 연결 함수 - 동적 연결 지원"""
    if connection_id and connection_id in connections:
        try:
            # 기존 연결이 유효한지 테스트
            conn = connections[connection_id]
            conn.ping()
            return conn
        except:
            # 연결이 끊어진 경우 제거
            del connections[connection_id]
    
    return None

@app.route('/api/connect', methods=['POST'])
def connect_oracle():
    """Oracle DB 연결"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        host = data.get('host', DEFAULT_DB_CONFIG['host'])
        port = data.get('port', DEFAULT_DB_CONFIG['port'])
        service_name = data.get('service_name', DEFAULT_DB_CONFIG['service_name'])
        
        if not username or not password:
            return jsonify({'error': '사용자명과 비밀번호가 필요합니다.'}), 400
        
        # 연결 문자열 생성
        dsn = f"{host}:{port}/{service_name}"
        
        # 연결 시도
        connection = cx_Oracle.connect(
            user=username,
            password=password,
            dsn=dsn,
            encoding='UTF-8'
        )
        
        # 연결 성공 시 연결 ID 생성 및 저장
        connection_id = hashlib.md5(f"{username}@{host}:{port}/{service_name}".encode()).hexdigest()
        connections[connection_id] = connection
        
        return jsonify({
            'success': True,
            'connection_id': connection_id,
            'message': 'Oracle DB 연결 성공!',
            'user': username,
            'host': host,
            'service_name': service_name
        })
        
    except Exception as e:
        return jsonify({'error': f'연결 실패: {str(e)}'}), 500

@app.route('/api/disconnect', methods=['POST'])
def disconnect_oracle():
    """Oracle DB 연결 해제"""
    try:
        data = request.get_json()
        connection_id = data.get('connection_id')
        
        if connection_id and connection_id in connections:
            connections[connection_id].close()
            del connections[connection_id]
            return jsonify({'success': True, 'message': '연결이 해제되었습니다.'})
        else:
            return jsonify({'error': '유효하지 않은 연결 ID입니다.'}), 400
            
    except Exception as e:
        return jsonify({'error': f'연결 해제 실패: {str(e)}'}), 500

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
        connection_id = data.get('connection_id')
        
        if not query:
            return jsonify({'error': '쿼리가 제공되지 않았습니다.'}), 400
        
        if not connection_id:
            return jsonify({'error': '연결 ID가 필요합니다. 먼저 DB에 연결해주세요.'}), 400
        
        connection = get_db_connection(connection_id)
        if not connection:
            return jsonify({'error': '유효하지 않은 연결입니다. 다시 연결해주세요.'}), 500
        
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
        
        return jsonify({
            'success': True,
            'data': results,
            'columns': columns,
            'row_count': len(results),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tables', methods=['POST'])
def get_tables():
    """사용 가능한 테이블 목록 조회"""
    try:
        data = request.get_json()
        connection_id = data.get('connection_id')
        
        if not connection_id:
            return jsonify({'error': '연결 ID가 필요합니다. 먼저 DB에 연결해주세요.'}), 400
        
        connection = get_db_connection(connection_id)
        if not connection:
            return jsonify({'error': '유효하지 않은 연결입니다. 다시 연결해주세요.'}), 500
        
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
        
        return jsonify({
            'success': True,
            'tables': tables,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/table-info', methods=['POST'])
def get_table_info():
    """특정 테이블의 구조 정보 조회"""
    try:
        data = request.get_json()
        table_name = data.get('table_name')
        connection_id = data.get('connection_id')
        
        if not table_name:
            return jsonify({'error': '테이블명이 필요합니다.'}), 400
        
        if not connection_id:
            return jsonify({'error': '연결 ID가 필요합니다. 먼저 DB에 연결해주세요.'}), 400
        
        connection = get_db_connection(connection_id)
        if not connection:
            return jsonify({'error': '유효하지 않은 연결입니다. 다시 연결해주세요.'}), 500
        
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
        
        return jsonify({
            'success': True,
            'table_name': table_name,
            'columns': columns,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sample-data', methods=['POST'])
def get_sample_data():
    """특정 테이블의 샘플 데이터 조회 (최대 10행)"""
    try:
        data = request.get_json()
        table_name = data.get('table_name')
        connection_id = data.get('connection_id')
        
        if not table_name:
            return jsonify({'error': '테이블명이 필요합니다.'}), 400
        
        if not connection_id:
            return jsonify({'error': '연결 ID가 필요합니다. 먼저 DB에 연결해주세요.'}), 400
        
        connection = get_db_connection(connection_id)
        if not connection:
            return jsonify({'error': '유효하지 않은 연결입니다. 다시 연결해주세요.'}), 500
        
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
    print("- POST /api/connect : Oracle DB 연결")
    print("- POST /api/disconnect : Oracle DB 연결 해제")
    print("- POST /api/query : Oracle 쿼리 실행")
    print("- POST /api/tables : 사용 가능한 테이블 목록")
    print("- POST /api/table-info : 테이블 구조 정보")
    print("- POST /api/sample-data : 테이블 샘플 데이터")
    app.run(debug=True, host='0.0.0.0', port=5001) 