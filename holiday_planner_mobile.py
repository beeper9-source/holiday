from flask import Flask, render_template, request, jsonify, redirect, url_for
import json
import os
from datetime import datetime, timedelta

app = Flask(__name__)

# 추석연휴 기간 설정 (10월 2일 ~ 10월 12일)
holiday_start = datetime(2025, 10, 2)
holiday_end = datetime(2025, 10, 12)
holiday_days = [(holiday_start + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(11)]

def load_data():
    """데이터 로드"""
    if os.path.exists('holiday_data.json'):
        try:
            with open('holiday_data.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_data(data):
    """데이터 저장"""
    with open('holiday_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@app.route('/')
def index():
    """메인 페이지"""
    return render_template('index.html', holiday_days=holiday_days)

@app.route('/api/data')
def get_data():
    """전체 데이터 조회"""
    return jsonify(load_data())

@app.route('/api/data/<date>')
def get_day_data(date):
    """특정 날짜 데이터 조회"""
    data = load_data()
    if date not in data:
        data[date] = {'plans': [], 'achievements': [], 'rating': 0, 'memo': ''}
        save_data(data)
    return jsonify(data[date])

@app.route('/api/plan', methods=['POST'])
def add_plan():
    """계획 추가"""
    data = request.json
    date = data['date']
    content = data['content']
    
    holiday_data = load_data()
    if date not in holiday_data:
        holiday_data[date] = {'plans': [], 'achievements': [], 'rating': 0, 'memo': ''}
    
    holiday_data[date]['plans'].append({
        'content': content,
        'completed': False,
        'created_at': datetime.now().strftime('%H:%M')
    })
    
    save_data(holiday_data)
    return jsonify({'success': True})

@app.route('/api/plan/<date>/<int:index>/complete', methods=['POST'])
def complete_plan(date, index):
    """계획 완료 처리"""
    holiday_data = load_data()
    if date in holiday_data and index < len(holiday_data[date]['plans']):
        holiday_data[date]['plans'][index]['completed'] = True
        save_data(holiday_data)
        return jsonify({'success': True})
    return jsonify({'success': False})

@app.route('/api/plan/<date>/<int:index>', methods=['DELETE'])
def delete_plan(date, index):
    """계획 삭제"""
    holiday_data = load_data()
    if date in holiday_data and index < len(holiday_data[date]['plans']):
        holiday_data[date]['plans'].pop(index)
        save_data(holiday_data)
        return jsonify({'success': True})
    return jsonify({'success': False})

@app.route('/api/achievement', methods=['POST'])
def add_achievement():
    """실적 추가"""
    data = request.json
    date = data['date']
    content = data['content']
    
    holiday_data = load_data()
    if date not in holiday_data:
        holiday_data[date] = {'plans': [], 'achievements': [], 'rating': 0, 'memo': ''}
    
    holiday_data[date]['achievements'].append({
        'content': content,
        'created_at': datetime.now().strftime('%H:%M')
    })
    
    save_data(holiday_data)
    return jsonify({'success': True})

@app.route('/api/achievement/<date>/<int:index>', methods=['DELETE'])
def delete_achievement(date, index):
    """실적 삭제"""
    holiday_data = load_data()
    if date in holiday_data and index < len(holiday_data[date]['achievements']):
        holiday_data[date]['achievements'].pop(index)
        save_data(holiday_data)
        return jsonify({'success': True})
    return jsonify({'success': False})

@app.route('/api/rating', methods=['POST'])
def save_rating():
    """평가 저장"""
    data = request.json
    date = data['date']
    rating = data['rating']
    
    holiday_data = load_data()
    if date not in holiday_data:
        holiday_data[date] = {'plans': [], 'achievements': [], 'rating': 0, 'memo': ''}
    
    holiday_data[date]['rating'] = rating
    save_data(holiday_data)
    return jsonify({'success': True})

@app.route('/api/memo', methods=['POST'])
def save_memo():
    """메모 저장"""
    data = request.json
    date = data['date']
    memo = data['memo']
    
    holiday_data = load_data()
    if date not in holiday_data:
        holiday_data[date] = {'plans': [], 'achievements': [], 'rating': 0, 'memo': ''}
    
    holiday_data[date]['memo'] = memo
    save_data(holiday_data)
    return jsonify({'success': True})

@app.route('/api/stats')
def get_stats():
    """통계 조회"""
    holiday_data = load_data()
    
    total_plans = sum(len(data.get('plans', [])) for data in holiday_data.values())
    completed_plans = sum(
        sum(1 for plan in data.get('plans', []) if plan.get('completed', False))
        for data in holiday_data.values()
    )
    total_achievements = sum(len(data.get('achievements', [])) for data in holiday_data.values())
    avg_rating = sum(data.get('rating', 0) for data in holiday_data.values()) / max(len(holiday_data), 1)
    
    return jsonify({
        'total_plans': total_plans,
        'completed_plans': completed_plans,
        'completion_rate': (completed_plans / max(total_plans, 1)) * 100,
        'total_achievements': total_achievements,
        'avg_rating': avg_rating
    })

if __name__ == '__main__':
    # templates 폴더 생성
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    app.run(host='0.0.0.0', port=5000, debug=True)
