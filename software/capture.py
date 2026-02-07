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

    def append_samples(self, new_samples):
        """Append new binary samples to the capture"""
        if not new_samples:
            return
            
        new_channels = self._unpack_channels(new_samples)
        
        # Append to existing channels
        for ch in range(self.num_channels):
            self.channels[ch] = np.concatenate((self.channels[ch], new_channels[ch]))
        
        # Update sample count and time
        new_count = len(new_samples)
        start_time = self.time[-1] + (self.sample_period_ns / 1e9) if len(self.time) > 0 else 0
        new_time = start_time + np.arange(new_count) * (self.sample_period_ns / 1e9)
        
        self.time = np.concatenate((self.time, new_time))
        self.sample_count += new_count

    def trim_start(self, count):
        """Remove samples from the beginning (for rolling buffer)"""
        if count <= 0:
            return
        if count >= self.sample_count:
            # Clear everything?
            # Ideally reset, but simplified:
            count = self.sample_count - 1 # Keep at least one?
            
        for ch in range(self.num_channels):
            self.channels[ch] = self.channels[ch][count:]
            
        self.time = self.time[count:]
        self.sample_count -= count

    def keep_duration(self, duration_seconds):
        """Retain only the last 'duration_seconds' of data"""
        if self.sample_count == 0:
            return
            
        # Calculate max samples based on rate
        # sample_period_ns is per sample
        # rate = 1e9 / sample_period_ns
        # max_samples = duration * rate
        
        max_samples = int(duration_seconds * (1e9 / self.sample_period_ns))
        
        if self.sample_count > max_samples:
            trim_count = self.sample_count - max_samples
            self.trim_start(trim_count)
