import serial
import serial.tools.list_ports
import time

class LogicAnalyzerDevice:
    """Device driver for STM32-UART-LA8 Logic Analyzer (DMA Version)"""
    
    def __init__(self, port=None, baudrate=115200):
        self.port = port
        self.baudrate = baudrate
        self.serial = None
        self.device_info = None
    
    @staticmethod
    def list_ports():
        """List available serial ports"""
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]
    
    def connect(self):
        """Connect to device"""
        try:
            self.serial = serial.Serial(self.port, self.baudrate, timeout=2)
            time.sleep(0.2)  # Wait for device to be ready
            
            # Clear any pending data
            self.serial.reset_input_buffer()
            
            # Query device info with 'I' command
            self.serial.write(b'I')
            time.sleep(0.2)
            
            # Read response lines
            response_lines = []
            start_time = time.time()
            while time.time() - start_time < 1.0:
                if self.serial.in_waiting > 0:
                    line = self.serial.readline().decode('utf-8', errors='ignore').strip()
                    if line:
                        response_lines.append(line)
                    if 'MAX:' in line:  # Last line of info
                        break
            
            # Parse device info
            if response_lines:
                self.device_info = {
                    'type': 'info',
                    'device_name': 'STM32-UART-LA8',
                    'version': '3.1-UART',
                    'channels': 8,
                    'buffer_size': 2048,
                    'max_rate': 6000000
                }
                
                # Parse specific info
                for line in response_lines:
                    if 'VERSION:' in line:
                        self.device_info['version'] = line.split(':')[1]
                    elif 'CHANNELS:' in line:
                        self.device_info['channels'] = int(line.split(':')[1])
                    elif 'BUFFER:' in line:
                        self.device_info['buffer_size'] = int(line.split(':')[1])
                    elif 'MAX:' in line:
                        max_str = line.split(':')[1].replace('MHz', '').replace('Hz', '')
                        self.device_info['max_rate'] = int(float(max_str) * 1000000)
                
                return True
            
            return False
            
        except Exception as e:
            print(f"Connection error: {e}")
            raise
    
    def disconnect(self):
        """Disconnect from device"""
        if self.serial:
            self.serial.close()
            self.serial = None
    
    def reset_device(self):
        """Reset device using firmware 'R' command"""
        if not self.serial:
            return False
        
        try:
            # Send reset command
            self.serial.reset_input_buffer()
            self.serial.write(b'R')
            time.sleep(0.5)  # Wait for reset to complete
            
            # Clear any response
            if self.serial.in_waiting > 0:
                self.serial.read(self.serial.in_waiting)
            
            self.serial.reset_input_buffer()
            return True
        except Exception as e:
            print(f"Reset error: {e}")
            return False
    
    def capture(self, timeout=5):
        """Request capture and read data"""
        if not self.serial:
            return None
        
        try:
            # Clear buffers
            self.serial.reset_input_buffer()
            
            # Send capture command
            self.serial.write(b'C')
            
            # Wait a bit for response to start
            time.sleep(0.1)
            
            # Check for immediate error response
            if self.serial.in_waiting > 0:
                peek = self.serial.read(self.serial.in_waiting)
                if b'ERROR:BUSY' in peek:
                    print("Device is BUSY - resetting...")
                    self.reset_device()
                    time.sleep(1.0)  # Wait longer for device to be ready
                    self.serial.reset_input_buffer()
                    # Don't retry immediately - return None and let GUI retry
                    print("Reset complete. Please try capture again.")
                    return None
                elif b'ERROR' in peek:
                    print(f"Device error: {peek}")
                    return None
                else:
                    # Put data back for processing
                    # Can't actually put it back, so we need to handle this differently
                    pass
            
            # Read header line "DATA:"
            start_time = time.time()
            header_found = False
            buffer = b''
            
            while time.time() - start_time < timeout:
                if self.serial.in_waiting > 0:
                    buffer += self.serial.read(self.serial.in_waiting)
                    
                    if b'DATA:' in buffer:
                        # Find position of DATA:
                        data_pos = buffer.find(b'DATA:')
                        buffer = buffer[data_pos:]  # Remove anything before DATA:
                        header_found = True
                        break
                    
                    if b'ERROR' in buffer:
                        print(f"Error in response: {buffer}")
                        return None
                
                time.sleep(0.01)
            
            if not header_found:
                print(f"Error: DATA header not found. Received: {buffer[:100]}")
                return None
            
            # Remove "DATA:" from buffer
            buffer = buffer[5:]
            
            # Read count (4 bytes)
            while len(buffer) < 4 and time.time() - start_time < timeout:
                if self.serial.in_waiting > 0:
                    buffer += self.serial.read(self.serial.in_waiting)
                time.sleep(0.01)
            
            if len(buffer) < 4:
                return None
            
            count_bytes = buffer[:4]
            buffer = buffer[4:]
            
            sample_count = (count_bytes[0] | 
                          (count_bytes[1] << 8) | 
                          (count_bytes[2] << 16) | 
                          (count_bytes[3] << 24))
            
            # Read sample_rate_hz (4 bytes)
            while len(buffer) < 4 and time.time() - start_time < timeout:
                if self.serial.in_waiting > 0:
                    buffer += self.serial.read(self.serial.in_waiting)
                time.sleep(0.01)
            
            if len(buffer) < 4:
                return None
            
            rate_bytes = buffer[:4]
            buffer = buffer[4:]
            
            sample_rate_hz = (rate_bytes[0] | 
                            (rate_bytes[1] << 8) | 
                            (rate_bytes[2] << 16) | 
                            (rate_bytes[3] << 24))
            
            # Read newline
            while len(buffer) < 1 and time.time() - start_time < timeout:
                if self.serial.in_waiting > 0:
                    buffer += self.serial.read(self.serial.in_waiting)
                time.sleep(0.01)
            
            if buffer[0:1] == b'\n':
                buffer = buffer[1:]
            
            # Read sample data
            while len(buffer) < sample_count and time.time() - start_time < timeout:
                if self.serial.in_waiting > 0:
                    buffer += self.serial.read(self.serial.in_waiting)
                time.sleep(0.01)
            
            samples = buffer[:sample_count]
            buffer = buffer[sample_count:]
            
            if len(samples) < sample_count:
                print(f"Warning: Expected {sample_count} samples, got {len(samples)}")
            
            # Calculate sample period in nanoseconds from sample rate
            if sample_rate_hz > 0:
                sample_period_ns = int(1_000_000_000 / sample_rate_hz)
            else:
                sample_period_ns = 1000  # Default 1us if rate is 0
            
            # Return in expected format
            return {
                'type': 'capture',
                'samples': samples,
                'sample_period_ns': sample_period_ns,
                'sample_count': len(samples),
                'sample_rate_hz': sample_rate_hz
            }
            
        except Exception as e:
            print(f"Capture error: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def set_sample_rate(self, rate_code):
        """Set sample rate using firmware commands
        rate_code: '1' = 1MHz, '2' = 2MHz, '5' = 5MHz, '6' = 6MHz
        """
        if not self.serial:
            return False
        
        self.serial.reset_input_buffer()
        self.serial.write(rate_code.encode())
        time.sleep(0.1)
        
        # Read response
        if self.serial.in_waiting > 0:
            response = self.serial.readline().decode('utf-8', errors='ignore').strip()
            return 'OK:' in response
        
        return False
