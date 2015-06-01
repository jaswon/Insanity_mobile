from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.properties import NumericProperty, ListProperty, ObjectProperty, StringProperty
from kivy.graphics import Rectangle, Ellipse, Color
from kivy.animation import Animation
from kivy.core.window import Window
from kivy.lang import Builder
import math
from random import shuffle

Builder.load_string('''
#:import Window kivy.core.window.Window

<SwipeGame>:
    maze: container_id

    GameContainer:
        id: container_id

    GameLabel:
        text: "deaths: "
        pos: Window.width/2-25,(Window.height+self.parent.maze.segmDim*(self.parent.maze.mazeDim*2+1))/2-15
        halign: 'right'
        text_size: Window.width/3, None
    GameLabel:
        text: "level: "
        pos: Window.width/2-25,(Window.height+self.parent.maze.segmDim*(self.parent.maze.mazeDim*2+1))/2+15
        halign: 'right'
        text_size: Window.width/3, None
    GameLabel:
        text: self.parent.str_deaths
        halign: 'left'
        text_size: Window.width/3, None
        pos: Window.width*5/6-25,(Window.height+self.parent.maze.segmDim*(self.parent.maze.mazeDim*2+1))/2-15
    GameLabel:
        text: self.parent.str_level
        halign: 'left'
        text_size: Window.width/3, None
        pos: Window.width*5/6-25,(Window.height+self.parent.maze.segmDim*(self.parent.maze.mazeDim*2+1))/2+15


<MazeVeil>:
    canvas:
        Color:
            hsv: 0,0,0
            a: self.shade
        Rectangle:
            size: Window.width, Window.height
            pos: 0,0

<GameSprite>:
    canvas:
        Color:
            rgba: 1,1,1,1
        Ellipse:
            pos: self.x*self.dim+self.pad/2+self.x_buf, self.y*self.dim+self.pad/2+self.y_buf
            size: self.dim-self.pad, self.dim-self.pad

<GameLabel@Label>:
    font_size: 30
    font_name: 'geo.ttf'
''')



class GameContainer(Widget):

    dx = NumericProperty(0)
    dy = NumericProperty(0)
    mazeDim = NumericProperty(1)
    segmDim = NumericProperty(0.0)
    dispMaze = ListProperty([])
    player = ObjectProperty(None)
    veil = ObjectProperty(None)
    x_buf = NumericProperty(0.)
    y_buf = NumericProperty(0.)


    def on_touch_down(self, touch):
        self.dx = touch.x
        self.dy = touch.y
    pass

    def on_touch_up(self, touch):
        self.dx = touch.x - self.dx
        self.dy = touch.y - self.dy
        theta = math.atan2(self.dy,self.dx)
        move = self.player.size[0]
        if abs(self.dx) > 0 and abs(self.dy) > 0:
            if abs(theta) < math.pi/4:
                self.player.move(0,2)
            elif theta > math.pi/4 and theta < math.pi*3/4:
                self.player.move(1,2)
            elif abs(theta) > math.pi*3/4:
                self.player.move(2,2)
            else:
                self.player.move(3,2)

    def delete(self, i, j):
        self.canvas.remove(self.dispMaze[i][j])
        self.dispMaze[i][j] = None

    def buildMaze(self):
        with self.canvas:
            self.canvas.clear()
            self.dispMaze = []
            blocksize = (self.segmDim,self.segmDim)
            for i in range(self.mazeDim*2+1):
                self.dispMaze.append([])
                for j in range(self.mazeDim*2+1):
                    blockpos = (j*self.segmDim+self.x_buf,i*self.segmDim+self.y_buf)
                    self.dispMaze[i].append(Rectangle(pos=blockpos, size=blocksize))
            self.delete(self.mazeDim,0)
            self.delete(self.mazeDim,self.mazeDim*2)
            for i in range(self.mazeDim):
                for j in range(self.mazeDim):
                    self.delete(i*2+1,j*2+1)
            cur = [self.mazeDim,1]
            path = [cur]
            visited = []
            dirs = [[2,0],[0,-2],[-2,0],[0,2]]
            for i in range(self.mazeDim*2+1):
                visited.append([False] * (self.mazeDim*2+1))
            visited[cur[0]][cur[1]] = True
            while len(path) > 0:
                shuffle(dirs)
                dir = None
                for i in dirs:
                    y = cur[0]+i[0]
                    x = cur[1]+i[1]
                    if x > 0 and x < self.mazeDim*2+1 and \
                        y > 0 and y < self.mazeDim*2+1 and \
                        not visited[cur[0]+i[0]][cur[1]+i[1]]:
                            dir = list(i)
                            break
                if dir is None:
                    cur = path.pop()
                else:
                    self.delete(cur[0]+dir[0]/2,cur[1]+dir[1]/2)
                    visited[cur[0]+dir[0]][cur[1]+dir[1]] = True
                    cur = [cur[0]+dir[0],cur[1]+dir[1]]
                    path.append(cur)

    def start(self):
        self.mazeDim += 2
        self.segmDim = (min(Window.width, Window.height) - 100) / (self.mazeDim*2+1)
        self.x_buf = (Window.width-self.segmDim*(self.mazeDim*2+1))/2
        self.y_buf = (Window.height*2/3-self.segmDim*(self.mazeDim*2+1))/2
        self.buildMaze()
        self.veil = MazeVeil()
        self.add_widget(self.veil)
        self.player = GameSprite()
        self.add_widget(self.player)
        self.player.dim = self.segmDim
        self.player.x = 0
        self.player.y = self.mazeDim
        self.player.x_buf = self.x_buf
        self.player.y_buf = self.y_buf
        self.player.move(0,1)


