# 颜色
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

RED = (255, 0, 0)
BLUE = (0, 0, 255)

YELLOW = (255, 255, 0)  # 选择移除的环
GRAY = (200, 200, 200)  # 空
GREEN = (0, 255, 0)     # 可到达
ORANGE = (255, 165, 0)  # 提示要消除的棋子

# 游戏阶段常量
PLACE_RINGS = "place_rings"
MOVE_RINGS = "move_rings"
REMOVE_RING = "remove_ring"

# 方向向量
DIRECTIONS = [
    (1, 0),    # 右
    (0, 1),    # 下右
    (-1, 1),   # 下左
    (-1, 0),   # 左
    (0, -1),   # 左上
    (1, -1)    # 右上
]

MAX_JUMP_STEPS = 10  
NUM_RINGS = 5 
BOARDSIZE = 800  # 游戏窗口大小