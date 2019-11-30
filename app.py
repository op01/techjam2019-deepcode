from flask import Flask, escape, request, jsonify
import pickledb
import math
from itertools import combinations
from werkzeug.debug import DebuggedApplication
app = Flask(__name__)
db = pickledb.load('example.db', True,sig=False)

@app.route('/')
def hello():
    name = request.args.get("name", "World")
    #return f'Hello, {escape(name)}!'
    return 'Hello'
def convert_pos(old):
    ret={}
    if 'north' in old:
        ret['y']=old['north']
    if 'south' in old:
        ret['y']=-old['south']
    if 'east' in old:
        ret['x']=old['east']
    if 'west' in old:
        ret['x']=-old['west']
    return ret
@app.route('/distance',methods=['POST'])
def distance():
    if isinstance(request.json['first_pos'],str):
        pos = db.get(request.json['first_pos'])['position']
        ax = pos['x']
        ay = pos['y']
    else:
        pos = convert_pos(request.json['first_pos'])
        ax = pos['x']
        ay = pos['y']
    if isinstance(request.json['second_pos'],str):
        pos = db.get(request.json['second_pos'])['position']
        bx = pos['x']
        by = pos['y']
    else:
        pos = convert_pos(request.json['second_pos'])
        bx = pos['x']
        by = pos['y']
    ret = math.sqrt((ax-bx)*(ax-bx)+(ay-by)*(ay-by)) 
    if 'metric' in request.json:
        metric = request.json['metric']
        ret = .0
        if metric == 'manhattan': ret = abs(ax-bx)+abs(ay-by)
        elif metric == 'euclidean': ret = math.sqrt((ax-bx)*(ax-bx)+(ay-by)*(ay-by))
    return jsonify({'distance': ret})
def euclidean_distance(ax,ay,bx,by):
    return math.sqrt((ax-bx)*(ax-bx)+(ay-by)*(ay-by))
@app.route('/robot/<robot_id>/position')
def getrpos(robot_id):
    key='robot#'+robot_id
    if db.get(key) == False:
        return '',404
    return jsonify({'position':db.get(key)['position']})

@app.route('/robot/<robot_id>/position',methods=['PUT'])
def setrpos(robot_id):
    key='robot#'+robot_id
    data = {}
    if db.get(key) != False:
        data = db.get(key)
    if 'x' in request.json['position']:
        data['position'] = request.json['position']
    else:
        data['position'] = convert_pos(request.json['position'])
    db.set(key,data)
    return '',204

@app.route('/nearest',methods=['POST'])
def nearest():
    pos = request.json['ref_position']
    x = pos['x']
    y = pos['y']
    k = 1
    if 'k' in request.json:
        k = request.json['k']
    keys = db.getall()
    robot_list=[]
    for key in keys:
        if key.startswith('robot#'):
            r=db.get(key)
            r['id']=key
            robot_list.append(r)
    ans=[]
    if len(robot_list)==0:
        pass
    else:
        robot_list.sort(key=lambda r:(euclidean_distance(r['position']['x'],r['position']['y'],x,y),int(r['id'][6:])))
        ans=list(map(lambda x:x['id'],robot_list[:k]))
        # selected_robot = robot_list[0]
        # for robot in robot_list:
        #     if 'position' in robot:
        #         rx = robot['position']['x']
        #         ry = robot['position']['y']
        #         srx = selected_robot['position']['x']
        #         sry = selected_robot['position']['y']
        #         if euclidean_distance(x,y,rx,ry) < euclidean_distance(x,y,srx,sry):
        #             selected_robot = robot
        # ans.append(int(selected_robot['id'][6:]))
    return jsonify({"robot_ids":ans})

@app.route('/alien/<object_dna>/report',methods=['POST'])
def report_alien(object_dna):
    global debugx
    key='alien#'+object_dna
    if db.get(key) != False:
        alien = db.get(key)
    else:
        alien = {'report':[]}
    report = {
        'distance':request.json['distance']
    }
    report['robot'] = db.get('robot#'+str(request.json['robot_id']))
    alien['report'].append(report)
    db.set(key,alien)
    return '',204

