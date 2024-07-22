from ctypes import (
    CFUNCTYPE,
    POINTER,
    Structure,
    Union,
    c_char,
    c_char_p,
    c_double,
    c_int,
    c_long,
    c_short,
    c_ubyte,
    c_uint,
    c_ulonglong,
    c_ushort,
    c_void_p,
)
from enum import IntFlag

size_t: type = c_ulonglong
boolean: type = c_ubyte
JSAMPLE: type = c_ubyte
J12SAMPLE: type = c_short
J16SAMPLE: type = c_ushort
JCOEF: type = c_short
JOCTET: type = c_ubyte
UINT8: type = c_ubyte
UINT16: type = c_ushort
JDIMENSION: type = c_uint
DCTSIZE = 8  # The basic DCT block is 8x8 samples
DCTSIZE2 = 64  # DCTSIZE squared; # of elements in a block
NUM_QUANT_TBLS = 4  # Quantization tables are numbered 0..3
NUM_HUFF_TBLS = 4  # Huffman tables are numbered 0..3
NUM_ARITH_TBLS = 16  # Arith-coding tables are numbered 0..15
MAX_COMPS_IN_SCAN = 4  # JPEG limit on # of components in one scan
MAX_SAMP_FACTOR = 4  # JPEG limit on sampling factors
# Unfortunately, some bozo at Adobe saw no reason to be bound by the standard;
# the PostScript DCT filter can emit files with many more than 10 blocks/MCU.
# If you happen to run across such a file, you can up D_MAX_BLOCKS_IN_MCU
# to handle it.  We even let you do this from the jconfig.h file.  However,
# we strongly discourage changing C_MAX_BLOCKS_IN_MCU; just because Adobe
# sometimes emits noncompliant files doesn't mean you should too.
C_MAX_BLOCKS_IN_MCU = 10  # compressor's limit on data units/MCU
D_MAX_BLOCKS_IN_MCU = 10  # decompressor's limit on data units/MCU
JSAMPROW: type = POINTER(JSAMPLE)  # ptr to one image row of pixel samples.
JSAMPARRAY: type = POINTER(JSAMPROW)  # ptr to some rows (a 2-D sample array)
JSAMPIMAGE: type = POINTER(JSAMPARRAY)  # a 3-D sample array: top index is color
J12SAMPROW: type = POINTER(J12SAMPLE)  # ptr to one image row of 12-bit pixel
#                                        samples.
J12SAMPARRAY: type = POINTER(J12SAMPROW)  # ptr to some 12-bit sample rows (a 2-D
#                                           12-bit sample array)
J12SAMPIMAGE: type = POINTER(J12SAMPARRAY)  # a 3-D 12-bit sample array: top index is
#                                             color
J16SAMPROW: type = POINTER(J16SAMPLE)  # ptr to one image row of 16-bit pixel
#                                        samples.
J16SAMPARRAY: type = POINTER(J16SAMPROW)  # ptr to some 16-bit sample rows (a 2-D
#                                           16-bit sample array)
J16SAMPIMAGE: type = POINTER(J16SAMPARRAY)  # a 3-D 16-bit sample array: top index is
#                                             color
JBLOCK: type = JCOEF * DCTSIZE2  # one block of coefficients
JBLOCKROW: type = POINTER(JBLOCK)  # pointer to one row of coefficient blocks
JBLOCKARRAY: type = POINTER(JBLOCKROW)  # a 2-D array of coefficient blocks
JBLOCKIMAGE: type = POINTER(JBLOCKARRAY)  # a 3-D array of coefficient blocks
JCOEFPTR: type = POINTER(JCOEF)  # useful in a couple of places


class JQUANT_TBL(Structure):
    _fields_ = (
        # This array gives the coefficient quantizers in natural array order
        # (not the zigzag order in which they are stored in a JPEG DQT marker).
        # CAUTION: IJG versions prior to v6a kept this array in zigzag order.
        ("quantval", UINT16 * DCTSIZE2),  # quantization step for each coefficient

        # This field is used only during compression.  It's initialized FALSE when
        # the table is created, and set TRUE when it's been output to the file.
        # You could suppress output of a table by setting this to TRUE.
        # (See jpeg_suppress_tables for an example.)
        ("sent_table", boolean),  # TRUE when table has been output
    )


class JHUFF_TBL(Structure):
    _fields_ = (
        # These two fields directly represent the contents of a JPEG DHT marker
        ("bits", UINT8 * 17),  # bits[k] = # of symbols with codes of

        # length k bits; bits[0] is unused
        ("huffval", UINT8 * 256),  # The symbols, in order of incr code length

        # This field is used only during compression.  It's initialized FALSE when
        # the table is created, and set TRUE when it's been output to the file.
        # You could suppress output of a table by setting this to TRUE.
        # (See jpeg_suppress_tables for an example.)
        ("sent_table", boolean),  # TRUE when table has been output
    )


