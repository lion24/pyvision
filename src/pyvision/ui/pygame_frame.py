import tkinter as tk
import os
import pygame

from pyvision.utils.observer import ConcreteSubject

class PygameFrame(tk.Frame, ConcreteSubject):
    def __init__(self, master=None, width = 1280, height = 720, fps = 30, **kwargs):
        #self.pygame_frame = tk.Frame(self, width=self.width, height=self.height)
        super().__init__(master, width=width, height=height, **kwargs)
        ConcreteSubject.__init__(self)
        self.width = width
        self.height = height
        self.fps = fps

        self.init_pygame()

    def init_pygame(self):
        os.environ['SDL_WINDOWID'] = str(self.winfo_id())
        os.environ['SDL_VIDEODRIVER'] = 'windib'
        pygame.display.init()
        flags = pygame.FULLSCREEN | pygame.NOFRAME
        self.screen = pygame.display.set_mode((self.width, self.height), flags)
        self.after(100, self.update_pygame)

    def update_pygame(self):
        pygame.display.flip()
        self.notify()
        self.after(1000 // self.fps, self.update_pygame)