class GameSprite(Widget):
    x = NumericProperty(0)
    y = NumericProperty(0)
    x_buf = NumericProperty(0)
    y_buf = NumericProperty(0)
    dim = NumericProperty(0)
    pad = NumericProperty(10)
    speed = NumericProperty(.05)

    def move(self, dir, len):
        if len != 0:
            dx = (1 if dir < 2 else -1) * (1 if dir % 2 == 0 else 0)
            dy = (1 if dir < 2 else -1) * (1 if dir % 2 == 1 else 0)

            anim = Animation(x=self.x+dx, y=self.y+dy, duration=self.speed)
            anim.bind(on_complete=(lambda x,y: self.checks(dir,len-1)))
            anim.start(self)

    def checks(self,dir,len):
        if self.parent.dispMaze[int(self.y)][int(self.x)] is not None:
            self.parent.parent.deaths += 1
            self.parent.veil.shade=0
            anim = Animation(shade=1, duration=.1)
            anim.start(self.parent.veil)
            self.x = 0
            self.y = self.parent.mazeDim
            Animation(x=self.x+1, duration=self.speed).start(self)
        elif self.x == 0:
            Animation.stop_all(self)
            Animation(x=self.x+1, duration=self.speed).start(self)
        elif self.x == self.parent.mazeDim*2:
            self.parent.parent.level += 1
            Animation.stop_all(self)
            self.parent.start()
        else:
            self.move(dir,len)

class MazeVeil(Widget):
    shade = NumericProperty(1)


class SwipeGame(Widget):

    deaths = NumericProperty(0)
    level = NumericProperty(1)

    str_deaths = StringProperty('0')
    str_level = StringProperty('1')

    def start(self):
        self.maze.start()

    def on_deaths(self, instance, value):
        self.str_deaths = str(self.deaths)

    def on_level(self, instance, value):
        self.str_level = str(self.level)

class swipeApp(App):

    game_engine = ObjectProperty(None)

    def on_start(self):
        self.game_engine.start()

    def build(self):
        self.game_engine = SwipeGame()
        return self.game_engine

if __name__ == '__main__':
    swipeApp().run()