class jpeg_component_info(Structure):
    _fields_ = (
        # for decompression, they are read from the SOF marker.
        ("component_id", c_int),  # identifier for this component (0..255)

        ("component_index", c_int),  # its index in SOF or cinfo->comp_info[]

        ("h_samp_factor", c_int),  # horizontal sampling factor (1..4)

        ("v_samp_factor", c_int),  # vertical sampling factor (1..4)

        ("quant_tbl_no", c_int),  # quantization table selector (0..3)

        # The decompressor output side may not use these variables.
        ("dc_tbl_no", c_int),  # DC entropy table selector (0..3)

        ("ac_tbl_no", c_int),  # AC entropy table selector (0..3)

        # Component's size in data units.
        # In lossy mode, any dummy blocks added to complete an MCU are not counted;
        # therefore these values do not depend on whether a scan is interleaved or
        # not.  In lossless mode, these are always equal to the image width and
        # height.
        ("width_in_blocks", JDIMENSION),

        ("height_in_blocks", JDIMENSION),

        ("DCT_scaled_size", c_int),

        # The downsampled dimensions are the component's actual, unpadded number
        # of samples at the main buffer (preprocessing/compression interface), thus
        # downsampled_width = ceil(image_width * Hi/Hmax)
        # and similarly for height.  For lossy decompression, IDCT scaling is
        # included, so
        # downsampled_width = ceil(image_width * Hi/Hmax * DCT_[h_]scaled_size/DCTSIZE)
        # In lossless mode, these are always equal to the image width and height.
        ("downsampled_width", JDIMENSION),  # actual width in samples

        ("downsampled_height", JDIMENSION),  # actual height in samples

        # This flag is used only for decompression.  In cases where some of the
        # components will be ignored (eg grayscale output from YCbCr image),
        # we can skip most computations for the unused components.
        ("component_needed", boolean),  # do we need the value of this component?

        # The decompressor output side may not use these variables.
        ("MCU_width", c_int),  # number of data units per MCU, horizontally

        ("MCU_height", c_int),  # number of data units per MCU, vertically

        ("MCU_blocks", c_int),  # MCU_width * MCU_height

        ("MCU_sample_width", c_int),  # MCU width in samples, MCU_width*DCT_[h_]scaled_size

        ("last_col_width", c_int),  # # of non-dummy data units across in last MCU

        ("last_row_height", c_int),  # # of non-dummy data units down in last MCU

        # Saved quantization table for component; NULL if none yet saved.
        # See jdinput.c comments about the need for this information.
        # This field is currently used only for decompression.
        ("quant_table", POINTER(JQUANT_TBL)),

        # Private per-component storage for DCT or IDCT subsystem.
        ("dct_table", c_void_p),
    )


class jpeg_scan_info(Structure):
    _fields_ = (
        ("comps_in_scan", c_int),  # number of components encoded in this scan

        ("component_index", c_int * MAX_COMPS_IN_SCAN),  # their SOF/comp_info[] indexes

        ("Ss", c_int),  # progressive JPEG spectral selection parms
        #                 (Ss is the predictor selection value in
        #                 lossless mode)

        ("Se", c_int),  # progressive JPEG spectral selection parms
        #                 (Ss is the predictor selection value in
        #                 lossless mode)

        ("Ah", c_int),  # progressive JPEG successive approx. parms
        #                 (Al is the point transform value in lossless
        #                 mode)

        ("Al", c_int),  # progressive JPEG successive approx. parms
        #                 (Al is the point transform value in lossless
        #                 mode)
    )


class jpeg_marker_struct(Structure):
    pass


jpeg_saved_marker_ptr: type = POINTER(jpeg_marker_struct)


class jpeg_marker_struct(Structure):
    _fields_ = (
        ("next", jpeg_saved_marker_ptr),  # next in list, or NULL

        ("marker", UINT8),  # marker code: JPEG_COM, or JPEG_APP0+n

        ("original_length", c_uint),  # # bytes of data in the file

        ("data_length", c_uint),  # # bytes of data saved at data[]

        ("data", POINTER(JOCTET)),  # the data contained in the marker
    )


JCS_EXTENSIONS = 1
JCS_ALPHA_EXTENSIONS = 1


class J_COLOR_SPACE(IntFlag):
    JCS_UNKNOWN = 0
    JCS_GRAYSCALE = 1
    JCS_RGB = 2
    JCS_YCbCr = 3
    JCS_CMYK = 4
    JCS_YCCK = 5
    JCS_EXT_RGB = 6
    JCS_EXT_RGBX = 7
    JCS_EXT_BGR = 8
    JCS_EXT_BGRX = 9
    JCS_EXT_XBGR = 10
    JCS_EXT_XRGB = 11
    JCS_EXT_RGBA = 12
    JCS_EXT_BGRA = 13
    JCS_EXT_ABGR = 14
    JCS_EXT_ARGB = 15
    JCS_RGB565 = 16


