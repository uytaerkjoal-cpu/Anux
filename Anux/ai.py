import sys
import ctypes
import pygame
import win32api
import win32con
import win32gui
from mss import mss
import cv2
import numpy as np
import torch
from ultralytics import YOLO

ctypes.windll.user32.SetProcessDPIAware()

device = "cuda:0" # или cpu!!!
print(f"Using device: {device}")

model = YOLO("yolo11s.pt")

FOV_RADIUS = 200

def move_mouse(target_x, target_y):
    current_pos = win32api.GetCursorPos()
    dx = int((target_x - current_pos[0]) * 0.95)
    dy = int((target_y - current_pos[1]) * 0.95)
    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, dx, dy, 0, 0)

USER32 = ctypes.windll.user32
SCREEN_WIDTH = USER32.GetSystemMetrics(0)
SCREEN_HEIGHT = USER32.GetSystemMetrics(1)

SIZE = 640
scan_left = (SCREEN_WIDTH - SIZE) // 2
scan_top = (SCREEN_HEIGHT - SIZE) // 2
monitor = {"top": scan_top, "left": scan_left, "width": SIZE, "height": SIZE}

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.NOFRAME | pygame.HWSURFACE | pygame.DOUBLEBUF)
FUCHSIA = (255, 0, 128)

hwnd = pygame.display.get_wm_info()['window']
style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, style | win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT | win32con.WS_EX_TOPMOST | win32con.WS_EX_TOOLWINDOW)
win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(*FUCHSIA), 0, win32con.LWA_COLORKEY)

sct = mss()

try:
    while True:
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
        screen.fill(FUCHSIA)
        pygame.draw.circle(screen, (255, 255, 255), (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), FOV_RADIUS, 1)

        screenshot = sct.grab(monitor)
        frame = np.frombuffer(screenshot.raw, dtype=np.uint8).reshape(SIZE, SIZE, 4)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

        results = model.predict(source=frame, classes=[0], device=device, conf=0.25, imgsz=256, verbose=False)

        closest_head = None
        min_dist = float('inf')
        
        for result in results:
            if result.boxes is not None:
                for box in result.boxes.xyxy.cpu().numpy():
                    x1, y1, x2, y2 = map(int, box)
                    hx = x1 + (x2 - x1) // 2
                    hy = y1 + (y2 - y1) // 12
                    
                    dist = ((hx - 320)**2 + (hy - 320)**2)**0.5
                    
                    if dist < min_dist and dist < FOV_RADIUS:
                        min_dist = dist
                        closest_head = (hx + scan_left, hy + scan_top)
                    
                    pygame.draw.circle(screen, (255, 0, 0), (hx + scan_left, hy + scan_top), 2)

        if win32api.GetAsyncKeyState(win32con.VK_RBUTTON) < 0:
            if closest_head:
                move_mouse(closest_head[0], closest_head[1])

        pygame.display.flip()

except KeyboardInterrupt:
    pygame.quit()
    sys.exit()