def find2intersect(x0,y0,r0,x1,y1,r1):
    # /* dx and dy are the vertical and horizontal distances between
    # * the circle centers.
    # */
    dx = x1 - x0
    dy = y1 - y0

    # /* Determine the straight-line distance between the centers. */
    d = Math.sqrt((dy*dy) + (dx*dx))

    # /* Check for solvability. */
    if d > (r0 + r1):
        # /* no solution. circles do not intersect. */
        return false
    if d < Math.abs(r0 - r1):
        # /* no solution. one circle is contained in the other */
        return false

    # /* 'point 2' is the point where the line through the circle
    # * intersection points crosses the line between the circle
    # * centers.
    # */

    # /* Determine the distance from point 0 to point 2. */
    a = ((r0*r0) - (r1*r1) + (d*d)) / (2.0 * d)

    # /* Determine the coordinates of point 2. */
    point2_x = x0 + (dx * a/d)
    point2_y = y0 + (dy * a/d)

    # /* Determine the distance from point 2 to either of the
    # * intersection points.
    # */
    h = Math.sqrt((r0*r0) - (a*a))

    # /* Now determine the offsets of the intersection points from
    # * point 2.
    # */
    rx = -dy * (h/d)
    ry = dx * (h/d)

    # /* Determine the absolute intersection points. */
    intersectionPoint1_x = point2_x + rx
    intersectionPoint2_x = point2_x - rx
    intersectionPoint1_y = point2_y + ry
    intersectionPoint2_y = point2_y - ry
    return intersectionPoint1_x,intersectionPoint1_y,intersectionPoint2_x,intersectionPoint2_y

@app.route('/alien/<object_dna>/position')
def find_alien(object_dna):
    alien = db.get('alien#'+object_dna)
    if len(alien['report']) < 2: return '',424

    x1 = alien['report'][0]['robot']['position']['x']
    y1 = alien['report'][0]['robot']['position']['y']
    r1 = alien['report'][0]['distance']
    x2 = x1
    y2 = y1
    r2 = r1
    for report in alien['report']:
        if report['robot']['position']['x'] != x1 or report['robot']['position']['y']!=y1:
            x2 = report['robot']['position']['x']
            y2 = report['robot']['position']['y']
            break
    if x1 == x2 and y1 == y2:
        return '', 424
    x1, y1, x2, y2 = find2intersect(x1,y1,r1,x2,y2,r2)
    if abs(x1-x2) < 1e-9 and abs(y1-y2) < 1e-9:
        return jsonify({'position': {'x': x1, 'y':y1}})
    for report in alien['report']:
        x = report['robot']['position']['x']
        y = report['robot']['position']['y']
        r = report['distance']
        c1 = (abs((x1-x)*(x1-x)+(y1-y)*(y1-y) - r*r) < 1e-9)
        c2 = (abs((x2-x)*(x2-x)+(y2-y)*(y2-y) - r*r) < 1e-9)
        if c1 and c2: continue
        elif c1: return jsonify({'position': {'x': x1, 'y':y1}})
        elif c2: return jsonify({'position': {'x': x2, 'y':y2}})
    return '',424
def euclidean_distance2(p1,p2):
    return euclidean_distance(p1[0],p1[1],p2[0],p2[1])
def closest(points_list):
    return min((euclidean_distance2(p1, p2), p1, p2) for p1, p2 in combinations(points_list, r=2))

@app.route('/closestpair')
def closestpair():
    keys = db.getall()
    points_list=[]
    for k in keys:
        if k.startswith('robot#'):
            r=db.get(k)
            points_list.append((r['position']['x'],r['position']['y']))
    if len(points_list)<2:
        return '',424
    return jsonify({'distance':closest(points_list)[0]})
    
    