JCS_UNKNOWN = J_COLOR_SPACE.JCS_UNKNOWN
JCS_GRAYSCALE = J_COLOR_SPACE.JCS_GRAYSCALE
JCS_RGB = J_COLOR_SPACE.JCS_RGB
JCS_YCbCr = J_COLOR_SPACE.JCS_YCbCr
JCS_CMYK = J_COLOR_SPACE.JCS_CMYK
JCS_YCCK = J_COLOR_SPACE.JCS_YCCK
JCS_EXT_RGB = J_COLOR_SPACE.JCS_EXT_RGB
JCS_EXT_RGBX = J_COLOR_SPACE.JCS_EXT_RGBX
JCS_EXT_BGR = J_COLOR_SPACE.JCS_EXT_BGR
JCS_EXT_BGRX = J_COLOR_SPACE.JCS_EXT_BGRX
JCS_EXT_XBGR = J_COLOR_SPACE.JCS_EXT_XBGR
JCS_EXT_XRGB = J_COLOR_SPACE.JCS_EXT_XRGB
JCS_EXT_RGBA = J_COLOR_SPACE.JCS_EXT_RGBA
JCS_EXT_BGRA = J_COLOR_SPACE.JCS_EXT_BGRA
JCS_EXT_ABGR = J_COLOR_SPACE.JCS_EXT_ABGR
JCS_EXT_ARGB = J_COLOR_SPACE.JCS_EXT_ARGB
JCS_RGB565 = J_COLOR_SPACE.JCS_RGB565


class J_DCT_METHOD(IntFlag):
    JDCT_ISLOW = 0
    JDCT_IFAST = 1
    JDCT_FLOAT = 2


JDCT_ISLOW = J_DCT_METHOD.JDCT_ISLOW
JDCT_IFAST = J_DCT_METHOD.JDCT_IFAST
JDCT_FLOAT = J_DCT_METHOD.JDCT_FLOAT


JDCT_DEFAULT = JDCT_ISLOW
JDCT_FASTEST = JDCT_IFAST


class J_DITHER_MODE(IntFlag):
    JDITHER_NONE = 0
    JDITHER_ORDERED = 1
    JDITHER_FS = 2


JDITHER_NONE = J_DITHER_MODE.JDITHER_NONE
JDITHER_ORDERED = J_DITHER_MODE.JDITHER_ORDERED
JDITHER_FS = J_DITHER_MODE.JDITHER_FS


# Forward declaration. Definition of _fields_ will appear later.
class jpeg_memory_mgr(Structure):
    pass


# Forward declaration. Definition of _fields_ will appear later.
class jpeg_error_mgr(Structure):
    pass


# Forward declaration. Definition of _fields_ will appear later.
class jpeg_progress_mgr(Structure):
    pass


class jpeg_common_struct(Structure):
    _fields_ = (
        ("err", POINTER(jpeg_error_mgr)),  # Fields common to both master struct types

        ("mem", POINTER(jpeg_memory_mgr)),  # Fields common to both master struct types

        ("progress", POINTER(jpeg_progress_mgr)),  # Fields common to both master struct types

        ("client_data", c_void_p),  # Fields common to both master struct types

        ("is_decompressor", boolean),  # Fields common to both master struct types

        ("global_state", c_int),  # Fields common to both master struct types
    )


j_common_ptr: type = POINTER(jpeg_common_struct)


class jpeg_compress_struct(Structure):
    pass


j_compress_ptr: type = POINTER(jpeg_compress_struct)


class jpeg_decompress_struct(Structure):
    pass


j_decompress_ptr: type = POINTER(jpeg_decompress_struct)


class jpeg_entropy_encoder(Structure):
    pass


class jpeg_c_main_controller(Structure):
    pass


class jpeg_c_prep_controller(Structure):
    pass


class jpeg_c_coef_controller(Structure):
    pass


class jpeg_comp_master(Structure):
    pass


class jpeg_downsampler(Structure):
    pass


# Forward declaration. Definition of _fields_ will appear later.
class jpeg_destination_mgr(Structure):
    pass


class jpeg_marker_writer(Structure):
    pass


class jpeg_forward_dct(Structure):
    pass


class jpeg_color_converter(Structure):
    pass


