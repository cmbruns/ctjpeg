import ctypes

from .jpeglib import JOCTET


class PyJpegSource(object):
    def __init__(self, file):
        self.file = file
        self.c_info = jpeg_decompress_struct()
        jpeg_create_decompress(byref(self.c_info), JPEG_LIB_VERSION, sizeof(jpeg_decompress_struct))
        self.err = MyErrorManager(self.c_info)
        self.c_info.err = ctypes.pointer(self.err.pub)
        self.pub = jpeg_source_mgr()
        self.c_info.src = ctypes.pointer(self.pub)
        self.buf_size = 4096
        self.buffer = (JOCTET * self.buf_size)()
        #
        self.pub.init_source = pfn_init_source(self.init_source)
        self.pub.fill_input_buffer = pfn_fill_input_buffer(self.fill_input_buffer)
        self.pub.skip_input_data = pfn_skip_input_data(self.skip_input_data)
        self.pub.resync_to_restart = pfn_resync_to_restart(jpeg_resync_to_restart)  # Use default implementation
        self.pub.term_source = pfn_term_source(self.term_source)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.c_info is not None:
            jpeg_destroy_decompress(self.c_info)
            self.c_info = None

    def init_source(self, c_info: j_decompress_ptr) -> None:
        """
        Initialize source --- called by jpeg_read_header
        before any data is actually read.
        """
        # https://stackoverflow.com/questions/6327784/how-to-use-libjpeg-to-read-a-jpeg-from-a-stdistream
        self.file.seek(0)

    def fill_input_buffer(self, c_info: j_decompress_ptr) -> bool:
        """
        Fill the input buffer --- called whenever buffer is emptied.

        In typical applications, this should read fresh data into the buffer
        (ignoring the current state of next_input_byte & bytes_in_buffer),
        reset the pointer & count to the start of the buffer, and return TRUE
        indicating that the buffer has been reloaded.  It is not necessary to
        fill the buffer entirely, only to obtain at least one more byte.

        There is no such thing as an EOF return.  If the end of the file has been
        reached, the routine has a choice of ERREXIT() or inserting fake data into
        the buffer.  In most cases, generating a warning message and inserting a
        fake EOI marker is the best course of action --- this will allow the
        decompressor to output however much of the image is there.  However,
        the resulting error message is misleading if the real problem is an empty
        input file, so we handle that case specially.

        In applications that need to be able to suspend compression due to input
        not being available yet, a FALSE return indicates that no more data can be
        obtained right now, but more may be forthcoming later.  In this situation,
        the decompressor will return to its caller (with an indication of the
        number of scanlines it has read, if any).  The application should resume
        decompression after it has loaded more data into the input buffer.  Note
        that there are substantial restrictions on the use of suspension --- see
        the documentation.

        When suspending, the decompressor will back up to a convenient restart point
        (typically the start of the current MCU). next_input_byte & bytes_in_buffer
        indicate where the restart point will be if the current call returns FALSE.
        Data beyond this point must be rescanned after resumption, so move it to
        the front of the buffer rather than discarding it.
        """
        src = self.pub
        err = self.err.pub
        bytes_src = self.file.read(self.buf_size)
        n_bytes = len(bytes_src)
        buf_src = ctypes.c_char_p(bytes_src)  # clever cast to avoid unwriteable error
        ctypes.memmove(self.buffer, buf_src, n_bytes)
        if n_bytes <= 0:
            if src.start_of_file:  # Treat empty input file as fatal error
                err.msg_code = JERR_INPUT_EMPTY
                err.error_exit(c_info)
                return False
            err.msg_code = JWRN_JPEG_EOF
            err.emit_message(c_info, -1)
            # Insert a fake EOI marker
            self.buffer[0] = 0xff
            self.buffer[1] = 0xd9  # JPEG_EOI
            n_bytes = 2
        offset = 0
        src.next_input_byte = (JOCTET * (self.buf_size - offset)).from_buffer(self.buffer, offset)
        src.bytes_in_buffer = n_bytes
        src.start_of_file = False
        return True

    def skip_input_data(self, c_info: j_decompress_ptr, num_bytes: int) -> None:
        """
        Skip data --- used to skip over a potentially large amount of
        uninteresting data (such as an APPn marker).

        Writers of suspendable-input applications must note that skip_input_data
        is not granted the right to give a suspension return.  If the skip extends
        beyond the data currently in the buffer, the buffer can be marked empty so
        that the next read will cause a fill_input_buffer call that can suspend.
        Arranging for additional bytes to be discarded before reloading the input
        buffer is the application writer's problem.
        """
        if num_bytes <= 0:
            return
        src = self.pub
        while num_bytes > src.bytes_in_buffer:
            num_bytes -= src.bytes_in_buffer
            assert self.fill_input_buffer(c_info)
            # note we assume that fill_input_buffer will never return FALSE,
            # so suspension need not be handled.
        # TODO: this is only correct if the prior offset is zero...
        # We want to emulate "src->next_input_byte += (size_t)num_bytes;" here. It's a lot of lines below...
        # First compute pointer addresses as integers
        next_addr = ctypes.cast(src.next_input_byte, ctypes.c_void_p).value
        buff_addr = ctypes.cast(self.buffer, ctypes.c_void_p).value
        old_offset_bytes = next_addr - buff_addr  # how deep into the buffer is next_input_byte?
        new_offset_bytes = old_offset_bytes + num_bytes
        src.next_input_byte = (JOCTET * (self.buf_size - new_offset_bytes)).from_buffer(self.buffer, new_offset_bytes)
        src.bytes_in_buffer -= num_bytes

    def term_source(self, c_info: j_decompress_ptr) -> None:
        """
        Terminate source --- called by jpeg_finish_decompress
        after all data has been read.  Often a no-op.

        NB: *not* called by jpeg_abort or jpeg_destroy; surrounding
        application must deal with any cleanup that should happen even
        for error exit.
        """
        pass  # no work necessary here
