# 3D Movie Maker File Formats

This document describes some of the binary file formats used by [Microsoft 3D Movie Maker](https://en.wikipedia.org/wiki/3D_Movie_Maker) (3DMM).

While the abundance of tools and mods for 3DMM demonstrates that these file formats have already been reverse-engineered by others, I've been unable to find documentation for most the formats described in this document.

## General Notes

* In this document, "transform" is used (as it often is) to mean "[transformation matrix](https://en.wikipedia.org/wiki/Transformation_matrix)".
* All numeric values are little-endian.
* All floating-point values are stored as signed 32-bit (4-byte) integers. To convert them to their floating point values, divide by 65,535 (2<sup>16</sup> - 1).
  * I figured out the scale factor by looking at the transforms for Totem Pole 1, some of which are clearly identity matrices and contain only the values 0 and 65,532.
* 3DMM uses the [BRender (Blazing Render) 3D engine](https://en.wikipedia.org/wiki/Argonaut_Games#BRender).
* 3DMM's data files are stored in multiple compressed archive files in the program directory (`C:\Program Files (x86)\Microsoft Kids\3D Movie Maker` by default when installed on a 64-bit version of Windows). Individual data files can be extracted from the archive files using [3DMM Pencil++](http://frank.weindel.info/proj.pencil.html) by Frank Weindel.
* Some of the 3DMM data file formats have been documented by Foone Turing [here](https://floppy.foone.org/w/3DMM_Chunks_List). For some formats (like [GLXF](https://floppy.foone.org/w/GLXF)) there's only a link to documentation written by Scott Walentys, but [the repository](https://github.com/walentys/3DMMFBX) containing this documentation is no longer available (as of June 2021, GitHub returns a 404 when trying to access it).
* All the 3DMM data files I've examined start with 0x01_00_03_03. The meaning of these four bytes is discussed [in a blog post by Ben Stone](https://benstoneonline.com/posts/reverse-engineering-3d-movie-maker-part-five/) and [in Foone Turing's documentation](https://floppy.foone.org/w/Chunk_Signature).

## BMDL (3D Model)

The model format associated with the BRender engine. Relevant BRender documentation is archived [here](https://rr2000.cwaboard.co.uk/R4/BRENDER/TEBK_50.HTM) and [here](https://rr2000.cwaboard.co.uk/R4/BRENDER/UGBK_37.HTM) (unfortunately neither of these pages provide the format specification).

Note: Foone documented this file format [here](https://floppy.foone.org/w/BMDL).

Offset | Type | Length | Description
---|---|---|---
0 | N/A | 4 | Signature (0x01_00_03_03)
4 | uint | 2 | Vertex count (N<sub>vertices</sub>)
6 | uint | 2 | Triangle count (N<sub>triangles</sub>)
8 | N/A | 40 | Unknown (likely additional data, e.g., model flags, pivot point; usually all zeroes)
48 | N/A | 32 * N<sub>vertices</sub> | Vertices (see below)
48 + 32 * N<sub>vertices</sub> | N/A | 32 * N<sub>triangles</sub> | Triangles (see below)

### Vertex

Each vertex is represented by 32 bytes. All values should be divided by 65,535 to convert them to floating-point numbers.

Offsets are relative to the start of each vertex.

Offset | Type | Length | Description
---|---|---|---
0 | int | 4 | X coordinate
4 | int | 4 | Y coordinate
8 | int | 4 | Z coordinate
12 | int | 4 | U texture coordinate
16 | int | 4 | V texture coordinate
20 | N/A | 12 | Unknown (likely optional additional data, e.g., vertex colours, but usually all zeroes)

### Triangle

Each triangle is represented by 32 bytes.

Offsets are relative to the start of each triangle.

Offset | Type | Length | Description
---|---|---|---
0 | uint | 2 | Index of first vertex
2 | uint | 2 | Index of second vertex
4 | uint | 2 | Index of third vertex
6 | N/A | 26 | Unknown (likely optional additional data, e.g., smoothing group, edge flags, materials, etc., but usually zeroes; sometimes the value at offset 16 is 1)

## GGCL (List of Frames)

A GGCL file contains the list of frames for an animation. 

In 3D Movie Maker, characters are animated by transforming their individual parts (which are separate models) rather than through the use of [skeletal animation](https://en.wikipedia.org/wiki/Skeletal_animation).

Each frame consists of a list of pairs of model and transform indices. For a given frame, each pair specifies a model and the transform that should be applied to it (the transforms of the model's parent model(s) should also be applied). See the GLXF section for further details.

The number of pairs contained in each frame may vary to account for instances of models that are present in some frames but not others.

Offset | Type | Length | Description
---|---|---|---
0 | N/A | 4 | Signature (0x01_00_03_03)
4 | uint| 4 | Number of frames (N<sub>frames</sub>)
8 | unit | 4 | Length of frame data (L<sub>frame data</sub>)
12 | N/A | 4 | Unknown (always 0xFF_FF_FF_FF)
16 | uint | 4 | Unknown (always 8); might be frame rate
20 | N/A | 4 | Unknown (always 0x00_00_00_00)
24 | N/A | L<sub>frame data</sub> | Frames (see below)
24 + L<sub>frame data</sub> | N/A | 4 + 4 * (N<sub>frames</sub> - 1) | Frame lengths (see below)

### Frame

Each frame contains N<sub>pairs</sub> pairs of model and transform indices (N<sub>pairs</sub> = (L<sub>frame</sub> - 8)/4). Note that L<sub>frame</sub> must be obtained from the frame lengths section of the file (described in the "Frame Lengths" section, below).

Offsets are relative.

Offset | Type | Length | Description
---|---|---|---
0 | uint | 4 | Unknown (3DMM Pencil++ calls this value "move units")
4 | N/A | N<sub>pairs</sub> * 4 | Pairs (see blow)
4 + (N<sub>pairs</sub> * 4) | N/A | 4 | Unknown (always 0x00_00_00_00)

### Pair

N<sub>pairs</sub> pairs of model and transform indices occur within each frame.

Offsets are relative.

Offset | Type | Length | Description
---|---|---|---
0 | uint | 2 | Index of model (BMDL file associated with actor)
2 | uint | 2 | Index of transform (within GLXF file associated with animation)

### Frame Lengths

A list of frame lengths and offsets follows the frames themselves.

Offsets are relative.

For all frames except the last frame:

Offset | Type | Length | Description
---|---|---|---
0 | uint | 4 | Length of frame
4 | uint | 4 | Offset to start of next frame relative to start of frame data section in file (24)

Only the length is specified for the last frame.

## GLCR (Colour Palette)

Offset | Type | Length | Description
---|---|---|---
0 | N/A | 4 | Signature (0x01_00_03_03)
4 | uint | 4 | Number of channels (N<sub>channels</sub>); usually 4
8 | uint | 4 | Number of colours (N<sub>colours</sub>)
12 | N/A | N<sub>colours</sub> * N<sub>channels</sub> | Colours (see below)

### Colour

Each colour consists of N<sub>channels</sub> bytes, each specifying the unsigned value of a colour channel.

Offsets are relative.

Offset | Type | Length | Description
---|---|---|---
0 | uint | 1 | Blue component
1 | uint | 1 | Green component
2 | uint | 1 | Red component
3 | uint | 1 | Alpha component

## GLPI (List of Actor Body Part Parents)

In the GGCL file (described in detail above) for one of an actor's animations, each frame contains a list of pairs of models (stored in BMDL files) and transforms (stored in the actor's GLXF file). Each pair represents one of the actor's body parts. Multiple pairs may refer to the same model if it's used more than once (for example, both Fabrice the rat's front legs use the same model).

Each body part/GGCL pair may have a parent: if so, the model associated with that pair should first have the pair's transform applied to it, then the transform of the pair's parent, then the transform of the pair's parent's parent (if applicable), and so forth.

Body part parents are stored in the GLPI file. There is only one GLPI file for each actor, not one for each animation that actor possesses, so the order of body parts within each frame of every GGCL file must be consistent.

Offset | Type | Length | Description
---|---|---|---
0 | N/A | 4 | Signature (0x01_00_03_03)
4 | N/A | 8 | Unknown (always 2)
8 | uint | 4 | Number of body parts/GGCL pairs for which a parent is specified (N)
12 | N/A | N * 2 | N parent IDs

### Parent ID

Each parent ID is a single, two-byte, signed integer. A value of -1 means the body part has no parent (only its own transform should be applied to the model associated with it).

## GLXF (List of Transformation Matrices)

Transforms in 3DMM appear to use the [`br_matrix34` type from BRender](https://rr2000.cwaboard.co.uk/R4/BRENDER/TEBK_47.HTM#MARKER2_212), as each stores 12 of the 16 elements of an affine transformation matrix in homogenous form (for those unfamiliar with these transformations, [this page](https://www.brainvoyager.com/bv/doc/UsersGuide/CoordsAndTransforms/SpatialTransformationMatrices.html) contains a good summary). Elements are stored in [row-major order](https://en.wikipedia.org/wiki/Row-_and_column-major_order) but skip the fourth column (which contains constant values as described in the next paragraph).

Although transforms typically place the constant values of the transform (three zeroes and a one) in the last row (with translations located in the last column), the 3DMM/BRender transforms are transposed. This means that, instead of doing this to apply a transform (assuming *v* is a column vector containing the three coordinates of a point in space, plus an extra one as required by homogenous form):

*v<sub>transformed</sub> = Tv*

one instead does this:

*v<sub>transformed</sub><sup>T</sup> = v<sup>T</sup>T<sup>T</sup>*

When applying multiple transforms, instead of this:

*v<sub>transformed</sub> = T<sub>third</sub>T<sub>second</sub>T<sub>first</sub>v*

the order is reversed:

*v<sub>transformed</sub><sup>T</sup> = v<sup>T</sup>T<sub>first</sub><sup>T</sup>T<sub>second</sub><sup>T</sup>T<sub>third</sub><sup>T</sup>*

As mentioned in the GGCL section, some models have multiple transforms applied to them. In these cases, all transforms in the chain must be applied, starting with the current model's transform relative to its immediate parent and then going back up the chain.

For example, for Fabrice the rat, the eyes are transformed relative to the head, the head is transformed relative to the body, and the body is transformed relative to the global coordinate system. Accordingly, the chain of transforms looks like this:

*v<sub>transformed</sub><sup>T</sup> = v<sup>T</sup>T<sub>eye-to-head</sub><sup>T</sup>T<sub>head-to-body</sub><sup>T</sup>T<sub>body-to-global</sub><sup>T</sup>*

I haven't determined which file contains parenting information, but it can be determined by inspection easily enough (for each model, first apply just its transform, inspect the result, then try its transform followed by the transform for a model that you think may be its parent, etc.).

Offset | Type | Length | Description
---|---|---|---
0 | N/A | 4 | Signature (0x01_00_03_03)
4 | uint | 4 | Size of each transformation matrix (48 bytes)
8 | unit | 4 | Number of transformation matrices in file (N<sub>matrices</sub>)
12 | N/A | N<sub>matrices</sub> * 48 | Transformation matrices (see below)

### Transformation Matrix

As described above, transforms are transposed compared to their typical use, i.e., this section stores *T<sup>T</sup>*, not *T*.

All numbers must be divided by 65,535 to obtain their actual floating-point value.

Offsets are relative.

Offset | Type | Length | Description
---|---|---|---
0 | uint | 4 | The element in row 0, column 0 (e00)
4 | uint | 4 | e01
8 | uint | 4 | e02 (e03 is 0)
12 | uint | 4 | e10
16 | uint | 4 | e11
20 | uint | 4 | e12 (e13 is 0)
24 | uint | 4 | e20
28 | uint | 4 | e21
32 | uint | 4 | e22 (e23 is 0)
36 | uint | 4 | e30
40 | uint | 4 | e31
44 | uint | 4 | e32 (e33 is 1)

## TMAP (Texture Map)

Some textures contain one or more columns of apparent junk pixels (random colours) on the right side of the image. These columns are included in the column count (i.e., width) stored in the `TMAP` file.

Materials that reference textures containing junk data also reference a `TXXF` file (materials referencing textures with no junk data do not), so presumably the `TXXF` file contains information that crops the texture or otherwise specifies how the extra columns are to be interpreted.

Offset | Type | Length | Description
---|---|---|---
0 | N/A | 4 | Signature (0x01_00_03_03)
4 | uint | 2 | Unknown, but always seems to equal the width of the texture
6 | uint | 2 | Unknown (larger than any texture dimensions, smaller than pixel count; perhaps a colour palette index/ID?)
8 | N/A | 4 | Unknown (always 0x00_00_00_00)
12 | uint | 2 | Width
14 | uint | 2 | Height
16 | N/A | 4 | Unknown (always 0x00_00_00_00)
20 | uint (multiple) | width * height | One-byte indices into a colour palette (see GLCR section); order is left to right, bottom to top