class jpeg_compress_struct(Structure):
    _fields_ = (
        ("err", POINTER(jpeg_error_mgr)),  # Fields shared with jpeg_decompress_struct

        ("mem", POINTER(jpeg_memory_mgr)),  # Fields shared with jpeg_decompress_struct

        ("progress", POINTER(jpeg_progress_mgr)),  # Fields shared with jpeg_decompress_struct

        ("client_data", c_void_p),  # Fields shared with jpeg_decompress_struct

        ("is_decompressor", boolean),  # Fields shared with jpeg_decompress_struct

        ("global_state", c_int),  # Fields shared with jpeg_decompress_struct

        # Destination for compressed data
        ("dest", POINTER(jpeg_destination_mgr)),

        ("image_width", JDIMENSION),  # input image width

        ("image_height", JDIMENSION),  # input image height

        ("input_components", c_int),  # # of color components in input image

        ("in_color_space", J_COLOR_SPACE),  # colorspace of input image

        ("input_gamma", c_double),  # image gamma of input image

        ("data_precision", c_int),  # bits of precision in image data

        ("num_components", c_int),  # # of color components in JPEG image

        ("jpeg_color_space", J_COLOR_SPACE),  # colorspace of JPEG image

        ("comp_info", POINTER(jpeg_component_info)),

        ("quant_tbl_ptrs", POINTER(JQUANT_TBL) * NUM_QUANT_TBLS),

        ("dc_huff_tbl_ptrs", POINTER(JHUFF_TBL) * NUM_HUFF_TBLS),

        ("ac_huff_tbl_ptrs", POINTER(JHUFF_TBL) * NUM_HUFF_TBLS),

        ("arith_dc_L", UINT8 * NUM_ARITH_TBLS),  # L values for DC arith-coding tables

        ("arith_dc_U", UINT8 * NUM_ARITH_TBLS),  # U values for DC arith-coding tables

        ("arith_ac_K", UINT8 * NUM_ARITH_TBLS),  # Kx values for AC arith-coding tables

        ("num_scans", c_int),  # # of entries in scan_info array

        ("scan_info", POINTER(jpeg_scan_info)),  # script for multi-scan file, or NULL

        ("raw_data_in", boolean),  # TRUE=caller supplies downsampled data

        ("arith_code", boolean),  # TRUE=arithmetic coding, FALSE=Huffman

        ("optimize_coding", boolean),  # TRUE=optimize entropy encoding parms

        ("CCIR601_sampling", boolean),  # TRUE=first samples are cosited

        ("smoothing_factor", c_int),  # 1..100, or 0 for no input smoothing

        ("dct_method", J_DCT_METHOD),  # DCT algorithm selector

        # The restart interval can be specified in absolute MCUs by setting
        # restart_interval, or in MCU rows by setting restart_in_rows
        # (in which case the correct restart_interval will be figured
        # for each scan).
        ("restart_interval", c_uint),  # MCUs per restart, or 0 for no restart

        ("restart_in_rows", c_int),  # if > 0, MCU rows per restart interval

        ("write_JFIF_header", boolean),  # should a JFIF marker be written?

        ("JFIF_major_version", UINT8),  # What to write for the JFIF version number

        ("JFIF_minor_version", UINT8),

        # ratio is defined by X_density/Y_density even when density_unit=0.
        ("density_unit", UINT8),  # JFIF code for pixel size units

        ("X_density", UINT16),  # Horizontal pixel density

        ("Y_density", UINT16),  # Vertical pixel density

        ("write_Adobe_marker", boolean),  # should an Adobe marker be written?

        ("next_scanline", JDIMENSION),  # 0 .. image_height-1

        # These fields are computed during compression startup
        ("progressive_mode", boolean),  # TRUE if scan script uses progressive mode

        ("max_h_samp_factor", c_int),  # largest h_samp_factor

        ("max_v_samp_factor", c_int),  # largest v_samp_factor

        ("total_iMCU_rows", JDIMENSION),  # # of iMCU rows to be input to coefficient or
        #                                   difference controller

        # These fields are valid during any one scan.
        # They describe the components and MCUs actually appearing in the scan.
        ("comps_in_scan", c_int),  # # of JPEG components in this scan

        ("cur_comp_info", POINTER(jpeg_component_info) * MAX_COMPS_IN_SCAN),

        ("MCUs_per_row", JDIMENSION),  # # of MCUs across the image

        ("MCU_rows_in_scan", JDIMENSION),  # # of MCU rows in the image

        ("blocks_in_MCU", c_int),  # # of data units per MCU

        ("MCU_membership", c_int * C_MAX_BLOCKS_IN_MCU),

        ("Ss", c_int),  # progressive/lossless JPEG parameters for
        #                 scan

        ("Se", c_int),  # progressive/lossless JPEG parameters for
        #                 scan

        ("Ah", c_int),  # progressive/lossless JPEG parameters for
        #                 scan

        ("Al", c_int),  # progressive/lossless JPEG parameters for
        #                 scan

        # Links to compression subobjects (methods and private variables of modules)
        ("master", POINTER(jpeg_comp_master)),

        ("main", POINTER(jpeg_c_main_controller)),

        ("prep", POINTER(jpeg_c_prep_controller)),

        ("coef", POINTER(jpeg_c_coef_controller)),

        ("marker", POINTER(jpeg_marker_writer)),

        ("cconvert", POINTER(jpeg_color_converter)),

        ("downsample", POINTER(jpeg_downsampler)),

        ("fdct", POINTER(jpeg_forward_dct)),

        ("entropy", POINTER(jpeg_entropy_encoder)),

        ("script_space", POINTER(jpeg_scan_info)),  # workspace for jpeg_simple_progression

        ("script_space_size", c_int),
    )


class jpeg_entropy_decoder(Structure):
    pass


class jpeg_color_quantizer(Structure):
    pass


class jpeg_upsampler(Structure):
    pass


# Forward declaration. Definition of _fields_ will appear later.
class jpeg_source_mgr(Structure):
    pass


class jpeg_decomp_master(Structure):
    pass


class jpeg_color_deconverter(Structure):
    pass


class jpeg_marker_reader(Structure):
    pass


