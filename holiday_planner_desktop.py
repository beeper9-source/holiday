import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import os
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd

class HolidayPlannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🎑 추석연휴 계획 관리 시스템")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        # 추석연휴 기간 설정 (10월 2일 ~ 10월 12일)
        self.holiday_start = datetime(2024, 10, 2)
        self.holiday_end = datetime(2024, 10, 12)
        self.holiday_days = [(self.holiday_start + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(11)]
        
        # 데이터 초기화
        self.holiday_data = self.load_data()
        
        # GUI 구성
        self.setup_gui()
        
        # 초기 데이터 로드
        self.load_day_data()
    
    def setup_gui(self):
        """GUI 구성"""
        # 메인 프레임
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 제목
        title_label = ttk.Label(main_frame, text="🎑 추석연휴 계획 관리 시스템", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        subtitle_label = ttk.Label(main_frame, text="2024년 10월 2일 ~ 10월 12일 (11일간)", 
                                 font=('Arial', 10))
        subtitle_label.grid(row=1, column=0, columnspan=3, pady=(0, 20))
        
        # 왼쪽 프레임 (입력/관리)
        left_frame = ttk.LabelFrame(main_frame, text="📝 계획 및 실적 관리", padding="10")
        left_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # 날짜 선택
        ttk.Label(left_frame, text="날짜 선택:").grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        self.date_var = tk.StringVar(value=self.holiday_days[0])
        self.date_combo = ttk.Combobox(left_frame, textvariable=self.date_var, 
                                     values=self.holiday_days, state="readonly", width=20)
        self.date_combo.grid(row=0, column=1, pady=(0, 10))
        self.date_combo.bind('<<ComboboxSelected>>', self.on_date_change)
        
        # 탭 노트북
        self.notebook = ttk.Notebook(left_frame)
        self.notebook.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # 계획 탭
        self.plan_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.plan_frame, text="📝 계획")
        self.setup_plan_tab()
        
        # 실적 탭
        self.achievement_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.achievement_frame, text="✅ 실적")
        self.setup_achievement_tab()
        
        # 평가 탭
        self.rating_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.rating_frame, text="⭐ 평가")
        self.setup_rating_tab()
        
        # 오른쪽 프레임 (차트/통계)
        right_frame = ttk.LabelFrame(main_frame, text="📊 진행률 및 통계", padding="10")
        right_frame.grid(row=2, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 통계 라벨
        self.stats_frame = ttk.Frame(right_frame)
        self.stats_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 차트 프레임
        self.chart_frame = ttk.Frame(right_frame)
        self.chart_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 버튼 프레임
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=(20, 0))
        
        ttk.Button(button_frame, text="💾 데이터 저장", command=self.save_data).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="🔄 새로고침", command=self.refresh_data).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="📊 차트 업데이트", command=self.update_charts).pack(side=tk.LEFT)
        
        # 그리드 가중치 설정
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        left_frame.columnconfigure(1, weight=1)
        left_frame.rowconfigure(1, weight=1)
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(1, weight=1)
    
    def setup_plan_tab(self):
        """계획 탭 설정"""
        # 새 계획 입력
        ttk.Label(self.plan_frame, text="새 계획:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.plan_entry = ttk.Entry(self.plan_frame, width=30)
        self.plan_entry.grid(row=0, column=1, pady=(0, 5))
        ttk.Button(self.plan_frame, text="추가", command=self.add_plan).grid(row=0, column=2, pady=(0, 5), padx=(5, 0))
        
        # 계획 목록
        ttk.Label(self.plan_frame, text="계획 목록:").grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=(10, 5))
        
        # 트리뷰로 계획 목록 표시
        columns = ('content', 'status', 'time')
        self.plan_tree = ttk.Treeview(self.plan_frame, columns=columns, show='headings', height=8)
        
        self.plan_tree.heading('content', text='계획 내용')
        self.plan_tree.heading('status', text='상태')
        self.plan_tree.heading('time', text='등록 시간')
        
        self.plan_tree.column('content', width=200)
        self.plan_tree.column('status', width=80)
        self.plan_tree.column('time', width=100)
        
        self.plan_tree.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # 스크롤바
        plan_scrollbar = ttk.Scrollbar(self.plan_frame, orient=tk.VERTICAL, command=self.plan_tree.yview)
        plan_scrollbar.grid(row=2, column=3, sticky=(tk.N, tk.S))
        self.plan_tree.configure(yscrollcommand=plan_scrollbar.set)
        
        # 버튼들
        button_frame = ttk.Frame(self.plan_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=(10, 0))
        
        ttk.Button(button_frame, text="완료 처리", command=self.complete_plan).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="삭제", command=self.delete_plan).pack(side=tk.LEFT)
        
        # 그리드 가중치
        self.plan_frame.columnconfigure(1, weight=1)
        self.plan_frame.rowconfigure(2, weight=1)
    
    def setup_achievement_tab(self):
        """실적 탭 설정"""
        # 새 실적 입력
        ttk.Label(self.achievement_frame, text="새 실적:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.achievement_entry = ttk.Entry(self.achievement_frame, width=30)
        self.achievement_entry.grid(row=0, column=1, pady=(0, 5))
        ttk.Button(self.achievement_frame, text="추가", command=self.add_achievement).grid(row=0, column=2, pady=(0, 5), padx=(5, 0))
        
        # 실적 목록
        ttk.Label(self.achievement_frame, text="실적 목록:").grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=(10, 5))
        
        # 트리뷰로 실적 목록 표시
        columns = ('content', 'time')
        self.achievement_tree = ttk.Treeview(self.achievement_frame, columns=columns, show='headings', height=8)
        
        self.achievement_tree.heading('content', text='실적 내용')
        self.achievement_tree.heading('time', text='등록 시간')
        
        self.achievement_tree.column('content', width=200)
        self.achievement_tree.column('time', width=100)
        
        self.achievement_tree.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # 스크롤바
        achievement_scrollbar = ttk.Scrollbar(self.achievement_frame, orient=tk.VERTICAL, command=self.achievement_tree.yview)
        achievement_scrollbar.grid(row=2, column=3, sticky=(tk.N, tk.S))
        self.achievement_tree.configure(yscrollcommand=achievement_scrollbar.set)
        
        # 버튼들
        button_frame = ttk.Frame(self.achievement_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=(10, 0))
        
        ttk.Button(button_frame, text="삭제", command=self.delete_achievement).pack(side=tk.LEFT)
        
        # 그리드 가중치
        self.achievement_frame.columnconfigure(1, weight=1)
        self.achievement_frame.rowconfigure(2, weight=1)
    
    def setup_rating_tab(self):
        """평가 탭 설정"""
        # 하루 평가
        ttk.Label(self.rating_frame, text="하루 평가 (0-10점):").grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        self.rating_var = tk.IntVar(value=0)
        self.rating_scale = ttk.Scale(self.rating_frame, from_=0, to=10, 
                                     orient=tk.HORIZONTAL, variable=self.rating_var)
        self.rating_scale.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.rating_label = ttk.Label(self.rating_frame, text="0점")
        self.rating_label.grid(row=0, column=2, pady=(0, 10), padx=(10, 0))
        
        # 평가 저장 버튼
        ttk.Button(self.rating_frame, text="평가 저장", command=self.save_rating).grid(row=1, column=0, columnspan=3, pady=(0, 20))
        
        # 메모
        ttk.Label(self.rating_frame, text="메모:").grid(row=2, column=0, columnspan=3, sticky=tk.W, pady=(0, 5))
        
        self.memo_text = scrolledtext.ScrolledText(self.rating_frame, height=6, width=40)
        self.memo_text.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # 메모 저장 버튼
        ttk.Button(self.rating_frame, text="메모 저장", command=self.save_memo).grid(row=4, column=0, columnspan=3)
        
        # 그리드 가중치
        self.rating_frame.columnconfigure(1, weight=1)
        self.rating_frame.rowconfigure(3, weight=1)
        
        # 스케일 값 변경 이벤트
        self.rating_scale.configure(command=self.on_rating_change)
    
    def on_rating_change(self, value):
        """평가 점수 변경 이벤트"""
        self.rating_label.config(text=f"{int(float(value))}점")
    
    def on_date_change(self, event=None):
        """날짜 변경 이벤트"""
        self.load_day_data()
    
    def load_day_data(self):
        """선택된 날짜의 데이터 로드"""
        selected_date = self.date_var.get()
        
        # 해당 날짜 데이터 초기화
        if selected_date not in self.holiday_data:
            self.holiday_data[selected_date] = {
                'plans': [],
                'achievements': [],
                'rating': 0,
                'memo': ''
            }
        
        # 계획 목록 업데이트
        self.update_plan_list()
        
        # 실적 목록 업데이트
        self.update_achievement_list()
        
        # 평가 및 메모 업데이트
        data = self.holiday_data[selected_date]
        self.rating_var.set(data.get('rating', 0))
        self.rating_label.config(text=f"{data.get('rating', 0)}점")
        self.memo_text.delete(1.0, tk.END)
        self.memo_text.insert(1.0, data.get('memo', ''))
    
    def update_plan_list(self):
        """계획 목록 업데이트"""
        # 기존 항목 삭제
        for item in self.plan_tree.get_children():
            self.plan_tree.delete(item)
        
        # 새 항목 추가
        selected_date = self.date_var.get()
        if selected_date in self.holiday_data:
            plans = self.holiday_data[selected_date].get('plans', [])
            for plan in plans:
                status = "완료" if plan.get('completed', False) else "진행중"
                self.plan_tree.insert('', tk.END, values=(
                    plan['content'],
                    status,
                    plan.get('created_at', '')
                ))
    
    def update_achievement_list(self):
        """실적 목록 업데이트"""
        # 기존 항목 삭제
        for item in self.achievement_tree.get_children():
            self.achievement_tree.delete(item)
        
        # 새 항목 추가
        selected_date = self.date_var.get()
        if selected_date in self.holiday_data:
            achievements = self.holiday_data[selected_date].get('achievements', [])
            for achievement in achievements:
                self.achievement_tree.insert('', tk.END, values=(
                    achievement['content'],
                    achievement.get('created_at', '')
                ))
    
    def add_plan(self):
        """계획 추가"""
        plan_text = self.plan_entry.get().strip()
        if not plan_text:
            messagebox.showwarning("경고", "계획 내용을 입력해주세요.")
            return
        
        selected_date = self.date_var.get()
        if selected_date not in self.holiday_data:
            self.holiday_data[selected_date] = {'plans': [], 'achievements': [], 'rating': 0, 'memo': ''}
        
        self.holiday_data[selected_date]['plans'].append({
            'content': plan_text,
            'completed': False,
            'created_at': datetime.now().strftime('%H:%M')
        })
        
        self.plan_entry.delete(0, tk.END)
        self.update_plan_list()
        messagebox.showinfo("성공", "계획이 추가되었습니다.")
    
    def add_achievement(self):
        """실적 추가"""
        achievement_text = self.achievement_entry.get().strip()
        if not achievement_text:
            messagebox.showwarning("경고", "실적 내용을 입력해주세요.")
            return
        
        selected_date = self.date_var.get()
        if selected_date not in self.holiday_data:
            self.holiday_data[selected_date] = {'plans': [], 'achievements': [], 'rating': 0, 'memo': ''}
        
        self.holiday_data[selected_date]['achievements'].append({
            'content': achievement_text,
            'created_at': datetime.now().strftime('%H:%M')
        })
        
        self.achievement_entry.delete(0, tk.END)
        self.update_achievement_list()
        messagebox.showinfo("성공", "실적이 추가되었습니다.")
    
    def complete_plan(self):
        """계획 완료 처리"""
        selection = self.plan_tree.selection()
        if not selection:
            messagebox.showwarning("경고", "완료할 계획을 선택해주세요.")
            return
        
        selected_date = self.date_var.get()
        item = self.plan_tree.item(selection[0])
        plan_content = item['values'][0]
        
        # 해당 계획 찾아서 완료 처리
        for plan in self.holiday_data[selected_date]['plans']:
            if plan['content'] == plan_content:
                plan['completed'] = True
                break
        
        self.update_plan_list()
        messagebox.showinfo("성공", "계획이 완료 처리되었습니다.")
    
    def delete_plan(self):
        """계획 삭제"""
        selection = self.plan_tree.selection()
        if not selection:
            messagebox.showwarning("경고", "삭제할 계획을 선택해주세요.")
            return
        
        if messagebox.askyesno("확인", "선택한 계획을 삭제하시겠습니까?"):
            selected_date = self.date_var.get()
            item = self.plan_tree.item(selection[0])
            plan_content = item['values'][0]
            
            # 해당 계획 삭제
            self.holiday_data[selected_date]['plans'] = [
                plan for plan in self.holiday_data[selected_date]['plans'] 
                if plan['content'] != plan_content
            ]
            
            self.update_plan_list()
            messagebox.showinfo("성공", "계획이 삭제되었습니다.")
    
    def delete_achievement(self):
        """실적 삭제"""
        selection = self.achievement_tree.selection()
        if not selection:
            messagebox.showwarning("경고", "삭제할 실적을 선택해주세요.")
            return
        
        if messagebox.askyesno("확인", "선택한 실적을 삭제하시겠습니까?"):
            selected_date = self.date_var.get()
            item = self.achievement_tree.item(selection[0])
            achievement_content = item['values'][0]
            
            # 해당 실적 삭제
            self.holiday_data[selected_date]['achievements'] = [
                achievement for achievement in self.holiday_data[selected_date]['achievements'] 
                if achievement['content'] != achievement_content
            ]
            
            self.update_achievement_list()
            messagebox.showinfo("성공", "실적이 삭제되었습니다.")
    
    def save_rating(self):
        """평가 저장"""
        selected_date = self.date_var.get()
        if selected_date not in self.holiday_data:
            self.holiday_data[selected_date] = {'plans': [], 'achievements': [], 'rating': 0, 'memo': ''}
        
        self.holiday_data[selected_date]['rating'] = self.rating_var.get()
        messagebox.showinfo("성공", f"평가가 저장되었습니다. ({self.rating_var.get()}/10점)")
    
    def save_memo(self):
        """메모 저장"""
        selected_date = self.date_var.get()
        if selected_date not in self.holiday_data:
            self.holiday_data[selected_date] = {'plans': [], 'achievements': [], 'rating': 0, 'memo': ''}
        
        self.holiday_data[selected_date]['memo'] = self.memo_text.get(1.0, tk.END).strip()
        messagebox.showinfo("성공", "메모가 저장되었습니다.")
    
    def update_charts(self):
        """차트 업데이트"""
        # 기존 차트 제거
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
        
        # 통계 계산
        total_plans = sum(len(data.get('plans', [])) for data in self.holiday_data.values())
        completed_plans = sum(
            sum(1 for plan in data.get('plans', []) if plan.get('completed', False))
            for data in self.holiday_data.values()
        )
        total_achievements = sum(len(data.get('achievements', [])) for data in self.holiday_data.values())
        avg_rating = sum(data.get('rating', 0) for data in self.holiday_data.values()) / max(len(self.holiday_data), 1)
        
        # 통계 라벨 업데이트
        for widget in self.stats_frame.winfo_children():
            widget.destroy()
        
        ttk.Label(self.stats_frame, text=f"총 계획 수: {total_plans}").grid(row=0, column=0, sticky=tk.W, padx=(0, 20))
        ttk.Label(self.stats_frame, text=f"완료율: {(completed_plans/max(total_plans,1)*100):.1f}%").grid(row=0, column=1, sticky=tk.W, padx=(0, 20))
        ttk.Label(self.stats_frame, text=f"총 실적 수: {total_achievements}").grid(row=1, column=0, sticky=tk.W, padx=(0, 20))
        ttk.Label(self.stats_frame, text=f"평균 평가: {avg_rating:.1f}/10").grid(row=1, column=1, sticky=tk.W, padx=(0, 20))
        
        # 차트 데이터 준비
        chart_data = []
        for date in self.holiday_days:
            if date in self.holiday_data:
                data = self.holiday_data[date]
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
        
        # 차트 생성
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6))
        
        # 완료율 차트
        dates = [item['날짜'] for item in chart_data]
        completion_rates = [item['완료율'] for item in chart_data]
        
        ax1.bar(dates, completion_rates, color='skyblue', alpha=0.7)
        ax1.set_title('일자별 계획 완료율')
        ax1.set_ylabel('완료율 (%)')
        ax1.set_ylim(0, 100)
        
        # 평가 점수 차트
        ratings = [item['평가'] for item in chart_data]
        
        ax2.plot(dates, ratings, marker='o', color='orange', linewidth=2, markersize=6)
        ax2.set_title('일자별 하루 평가 점수')
        ax2.set_ylabel('평가 점수')
        ax2.set_ylim(0, 10)
        
        plt.tight_layout()
        
        # 차트를 tkinter에 임베드
        canvas = FigureCanvasTkAgg(fig, self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def refresh_data(self):
        """데이터 새로고침"""
        self.load_day_data()
        self.update_charts()
        messagebox.showinfo("성공", "데이터가 새로고침되었습니다.")
    
    def load_data(self):
        """데이터 로드"""
        if os.path.exists('holiday_data.json'):
            try:
                with open('holiday_data.json', 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_data(self):
        """데이터 저장"""
        try:
            with open('holiday_data.json', 'w', encoding='utf-8') as f:
                json.dump(self.holiday_data, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("성공", "데이터가 저장되었습니다.")
        except Exception as e:
            messagebox.showerror("오류", f"데이터 저장 중 오류가 발생했습니다: {str(e)}")

def main():
    root = tk.Tk()
    app = HolidayPlannerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
