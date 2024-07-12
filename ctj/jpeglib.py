from ctypes import CFUNCTYPE, c_int, c_ushort, Structure, c_short, POINTER, c_ubyte

JSAMPLE = c_ubyte

J12SAMPLE = c_short

J16SAMPLE = c_ushort

JCOEF = c_short

UINT16 = c_ushort

boolean = c_int

JSAMPROW = POINTER(JSAMPLE)  # ptr to one image row of pixel samples. 

JSAMPARRAY = POINTER(JSAMPROW)  # ptr to some rows (a 2-D sample array) 

JSAMPIMAGE = POINTER(JSAMPARRAY)  # a 3-D sample array: top index is color 

J12SAMPROW = POINTER(J12SAMPLE)  # ptr to one image row of 12-bit pixel
# samples. 

J12SAMPARRAY = POINTER(J12SAMPROW)  # ptr to some 12-bit sample rows (a 2-D
# 12-bit sample array) 

J12SAMPIMAGE = POINTER(J12SAMPARRAY)  # a 3-D 12-bit sample array: top index is
# color 

J16SAMPROW = POINTER(J16SAMPLE)  # ptr to one image row of 16-bit pixel
# samples. 

J16SAMPARRAY = POINTER(J16SAMPROW)  # ptr to some 16-bit sample rows (a 2-D
# 16-bit sample array) 

J16SAMPIMAGE = POINTER(J16SAMPARRAY)  # a 3-D 16-bit sample array: top index is
# color 

JBLOCK = JCOEF * 64  # one block of coefficients 

JBLOCKROW = POINTER(JBLOCK)  # pointer to one row of coefficient blocks 

JBLOCKARRAY = POINTER(JBLOCKROW)  # a 2-D array of coefficient blocks 

JBLOCKIMAGE = POINTER(JBLOCKARRAY)  # a 3-D array of coefficient blocks 

JCOEFPTR = POINTER(JCOEF)  # useful in a couple of places 

class JQUANT_TBL(Structure):
    _fields_ = (
        # This array gives the coefficient quantizers in natural array order
        # (not the zigzag order in which they are stored in a JPEG DQT marker).
        # CAUTION: IJG versions prior to v6a kept this array in zigzag order.
        ("quantval", UINT16 * 64),  # quantization step for each coefficient 
        # This field is used only during compression.  It's initialized FALSE when
        # the table is created, and set TRUE when it's been output to the file.
        # You could suppress output of a table by setting this to TRUE.
        # (See jpeg_suppress_tables for an example.)
        ("sent_table", boolean),  # TRUE when table has been output 
    )


jpeg_saved_marker_ptr = POINTER(struct jpeg_marker_struct)

j_common_ptr = POINTER(struct jpeg_common_struct)

j_compress_ptr = POINTER(struct jpeg_compress_struct)

j_decompress_ptr = POINTER(struct jpeg_decompress_struct)

jvirt_sarray_ptr = POINTER(struct jvirt_sarray_control)

jvirt_barray_ptr = POINTER(struct jvirt_barray_control)

# Routine signature for application-supplied marker processing methods.
# Need not pass marker code since it is stored in cinfo->unread_marker.
jpeg_marker_parser_method = CFUNCTYPE(boolean, j_decompress_ptr)

__all__ = [
    "J12SAMPARRAY",
    "J12SAMPIMAGE",
    "J12SAMPLE",
    "J12SAMPROW",
    "J16SAMPARRAY",
    "J16SAMPIMAGE",
    "J16SAMPLE",
    "J16SAMPROW",
    "JBLOCK",
    "JBLOCKARRAY",
    "JBLOCKIMAGE",
    "JBLOCKROW",
    "JCOEF",
    "JCOEFPTR",
    "JQUANT_TBL",
    "JSAMPARRAY",
    "JSAMPIMAGE",
    "JSAMPLE",
    "JSAMPROW",
    "UINT16",
    "boolean",
    "j_common_ptr",
    "j_compress_ptr",
    "j_decompress_ptr",
    "jpeg_marker_parser_method",
    "jpeg_saved_marker_ptr",
    "jvirt_barray_ptr",
    "jvirt_sarray_ptr",
]

