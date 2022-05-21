import bpy
import random 
from mathutils import Vector, Matrix

#variables
count = 50 
cubes=[]

#delete every existing node_group 
for grp in bpy.data.node_groups:
    bpy.data.node_groups.remove(grp)

#delete every existing object
for ob in bpy.data.objects:   
    bpy.data.objects.remove(ob)
    
#add counter object, set position of counter object below other cube
bpy.ops.mesh.primitive_cube_add(location = (-2.5, 0, -3.375)) 
bpy.context.active_object.name = 'Counter'

#add geometry node modifier
bpy.ops.object.modifier_add(type='NODES')

#get and clear node_group
node_grp = bpy.data.node_groups[-1] 
node_grp.nodes.clear()

#add nodes
stringToCurves = node_grp.nodes.new("GeometryNodeStringToCurves")
fillCurve = node_grp.nodes.new("GeometryNodeFillCurve")
transform = node_grp.nodes.new("GeometryNodeTransform")
joinStrings = node_grp.nodes.new("GeometryNodeStringJoin")
comparisonString = node_grp.nodes.new("FunctionNodeInputString")
comparisonCounter = node_grp.nodes.new("FunctionNodeValueToString")
arrayString = node_grp.nodes.new("FunctionNodeInputString")
arrayCounter = node_grp.nodes.new("FunctionNodeValueToString")
groupOutput = node_grp.nodes.new('NodeGroupOutput')

#90 degree rotation of the counter object
transform.inputs[2].default_value[0] = 1.5708 
#set default values of some nodes
comparisonString.string = "Comparisons:"
arrayString.string = "Array Accesses:"
stringToCurves.inputs[1].default_value = 2
joinStrings.inputs[0].default_value = " "

#connect nodes to eachother
node_grp.links.new(fillCurve.outputs[0], groupOutput.inputs[0])
node_grp.links.new(transform.outputs[0], fillCurve.inputs[0])
node_grp.links.new(stringToCurves.outputs[0], transform.inputs[0])
node_grp.links.new(joinStrings.outputs[0], stringToCurves.inputs[0])
node_grp.links.new(comparisonCounter.outputs[0], joinStrings.inputs[1])
node_grp.links.new(comparisonString.outputs[0], joinStrings.inputs[1])
node_grp.links.new(arrayCounter.outputs[0], joinStrings.inputs[1])
node_grp.links.new(arrayString.outputs[0], joinStrings.inputs[1])

#fill arrays with numbers between 1 & count
ran = list(range(1,count+1))

#randomize array order
random.shuffle(ran)

#sets origin of cube to bottom of mesh
def origin_to_bottom(ob, matrix=Matrix()):
    me = ob.data
    mw = ob.matrix_world
    local_verts = [matrix @ Vector(v[:]) for v in ob.bound_box]
    o = sum(local_verts, Vector()) / 8
    o.z = min(v.z for v in local_verts)
    o = matrix.inverted() @ o
    me.transform(Matrix.Translation(-o))
    mw.translation = mw @ o
    
#create cubes with random location
for i in range(count):
    bpy.ops.mesh.primitive_cube_add(location=(ran[i], 0, 0), scale=(0.25, 0.25, 0.25))   
    
#shuffle array
random.shuffle(ran)
  
#assign random scale to all cubes and add them to array
i = 0
for ob in bpy.data.objects:
    if ob.type == 'MESH' and ob.name != "Counter":    
        origin_to_bottom(ob)
        ob.scale.z = ran[i]
        cubes.append(ob)
        i += 1

#sort array based on location.x        
cubes.sort(key = lambda obj: obj.location.x)

#start at frame 0
iframe=0
originFrame = 0 

#insertion sort alogrithm
for i in range(0, count):
    
    #defines key_item that is compared until correct location
    key_item = cubes[i]
    key_item.location.x = i
    j = i - 1
    print(i)
    while j >= 0 and cubes[j].scale.z > key_item.scale.z:
        
        #sets position of item in array
        cubes[j + 1] = cubes[j]
        cubes[j + 1].location.x = j 
        
        #sets location
        cubes[j].location.x = j + 1 
        j -= 1
        
        #adding keyframes to all cubes whenever one position/location is shifted
        for cube in cubes:
            cube.keyframe_insert(data_path="location", frame=iframe)       
        
        #next frame
        iframe+=1  
 
            
    #place key_item into correct position/location
    cubes[j + 1] = key_item
    cubes[j + 1].location.x = i
    key_item.location.x = j + 1
    
    #origin and target index of key_item in array
    origin = i
    target = j + 1
    
    x = 0
    while x <= (origin-target):
        
        #set location/position for key_item + add keyframes
        key_item.location.x = origin - x
        key_item.keyframe_insert(data_path="location", frame= originFrame + x - 1)
        
        x += 1
    
    originFrame = iframe


    

    
    