class jpeg_d_main_controller(Structure):
    pass


class jpeg_d_coef_controller(Structure):
    pass


class jpeg_inverse_dct(Structure):
    pass


class jpeg_input_controller(Structure):
    pass


class jpeg_d_post_controller(Structure):
    pass


class jpeg_decompress_struct(Structure):
    _fields_ = (
        ("err", POINTER(jpeg_error_mgr)),  # Fields shared with jpeg_compress_struct

        ("mem", POINTER(jpeg_memory_mgr)),  # Fields shared with jpeg_compress_struct

        ("progress", POINTER(jpeg_progress_mgr)),  # Fields shared with jpeg_compress_struct

        ("client_data", c_void_p),  # Fields shared with jpeg_compress_struct

        ("is_decompressor", boolean),  # Fields shared with jpeg_compress_struct

        ("global_state", c_int),  # Fields shared with jpeg_compress_struct

        # Source of compressed data
        ("src", POINTER(jpeg_source_mgr)),

        ("image_width", JDIMENSION),  # nominal image width (from SOF marker)

        ("image_height", JDIMENSION),  # nominal image height

        ("num_components", c_int),  # # of color components in JPEG image

        ("jpeg_color_space", J_COLOR_SPACE),  # colorspace of JPEG image

        ("out_color_space", J_COLOR_SPACE),  # colorspace for output

        ("scale_num", c_uint),  # fraction by which to scale image

        ("scale_denom", c_uint),  # fraction by which to scale image

        ("output_gamma", c_double),  # image gamma wanted in output

        ("buffered_image", boolean),  # TRUE=multiple output passes

        ("raw_data_out", boolean),  # TRUE=downsampled data wanted

        ("dct_method", J_DCT_METHOD),  # IDCT algorithm selector

        ("do_fancy_upsampling", boolean),  # TRUE=apply fancy upsampling

        ("do_block_smoothing", boolean),  # TRUE=apply interblock smoothing

        ("quantize_colors", boolean),  # TRUE=colormapped output wanted

        # the following are ignored if not quantize_colors:
        ("dither_mode", J_DITHER_MODE),  # type of color dithering to use

        ("two_pass_quantize", boolean),  # TRUE=use two-pass color quantization

        ("desired_number_of_colors", c_int),  # max # colors to use in created colormap

        # these are significant only in buffered-image mode:
        ("enable_1pass_quant", boolean),  # enable future use of 1-pass quantizer

        ("enable_external_quant", boolean),  # enable future use of external colormap

        ("enable_2pass_quant", boolean),  # enable future use of 2-pass quantizer

        ("output_width", JDIMENSION),  # scaled image width

        ("output_height", JDIMENSION),  # scaled image height

        ("out_color_components", c_int),  # # of color components in out_color_space

        ("output_components", c_int),  # # of color components returned

        # output_components is 1 (a colormap index) when quantizing colors;
        # otherwise it equals out_color_components.
        ("rec_outbuf_height", c_int),  # min recommended height of scanline buffer

        # When quantizing colors, the output colormap is described by these fields.
        # The application can supply a colormap by setting colormap non-NULL before
        # calling jpeg_start_decompress; otherwise a colormap is created during
        # jpeg_start_decompress or jpeg_start_output.
        # The map has out_color_components rows and actual_number_of_colors columns.
        ("actual_number_of_colors", c_int),  # number of entries in use

        ("colormap", JSAMPARRAY),  # The color map as a 2-D pixel array
        #                            If data_precision is 12, then this is
        #                            actually a J12SAMPARRAY, so callers must
        #                            type-cast it in order to read/write 12-bit
        #                            samples from/to the array.

        # Row index of next scanline to be read from jpeg_read_scanlines().
        # Application may use this to control its processing loop, e.g.,
        # "while (output_scanline < output_height)".
        ("output_scanline", JDIMENSION),  # 0 .. output_height-1

        # Current input scan number and number of iMCU rows completed in scan.
        # These indicate the progress of the decompressor input side.
        ("input_scan_number", c_int),  # Number of SOS markers seen so far

        ("input_iMCU_row", JDIMENSION),  # Number of iMCU rows completed

        # The "output scan number" is the notional scan being displayed by the
        # output side.  The decompressor will not allow output scan/row number
        # to get ahead of input scan/row, but it can fall arbitrarily far behind.
        ("output_scan_number", c_int),  # Nominal scan number being displayed

        ("output_iMCU_row", JDIMENSION),  # Number of iMCU rows read

        # Current progression status.  coef_bits[c][i] indicates the precision
        # with which component c's DCT coefficient i (in zigzag order) is known.
        # It is -1 when no data has yet been received, otherwise it is the point
        # transform (shift) value for the most recent scan of the coefficient
        # (thus, 0 at completion of the progression).
        # This pointer is NULL when reading a non-progressive file.
        ("coef_bits", POINTER(c_int * 64)),  # -1 or current Al value for each coef

        ("quant_tbl_ptrs", POINTER(JQUANT_TBL) * NUM_QUANT_TBLS),

        ("dc_huff_tbl_ptrs", POINTER(JHUFF_TBL) * NUM_HUFF_TBLS),

        ("ac_huff_tbl_ptrs", POINTER(JHUFF_TBL) * NUM_HUFF_TBLS),

        ("data_precision", c_int),  # bits of precision in image data

        ("comp_info", POINTER(jpeg_component_info)),

        ("progressive_mode", boolean),  # TRUE if SOFn specifies progressive mode

        ("arith_code", boolean),  # TRUE=arithmetic coding, FALSE=Huffman

        ("arith_dc_L", UINT8 * NUM_ARITH_TBLS),  # L values for DC arith-coding tables

        ("arith_dc_U", UINT8 * NUM_ARITH_TBLS),  # U values for DC arith-coding tables

        ("arith_ac_K", UINT8 * NUM_ARITH_TBLS),  # Kx values for AC arith-coding tables

        ("restart_interval", c_uint),  # MCUs per restart interval, or 0 for no restart

        # These fields record data obtained from optional markers recognized by
        # the JPEG library.
        ("saw_JFIF_marker", boolean),  # TRUE iff a JFIF APP0 marker was found

        # Data copied from JFIF marker; only valid if saw_JFIF_marker is TRUE:
        ("JFIF_major_version", UINT8),  # JFIF version number

        ("JFIF_minor_version", UINT8),

        ("density_unit", UINT8),  # JFIF code for pixel size units

        ("X_density", UINT16),  # Horizontal pixel density

        ("Y_density", UINT16),  # Vertical pixel density

        ("saw_Adobe_marker", boolean),  # TRUE iff an Adobe APP14 marker was found

        ("Adobe_transform", UINT8),  # Color transform code from Adobe marker

        ("CCIR601_sampling", boolean),  # TRUE=first samples are cosited

        # Aside from the specific data retained from APPn markers known to the
        # library, the uninterpreted contents of any or all APPn and COM markers
        # can be saved in a list for examination by the application.
        ("marker_list", jpeg_saved_marker_ptr),  # Head of list of saved markers

        # These fields are computed during decompression startup
        ("max_h_samp_factor", c_int),  # largest h_samp_factor

        ("max_v_samp_factor", c_int),  # largest v_samp_factor

        ("min_DCT_scaled_size", c_int),  # smallest DCT_scaled_size of any component

        ("total_iMCU_rows", JDIMENSION),  # # of iMCU rows in image

        ("sample_range_limit", POINTER(JSAMPLE)),  # table for fast range-limiting
        #                                            If data_precision is 12 or 16, then this is
        #                                            actually a J12SAMPLE pointer or a J16SAMPLE
        #                                            pointer, so callers must type-cast it in
        #                                            order to read 12-bit or 16-bit samples from
        #                                            the array.

        # These fields are valid during any one scan.
        # They describe the components and MCUs actually appearing in the scan.
        # Note that the decompressor output side must not use these fields.
        ("comps_in_scan", c_int),  # # of JPEG components in this scan

        ("cur_comp_info", POINTER(jpeg_component_info) * MAX_COMPS_IN_SCAN),

        ("MCUs_per_row", JDIMENSION),  # # of MCUs across the image

        ("MCU_rows_in_scan", JDIMENSION),  # # of MCU rows in the image

        ("blocks_in_MCU", c_int),  # # of data units per MCU

        ("MCU_membership", c_int * D_MAX_BLOCKS_IN_MCU),

        ("Ss", c_int),  # progressive/lossless JPEG parameters for
        #                 scan

        ("Se", c_int),  # progressive/lossless JPEG parameters for
        #                 scan

        ("Ah", c_int),  # progressive/lossless JPEG parameters for
        #                 scan

        ("Al", c_int),  # progressive/lossless JPEG parameters for
        #                 scan

        # This field is shared between entropy decoder and marker parser.
        # It is either zero or the code of a JPEG marker that has been
        # read from the data source, but has not yet been processed.
        ("unread_marker", c_int),

        # Links to decompression subobjects (methods, private variables of modules)
        ("master", POINTER(jpeg_decomp_master)),

        ("main", POINTER(jpeg_d_main_controller)),

        ("coef", POINTER(jpeg_d_coef_controller)),

        ("post", POINTER(jpeg_d_post_controller)),

        ("inputctl", POINTER(jpeg_input_controller)),

        ("marker", POINTER(jpeg_marker_reader)),

        ("entropy", POINTER(jpeg_entropy_decoder)),

        ("idct", POINTER(jpeg_inverse_dct)),

        ("upsample", POINTER(jpeg_upsampler)),

        ("cconvert", POINTER(jpeg_color_deconverter)),

        ("cquantize", POINTER(jpeg_color_quantizer)),
    )


