import numpy as np
import pyglet as pg
import random
import math

window = pg.window.Window(resizable=True)
graph = {}

class Node:
    def __init__(self,label,x=0,y=0,color=(150,150,150)):
        self.r = 30
        self.x = x
        self.y = y
        self.color = color
        self.label = label
        self.neighbors = list()

    def add_neighbor(self,node,probability):
        self.neighbors.append({
            'Node':node,
            'prob':probability
            })

    def next_state(self):
        
        next_node = None
        if len(self.neighbors) != 0:
            pick_list = []
            for neighbor in self.neighbors:
                temp = [{'key':neighbor['Node'].label,'prob':neighbor['prob']}]*int(neighbor['prob']*10)
                pick_list.extend(temp)
            random.shuffle(pick_list)
            next_node = random.choice(pick_list)

        return next_node

    def reset_color(self):
        self.color = (150,150,150)

    def __str__(self):
        return self.label+':'+str([(n['Node'].label,n['prob']) for n in self.neighbors])
    
    def __repr__(self):
        return self.label+':'+str([(n['Node'].label,n['prob']) for n in self.neighbors])


def get_node(key,graph): 
    global records
    existing_node = graph.get(key)
    if existing_node==None:
        graph[key] = Node(key)
        records[key] = 0
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
                label = prefix+str(j)
                """ if col == 1 and node.label == label :
                    break """
                neighbor = get_node(label,graph)
                graph.get(node.label).add_neighbor(neighbor,col)
            j+=1
    
    return graph


def set_nodes_positions(graph):
    x = 100
    y = window.height-50
    for key in graph:
        graph[key].x = x
        graph[key].y = y
        x+=100
        if x > window.width:
            y-= 100
            x = 100

def find_node_by_coordinates(x,y):
    node = None
    for n in graph.values():
        if  n.x - n.r < x < n.x + n.r and n.y - n.r < y < n.y + n.r :
            node = n
            break

    return node

def normalized_dist_vector(vec1,vec2):
    n_dist_vec = vec1
    if (vec1 != vec2).any():
        distance_vec = vec2-vec1
        n_dist_vec = distance_vec / np.sqrt(np.sum(distance_vec**2))
        n_dist_vec = n_dist_vec*29 + vec1

    return n_dist_vec

def get_label_pos(src,dest):
    if (src != dest).any():
        middle = (src+dest)/2
        d = src-dest
        d = d / np.sqrt(np.sum(d**2))
        orth_vec = np.array([-d[1]/d[0],1]) if d[0]!=0 else np.array([1,0])
        orth_vec = orth_vec / np.sqrt(np.sum(orth_vec**2))
        pos = middle + orth_vec*15
        return pos
    return dest

def draw_nodes(graph):
    for node in graph.values():
        draw_connections(node)

    for node in graph.values():
        circle = pg.shapes.Circle(node.x,node.y,node.r,color=node.color)
        pglabel = pg.text.Label(text=node.label,x=node.x,y= node.y,color=(0,0,0,255),
                                    anchor_x='center',anchor_y='center')
        pglabel.bold=True
        circle.draw()
        pglabel.draw()

def draw_connections(node):
    for elem in node.neighbors:
        neighbor = elem['Node']
        prob = elem['prob']
        arrow = pg.graphics.Batch()
        if neighbor.label != node.label:
            source = np.array([node.x,node.y])
            dest = np.array([neighbor.x,neighbor.y])

            line = pg.shapes.Line(node.x,node.y,dest[0],dest[1],width=3,color=(200,200,200),batch=arrow)
            
            dist_vector = normalized_dist_vector(dest,source)
            rec = pg.shapes.Rectangle(dist_vector[0],dist_vector[1],18,18,color=(200,200,200),batch=arrow)
            rec.anchor_x = rec.width//2
            rec.anchor_y = rec.height//2

            label_pos = get_label_pos(source,dest)
            
        else :
            arc = pg.shapes.Arc(node.x-node.r,node.y-node.r,20,batch=arrow)
            label_pos = (arc.x-node.r,arc.y-node.r)

        label = pg.text.Label(text=str(prob),x=label_pos[0],y=label_pos[1],
                        anchor_x='center',anchor_y='center',batch=arrow)
        label.bold = True
        arrow.draw()

records = {}
def draw_records():
    labels_batch = pg.graphics.Batch()
    labels = []
    xoff = (window.width)//(len(records)+1)
    x = xoff
    for key in records:
        label = pg.text.Label(text=key + ': '+str(records[key]),x=x,y=30,
                    anchor_x='center',anchor_y='center',batch=labels_batch)
        label.bold = True
        labels.append(label)
        x+= xoff
    labels_batch.draw()


selectedNode = None
@window.event
def on_mouse_press(x,y,button,modifiers):
    global graph,selectedNode
    if button == 1:
        selectedNode = find_node_by_coordinates(x,y)

@window.event
def on_mouse_drag(x,y,dx,dy,button,modifiers):
    global selectedNode
    if selectedNode!= None:
        selectedNode.x = x
        selectedNode.y = y

@window.event
def on_draw():
    window.clear()
    draw_nodes(graph)
    draw_records()
  
start = False
current_node_key = 'S1'
previous_node_key = None
@window.event
def on_key_press(symbole,modifier):
    global start,current_node_key,records
    if symbole==32: #space bar
        start = not start
        
    else:
        current_node_key = 'S1'
        for key in records:
            records[key] = 0




def start_simulation(value):
    global graph,current_node_key,previous_node_key,start,records
    if start:
        if previous_node_key != None:
            graph[previous_node_key].reset_color()
            
        previous_node_key = current_node_key
    
        node = graph[current_node_key]
        node.color = (200,100,20)
        records[current_node_key] += 1
       
        next_node = node.next_state()
        
        if next_node['prob'] == 1 and next_node['key'] == current_node_key: 
            current_node_key = 'S1'
        else:
            current_node_key = next_node['key']
        



def main():
    global graph
    
    trans_matrix = ['transition_matrix.csv','test.csv']
    graph = get_graph(trans_matrix[0])
    set_nodes_positions(graph)

    pg.clock.schedule_interval(start_simulation,1/5)

    window.set_caption('Markove Chaine Simulation')
    pg.app.run()

if __name__ == "__main__":
    main()