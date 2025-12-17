import pygame
import os
import math
import struct

# Audio module for Zombie Car game
# Handles all audio initialization, loading, and playback

class AudioManager:
    def __init__(self, mixer_available):
        self.MIXER_AVAILABLE = mixer_available
        self.AUDIO_ENABLED = True if mixer_available else False
        self.AUDIO_VOLUME_MUSIC = 0.4
        self.AUDIO_VOLUME_SFX = 0.6
        
        # Engine volume behaviour: idle is soft (factor 0..1 relative to AUDIO_VOLUME_SFX), drive increases to a louder factor
        self.ENGINE_VOLUME_IDLE_FACTOR = 0.25  # softly audible when idle
        self.ENGINE_VOLUME_DRIVE_FACTOR = 1.0   # full SFX volume when driving
        self.ENGINE_VOLUME_STEP = 0.04         # per-frame smoothing step toward target factor
        
        # Audio paths
        self.MENU_MUSIC_PATH = os.path.join("assets", "music", "menu.mp3")
        self.BG_MUSIC_PATH = os.path.join("assets", "music", "music.mp3")
        self.ENGINE_SOUND_PATH = os.path.join("assets", "music", "menu.wav")
        
        # Audio state
        self._menu_music_loaded = False
        self._bg_music_loaded = False
        self._engine_sound = None
        self._engine_playing = False
        
        # Initialize audio assets
        self._load_audio_assets()
        
        # Auto-start menu music
        if self.AUDIO_ENABLED and self._menu_music_loaded:
            try:
                self.play_menu_music()
            except Exception as e:
                print(f"Auto-start menu music failed: {e}")
        
        # Auto test tone
        if self.MIXER_AVAILABLE:
            try:
                test_tone = self.synth_sine_sound(frequency=440.0, duration=0.5, volume=0)
                if test_tone:
                    print("Auto test tone: playing")
                    try:
                        test_tone.play()
                    except Exception as e:
                        print(f"Auto test tone play failed: {e}")
                else:
                    print("Auto test tone: synthesis failed")
            except Exception as e:
                print(f"Auto test tone failed: {e}")
    
    def _load_audio_assets(self):
        """Load audio files if mixer is available"""
        if not self.MIXER_AVAILABLE:
            return
        
        try:
            menu_exists = os.path.exists(self.MENU_MUSIC_PATH)
            bg_exists = os.path.exists(self.BG_MUSIC_PATH)
            engine_exists = os.path.exists(self.ENGINE_SOUND_PATH)
            
            print(f"Audio files - menu: {menu_exists}, bg: {bg_exists}, engine: {engine_exists}")
            
            if menu_exists:
                try:
                    pygame.mixer.music.load(self.MENU_MUSIC_PATH)
                    self._menu_music_loaded = True
                except Exception as e:
                    print(f"Failed to load menu music: {e}")
            
            if bg_exists:
                self._bg_music_loaded = True
            
            if engine_exists:
                try:
                    self._engine_sound = pygame.mixer.Sound(self.ENGINE_SOUND_PATH)
                    # set initial idle volume (will be adjusted when driving)
                    try:
                        self._engine_sound.set_volume(self.AUDIO_VOLUME_SFX * self.ENGINE_VOLUME_IDLE_FACTOR)
                    except Exception:
                        self._engine_sound.set_volume(self.AUDIO_VOLUME_SFX)
                except Exception as e:
                    print(f"Failed to load engine sound: {e}")
        except Exception as e:
            print(f"Audio load error: {e}")
            self.AUDIO_ENABLED = False
        
        print(f"_menu_music_loaded={self._menu_music_loaded}, _bg_music_loaded={self._bg_music_loaded}, engine_loaded={self._engine_sound is not None}, AUDIO_ENABLED={self.AUDIO_ENABLED}")
        
        # If engine sound wasn't loaded from file, synth one as fallback
        if self.MIXER_AVAILABLE and self._engine_sound is None:
            self._engine_sound = self.synth_sine_sound(frequency=110.0, duration=1.0, volume=0)
            if self._engine_sound:
                # set initial idle volume for synthesized sound as well
                try:
                    pass
                except Exception:
                    self._engine_sound.set_volume(self.AUDIO_VOLUME_SFX)
                print("Synthesized engine sound for fallback")
            else:
                print("No engine sound available and synthesis failed")
    
    def play_menu_music(self):
        """Play menu music in a loop"""
        if not self.AUDIO_ENABLED or not self._menu_music_loaded:
            print("play_menu_music: skipped (audio disabled or file missing)")
            return
        try:
            print("play_menu_music: attempting to play")
            pygame.mixer.music.load(self.MENU_MUSIC_PATH)
            pygame.mixer.music.set_volume(self.AUDIO_VOLUME_MUSIC)
            pygame.mixer.music.play(-1)
            print("play_menu_music: playing")
        except Exception as e:
            print(f"Failed to play menu music: {e}")
    
    def play_bg_music(self):
        """Play background music for gameplay"""
        if not self.AUDIO_ENABLED:
            print("play_bg_music: skipped (audio disabled)")
            return
        try:
            # If explicit background track is missing, fall back to menu music if available
            if self._bg_music_loaded:
                path = self.BG_MUSIC_PATH
            elif self._menu_music_loaded:
                path = self.MENU_MUSIC_PATH
                print("play_bg_music: falling back to menu music")
            else:
                print("play_bg_music: skipped (no tracks available)")
                return
            
            print(f"play_bg_music: attempting to play {path}")
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(self.AUDIO_VOLUME_MUSIC)
            pygame.mixer.music.play(-1)
            print("play_bg_music: playing")
        except Exception as e:
            print(f"Failed to play background music: {e}")
    
    def stop_music(self):
        """Stop currently playing music"""
        if not self.AUDIO_ENABLED:
            return
        try:
            pygame.mixer.music.stop()
        except Exception:
            pass
    
    def stop_engine_sound(self):
        """Stop engine sound effect"""
        try:
            if self._engine_sound:
                self._engine_sound.stop()
        except Exception:
            pass
    
    def get_engine_sound(self):
        """Get the engine sound object"""
        return self._engine_sound
    
    def set_volumes(self, music_volume, sfx_volume):
        """Update audio volumes"""
        self.AUDIO_VOLUME_MUSIC = music_volume
        self.AUDIO_VOLUME_SFX = sfx_volume
        
        if self.MIXER_AVAILABLE:
            try:
                pygame.mixer.music.set_volume(self.AUDIO_VOLUME_MUSIC)
                if self._engine_sound:
                    self._engine_sound.set_volume(self.AUDIO_VOLUME_SFX * self.ENGINE_VOLUME_IDLE_FACTOR)
            except:
                pass
    
    def synth_sine_sound(self, frequency=100.0, duration=1.0, volume=0):
        """Generate a pygame.mixer.Sound containing a sine wave.
        
        Returns None if mixer not initialized or generation fails.
        """
        if not self.MIXER_AVAILABLE:
            return None
        try:
            fmt = pygame.mixer.get_init()  # (frequency, size, channels)
            if not fmt:
                sr = 44100
                channels = 2
            else:
                sr = fmt[0]
                channels = fmt[2] if len(fmt) > 2 else 2
            
            n_samples = int(sr * duration)
            max_amp = int(volume * 32767)
            
            buf = bytearray()
            for i in range(n_samples):
                t = i / sr
                sample = int(max_amp * math.sin(2.0 * math.pi * frequency * t))
                # pack as signed 16-bit little-endian
                packed = struct.pack('<h', sample)
                if channels == 2:
                    buf.extend(packed)
                    buf.extend(packed)
                else:
                    buf.extend(packed)
            sound = pygame.mixer.Sound(buffer=bytes(buf))
            return sound
        except Exception as e:
            print(f"synth_sine_sound failed: {e}")
            return None
