import requests
import json
from typing import List, Optional
import time

class TicTacToeClient:
    def __init__(self, api_url="http://localhost:8000"):
        self.api_url = api_url
        self.game_id = None
        self.board = [" "] * 9
        self.current_player = "X"
        self.game_status = "playing"
    
    def print_board(self, board: List[str]):
        """打印棋盤"""
        print("\n")
        print(f" {board[0]} | {board[1]} | {board[2]} ")
        print("-----------")
        print(f" {board[3]} | {board[4]} | {board[5]} ")
        print("-----------")
        print(f" {board[6]} | {board[7]} | {board[8]} ")
        print("\n")
    
    def print_board_with_numbers(self):
        """打印帶數字的棋盤示例"""
        example = [str(i+1) for i in range(9)]
        print("\n位置對照表:")
        print(f" {example[0]} | {example[1]} | {example[2]} ")
        print("-----------")
        print(f" {example[3]} | {example[4]} | {example[5]} ")
        print("-----------")
        print(f" {example[6]} | {example[7]} | {example[8]} ")
        print("\n")
    
    def start_new_game(self):
        """在服務器上開始新遊戲"""
        try:
            response = requests.post(f"{self.api_url}/new-game")
            if response.status_code == 200:
                game_state = response.json()
                self.game_id = game_state["game_id"]
                self.board = game_state["board"]
                self.current_player = game_state["current_player"]
                self.game_status = game_state["status"]
                print(f"新遊戲已創建！遊戲 ID: {self.game_id}")
                return True
            else:
                print("無法創建新遊戲")
                return False
        except requests.exceptions.ConnectionError:
            print("無法連接到 API 服務器。請確保服務器正在運行。")
            return False
    
    def make_move(self, position: int) -> bool:
        """發送移動到 API"""
        if not self.game_id:
            print("請先開始新遊戲")
            return False
        
        move_data = {
            "board": self.board,
            "position": position - 1,  # 轉換為 0-based index
            "player": self.current_player,
            "game_id": self.game_id
        }
        
        try:
            response = requests.post(f"{self.api_url}/move", json=move_data)
            
            if response.status_code == 200:
                result = response.json()
                
                if result["valid_move"]:
                    # 更新本地狀態
                    self.board = result["new_board"]
                    self.current_player = result["next_player"]
                    
                    # 顯示結果
                    self.print_board(self.board)
                    print(f"✅ {result['message']}")
                    
                    # 檢查遊戲是否結束
                    if result["winner"] or result["is_draw"]:
                        self.game_status = "finished"
                        return True
                else:
                    print(f"❌ {result['message']}")
                    return False
            else:
                print(f"API 錯誤: {response.status_code}")
                return False
                
        except requests.exceptions.ConnectionError:
            print("無法連接到 API 服務器")
            return False
        
        return True
    
    def get_ai_suggestion(self, difficulty="medium"):
        """獲取 AI 建議"""
        if not self.game_id:
            print("請先開始新遊戲")
            return None
        
        try:
            response = requests.get(
                f"{self.api_url}/ai-move/{self.game_id}",
                params={"difficulty": difficulty}
            )
            
            if response.status_code == 200:
                suggestion = response.json()
                if suggestion["move"] is not None:
                    print(f"🤖 AI 建議: 位置 {suggestion['position']}")
                    return suggestion["move"]
                else:
                    print("🤖 AI: 沒有可用的位置")
            else:
                print("無法獲取 AI 建議")
                
        except requests.exceptions.ConnectionError:
            print("無法連接到 API 服務器")
        
        return None
    
    def play_human_vs_human(self):
        """人 vs 人 模式"""
        print("\n=== 人 vs 人 模式 ===")
        self.print_board_with_numbers()
        
        while self.game_status == "playing":
            print(f"\n當前玩家: {self.current_player}")
            
            # 獲取玩家輸入
            try:
                move = int(input(f"玩家 {self.current_player}, 請選擇位置 (1-9): "))
                if 1 <= move <= 9:
                    self.make_move(move)
                else:
                    print("請輸入 1-9 的數字")
            except ValueError:
                print("請輸入有效的數字")
    
    def play_vs_ai(self, ai_difficulty="medium"):
        """人 vs AI 模式"""
        print("\n=== 人 vs AI 模式 ===")
        print(f"AI 難度: {ai_difficulty}")
        print("你是 X, AI 是 O")
        self.print_board_with_numbers()
        
        while self.game_status == "playing":
            if self.current_player == "X":  # 人類回合
                print("\n你的回合:")
                try:
                    move = int(input("請選擇位置 (1-9): "))
                    if 1 <= move <= 9:
                        self.make_move(move)
                    else:
                        print("請輸入 1-9 的數字")
                except ValueError:
                    print("請輸入有效的數字")
            else:  # AI 回合
                print("\nAI 思考中...")
                time.sleep(0.5)
                ai_move = self.get_ai_suggestion(ai_difficulty)
                if ai_move is not None:
                    print(f"AI 選擇了位置 {ai_move + 1}")
                    self.make_move(ai_move + 1)
    
    def play_ai_vs_ai(self):
        """AI vs AI 模式 (觀戰)"""
        print("\n=== AI vs AI 觀戰模式 ===")
        print("AI X  vs  AI O")
        print("觀戰中...\n")
        
        round_num = 1
        while self.game_status == "playing":
            print(f"\n--- 第 {round_num} 回合 ---")
            print(f"當前玩家: {self.current_player}")
            
            time.sleep(1)  # 觀戰延遲
            
            # 獲取 AI 建議
            ai_move = self.get_ai_suggestion("hard")
            if ai_move is not None:
                print(f"AI {self.current_player} 選擇了位置 {ai_move + 1}")
                self.make_move(ai_move + 1)
            
            round_num += 1
    
    def play_again(self):
        """詢問是否再玩一局"""
        choice = input("\n是否再玩一局? (y/n): ").lower()
        return choice == 'y'

