ORDER_LITTLE = 'little'
FRAMES_START = 24
BYTE_COUNT_MOVE_UNITS = 4
BYTE_COUNT_END_MARKER = 4

# Returns list of frames.
# Each frame contains an unknown value and a list of pairs of BMDL and GLXF indices.
def load_ggcl(file_path):

    with open(file_path, 'rb') as file:
        data = file.read()

    frame_count = int.from_bytes(data[4:8], byteorder=ORDER_LITTLE, signed=False)
    total_frame_data_length = int.from_bytes(data[8:12], byteorder=ORDER_LITTLE, signed=False)

    frame_data_length = int(total_frame_data_length / frame_count)
    reference_count_per_frame = int((frame_data_length - BYTE_COUNT_MOVE_UNITS - BYTE_COUNT_END_MARKER) / 4)

    frames = []

    for i in range(frame_count):

        frame_start = FRAMES_START + i*frame_data_length

        move_units = int.from_bytes(data[frame_start:frame_start+BYTE_COUNT_MOVE_UNITS], byteorder=ORDER_LITTLE, signed=False)

        indices = []

        for j in range(reference_count_per_frame):

            offset_index_bmdl = BYTE_COUNT_MOVE_UNITS + j*4
            offset_index_glxf = offset_index_bmdl + 2

            index_bmdl = int.from_bytes(data[frame_start+offset_index_bmdl:frame_start+offset_index_bmdl+2], byteorder=ORDER_LITTLE, signed=False)
            index_glxf = int.from_bytes(data[frame_start+offset_index_glxf:frame_start+offset_index_glxf+2], byteorder=ORDER_LITTLE, signed=False)

            indices.append((index_bmdl, index_glxf))
        
        frames.append((move_units, indices))
    
    return frames
