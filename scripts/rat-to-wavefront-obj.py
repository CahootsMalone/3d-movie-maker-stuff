import os
from threedmm_read_glxf import load_transforms
from threedmm_read_ggcl import load_ggcl
from threedmm_misc import apply_transform
from threedmm_bmdl import ThreeDMovieMakerBMDL

# By inspection of Totem Pole 1 transforms: identity matrix has elements set to 65532 where 1.0 would make sense.
SCALE_TRANSFORM = 65535.0

EXTENSION_BMDL = '.BMDL'

def add_bmdl_to_obj_file(path_bmdl_file, path_obj_file, existing_vertex_count, object_name, transforms, mat_name):

    source_model = ThreeDMovieMakerBMDL(path_bmdl_file)

    vertex_count = len(source_model.vertices)
    triangle_count = len(source_model.triangles)

    with open(path_obj_file, 'a') as obj_file:

        obj_file.write("o " + object_name + "\n")
        obj_file.write("s 1\n")
        obj_file.write("usemtl " + mat_name + "\n")

        for i in range(vertex_count):
            
            vertex = source_model.vertices[i]

            new_vector = [vertex.x, vertex.y, vertex.z]
            for transform in transforms:
                new_vector = apply_transform(transform, new_vector, SCALE_TRANSFORM, 1)

            obj_file.write("v " + str(new_vector[0]) + " " + str(new_vector[1]) + " " + str(new_vector[2]) + "\n")
            obj_file.write("vt " + str(vertex.u) + " " + str(vertex.v) + "\n")

        for i in range(triangle_count):

            triangle = source_model.triangles[i]

            # Vertex indices in Wavefront OBJ format start at one, not zero.
            v1 = triangle.v1 + existing_vertex_count + 1
            v2 = triangle.v2 + existing_vertex_count + 1
            v3 = triangle.v3 + existing_vertex_count + 1
            
            obj_file.write("f " + str(v1) + "/" + str(v1) + " " + str(v2) + "/" + str(v2) + " " + str(v3) + "/" + str(v3) + "\n")
    
    return vertex_count


path_base = "C:/3D Movie Maker stuff/Rat"
glxf_path = path_base + "/rat at rest.GLXF"
ggcl_path = path_base + "/rat at rest.GGCL"
path_bmdl_directory = path_base



transforms = load_transforms(glxf_path)

for i in range(len(transforms)):
    print("Transform " + str(i) + ": " + str(transforms[i]))



frames = load_ggcl(ggcl_path)

for i in range(len(frames)):
    print("Frame " + str(i))
    for j in range(len(frames[i])):
        print("\t" + str(frames[i][j]))



bmdl_files = []

# TODO order intelligently rather than requiring leading zeroes in file names.
for file in os.listdir(path_bmdl_directory):
    if file.endswith(EXTENSION_BMDL):
        bmdl_files.append(file)

print(bmdl_files)



identity_transform = [SCALE_TRANSFORM, 0, 0, 0, SCALE_TRANSFORM, 0, 0, 0, SCALE_TRANSFORM, 0, 0, 0]

for frame_index in range(len(frames)):

    out_path = 'out-' + str(frame_index) + '.obj'

    with open(out_path, 'w') as out_file:
        out_file.write("# BMDL from 3D Movie Maker converted to Wavefront OBJ\n")

    vertex_count = 0

    print("Frame " + str(frame_index))
    print("\tMove units: " + str(frames[frame_index][0]))

    for pair_index in range(len(frames[frame_index][1])):
        
        index_bmdl = frames[frame_index][1][pair_index][0]
        index_glxf = frames[frame_index][1][pair_index][1]
        
        print("\tBMDL: " + str(index_bmdl) + ", GLXF: " + str(index_glxf))

        bmdl_file_name = bmdl_files[index_bmdl]
        bmdl_path = path_bmdl_directory + "/" + bmdl_file_name
        object_name = bmdl_file_name

        material_name = "mat" + bmdl_file_name

        if pair_index == 0:
            # Just apply the specified transform.
            vertex_count += add_bmdl_to_obj_file(bmdl_path, out_path, vertex_count, object_name, [transforms[index_glxf]], material_name)
        elif index_bmdl in [6, 7, 8, 9, 10]: # Eyes, ears, and nose of rat
            # TODO figure this out based on a file, not by inspection; unknown where this info is stored

            index_first_glxf = frames[frame_index][1][0][1]
            index_head_glxf = frames[frame_index][1][6][1]
            
            # Located correctly relative to each other, but rotated and too large
            #vertex_count += add_bmdl_to_obj_file(bmdl_path, out_path, vertex_count, object_name, [transforms[index_glxf]])

            # Located correctly relative to each other, but rotated and too large; slightly different scale and position
            #vertex_count += add_bmdl_to_obj_file(bmdl_path, out_path, vertex_count, object_name, [transforms[index_glxf], transforms[index_head_glxf]])

            vertex_count += add_bmdl_to_obj_file(bmdl_path, out_path, vertex_count, object_name, [transforms[index_glxf], transforms[index_head_glxf], transforms[index_first_glxf]], material_name)
        else:
            # Apply the transform from the first pair, then the specified transform.
            index_first_glxf = frames[frame_index][1][0][1]
            vertex_count += add_bmdl_to_obj_file(bmdl_path, out_path, vertex_count, object_name, [transforms[index_glxf], transforms[index_first_glxf]], material_name)
