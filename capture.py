import numpy as np

class Capture:
    def __init__(self, samples, sample_period_ns, num_channels=8):
        """
        samples: bytes or bytearray, each byte = 8 channels
        sample_period_ns: time between samples in nanoseconds
        """
        self.num_channels = num_channels
        self.sample_period_ns = sample_period_ns
        self.sample_count = len(samples)
        
        # Unpack into per-channel arrays
        self.channels = self._unpack_channels(samples)
        
        # Time axis in seconds
        self.time = np.arange(self.sample_count) * (sample_period_ns / 1e9)
    
    def _unpack_channels(self, samples):
        """Convert byte stream to per-channel bit arrays"""
        channels = []
        sample_array = np.frombuffer(samples, dtype=np.uint8)
        
        for ch in range(self.num_channels):
            # Extract bit ch from each sample
            channel_data = (sample_array >> ch) & 0x01
            channels.append(channel_data)
        
        return channels
    
    def get_channel(self, ch_num):
        """Get data for specific channel"""
        return self.channels[ch_num]
    
    def get_sample_rate_mhz(self):
        """Return sample rate in MHz"""
        return 1000.0 / self.sample_period_ns
