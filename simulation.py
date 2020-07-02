import numpy as np
import pyglet as pg
import random

window = pg.window.Window()
graph = {}

class Node:
    def __init__(self,label,x=0,y=0):
        self.r = 30
        self.x = x
        self.y = y
        self.label = label
        self.neighbors = list()

    def add_neighbor(self,node,probability):
        self.neighbors.append({
            'Node':node,
            'prob':probability
            })

    def __str__(self):
        return self.label+':'+str([(n['Node'].label,n['prob']) for n in self.neighbors])
    
    def __repr__(self):
        return self.label+':'+str([(n['Node'].label,n['prob']) for n in self.neighbors])


def get_node(key,graph): 
    existing_node = graph.get(key)
    if existing_node==None:
        graph[key] = Node(key)
        return graph[key]
    return existing_node

def get_graph(path):
    prefix = 'S'
    trans_matrix = np.loadtxt(open(path,'r'),delimiter=',')
    graph = {}

    i=1
    for row in trans_matrix:
        node = get_node(prefix+str(i),graph)
        i+=1
        j=1
        for col in row:
            if col>0:
                neighbor = get_node(prefix+str(j),graph)
                graph.get(node.label).add_neighbor(neighbor,col)
            j+=1
    return graph

def draw_node(node):
    batch = pg.graphics.Batch()
    circle = pg.shapes.Circle(node.x,node.y,node.r,batch=batch)
    pglabel = pg.text.Label(text=node.label,x=circle.x,y= circle.y,color=(0,0,0,255),
                                anchor_x='center',anchor_y='center' ,batch=batch)
    pglabel.bold=True
    draw_connections(node)
    batch.draw()
    


def draw_connections(node):
    
    for elem in node.neighbors:
        neighbor = elem['Node']
        prob = elem['prob']

        arrow = pg.graphics.Batch()
        destX = neighbor.x
        destY = neighbor.y
        
        line = pg.shapes.Line(node.x,node.y,destX,destY,batch=arrow)

        label = pg.text.Label(text=str(prob),x=(node.x+destX)//2,y=(node.y+destY)//2,
                    anchor_x='center',anchor_y='center',batch=arrow)

        arrow.draw()

def set_nodes_positions(graph):
    x = 150
    y = 150
    i=1
    for key in graph.keys():
        node = graph[key]
        if node.x==0 and node.y==0:
            node.x=x
            node.y=y
            for elem in node.neighbors:
                elem['Node'].x = x+ i*200
                elem['Node'].y = y
                y +=100
                x +=50
                i = -i

def find_node_by_coordinates(x,y):
    node = None
    for n in graph.values():
        if  n.x - n.r < x < n.x + n.r and n.y - n.r < y < n.y + n.r :
            node = n
            break

    return node

selectedNode = None
def on_mouse_press(x,y,button,modifiers):
    global graph,selectedNode
    if button == 1:
        selectedNode = find_node_by_coordinates(x,y)

def on_mouse_drag(x,y,dx,dy,button,modifiers):
    global selectedNode
    if selectedNode!= None:
        selectedNode.x = x
        selectedNode.y = y

@window.event
def on_draw():
    window.clear()
    global graph
    for node in graph.values():
        draw_node(node)
  

def main():
    global graph
    #pg.clock.schedule_interval(draw, 1/120.0)
    trans_matrix = 'transition_matrix.csv'#test.csv
    graph = get_graph(trans_matrix)
    set_nodes_positions(graph)
    
    window.on_mouse_drag = on_mouse_drag
    window.on_mouse_press = on_mouse_press
    pg.app.run()

if __name__ == "__main__":
    main()