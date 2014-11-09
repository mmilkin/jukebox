import zope.interface
from twisted.internet.task import LoopingCall


class IEncoder(zope.interface.Interface):
    """
    An IEncoder takes raw song data and transforms it in to an audio stream. It
    is also responsible for limiting the playback speed.
    """
    def __call__(song, data_callback, done_callback):
        """
        song: A instance of song object

        data_callback: a callable which will be called with each fragment of
            encoded data

        done_callback: a zero argument callable which is called when the song
            is over
        """


class CopyEncoder(object):
    """
    This encoder just reads from a file. It ignores the requirement to limit
    the playback speed so clients will drift around depending on when they
    start and how large of a buffer they have. The UI updates will also drift
    from the audio playback. But it has no external requirments, and it simple.
    """
    zope.interface.classProvides(IEncoder)

    def __init__(self, song, data_callback, done_callback):
        self.song = song
        self.data_callback = data_callback
        self.done_callback = done_callback
        self.file = open(self.song.path)

        self.lc = LoopingCall(self.process_file)
        self.lc.start(.25)  # TODO: bit rate?

    def process_file(self):
        data = self.file.read(1024 * 8)
        if not data:
            self.lc.stop()
            self.file.close()
            self.done_callback()
            return
        self.data_callback(data)


class GSTEncoder(object):
    # This class is untested deal with it
    # I am not going to mock out 90 gst calls
    zope.interface.classProvides(IEncoder)

    def __init__(self, song, data_callback, done_callback):
        import pygst
        pygst.require('0.10')
        import gst

        self.song = song
        self.data_callback = data_callback
        self.done_callback = done_callback

        self.encoder = gst.Pipeline('encoder')

        filesrc = gst.element_factory_make('filesrc', 'filesrc')
        filesrc.set_property('location', self.song.path)

        decodebin = gst.element_factory_make('decodebin', 'decodebin')
        decodebin.connect("new-decoded-pad", self.on_new_decodebin_pad)

        audioconvert = gst.element_factory_make('audioconvert', 'audioconvert')

        lame = gst.element_factory_make('lamemp3enc', 'lame')
        lame.set_property('quality', 1)

        sink = gst.element_factory_make('appsink', 'appsink')
        sink.set_property('emit-signals', True)
        sink.set_property('blocksize', 1024 * 32)
        sink.connect('new-buffer', self.data_ready)

        self.encoder.add(filesrc, decodebin, audioconvert, lame, sink)
        gst.element_link_many(filesrc, decodebin)
        gst.element_link_many(audioconvert, lame, sink)

        self.encoder.set_state(gst.STATE_PAUSED)

        bus = self.encoder.get_bus()
        bus.add_signal_watch()
        bus.connect('message', self.on_message)

    def data_ready(self, sink):
        self.data_callback(str(sink.emit('pull-buffer')))

    def on_new_decodebin_pad(self, dbin, pad, islast):
        import gst
        decodebin = pad.get_parent()
        pipeline = decodebin.get_parent()
        audioconvert = pipeline.get_by_name('audioconvert')
        decodebin.link(audioconvert)
        pipeline.set_state(gst.STATE_PLAYING)

    def on_message(self, bus, message):
        import gst
        t = message.type
        if t == gst.MESSAGE_EOS:
            self.encoder.set_state(gst.STATE_NULL)
            bus.remove_signal_watch()
            self.done_callback()
        elif t == gst.MESSAGE_ERROR:
            self.encoder.set_state(gst.STATE_NULL)
            bus.remove_signal_watch()
            err, debug = message.parse_error()
            print 'Error: %s' % err, debug
            self.done_callback()