def main():
    print("=" * 40)
    print("歡迎來到 Tic-Tac-Toe 遊戲 (FastAPI 版本)")
    print("=" * 40)
    
    # 檢查 API 連接
    client = TicTacToeClient(api_url="https://pythonapi-gilt.vercel.app/")
    try:
        response = requests.get(f"{client.api_url}/")
        if response.status_code == 200:
            print("✅ 成功連接到 API 服務器\n")
        else:
            print("❌ 無法連接到 API 服務器")
            print("請先運行: python api_server.py")
            return
    except:
        print("❌ 無法連接到 API 服務器")
        print("請先運行: python api_server.py")
        return
    
    while True:
        print("\n請選擇遊戲模式:")
        print("1. 人 vs 人")
        print("2. 人 vs AI")
        print("3. AI vs AI (觀戰)")
        print("4. 退出")
        
        choice = input("\n請選擇 (1-4): ")
        
        if choice == "1":
            # 人 vs 人
            while True:
                if client.start_new_game():
                    client.play_human_vs_human()
                    if not client.play_again():
                        break
        
        elif choice == "2":
            # 人 vs AI
            print("\n選擇 AI 難度:")
            print("1. 簡單")
            print("2. 中等")
            print("3. 困難")
            
            diff_choice = input("請選擇 (1-3): ")
            difficulty = {
                "1": "easy",
                "2": "medium",
                "3": "hard"
            }.get(diff_choice, "medium")
            
            while True:
                if client.start_new_game():
                    client.play_vs_ai(difficulty)
                    if not client.play_again():
                        break
        
        elif choice == "3":
            # AI vs AI
            while True:
                if client.start_new_game():
                    client.play_ai_vs_ai()
                    if not client.play_again():
                        break
        
        elif choice == "4":
            print("感謝遊玩！再見！")
            break
        
        else:
            print("無效的選擇，請重試")

if __name__ == "__main__":
    main()