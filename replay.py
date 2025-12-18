"""
Replay system for recording and playing back game sessions
"""
import pygame
import copy

class ReplayRecorder:
    """Records game state for replay"""
    def __init__(self):
        self.frames = []
        self.recording = False
        
    def start_recording(self):
        """Start recording a new session"""
        self.frames = []
        self.recording = True
        
    def stop_recording(self):
        """Stop recording"""
        self.recording = False
        
    def record_frame(self, car, zombies, distance, money):
        """Record current frame state"""
        if not self.recording:
            return
            
        # Record car state
        car_state = {
            'world_x': car.world_x,
            'y': car.y,
            'speed': car.speed,
            'vspeed': car.vspeed,
            'angle': car.angle,
            'health': car.health,
            'fuel': car.fuel,
            'max_health': car.max_health,
            'max_fuel': car.max_fuel
        }
        
        # Record zombie states
        zombie_states = []
        for zombie in zombies:
            zombie_state = {
                'x': zombie.x,
                'alive': zombie.alive,
                'dying': zombie.dying,
                'death_timer': zombie.death_timer,
                'health': zombie.health,
                'current_frame': zombie.current_frame,
                'type': zombie.__class__.__name__
            }
            zombie_states.append(zombie_state)
        
        # Store frame
        frame = {
            'car': car_state,
            'zombies': zombie_states,
            'distance': distance,
            'money': money
        }
        
        self.frames.append(frame)
    
    def get_recording(self):
        """Get the recorded frames"""
        return self.frames
    
    def has_recording(self):
        """Check if there's a recording available"""
        return len(self.frames) > 0


class ReplayPlayer:
    """Plays back recorded game sessions"""
    def __init__(self, frames):
        self.frames = frames
        self.current_frame = 0
        self.playing = False
        self.speed = 1.0  # Playback speed multiplier
        
    def start(self):
        """Start playback"""
        self.current_frame = 0
        self.playing = True
        
    def stop(self):
        """Stop playback"""
        self.playing = False
        
    def get_current_frame(self):
        """Get current frame data"""
        if self.current_frame < len(self.frames):
            return self.frames[self.current_frame]
        return None
    
    def advance(self):
        """Move to next frame"""
        if self.playing and self.current_frame < len(self.frames) - 1:
            self.current_frame += 1
            return True
        else:
            self.playing = False
            return False
    
    def is_finished(self):
        """Check if replay is finished"""
        return self.current_frame >= len(self.frames) - 1
    
    def set_speed(self, speed):
        """Set playback speed (1.0 = normal, 2.0 = 2x, etc)"""
        self.speed = max(0.1, min(speed, 5.0))


# Global recorder instance
_recorder = ReplayRecorder()

def get_recorder():
    """Get the global recorder instance"""
    return _recorder

def start_recording():
    """Start recording gameplay"""
    _recorder.start_recording()

def stop_recording():
    """Stop recording gameplay"""
    _recorder.stop_recording()

def record_frame(car, zombies, distance, money):
    """Record current frame"""
    _recorder.record_frame(car, zombies, distance, money)

def get_replay():
    """Get recorded frames for playback"""
    return _recorder.get_recording()

def has_replay():
    """Check if replay is available"""
    return _recorder.has_recording()
