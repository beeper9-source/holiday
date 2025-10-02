import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import os

# 페이지 설정
st.set_page_config(
    page_title="추석연휴 계획 관리",
    page_icon="🎑",
    layout="wide"
)

# 세션 상태 초기화
if 'holiday_data' not in st.session_state:
    st.session_state.holiday_data = {}

# 추석연휴 기간 설정 (10월 2일 ~ 10월 12일)
holiday_start = datetime(2024, 10, 2)
holiday_end = datetime(2024, 10, 12)
holiday_days = [(holiday_start + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(11)]

def load_data():
    """데이터 로드"""
    if os.path.exists('holiday_data.json'):
        with open('holiday_data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_data(data):
    """데이터 저장"""
    with open('holiday_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def initialize_day_data(date):
    """일자별 데이터 초기화"""
    if date not in st.session_state.holiday_data:
        st.session_state.holiday_data[date] = {
            'plans': [],
            'achievements': [],
            'notes': '',
            'rating': 0
        }

def main():
    st.title("🎑 추석연휴 계획 관리 시스템")
    st.markdown("**2024년 10월 2일 ~ 10월 12일 (11일간)**")
    
    # 데이터 로드
    if not st.session_state.holiday_data:
        st.session_state.holiday_data = load_data()
    
    # 사이드바 - 네비게이션
    st.sidebar.title("📅 메뉴")
    page = st.sidebar.selectbox(
        "페이지 선택",
        ["📝 일자별 계획 입력", "✅ 실적 입력", "📊 진행률 대시보드", "📋 전체 현황"]
    )
    
    if page == "📝 일자별 계획 입력":
        plan_input_page()
    elif page == "✅ 실적 입력":
        achievement_input_page()
    elif page == "📊 진행률 대시보드":
        dashboard_page()
    elif page == "📋 전체 현황":
        overview_page()

def plan_input_page():
    st.header("📝 일자별 계획 입력")
    
    # 날짜 선택
    selected_date = st.selectbox(
        "날짜를 선택하세요",
        holiday_days,
        format_func=lambda x: f"{x} ({datetime.strptime(x, '%Y-%m-%d').strftime('%m월 %d일 %A')})"
    )
    
    initialize_day_data(selected_date)
    
    st.subheader(f"📅 {selected_date} 계획")
    
    # 계획 입력
    col1, col2 = st.columns([2, 1])
    
    with col1:
        new_plan = st.text_input("새로운 계획을 입력하세요", key=f"plan_{selected_date}")
        
        if st.button("계획 추가", key=f"add_plan_{selected_date}"):
            if new_plan:
                st.session_state.holiday_data[selected_date]['plans'].append({
                    'content': new_plan,
                    'created_at': datetime.now().strftime('%H:%M'),
                    'completed': False
                })
                save_data(st.session_state.holiday_data)
                st.success("계획이 추가되었습니다!")
                st.rerun()
    
    with col2:
        if st.button("데이터 저장", key=f"save_{selected_date}"):
            save_data(st.session_state.holiday_data)
            st.success("데이터가 저장되었습니다!")
    
    # 기존 계획 목록
    if st.session_state.holiday_data[selected_date]['plans']:
        st.subheader("📋 등록된 계획")
        for i, plan in enumerate(st.session_state.holiday_data[selected_date]['plans']):
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                status = "✅" if plan['completed'] else "⏳"
                st.write(f"{status} {plan['content']} (등록: {plan['created_at']})")
            
            with col2:
                if st.button("완료", key=f"complete_{selected_date}_{i}"):
                    st.session_state.holiday_data[selected_date]['plans'][i]['completed'] = True
                    save_data(st.session_state.holiday_data)
                    st.rerun()
            
            with col3:
                if st.button("삭제", key=f"delete_{selected_date}_{i}"):
                    st.session_state.holiday_data[selected_date]['plans'].pop(i)
                    save_data(st.session_state.holiday_data)
                    st.rerun()

def achievement_input_page():
    st.header("✅ 실적 입력")
    
    # 날짜 선택
    selected_date = st.selectbox(
        "날짜를 선택하세요",
        holiday_days,
        format_func=lambda x: f"{x} ({datetime.strptime(x, '%Y-%m-%d').strftime('%m월 %d일 %A')})",
        key="achievement_date"
    )
    
    initialize_day_data(selected_date)
    
    st.subheader(f"📅 {selected_date} 실적")
    
    # 실적 입력
    col1, col2 = st.columns([2, 1])
    
    with col1:
        new_achievement = st.text_input("새로운 실적을 입력하세요", key=f"achievement_{selected_date}")
        
        if st.button("실적 추가", key=f"add_achievement_{selected_date}"):
            if new_achievement:
                st.session_state.holiday_data[selected_date]['achievements'].append({
                    'content': new_achievement,
                    'created_at': datetime.now().strftime('%H:%M')
                })
                save_data(st.session_state.holiday_data)
                st.success("실적이 추가되었습니다!")
                st.rerun()
    
    with col2:
        if st.button("데이터 저장", key=f"save_achievement_{selected_date}"):
            save_data(st.session_state.holiday_data)
            st.success("데이터가 저장되었습니다!")
    
    # 기존 실적 목록
    if st.session_state.holiday_data[selected_date]['achievements']:
        st.subheader("🏆 등록된 실적")
        for i, achievement in enumerate(st.session_state.holiday_data[selected_date]['achievements']):
            col1, col2 = st.columns([4, 1])
            
            with col1:
                st.write(f"🏆 {achievement['content']} (등록: {achievement['created_at']})")
            
            with col2:
                if st.button("삭제", key=f"delete_achievement_{selected_date}_{i}"):
                    st.session_state.holiday_data[selected_date]['achievements'].pop(i)
                    save_data(st.session_state.holiday_data)
                    st.rerun()
    
    # 하루 평가
    st.subheader("⭐ 하루 평가")
    rating = st.slider(
        "오늘 하루를 몇 점으로 평가하시나요?",
        min_value=0,
        max_value=10,
        value=st.session_state.holiday_data[selected_date]['rating'],
        key=f"rating_{selected_date}"
    )
    
    if st.button("평가 저장", key=f"save_rating_{selected_date}"):
        st.session_state.holiday_data[selected_date]['rating'] = rating
        save_data(st.session_state.holiday_data)
        st.success(f"평가가 저장되었습니다! ({rating}/10점)")
    
    # 메모
    st.subheader("📝 메모")
    notes = st.text_area(
        "오늘의 메모를 작성하세요",
        value=st.session_state.holiday_data[selected_date]['notes'],
        key=f"notes_{selected_date}"
    )
    
    if st.button("메모 저장", key=f"save_notes_{selected_date}"):
        st.session_state.holiday_data[selected_date]['notes'] = notes
        save_data(st.session_state.holiday_data)
        st.success("메모가 저장되었습니다!")

def dashboard_page():
    st.header("📊 진행률 대시보드")
    
    # 전체 통계
    col1, col2, col3, col4 = st.columns(4)
    
    total_plans = sum(len(data.get('plans', [])) for data in st.session_state.holiday_data.values())
    completed_plans = sum(
        sum(1 for plan in data.get('plans', []) if plan.get('completed', False))
        for data in st.session_state.holiday_data.values()
    )
    total_achievements = sum(len(data.get('achievements', [])) for data in st.session_state.holiday_data.values())
    avg_rating = sum(data.get('rating', 0) for data in st.session_state.holiday_data.values()) / max(len(st.session_state.holiday_data), 1)
    
    with col1:
        st.metric("총 계획 수", total_plans)
    
    with col2:
        completion_rate = (completed_plans / max(total_plans, 1)) * 100
        st.metric("완료율", f"{completion_rate:.1f}%")
    
    with col3:
        st.metric("총 실적 수", total_achievements)
    
    with col4:
        st.metric("평균 평가", f"{avg_rating:.1f}/10")
    
    # 일자별 진행률 차트
    st.subheader("📈 일자별 진행률")
    
    chart_data = []
    for date in holiday_days:
        if date in st.session_state.holiday_data:
            data = st.session_state.holiday_data[date]
            plans = data.get('plans', [])
            completed = sum(1 for plan in plans if plan.get('completed', False))
            total = len(plans)
            completion_rate = (completed / max(total, 1)) * 100
            
            chart_data.append({
                '날짜': f"{datetime.strptime(date, '%Y-%m-%d').strftime('%m/%d')}",
                '완료율': completion_rate,
                '평가': data.get('rating', 0),
                '계획수': total,
                '완료수': completed
            })
        else:
            chart_data.append({
                '날짜': f"{datetime.strptime(date, '%Y-%m-%d').strftime('%m/%d')}",
                '완료율': 0,
                '평가': 0,
                '계획수': 0,
                '완료수': 0
            })
    
    df_chart = pd.DataFrame(chart_data)
    
    # 완료율 차트
    fig_completion = px.bar(
        df_chart,
        x='날짜',
        y='완료율',
        title='일자별 계획 완료율',
        color='완료율',
        color_continuous_scale='RdYlGn'
    )
    fig_completion.update_layout(height=400)
    st.plotly_chart(fig_completion, use_container_width=True)
    
    # 평가 점수 차트
    fig_rating = px.line(
        df_chart,
        x='날짜',
        y='평가',
        title='일자별 하루 평가 점수',
        markers=True
    )
    fig_rating.update_layout(height=400)
    st.plotly_chart(fig_rating, use_container_width=True)

def overview_page():
    st.header("📋 전체 현황")
    
    # 일자별 상세 현황
    for date in holiday_days:
        if date in st.session_state.holiday_data:
            data = st.session_state.holiday_data[date]
            
            with st.expander(f"📅 {date} ({datetime.strptime(date, '%Y-%m-%d').strftime('%m월 %d일 %A')})"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("📝 계획")
                    if data.get('plans'):
                        for plan in data['plans']:
                            status = "✅" if plan.get('completed', False) else "⏳"
                            st.write(f"{status} {plan['content']}")
                    else:
                        st.write("등록된 계획이 없습니다.")
                
                with col2:
                    st.subheader("🏆 실적")
                    if data.get('achievements'):
                        for achievement in data['achievements']:
                            st.write(f"🏆 {achievement['content']}")
                    else:
                        st.write("등록된 실적이 없습니다.")
                
                # 평가 및 메모
                st.subheader("⭐ 평가 및 메모")
                col3, col4 = st.columns(2)
                
                with col3:
                    st.write(f"**평가:** {data.get('rating', 0)}/10점")
                
                with col4:
                    if data.get('notes'):
                        st.write(f"**메모:** {data['notes']}")
                    else:
                        st.write("**메모:** 없음")
        else:
            with st.expander(f"📅 {date} ({datetime.strptime(date, '%Y-%m-%d').strftime('%m월 %d일 %A')}) - 데이터 없음"):
                st.write("아직 데이터가 입력되지 않았습니다.")

if __name__ == "__main__":
    main()