JMSG_LENGTH_MAX = 200  # recommended size of format_message buffer
JMSG_STR_PARM_MAX = 80


class _MsgParmUnion(Union):
    _fields_ = (
        ("i", c_int * 8),

        ("s", c_char * JMSG_STR_PARM_MAX),
    )


jpeg_error_mgr._fields_ = (
        # Error exit handler: does not return to caller
        ("error_exit", CFUNCTYPE(None, j_common_ptr)),

        # Conditionally emit a trace or warning message
        ("emit_message", CFUNCTYPE(None, j_common_ptr, c_int)),

        # Routine that actually outputs a trace or error message
        ("output_message", CFUNCTYPE(None, j_common_ptr)),

        # Format a message string for the most recent JPEG error or message
        ("format_message", CFUNCTYPE(None, j_common_ptr, c_char_p)),

        # Reset error state variables at start of a new image
        ("reset_error_mgr", CFUNCTYPE(None, j_common_ptr)),

        # The message ID code and any parameters are saved here.
        # A message can have one string parameter or up to 8 int parameters.
        ("msg_code", c_int),

        ("msg_parm", _MsgParmUnion),

        ("trace_level", c_int),  # max msg_level that will be displayed

        # For recoverable corrupt-data errors, we emit a warning message,
        # but keep going unless emit_message chooses to abort.  emit_message
        # should count warnings in num_warnings.  The surrounding application
        # can check for bad data by seeing if num_warnings is nonzero at the
        # end of processing.
        ("num_warnings", c_long),  # number of corrupt-data warnings

        # These fields point to the table(s) of error message strings.
        # An application can change the table pointer to switch to a different
        # message list (typically, to change the language in which errors are
        # reported).  Some applications may wish to add additional error codes
        # that will be handled by the JPEG library error mechanism; the second
        # table pointer is used for this purpose.
        # 
        # First table includes all errors generated by JPEG library itself.
        # Error code 0 is reserved for a "no such error string" message.
        ("jpeg_message_table", POINTER(c_char_p)),  # Library errors

        ("last_jpeg_message", c_int),  # Table contains strings 0..last_jpeg_message

        # Second table can be added by application (see cjpeg/djpeg for example).
        # It contains strings numbered first_addon_message..last_addon_message.
        ("addon_message_table", POINTER(c_char_p)),  # Non-library errors

        ("first_addon_message", c_int),  # code for first string in addon table

        ("last_addon_message", c_int),  # code for last string in addon table
    )


