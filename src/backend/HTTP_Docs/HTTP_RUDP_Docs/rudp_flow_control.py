# Define flow control algorithm
class FlowControl:
    def __init__(self, mws):
        self.window_size = mws

    def get_window_size(self, sender_window):
        return min(sender_window.window_size, self.window_size)