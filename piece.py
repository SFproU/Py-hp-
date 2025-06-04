import pygame
from constants import *

class YinshPiece:
    def __init__(self, center, color=GRAY, is_ring=False):
        self.center = center   # 在屏幕上的位置 (x, y)
        self.color = color    
        self.is_ring = is_ring  # 是否是环(True)或棋子(False)
        self.radius = 20 if is_ring else 12  

    def draw(self, screen):
        if self.is_ring:
            # 绘制环(空心圆)
            pygame.draw.circle(screen, self.color, self.center, self.radius, 3)
        elif self.color != GRAY:
            # 绘制棋子(实心圆)
            pygame.draw.circle(screen, self.color, self.center, self.radius)