jpeg_progress_mgr._fields_ = (
        ("progress_monitor", CFUNCTYPE(None, j_common_ptr)),

        ("pass_counter", c_long),  # work units completed in this pass

        ("pass_limit", c_long),  # total number of work units in this pass

        ("completed_passes", c_int),  # passes completed so far

        ("total_passes", c_int),  # total number of passes expected
    )


jpeg_destination_mgr._fields_ = (
        ("next_output_byte", POINTER(JOCTET)),  # => next byte to write in buffer

        ("free_in_buffer", size_t),  # # of byte spaces remaining in buffer

        ("init_destination", CFUNCTYPE(None, j_compress_ptr)),

        ("empty_output_buffer", CFUNCTYPE(boolean, j_compress_ptr)),

        ("term_destination", CFUNCTYPE(None, j_compress_ptr)),
    )


jpeg_source_mgr._fields_ = (
        ("next_input_byte", POINTER(JOCTET)),  # => next byte to read from buffer

        ("bytes_in_buffer", size_t),  # # of bytes remaining in buffer

        ("init_source", CFUNCTYPE(None, j_decompress_ptr)),

        ("fill_input_buffer", CFUNCTYPE(boolean, j_decompress_ptr)),

        ("skip_input_data", CFUNCTYPE(None, j_decompress_ptr, c_long)),

        ("resync_to_restart", CFUNCTYPE(boolean, j_decompress_ptr, c_int)),

        ("term_source", CFUNCTYPE(None, j_decompress_ptr)),
    )


JPOOL_PERMANENT = 0  # lasts until master record is destroyed
JPOOL_IMAGE = 1  # lasts until done with image/datastream
JPOOL_NUMPOOLS = 2


class jvirt_sarray_control(Structure):
    pass


jvirt_sarray_ptr: type = POINTER(jvirt_sarray_control)


class jvirt_barray_control(Structure):
    pass


jvirt_barray_ptr: type = POINTER(jvirt_barray_control)


