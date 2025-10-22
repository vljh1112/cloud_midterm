from flask import Flask, jsonify, request, send_file, abort
from pathlib import Path
import json, os

app = Flask(__name__)

DATA_PATH = Path("/app/data/data.json")
DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
if not DATA_PATH.exists():
    DATA_PATH.write_text("[]", encoding="utf-8")

@app.get("/healthz")
def healthz():
    return "ok", 200

@app.get("/api/records")
def get_records():
    """GET /api/records : 저장된 데이터를 JSON으로 반환"""
    try:
        data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
        return jsonify(data)
    except json.JSONDecodeError:
        # 파일이 손상되었을 경우 빈 리스트 반환
        return jsonify([])
    except FileNotFoundError:
        return jsonify([])

@app.post("/api/records")
def add_record():
    """POST /api/records : {height, weight}를 받아 유효성 검사 후 누적 저장"""
    payload = request.get_json()

    # 유효성 검사
    if not payload or 'height' not in payload or 'weight' not in payload:
        abort(400, description="Invalid input. 'height' and 'weight' are required.")
    
    try:
        # 숫자 타입인지도 확인 (선택 사항이지만 권장)
        height = float(payload['height'])
        weight = float(payload['weight'])
    except ValueError:
        abort(400, description="Invalid input. 'height' and 'weight' must be numbers.")

    new_record = {"height": height, "weight": weight}

    # 데이터 읽기, 추가, 저장
    try:
        data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, FileNotFoundError):
        data = [] # 파일이 비어있거나 없으면 새 리스트 시작
        
    data.append(new_record)
    
    # JSON 파일 쓰기
    DATA_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    
    return jsonify(new_record), 201

@app.get("/api/download")
def download_json():
    """GET /api/download : data.json 파일 다운로드"""
    if not DATA_PATH.exists():
        abort(404, description="File not found.")
        
    return send_file(
        DATA_PATH,
        mimetype='application/json',
        as_attachment=True,
        download_name='data.json'
    )

if __name__ == "__main__":
    # 적절한 포트(예: 5000)로 0.0.0.0 에서 실행
    app.run(host="0.0.0.0", port=5000)