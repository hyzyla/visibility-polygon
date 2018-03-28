
import pygame
from visual_objects import Point
from visual_objects import Polygon
from visual_objects import Edge
from visibility import asano_algorithm
from pygame.color import Color


class App:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((600, 600))
        self.screen.fill(pygame.Color("white"))

        self.header = Header(self.screen)
        self.canvas = Canvas(self.screen)


    def mousebuttondown(self):
        if self.header.clicked():
            if self.header.clear_button.clicked():
                self.canvas.clear()
            elif self.header.auto_button.clicked():
                self.canvas.generate_auto()
            elif self.header.start_button.clicked():
                self.canvas.find_visabile_edges()
            elif self.header.border_button.clicked():
                self.canvas.find_visabile_edges(border=True)
        elif self.canvas.clicked():
            self.canvas.mousebuttondown()

    def run(self):
        done = False

        while not done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.mousebuttondown()
            
            self.header.draw(self.screen)
            self.canvas.draw(self.screen)
            pygame.display.flip()

class Header:
    def __init__(self, screen):
        self.surface = pygame.surface.Surface((600, 50))
        self.rect = self.surface.get_rect(center=(300, 25))
        self.clear_button = Button(screen, 'Clear', (60, 25), lambda: print("clear"))
        self.auto_button = Button(screen, 'Auto', (200, 25), lambda: print("Auto"), disabled=True)
        self.border_button = Button(screen, 'Start all', (400, 25), lambda: print("HELLO") )
        self.start_button = Button(screen, 'Start', (540, 25), lambda: print("Start"))
        self.draw(screen)

    def clicked(self):
        pos = pygame.mouse.get_pos()
        return self.rect.collidepoint(pos)

    def mousebuttondown(self):
        if self.clear_button.clicked():
            self.clear_button.callback()
        elif self.auto_button.clicked():
            self.auto_button.callback()
        elif self.border_button.clicked():
            self.border_button.callback()

    def draw(self, screen):
        self.surface.fill(Color("grey"))
        screen.blit(self.surface, self.rect)
        self.clear_button.draw(screen)
        self.auto_button.draw(screen)
        self.start_button.draw(screen)
        self.border_button.draw(screen)


class DrawablePolygon(Polygon):
    def __init__(self, points, *args, **kwargs):
        points = points.copy()
        super().__init__(points, *args, **kwargs)

    def draw(self, screen):
        yellow = pygame.Color('yellow')
        points = [p.coordinates for p in self.points]
        pygame.draw.polygon(screen, yellow, points)
        for p in self.points:
            p.draw(screen)



class DrawableEdge(Edge):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def draw(self, screen):
        color = pygame.Color("green")
        pygame.draw.line(screen, color, self.a.coordinates, self.b.coordinates, 3)


class Canvas:
    def __init__(self, screen):
        self.surface = pygame.surface.Surface((600, 550))
        self.rect = self.surface.get_rect(center=(300, 325))
        self.screen = screen
        self.points = []
        self.polygons = []
        self.visible_edges = []
        self.initial_point = None
        self.draw(screen)

    def generate_auto(self):
        for i in range(20, 400, 50):
            for j in range(70, 400, 50):
                polygon = DrawablePolygon([
                    DrawablePoint(i,   j),
                    DrawablePoint(i+10, j),
                    DrawablePoint(i+10, j+10),
                    DrawablePoint(i,   j+10)
                ])
                self.polygons.append(polygon)


    def find_visabile_edges(self, border=False):
        
        edges = asano_algorithm(self.initial_point, self.polygons)
        for e in edges:
            if border:
                self.visible_edges.append(DrawableEdge(e.a, e.b))
            elif e.visible:
                self.visible_edges.append(DrawableEdge(e.a, e.b))

    def clicked(self):
        pos = pygame.mouse.get_pos()
        return self.rect.collidepoint(pos)

    def mousebuttondown(self):
        point = DrawablePoint()
        if self.initial_point is None:
            self.initial_point = DrawablePoint(init=True)
            return
        for p in self.points:
            if p.close(point) and len(self.points) > 2:
                polygon = DrawablePolygon(self.points)
                self.polygons.append(polygon)
                self.points.clear()
                return
        self.points.append(point)

    def draw(self, screen):
        self.surface.fill(Color("white"))
        screen.blit(self.surface, self.rect)

        for p in self.polygons:
            p.draw(screen)

        for e in self.visible_edges:
            e.draw(screen)

        for p in self.points:
            p.draw(screen)

        if self.initial_point:
            self.initial_point.draw(screen)

    def clear(self):
        self.points.clear()
        self.polygons.clear()
        self.initial_point = None
        self.visible_edges.clear()
        self.screen.fill(pygame.Color("white"))


class DrawablePoint(Point):
    def __init__(self, x=None, y=None, init=False):
        if x is None and y is None:
            x, y = self.new_point()
        super().__init__(x, y)
        self.init = init

    def draw(self, screen):
        if self.init:
            color = pygame.Color("black")
            width = 9
        else:
            color = pygame.Color('red')
            width = 3
        pygame.draw.circle(screen, color, self.coordinates, width)

    def close(self, point, dist=10):
        return self.dist(point) < dist

    def new_point(self):
        pos = pygame.mouse.get_pos()
        return pos

class Button():
    def __init__(self, screen, txt, location, action, disabled=False, size=(80, 30)):
        self.color = Color("white")
        self.bg = Color("white")
        self.fg = Color("black")
        self.size = size
        self.disabled = disabled

        self.font = pygame.font.SysFont("Arial", 20)
        self.txt = txt
        self.txt_surf = self.font.render(self.txt, 1, self.fg)
        self.txt_rect = self.txt_surf.get_rect(center=[s//2 for s in self.size])

        self.surface = pygame.surface.Surface(size)
        self.rect = self.surface.get_rect(center=location)

        self.callback = action
        self.draw(screen)

    def draw(self, screen):
        self.mouseover()

        self.surface.fill(self.bg)
        self.surface.blit(self.txt_surf, self.txt_rect)
        screen.blit(self.surface, self.rect)

    def mouseover(self):
        if self.disabled:
            return
        self.bg = self.color
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos):
            self.bg = pygame.Color("bisque1")

    def clicked(self):
        pos = pygame.mouse.get_pos()
        return self.rect.collidepoint(pos)


if __name__ == "__main__":
    app = App()
    app.run()
