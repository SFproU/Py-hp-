import pygame
import sys
from board import YinshBoard
from constants import *
from piece import YinshPiece

class YinshGame:
    def __init__(self, boardsize=BOARDSIZE):
        pygame.init()
        self.board = YinshBoard(boardsize)
        self.screen = pygame.display.set_mode((boardsize, boardsize))
        pygame.display.set_caption('YINSH')
        self.font = pygame.font.Font(None, 40)
        self.large_font = pygame.font.Font(None, 80)
    # 游戏绘制
    def draw_game(self):

        self.screen.fill(WHITE)
        self.draw_lines()
        

        for pos, piece in self.board.pieces.items():
            piece.draw(self.screen)
        
        # 高亮可移除的环
        if self.board.game_phase == REMOVE_RING and self.board.removing_player is not None:
            self.highlight_removable_rings()
        
        # 显示可到达的位置
        if self.board.selected_ring is not None:
            self.show_reachable_positions()
        
        # 高亮当前五连
        if self.board.lines_to_remove and self.board.active_line_index < len(self.board.lines_to_remove):
            self.highlight_five_in_row()
        
        # 显示游戏状态信息
        self.draw_status()
        
        # 显示得分
        self.draw_scores()
        
        pygame.display.flip()  
    # 绘制棋盘网格线
    def draw_lines(self):
        for pos in self.board.positions:
            # 六边形的六个相邻方向
            neighbors = [
                (pos[0]+1, pos[1]),   # 右
                (pos[0], pos[1]+1),   # 右下
                (pos[0]-1, pos[1]+1), # 左下
                (pos[0]-1, pos[1]),   # 左
                (pos[0], pos[1]-1),   # 左上
                (pos[0]+1, pos[1]-1)  # 右上
            ]
            for neighbor in neighbors:
                if neighbor in self.board.positions:
                    # 绘制连接两个点的线
                    pygame.draw.line(self.screen, BLACK, 
                                   self.board.rc_to_xy(pos),
                                   self.board.rc_to_xy(neighbor), 2)
    
    def highlight_removable_rings(self):
        for pos, piece in self.board.pieces.items():
            if piece.is_ring and piece.color == self.board.removing_player:
                pygame.draw.circle(self.screen, YELLOW, piece.center, 22, 3)
    
    def show_reachable_positions(self):
        for end_pos, _ in self.board.reachable_info:
            center = self.board.rc_to_xy(end_pos)
            pygame.draw.circle(self.screen, GREEN, center, 5)
    
    def highlight_five_in_row(self):
        current_color, current_line = self.board.lines_to_remove[self.board.active_line_index]
        for pos in current_line[:5]:  
            # 仅高亮尚未移除的棋子
            if pos in self.board.pieces and self.board.pieces[pos].color == current_color:
                center = self.board.rc_to_xy(pos)
                pygame.draw.circle(self.screen, ORANGE, center, 15, 3)
    
    def draw_status(self):
        if self.board.game_phase == PLACE_RINGS:
            player_name = "Blue" if self.board.current_player == BLUE else "Red"
            status_text = f"Place Rings: {player_name} ({self.board.rings_placed[self.board.current_player]}/{NUM_RINGS})"
        elif self.board.game_phase == MOVE_RINGS:
            player_name = "Blue" if self.board.current_player == BLUE else "Red"
            status_text = f"{player_name}'s turn"
        elif self.board.game_phase == REMOVE_RING:
            if self.board.removing_player is not None:
                player_name = 'Red' if self.board.removing_player == RED else 'Blue'
                # 显示当前处理的是第几个五连
                if len(self.board.lines_to_remove) > 1:
                    additional = f" ({self.board.active_line_index + 1} of {len(self.board.lines_to_remove)})"
                else:
                    additional = ""
                status_text = f"{player_name}, remove a ring!{additional}"
            else:
                status_text = "Remove a ring!"
        
        text = self.font.render(status_text, True, BLACK)
        self.screen.blit(text, (self.board.BOARDSIZE//2-150, 20))
    
    def draw_scores(self):
        red_score = self.font.render(f'Red: {self.board.scores[RED]}', True, RED)
        blue_score = self.font.render(f'Blue: {self.board.scores[BLUE]}', True, BLUE)
        self.screen.blit(red_score, (20, 20))
        self.screen.blit(blue_score, (self.board.BOARDSIZE-150, 20))
    
    def game_over(self, winner=None):
        if winner is None:
            player = "Red" if self.board.current_player == RED else "Blue"
            text = self.large_font.render(f'{player} Wins!', True, YELLOW)
        else:
            text = self.large_font.render(f'{winner} Wins!', True, YELLOW)
            
        text_rect = text.get_rect(center=(self.board.BOARDSIZE//2, self.board.BOARDSIZE//2))
        self.screen.blit(text, text_rect)
        pygame.display.flip()  
        pygame.time.wait(3000)  
        pygame.quit()
        sys.exit()  
    
    def main_loop(self):
        while True:
            self.draw_game()
            
            # 处理事件
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_mouse_click(event.pos)
    
    def handle_mouse_click(self, mouse_pos):
        rc_pos = self.board.xy_to_rc(mouse_pos)
        
        # 确保点击位置在棋盘上
        if rc_pos not in self.board.pieces:
            return
        
        # 1. 放置环阶段
        if self.board.game_phase == PLACE_RINGS:
            self.handle_place_phase(rc_pos)
        
        # 2. 移动环阶段
        elif self.board.game_phase == MOVE_RINGS:
            self.handle_move_phase(rc_pos)
        
        # 3. 移除环阶段
        elif self.board.game_phase == REMOVE_RING:
            self.handle_remove_phase(rc_pos)
    
    def handle_place_phase(self, rc_pos):
        if self.board.pieces[rc_pos].color == GRAY:  # 确保位置为空
            # 放置环
            self.board.pieces[rc_pos] = YinshPiece(
                self.board.rc_to_xy(rc_pos),
                self.board.current_player,
                True
            )
            self.board.rings_placed[self.board.current_player] += 1
            # 切换玩家
            self.board.current_player = BLUE if self.board.current_player == RED else RED
            
            # 检查双方是否都放置了所有环
            if all(v == NUM_RINGS for v in self.board.rings_placed.values()):
                self.board.game_phase = MOVE_RINGS
                self.board.current_player = RED  # 红方开始移动
    
    def handle_move_phase(self, rc_pos):
        if self.board.selected_ring is None:
            # 选择一个环
            if self.board.pieces[rc_pos].is_ring and self.board.pieces[rc_pos].color == self.board.current_player:
                self.board.selected_ring = rc_pos
                self.board.pieces[rc_pos].color = YELLOW  # 高亮选中的环
                self.board.reachable_info = self.board.get_reachable_positions(rc_pos)  # 获取可移动位置
        else:
            moved = False
            # 尝试移动到选定的位置
            for end_pos, jumped in self.board.reachable_info:
                if rc_pos == end_pos:
                    if self.board.move_ring(self.board.selected_ring, rc_pos, jumped):
                        moved = True
                        break
            
            if moved:
                # 移动成功，重置选择
                self.board.selected_ring = None
                self.board.reachable_info = []
            else:
                # 移动失败，取消选择
                self.board.pieces[self.board.selected_ring].color = self.board.current_player
                self.board.selected_ring = None
                self.board.reachable_info = []
    
    def handle_remove_phase(self, rc_pos):
        # 移除选中的环 
        if self.board.pieces[rc_pos].is_ring and self.board.pieces[rc_pos].color == self.board.removing_player:
            self.board.pieces[rc_pos] = YinshPiece(self.board.rc_to_xy(rc_pos), GRAY)
            self.board.scores[self.board.removing_player] += 1
            
            # 检查是否获胜
            if self.board.scores[self.board.removing_player] >= 3:
                if self.board.removing_player == RED:
                    self.game_over("Red")
                else:
                    self.game_over("Blue")
            
            # 处理下一个五连
            self.board.process_next_line()

def main():
    game = YinshGame()
    game.main_loop()

if __name__ == "__main__":
    main()