import pygame
from constants import *
from piece import YinshPiece

class YinshBoard:
    def __init__(self, boardsize=BOARDSIZE):
        self.BOARDSIZE = boardsize
        self.CENTER = self.BOARDSIZE // 2
        self.EDGE = 50
        
        self.reset_game()
        
        # 初始化棋盘位置(六边形网格)
        self.positions = []
        for row in range(-5, 6):
            for col in range(-5, 6):
                if abs(row + col) <= 5:  
                    self.positions.append((row, col))
        
        # 创建空的棋子对象
        self.pieces = {pos: YinshPiece(self.rc_to_xy(pos)) for pos in self.positions}
        self.rings_placed = {RED: 0, BLUE: 0}

    #游戏状态
    def reset_game(self):
        self.selected_ring = None    # 当前选中的环的位置
        self.current_player = RED    # 当前玩家
        self.scores = {RED: 0, BLUE: 0}  # 玩家得分
        self.game_phase = PLACE_RINGS  # 游戏阶段
        self.reachable_info = []      # 可选移动位置的信息
        self.lines_to_remove = []     # 需要移除的五连
        self.active_line_index = 0    # 当前要处理哪个五连
        self.removing_player = None   # 当前需要移除环的玩家
        self.initial_player = None    # 记录移动阶段的初始玩家
    # 坐标转换 行列坐标->屏幕坐标
    def rc_to_xy(self, rc):
        row, col = rc
        x = self.CENTER + row * 55 + col * 28
        y = self.CENTER + col * 48
        return (int(x), int(y))
    # 屏幕坐标->行列坐标
    def xy_to_rc(self, pos):
        x, y = pos
        x -= self.CENTER
        y -= self.CENTER
        col = round(y / 48)
        row = round((x - col * 28) / 55)
        return (row, col)

    def get_reachable_positions(self, start_pos):
        reachable = []  # 可到达的位置
        
        for dr, dc in DIRECTIONS:  # 遍历每个方向
            # 1. 空白行直行移动
            pure_blank = []  # 连续空白位置
            step = 1
            while True:
                current_pos = (start_pos[0] + dr*step, start_pos[1] + dc*step)
                # 检查位置是否在棋盘上
                if current_pos not in self.pieces:
                    break
                
                piece = self.pieces[current_pos]
                # 检查位置是否空白且不是环
                if piece.color == GRAY and not piece.is_ring:
                    pure_blank.append((current_pos, []))  
                    step += 1
                else:
                    break
            
            reachable.extend(pure_blank)  # 添加所有连续空白位置
            
            # 2. 跨越棋子移动
            if pure_blank:
                last_blank = pure_blank[-1][0]  # 最后一个空白位置
                step_offset = len(pure_blank)    # 空白步骤数
            else:
                last_blank = start_pos           # 直接从起点开始
                step_offset = 0
            
            for jump_step in range(1, MAX_JUMP_STEPS + 1):
                current_pos = (last_blank[0] + dr*jump_step, 
                             last_blank[1] + dc*jump_step)
                
                # 检查位置是否在棋盘上
                if current_pos not in self.pieces:
                    break
                
                valid = True           # 当前跳跃是否有效
                jumped_pieces = []      # 被跨越的棋子位置
                
                # 检查跳跃路径上的每个位置
                for i in range(1, jump_step + 1):
                    check_pos = (last_blank[0] + dr*i, 
                                last_blank[1] + dc*i)
                    
                    # 检查位置是否在棋盘上
                    if check_pos not in self.pieces:
                        valid = False
                        break
                    
                    piece = self.pieces[check_pos]
                    # 终点位置检查
                    if i == jump_step:  # 终点
                        # 终点必须空白且不是环
                        if piece.color != GRAY or piece.is_ring:
                            valid = False
                            break
                    
                    # 路径中间位置检查
                    if i < jump_step:   # 中间点
                        # 中间点必须是有色棋子
                        if piece.is_ring or piece.color == GRAY:
                            valid = False
                            break
                        jumped_pieces.append(check_pos)
                
                # 如果找到有效跳跃路径，添加到可到达位置
                if valid and jumped_pieces:
                    total_step = step_offset + jump_step
                    final_pos = (start_pos[0] + dr*total_step,
                                start_pos[1] + dc*total_step)
                    reachable.append((final_pos, jumped_pieces))
                    break  

        return reachable
    
    def get_all_lines(self, color):
        possible_lines = []  # 找到的所有五连
        visited_positions = set()  # 位置是否访问
        
        for pos in self.positions:

            if pos in visited_positions:
                continue
                
            piece = self.pieces[pos]
            # 跳过非指定颜色、环或空白位置
            if piece.color != color or piece.is_ring or piece.color == GRAY:
                continue
                
            for dr, dc in DIRECTIONS:
                # 记录整条连续线
                full_line = []
                
                # 沿方向向前延伸
                current_pos = pos
                while current_pos in self.pieces:
                    current_piece = self.pieces[current_pos]
                    # 检查是否为指定颜色的棋子
                    if current_piece.color == color and not current_piece.is_ring:
                        full_line.append(current_pos)
                        current_pos = (current_pos[0] + dr, current_pos[1] + dc)
                    else:
                        break
                
                # 沿相反方向向后延伸
                current_pos = (pos[0] - dr, pos[1] - dc)
                while current_pos in self.pieces:
                    current_piece = self.pieces[current_pos]
                    if current_piece.color == color and not current_piece.is_ring:
                        full_line.insert(0, current_pos)  # 添加到开头
                        current_pos = (current_pos[0] - dr, current_pos[1] - dc)
                    else:
                        break
                
                # 只添加长度>=5的连续线
                if len(full_line) >= 5:
                    # 检查这条线是否已经被包含
                    if not any(set(full_line) == set(line) for (c, line) in possible_lines):
                        possible_lines.append((color, full_line))
                        visited_positions.update(full_line)  # 标记这些位置已访问
        
        return possible_lines

    def move_ring(self, start, end, jumped_pieces):

        self.initial_player = self.current_player
        
        # 更新起点
        self.pieces[start] = YinshPiece(
            self.rc_to_xy(start),
            self.current_player,
            False  
        )
        
        # 更新终点
        self.pieces[end] = YinshPiece(
            self.rc_to_xy(end),
            self.current_player,
            True  
        )
        
        # 翻转棋子
        for pos in jumped_pieces:
            current_color = self.pieces[pos].color
            new_color = BLUE if current_color == RED else RED
            self.pieces[pos].color = new_color
        
        # 重置五连记录
        self.lines_to_remove = []  
        self.active_line_index = 0
        
        # 检查五连
        for color in [RED, BLUE]:
            lines = self.get_all_lines(color)
            for (color, line) in lines:
                # 避免重复添加相同的五连
                if not any(set(line) == set(existing_line) for (c, existing_line) in self.lines_to_remove):
                    self.lines_to_remove.append((color, line))
        
        # 如果有五连形成，进入移除环阶段
        if self.lines_to_remove:
            self.game_phase = REMOVE_RING
            self.removing_player = self.lines_to_remove[self.active_line_index][0]
        else:
            self.current_player = BLUE if self.current_player == RED else RED
        return True
    
    # 处理下一个五连
    def process_next_line(self):
        # 先移除当前活动五连的棋子
        if self.active_line_index < len(self.lines_to_remove):
            current_color, current_line = self.lines_to_remove[self.active_line_index]
            for pos in current_line[:5]:
                if pos in self.pieces and self.pieces[pos].color == current_color:
                    self.pieces[pos] = YinshPiece(self.rc_to_xy(pos), GRAY)  # 清空位置
        
        # 检查是否还有更多五连
        if self.active_line_index < len(self.lines_to_remove) - 1:

            self.active_line_index += 1
            self.removing_player = self.lines_to_remove[self.active_line_index][0]
        else:

            self.game_phase = MOVE_RINGS

            self.current_player = BLUE if self.initial_player == RED else RED

            self.lines_to_remove = []
            self.active_line_index = 0
            self.removing_player = None
            self.initial_player = None