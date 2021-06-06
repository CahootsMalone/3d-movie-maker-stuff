def apply_transform(transform, vector, transform_scale_factor, vector_scale_factor):
    x = vector[0] / vector_scale_factor
    y = vector[1] / vector_scale_factor
    z = vector[2] / vector_scale_factor

    # See https://rr2000.cwaboard.co.uk/R4/BRENDER/TEBK_47.HTM#MARKER2_212

    e00 = transform[0] / transform_scale_factor
    e01 = transform[1] / transform_scale_factor
    e02 = transform[2] / transform_scale_factor
    e03 = 0

    e10 = transform[3] / transform_scale_factor
    e11 = transform[4] / transform_scale_factor
    e12 = transform[5] / transform_scale_factor
    e13 = 0

    e20 = transform[6] / transform_scale_factor
    e21 = transform[7] / transform_scale_factor
    e22 = transform[8] / transform_scale_factor
    e23 = 0

    e30 = transform[9] / transform_scale_factor
    e31 = transform[10] / transform_scale_factor
    e32 = transform[11] / transform_scale_factor
    e33 = 1

    xNew = x*e00 + y*e10 + z*e20 + 1*e30
    yNew = x*e01 + y*e11 + z*e21 + 1*e31
    zNew = x*e02 + y*e12 + z*e22 + 1*e32
    wNew = x*e03 + y*e13 + z*e23 + 1*e33

    return [xNew/wNew, yNew/wNew, zNew/wNew]
