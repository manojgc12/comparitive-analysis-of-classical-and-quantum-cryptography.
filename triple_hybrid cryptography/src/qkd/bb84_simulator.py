import os


class BB84Simulator:
    def __init__(self, error_rate=0.01, channel_loss=0.1):
        self.error_rate = error_rate
        self.channel_loss = channel_loss

    def get_protocol_info(self):
        return {"protocol": "BB84", "efficiency": 0.32}

    def generate_key(self, key_size=32):
        return os.urandom(key_size)  # simulate quantum key
