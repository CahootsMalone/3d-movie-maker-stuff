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


path_base = "C:/3D Movie Maker stuff/Cat"
glxf_path = path_base + "/at rest.GLXF"
ggcl_path = path_base + "/at rest.GGCL"
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

# For the cat, the first BMDL is empty and presumably serves to establish a coordinate frame for the cat.
# For the cat's spin animation, only the transform of the first pair (which uses BMDL 00) changes.
# BMDL 00 appears again in the sixth pair.


# By inspection, the cat's model hierarchy is:
# Pair 0 (reference frame 1)
#   Body
#     Front legs (2 models)
#     Tail
#     Pair 5 (reference frame 2)
#       Head
#         Ears (2 models)
#         Back of head (its own model, for some reason; the head otherwise has a large hole in it)


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
        elif index_bmdl in [2, 3, 4]: # Left front leg, right front leg, tail

            # Frame index / list of pairs / pair index / glxf
            # I should write a class for the frames as these nested indices are rather ridiculous!
            index_ref_1_glxf = frames[frame_index][1][0][1]
            index_body_glxf = frames[frame_index][1][1][1]

            vertex_count += add_bmdl_to_obj_file(bmdl_path, out_path, vertex_count, object_name, [transforms[index_glxf], transforms[index_body_glxf], transforms[index_ref_1_glxf]], material_name)
        elif index_bmdl in [5]: # Head
            index_ref_1_glxf = frames[frame_index][1][0][1]
            index_body_glxf = frames[frame_index][1][1][1]
            index_ref_2_glxf = frames[frame_index][1][5][1]

            vertex_count += add_bmdl_to_obj_file(bmdl_path, out_path, vertex_count, object_name, 
                [transforms[index_glxf], transforms[index_ref_2_glxf], transforms[index_body_glxf], transforms[index_ref_1_glxf]], material_name)

        elif index_bmdl in [6, 7, 8]: # Ears and back of cat's head (strange that the back of the head is separate from the rest of it)
            index_ref_1_glxf = frames[frame_index][1][0][1]
            index_body_glxf = frames[frame_index][1][1][1]
            index_ref_2_glxf = frames[frame_index][1][5][1]
            index_head_glxf = frames[frame_index][1][6][1] # The head is BMDL 05, which appears in the pair at index 6

            vertex_count += add_bmdl_to_obj_file(bmdl_path, out_path, vertex_count, object_name, 
                [transforms[index_glxf], transforms[index_head_glxf], transforms[index_ref_2_glxf], transforms[index_body_glxf], transforms[index_ref_1_glxf]], material_name)
        else:
            # Apply the transform from the first pair, then the specified transform.
            index_first_glxf = frames[frame_index][1][0][1]
            vertex_count += add_bmdl_to_obj_file(bmdl_path, out_path, vertex_count, object_name, 
                [transforms[index_glxf], transforms[index_first_glxf]], material_name)