jpeg_memory_mgr._fields_ = (
        # Method pointers
        ("alloc_small", CFUNCTYPE(c_void_p, j_common_ptr, c_int, size_t)),

        ("alloc_large", CFUNCTYPE(c_void_p, j_common_ptr, c_int, size_t)),

        # If cinfo->data_precision is 12 or 16, then this method and the
        # access_virt_sarray method actually return a J12SAMPARRAY or a
        # J16SAMPARRAY, so callers must type-cast the return value in order to
        # read/write 12-bit or 16-bit samples from/to the array.
        ("alloc_sarray", CFUNCTYPE(JSAMPARRAY, j_common_ptr, c_int, JDIMENSION, JDIMENSION)),

        ("alloc_barray", CFUNCTYPE(JBLOCKARRAY, j_common_ptr, c_int, JDIMENSION, JDIMENSION)),

        ("request_virt_sarray", CFUNCTYPE(jvirt_sarray_ptr, j_common_ptr, c_int, boolean, JDIMENSION, JDIMENSION, JDIMENSION)),

        ("request_virt_barray", CFUNCTYPE(jvirt_barray_ptr, j_common_ptr, c_int, boolean, JDIMENSION, JDIMENSION, JDIMENSION)),

        ("realize_virt_arrays", CFUNCTYPE(None, j_common_ptr)),

        ("access_virt_sarray", CFUNCTYPE(JSAMPARRAY, j_common_ptr, jvirt_sarray_ptr, JDIMENSION, JDIMENSION, boolean)),

        ("access_virt_barray", CFUNCTYPE(JBLOCKARRAY, j_common_ptr, jvirt_barray_ptr, JDIMENSION, JDIMENSION, boolean)),

        ("free_pool", CFUNCTYPE(None, j_common_ptr, c_int)),

        ("self_destruct", CFUNCTYPE(None, j_common_ptr)),

        # Limit on memory allocation for this JPEG object.  (Note that this is
        # merely advisory, not a guaranteed maximum; it only affects the space
        # used for virtual-array buffers.)  May be changed by outer application
        # after creating the JPEG object.
        ("max_memory_to_use", c_long),

        # Maximum allocation request accepted by alloc_large.
        ("max_alloc_chunk", c_long),
    )


# Routine signature for application-supplied marker processing methods.
# Need not pass marker code since it is stored in cinfo->unread_marker.
jpeg_marker_parser_method: type = CFUNCTYPE(boolean, j_decompress_ptr)
# Return value is one of:
JPEG_SUSPENDED = 0  # Suspended due to lack of input data
JPEG_HEADER_OK = 1  # Found valid image datastream
JPEG_HEADER_TABLES_ONLY = 2  # Found valid table-specs-only datastream
# #define JPEG_SUSPENDED       0    Suspended due to lack of input data
JPEG_REACHED_SOS = 1  # Reached start of new scan
JPEG_REACHED_EOI = 2  # Reached end of image
JPEG_ROW_COMPLETED = 3  # Completed one iMCU row
JPEG_SCAN_COMPLETED = 4  # Completed last iMCU row of a scan
JPEG_RST0 = 0xD0  # RST0 marker code
JPEG_EOI = 0xD9  # EOI marker code
JPEG_APP0 = 0xE0  # APP0 marker code
JPEG_COM = 0xFE  # COM marker code

__all__ = [
    "C_MAX_BLOCKS_IN_MCU",
    "DCTSIZE",
    "DCTSIZE2",
    "D_MAX_BLOCKS_IN_MCU",
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
    "JCS_ALPHA_EXTENSIONS",
    "JCS_EXTENSIONS",
    "JDCT_DEFAULT",
    "JDCT_FASTEST",
    "JDIMENSION",
    "JHUFF_TBL",
    "JMSG_LENGTH_MAX",
    "JMSG_STR_PARM_MAX",
    "JOCTET",
    "JPEG_APP0",
    "JPEG_COM",
    "JPEG_EOI",
    "JPEG_HEADER_OK",
    "JPEG_HEADER_TABLES_ONLY",
    "JPEG_REACHED_EOI",
    "JPEG_REACHED_SOS",
    "JPEG_ROW_COMPLETED",
    "JPEG_RST0",
    "JPEG_SCAN_COMPLETED",
    "JPEG_SUSPENDED",
    "JPOOL_IMAGE",
    "JPOOL_NUMPOOLS",
    "JPOOL_PERMANENT",
    "JQUANT_TBL",
    "JSAMPARRAY",
    "JSAMPIMAGE",
    "JSAMPLE",
    "JSAMPROW",
    "J_COLOR_SPACE",
    "J_DCT_METHOD",
    "J_DITHER_MODE",
    "MAX_COMPS_IN_SCAN",
    "MAX_SAMP_FACTOR",
    "NUM_ARITH_TBLS",
    "NUM_HUFF_TBLS",
    "NUM_QUANT_TBLS",
    "UINT16",
    "UINT8",
    "boolean",
    "j_common_ptr",
    "j_compress_ptr",
    "j_decompress_ptr",
    "jpeg_common_struct",
    "jpeg_component_info",
    "jpeg_compress_struct",
    "jpeg_compress_struct",
    "jpeg_decompress_struct",
    "jpeg_decompress_struct",
    "jpeg_destination_mgr",
    "jpeg_destination_mgr",
    "jpeg_error_mgr",
    "jpeg_error_mgr",
    "jpeg_marker_parser_method",
    "jpeg_marker_struct",
    "jpeg_marker_struct",
    "jpeg_memory_mgr",
    "jpeg_memory_mgr",
    "jpeg_progress_mgr",
    "jpeg_progress_mgr",
    "jpeg_saved_marker_ptr",
    "jpeg_scan_info",
    "jpeg_source_mgr",
    "jpeg_source_mgr",
    "jvirt_barray_control",
    "jvirt_barray_ptr",
    "jvirt_sarray_control",
    "jvirt_sarray_ptr",
    "size_t",
]
