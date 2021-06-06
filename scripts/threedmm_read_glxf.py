ORDER_LITTLE = 'little'
TRANSFORMS_START = 12

# Returns list of transforms, read in row major order.
def load_transforms(file_path):

    with open(file_path, 'rb') as file:
        data = file.read()

    transform_length = int.from_bytes(data[4:8], byteorder=ORDER_LITTLE, signed=False)
    transform_count = int.from_bytes(data[8:12], byteorder=ORDER_LITTLE, signed=False)

    transforms = []

    for i in range(transform_count):

        transform_start = TRANSFORMS_START + i*transform_length

        transform = []
        for j in range(12):

            offset = transform_start + j*4

            element = int.from_bytes(data[offset:offset+4], byteorder=ORDER_LITTLE, signed=True)

            transform.append(element)
        
        transforms.append(transform)
    
    return transforms
