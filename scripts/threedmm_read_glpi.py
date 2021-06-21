ORDER_LITTLE = 'little'

# Returns list of GGCL pair parent IDs (index into list is GGCL pair ID of child).
# A parent ID of -1 means the pair has no parent.
# Each GGCL pair specifies a model and a transform.
# The GLPI file specifies the parenting hierarchy.
# For example, the parent of the GGCL pair containing a character's head is usually the GGCL pair containing their body.
def read_glpi(file_path: str):

    with open(file_path, 'rb') as file:
        data = file.read()
    
    count = int.from_bytes(data[8:12], byteorder=ORDER_LITTLE, signed=False)

    out = []

    for i in range(count):
        offset = 12 + i*2
        out.append(int.from_bytes(data[offset:offset+2], byteorder=ORDER_LITTLE, signed=True))

    return out
