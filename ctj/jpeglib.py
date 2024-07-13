from ctypes import POINTER, c_uint, c_int, CFUNCTYPE, c_ushort, c_double, c_ubyte, c_short, c_void_p, Structure

JSAMPLE: type = c_ubyte
J12SAMPLE: type = c_short
J16SAMPLE: type = c_ushort
JCOEF: type = c_short
JOCTET: type = c_ubyte
UINT16: type = c_ushort
boolean: type = c_int
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
JBLOCK: type = JCOEF * 64  # one block of coefficients 
JBLOCKROW: type = POINTER(JBLOCK)  # pointer to one row of coefficient blocks 
JBLOCKARRAY: type = POINTER(JBLOCKROW)  # a 2-D array of coefficient blocks 
JBLOCKIMAGE: type = POINTER(JBLOCKARRAY)  # a 3-D array of coefficient blocks 
JCOEFPTR: type = POINTER(JCOEF)  # useful in a couple of places 


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


jpeg_saved_marker_ptr: type = POINTER(jpeg_marker_struct)
j_common_ptr: type = POINTER(jpeg_common_struct)
j_compress_ptr: type = POINTER(jpeg_compress_struct)
j_decompress_ptr: type = POINTER(jpeg_decompress_struct)


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
        ("quant_tbl_ptrs", POINTER(JQUANT_TBL) * 4),
        ("dc_huff_tbl_ptrs", POINTER(JHUFF_TBL) * 4),
        ("ac_huff_tbl_ptrs", POINTER(JHUFF_TBL) * 4),
        ("data_precision", c_int),  # bits of precision in image data 
        ("comp_info", POINTER(jpeg_component_info)),
        ("progressive_mode", boolean),  # TRUE if SOFn specifies progressive mode 
        ("arith_code", boolean),  # TRUE=arithmetic coding, FALSE=Huffman 
        ("arith_dc_L", UINT8 * 16),  # L values for DC arith-coding tables 
        ("arith_dc_U", UINT8 * 16),  # U values for DC arith-coding tables 
        ("arith_ac_K", UINT8 * 16),  # Kx values for AC arith-coding tables 
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
        ("cur_comp_info", POINTER(jpeg_component_info) * 4),
        ("MCUs_per_row", JDIMENSION),  # # of MCUs across the image 
        ("MCU_rows_in_scan", JDIMENSION),  # # of MCU rows in the image 
        ("blocks_in_MCU", c_int),  # # of data units per MCU 
        ("MCU_membership", c_int * 10),
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


jvirt_sarray_ptr: type = POINTER(jvirt_sarray_control)
jvirt_barray_ptr: type = POINTER(jvirt_barray_control)
# Routine signature for application-supplied marker processing methods.
# Need not pass marker code since it is stored in cinfo->unread_marker.
jpeg_marker_parser_method: type = CFUNCTYPE(boolean, j_decompress_ptr)


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
    "JOCTET",
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
    "jpeg_decompress_struct",
    "jpeg_marker_parser_method",
    "jpeg_saved_marker_ptr",
    "jvirt_barray_ptr",
    "jvirt_sarray_ptr",
]
