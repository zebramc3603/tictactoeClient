import tkinter as tk
from tkinter import messagebox, ttk
import requests
import threading
import time
from typing import Optional, List

class TicTacToeGUI:
    def __init__(self, api_url="http://localhost:8000"):
        self.api_url = api_url
        self.game_id = None
        self.board = [" "] * 9
        self.current_player = "X"
        self.game_status = "playing"
        self.player_mode = "human"  # "human", "vs_ai", "ai_vs_ai"
        self.ai_difficulty = "medium"
        self.ai_thinking = False
        
        # 創建主視窗
        self.window = tk.Tk()
        self.window.title("Tic-Tac-Toe (FastAPI 版本)")
        self.window.geometry("500x750")
        self.window.resizable(False, False)
        
        # 設置樣式
        self.setup_styles()
        
        # 創建 UI 元件
        self.create_widgets()
        
        # 檢查 API 連接
        self.check_api_connection()
    
    def setup_styles(self):
        """設置視窗樣式"""
        self.window.configure(bg='#2c3e50')
        
        # 顏色定義
        self.colors = {
            'bg': '#2c3e50',
            'fg': '#ecf0f1',
            'button': '#3498db',
            'button_hover': '#2980b9',
            'x_color': '#e74c3c',
            'o_color': '#2ecc71',
            'board_bg': '#34495e'
        }
    
    def create_widgets(self):
        """創建所有 UI 元件"""
        
        # 標題
        title_frame = tk.Frame(self.window, bg=self.colors['bg'])
        title_frame.pack(pady=20)
        
        title_label = tk.Label(
            title_frame,
            text="🎮 Tic-Tac-Toe",
            font=("Arial", 24, "bold"),
            bg=self.colors['bg'],
            fg=self.colors['fg']
        )
        title_label.pack()
        
        # API 狀態
        self.api_status_label = tk.Label(
            title_frame,
            text="檢查 API 連接中...",
            font=("Arial", 10),
            bg=self.colors['bg'],
            fg='#f39c12'
        )
        self.api_status_label.pack()
        
        # 遊戲信息
        info_frame = tk.Frame(self.window, bg=self.colors['bg'])
        info_frame.pack(pady=10)
        
        self.game_id_label = tk.Label(
            info_frame,
            text="遊戲 ID: 無",
            font=("Arial", 12),
            bg=self.colors['bg'],
            fg=self.colors['fg']
        )
        self.game_id_label.pack(side=tk.LEFT, padx=10)
        
        self.player_label = tk.Label(
            info_frame,
            text="當前玩家: X",
            font=("Arial", 12, "bold"),
            bg=self.colors['bg'],
            fg=self.colors['x_color']
        )
        self.player_label.pack(side=tk.LEFT, padx=10)
        
        # 控制面板
        control_frame = tk.Frame(self.window, bg=self.colors['bg'])
        control_frame.pack(pady=10)
        
        # 模式選擇
        mode_frame = tk.Frame(control_frame, bg=self.colors['bg'])
        mode_frame.pack(pady=5)
        
        tk.Label(
            mode_frame,
            text="遊戲模式:",
            font=("Arial", 11),
            bg=self.colors['bg'],
            fg=self.colors['fg']
        ).pack(side=tk.LEFT, padx=5)
        
        self.mode_var = tk.StringVar(value="human")
        modes = [
            ("人 vs 人", "human"),
            ("人 vs AI", "vs_ai"),
            ("AI vs AI", "ai_vs_ai")
        ]
        
        for text, value in modes:
            tk.Radiobutton(
                mode_frame,
                text=text,
                value=value,
                variable=self.mode_var,
                command=self.on_mode_change,
                bg=self.colors['bg'],
                fg=self.colors['fg'],
                selectcolor=self.colors['bg'],
                activebackground=self.colors['bg'],
                activeforeground=self.colors['fg']
            ).pack(side=tk.LEFT, padx=10)
        
        # AI 難度選擇
        difficulty_frame = tk.Frame(control_frame, bg=self.colors['bg'])
        difficulty_frame.pack(pady=5)
        
        tk.Label(
            difficulty_frame,
            text="AI 難度:",
            font=("Arial", 11),
            bg=self.colors['bg'],
            fg=self.colors['fg']
        ).pack(side=tk.LEFT, padx=5)
        
        self.difficulty_combo = ttk.Combobox(
            difficulty_frame,
            values=["簡單", "中等", "困難"],
            state="readonly",
            width=10
        )
        self.difficulty_combo.set("中等")
        self.difficulty_combo.pack(side=tk.LEFT, padx=5)
        self.difficulty_combo.bind('<<ComboboxSelected>>', self.on_difficulty_change)
        
        # 按鈕框架
        button_frame = tk.Frame(control_frame, bg=self.colors['bg'])
        button_frame.pack(pady=10)
        
        self.new_game_btn = tk.Button(
            button_frame,
            text="🆕 新遊戲",
            command=self.start_new_game,
            font=("Arial", 11),
            bg='#27ae60',
            fg='white',
            padx=15,
            pady=5,
            cursor='hand2'
        )
        self.new_game_btn.pack(side=tk.LEFT, padx=5)
        
        self.reset_btn = tk.Button(
            button_frame,
            text="🔄 重置",
            command=self.reset_game,
            font=("Arial", 11),
            bg='#e67e22',
            fg='white',
            padx=15,
            pady=5,
            cursor='hand2',
            state='disabled'
        )
        self.reset_btn.pack(side=tk.LEFT, padx=5)
        
        # 遊戲棋盤
        board_frame = tk.Frame(self.window, bg=self.colors['board_bg'], padx=10, pady=10)
        board_frame.pack(pady=20)
        
        self.buttons = []
        for i in range(9):
            row, col = i // 3, i % 3
            btn = tk.Button(
                board_frame,
                text=" ",
                font=("Arial", 24, "bold"),
                width=4,
                height=2,
                bg='white',
                fg='black',
                command=lambda idx=i: self.on_button_click(idx)
            )
            btn.grid(row=row, column=col, padx=2, pady=2)
            self.buttons.append(btn)
        
        # 消息顯示
        self.message_label = tk.Label(
            self.window,
            text="點擊『新遊戲』開始",
            font=("Arial", 12),
            bg=self.colors['bg'],
            fg=self.colors['fg'],
            wraplength=400
        )
        self.message_label.pack(pady=10)
        
        # AI 思考指示器
        self.ai_thinking_label = tk.Label(
            self.window,
            text="",
            font=("Arial", 10, "italic"),
            bg=self.colors['bg'],
            fg='#f39c12'
        )
        self.ai_thinking_label.pack()
    
    def check_api_connection(self):
        """檢查 API 連接"""
        try:
            response = requests.get(f"{self.api_url}/", timeout=3)
            if response.status_code == 200:
                self.api_status_label.config(
                    text="✅ API 連接正常",
                    fg='#2ecc71'
                )
                self.new_game_btn.config(state='normal')
            else:
                self.api_status_label.config(
                    text="❌ API 連接失敗",
                    fg='#e74c3c'
                )
        except:
            self.api_status_label.config(
                text="❌ 無法連接到 API 服務器",
                fg='#e74c3c'
            )
            self.new_game_btn.config(state='disabled')
            messagebox.showerror(
                "連接錯誤",
                "無法連接到 API 服務器！\n請確保服務器正在運行：python api_server.py"
            )
    
    def on_mode_change(self):
        """模式改變時的處理"""
        self.player_mode = self.mode_var.get()
        self.reset_game()
        
        if self.player_mode == "ai_vs_ai":
            messagebox.showinfo("AI 對戰", "觀戰模式：AI 將自動進行對戰")
    
    def on_difficulty_change(self, event=None):
        """難度改變時的處理"""
        difficulty_map = {
            "簡單": "easy",
            "中等": "medium",
            "困難": "hard"
        }
        self.ai_difficulty = difficulty_map[self.difficulty_combo.get()]
    
    def start_new_game(self):
        """開始新遊戲"""
        try:
            response = requests.post(f"{self.api_url}/new-game")
            if response.status_code == 200:
                game_state = response.json()
                self.game_id = game_state["game_id"]
                self.board = game_state["board"]
                self.current_player = game_state["current_player"]
                self.game_status = game_state["status"]
                
                # 更新 UI
                self.game_id_label.config(text=f"遊戲 ID: {self.game_id}")
                self.update_board_display()
                self.update_player_label()
                self.reset_btn.config(state='normal')
                self.message_label.config(text=f"遊戲開始！當前玩家: {self.current_player}")
                
                # 如果觀戰模式，開始 AI 對戰
                if self.player_mode == "ai_vs_ai":
                    self.start_ai_battle()
                # 如果對 AI 模式且 AI 先手
                elif self.player_mode == "vs_ai" and self.current_player == "O":
                    self.make_ai_move()
            else:
                messagebox.showerror("錯誤", "無法創建新遊戲")
        except requests.exceptions.ConnectionError:
            messagebox.showerror("錯誤", "無法連接到 API 服務器")
    
    def reset_game(self):
        """重置遊戲"""
        self.game_id = None
        self.board = [" "] * 9
        self.game_status = "playing"
        self.ai_thinking = False
        self.ai_thinking_label.config(text="")
        
        # 重置 UI
        self.game_id_label.config(text="遊戲 ID: 無")
        self.update_board_display()
        self.message_label.config(text="點擊『新遊戲』開始")
        self.reset_btn.config(state='disabled')
    
    def on_button_click(self, position):
        """按鈕點擊事件"""
        if not self.game_id:
            messagebox.showwarning("警告", "請先點擊『新遊戲』開始")
            return
        
        if self.game_status != "playing":
            messagebox.showinfo("提示", "遊戲已結束，請點擊『新遊戲』")
            return
        
        if self.ai_thinking:
            messagebox.showinfo("提示", "AI 正在思考中，請稍候...")
            return
        
        if self.player_mode == "human":
            # 人 vs 人 模式
            self.make_move(position + 1)  # 轉換為 1-based
        elif self.player_mode == "vs_ai":
            # 人 vs AI 模式
            if self.current_player == "X":  # 人類是 X
                if self.make_move(position + 1):
                    # 移動成功後，讓 AI 走下一步
                    if self.game_status == "playing":
                        self.window.after(500, self.make_ai_move)
            else:
                messagebox.showinfo("提示", "現在是 AI 的回合")
    
    def make_move(self, position: int) -> bool:
        """發送移動到 API"""
        move_data = {
            "board": self.board,
            "position": position - 1,
            "player": self.current_player,
            "game_id": self.game_id
        }
        
        try:
            response = requests.post(f"{self.api_url}/move", json=move_data)
            
            if response.status_code == 200:
                result = response.json()
                
                if result["valid_move"]:
                    # 更新狀態
                    self.board = result["new_board"]
                    self.current_player = result["next_player"]
                    
                    # 更新 UI
                    self.update_board_display()
                    self.update_player_label()
                    self.message_label.config(text=result["message"])
                    
                    # 檢查遊戲是否結束
                    if result["winner"] or result["is_draw"]:
                        self.game_status = "finished"
                        self.highlight_winner(result["winner"])
                    
                    return True
                else:
                    self.message_label.config(text=result["message"])
                    return False
            else:
                self.message_label.config(text=f"API 錯誤: {response.status_code}")
                return False
                
        except requests.exceptions.ConnectionError:
            self.message_label.config(text="無法連接到 API 服務器")
            return False
    
    def make_ai_move(self):
        """讓 AI 走一步"""
        if self.game_status != "playing" or self.ai_thinking:
            return
        
        self.ai_thinking = True
        self.ai_thinking_label.config(text="🤖 AI 思考中...")
        
        # 在另一個線程執行 AI 請求，避免界面卡頓
        def ai_thread():
            try:
                response = requests.get(
                    f"{self.api_url}/ai-move/{self.game_id}",
                    params={"difficulty": self.ai_difficulty}
                )
                
                if response.status_code == 200:
                    suggestion = response.json()
                    if suggestion["move"] is not None:
                        # 回到主線程更新 UI
                        self.window.after(0, lambda: self.execute_ai_move(suggestion["move"] + 1))
                    else:
                        self.window.after(0, self.ai_move_complete)
                else:
                    self.window.after(0, self.ai_move_complete)
            except:
                self.window.after(0, self.ai_move_complete)
        
        threading.Thread(target=ai_thread, daemon=True).start()
    
    def execute_ai_move(self, position):
        """執行 AI 移動"""
        if self.make_move(position):
            # 如果遊戲仍在進行且是 AI 對戰模式，繼續 AI 移動
            if (self.game_status == "playing" and 
                self.player_mode == "ai_vs_ai"):
                self.window.after(800, self.make_ai_move)
        
        self.ai_move_complete()
    
    def ai_move_complete(self):
        """AI 移動完成"""
        self.ai_thinking = False
        self.ai_thinking_label.config(text="")
    
    def start_ai_battle(self):
        """開始 AI 對戰"""
        if self.game_status == "playing":
            self.window.after(1000, self.make_ai_move)
    
    def update_board_display(self):
        """更新棋盤顯示"""
        for i in range(9):
            symbol = self.board[i]
            self.buttons[i].config(text=symbol)
            
            # 設置顏色
            if symbol == "X":
                self.buttons[i].config(fg=self.colors['x_color'])
            elif symbol == "O":
                self.buttons[i].config(fg=self.colors['o_color'])
            else:
                self.buttons[i].config(fg='black')
    
    def update_player_label(self):
        """更新玩家標籤"""
        if self.current_player:
            color = self.colors['x_color'] if self.current_player == "X" else self.colors['o_color']
            self.player_label.config(
                text=f"當前玩家: {self.current_player}",
                fg=color
            )
    
    def highlight_winner(self, winner):
        """高亮贏家"""
        if winner:
            for i in range(9):
                if self.board[i] == winner:
                    self.buttons[i].config(bg='#f1c40f')  # 金色高亮
    
    def run(self):
        """運行主循環"""
        self.window.mainloop()

# 主程式
if __name__ == "__main__":
    # 可以修改為你的 Vercel API 網址
    # API_URL = "http://localhost:8000"  # 本地測試
    API_URL = "https://pythonapi-gilt.vercel.app/"  # Vercel 部署
    
    app = TicTacToeGUI(api_url=API_URL)
    app.run()