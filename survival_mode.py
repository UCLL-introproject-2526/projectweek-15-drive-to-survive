import pygame
import asyncio
import random
from car import Car
from zombies import Zombie, fatZombie
from terrain import get_ground_height

# ==============================
# Survival Mode
# ==============================

class SurvivalMode:
    """Survival mode - survive as long as possible in one spot"""
    
    def __init__(self, screen, clock, width, height, font, small_font, car):
        self.screen = screen
        self.clock = clock
        self.WIDTH = width
        self.HEIGHT = height
        self.font = font
        self.small_font = small_font
        self.car = car
        
        # Survival stats
        self.survival_time = 0  # in seconds
        self.frame_count = 0
        self.kills = 0
        self.wave = 1
        self.zombies = []
        
        # Spawn settings
        self.spawn_timer = 0
        self.spawn_interval = 120  # frames between spawns
        self.zombies_per_wave = 3
        
        # Car is locked in position
        self.car.world_x = 500  # Fixed position
        self.car.speed = 0
        
        # Wave announcement
        self.wave_announce_timer = 0
        
        # Flat ground height for survival mode
        self.flat_ground_height = 460
        
        # Track kills without affecting real money (in survival, money stays infinite)
        self.survival_money = 0
        
    def get_flat_ground(self, x):
        """Return flat ground height for survival mode"""
        return self.flat_ground_height
        
    def spawn_wave(self):
        """Spawn a new wave of zombies"""
        self.wave += 1
        self.zombies_per_wave = min(3 + self.wave, 15)  # Cap at 15 zombies
        
        for i in range(self.zombies_per_wave):
            # Spawn zombies only from the right side (in front)
            x = self.car.world_x + random.randint(600, 1000)  # Right side only
            
            # Mix of zombie types based on wave
            if self.wave > 3 and random.random() < 0.3:
                zombie = fatZombie(x)
            else:
                zombie = Zombie(x)
            
            self.zombies.append(zombie)
        
        # Announce wave
        self.wave_announce_timer = 120  # 2 seconds
        
        # Decrease spawn interval for higher waves (more challenging)
        self.spawn_interval = max(60, 120 - (self.wave * 3))
    
    def update_weather(self, weather):
        """Update weather based on current wave"""
        # Change weather every 3 waves
        wave_tier = (self.wave - 1) // 3
        
        weather_types = ['rain', 'snow', 'fog', 'rain', 'snow']
        weather_type = weather_types[wave_tier % len(weather_types)]
        
        # Increase intensity with waves
        intensity = min(self.wave, 8)
        weather.set_weather(weather_type, intensity)
    
    def update_zombie_positions(self):
        """Move zombies towards the car in survival mode"""
        for z in self.zombies:
            if z.alive and not z.dying:
                # Calculate direction to car
                if z.x < self.car.world_x:
                    # Zombie is to the left, move right
                    z.x += 1.5  # Zombie speed
                elif z.x > self.car.world_x:
                    # Zombie is to the right, move left
                    z.x -= 1.5
    
    async def run(self):
        """Run survival mode game loop"""
        import state
        from main import audio_manager
        from visual_effects import DayNightCycle, WeatherSystem
        from controls_screen import ControlsScreen
        
        # Show controls screen before starting survival mode
        controls_screen = ControlsScreen(self.screen, self.font, self.small_font)
        continue_game = await controls_screen.show(self.car.controls, "Survival Mode")
        if not continue_game:
            return  # Player cancelled, return to menu
        
        # Start audio
        if audio_manager.AUDIO_ENABLED and audio_manager._bg_music_loaded:
            audio_manager.play_bg_music()
        
        # Visual effects - make it look dark/intense
        day_night = DayNightCycle()
        weather = WeatherSystem(self.WIDTH, self.HEIGHT)
        
        # Set weather based on wave (changes every few waves)
        self.update_weather(weather)
        
        # Spawn initial wave
        self.spawn_wave()
        
        running = True
        
        while running:
            self.clock.tick(60)
            await asyncio.sleep(0)
            self.frame_count += 1
            
            # Keep money locked at infinite in survival mode
            state.money = 999999999
            
            # Update survival time
            if self.frame_count % 60 == 0:
                self.survival_time += 1
            
            pressed = pygame.key.get_pressed()
            
            # Limited movement - car can only move slightly left/right
            move_range = 150
            if pressed[self.car.controls['accelerate_right']]:
                if self.car.world_x < 500 + move_range:
                    self.car.world_x += 2
            if pressed[self.car.controls['accelerate_left']]:
                if self.car.world_x > 500 - move_range:
                    self.car.world_x -= 2
            
            # Update car position - flat ground in survival mode
            flat_ground_y = 460  # Fixed flat ground height
            self.car.y = flat_ground_y - self.car.rect.height
            
            # Keep car flat (no tilt) in survival mode
            self.car.angle = 0
            self.car.air_angle = None
            self.car.vspeed = 0
            self.car.speed = 0  # No forward momentum
            
            # Update rect position for both collision and drawing
            self.car.rect.y = int(self.car.y)
            self.car.rect.x = self.WIDTH//3 - self.car.rect.width//2
            
            # Track zombie states BEFORE turret updates (to count turret kills)
            zombie_states_before = {}
            for z in self.zombies:
                zombie_states_before[id(z)] = (z.alive, z.dying)
            
            # Update upgrades
            self.car.update_upgrades(pressed, self.zombies)
            
            # Update weather
            weather.update()
            
            # Move zombies towards car
            self.update_zombie_positions()
            
            # Spawn timer
            self.spawn_timer += 1
            if self.spawn_timer >= self.spawn_interval and len(self.zombies) < 30:
                # Add individual zombies between waves - only from right side
                x = self.car.world_x + random.randint(600, 800)  # Right side only
                
                if self.wave > 4 and random.random() < 0.25:
                    self.zombies.append(fatZombie(x))
                else:
                    self.zombies.append(Zombie(x))
                
                self.spawn_timer = 0
            
            # Trigger new wave when all zombies are dead
            if len([z for z in self.zombies if z.alive]) == 0:
                self.spawn_wave()
                # Update weather for new wave
                self.update_weather(weather)
            
            # Draw everything
            from main import draw_background, WHITE, GROUND, GROUND_DARK
            
            draw_background(self.car.world_x)
            
            # Draw flat ground for survival mode
            ground_y = self.flat_ground_height
            pts = [(0, ground_y), (self.WIDTH, ground_y), (self.WIDTH, self.HEIGHT), (0, self.HEIGHT)]
            pygame.draw.polygon(self.screen, GROUND, pts)
            pygame.draw.line(self.screen, GROUND_DARK, (0, ground_y), (self.WIDTH, ground_y), 3)
            
            # Draw survival zone indicator - fixed screen positions
            # Calculate world positions for zone boundaries
            move_range = 150
            zone_left_world = 500 - move_range
            zone_right_world = 500 + move_range
            
            # Convert to screen coordinates
            zone_left_screen = zone_left_world - self.car.world_x + self.WIDTH // 3
            zone_right_screen = zone_right_world - self.car.world_x + self.WIDTH // 3
            
            pygame.draw.line(self.screen, (255, 255, 0), (zone_left_screen, 0), (zone_left_screen, self.HEIGHT), 3)
            pygame.draw.line(self.screen, (255, 255, 0), (zone_right_screen, 0), (zone_right_screen, self.HEIGHT), 3)
            
            self.car.draw(self.screen)
            self.car.draw_upgrades(self.car.world_x, self.screen)
            
            # Update and draw zombies
            for z in self.zombies[:]:
                # Get zombie state before turret updated
                was_alive_before, was_dying_before = zombie_states_before.get(id(z), (False, True))
                
                gained = z.update(self.car, self.get_flat_ground)
                if gained:
                    self.survival_money += gained  # Track in survival mode, don't affect campaign money
                    self.kills += 1
                
                # Count kills from turrets (zombie was alive before turret update, now dying/dead)
                if was_alive_before and not was_dying_before:
                    if (z.dying or not z.alive) and not gained:
                        self.kills += 1
                
                z.draw(self.screen, self.car.world_x, self.get_flat_ground)
                
                # Remove dead zombies after animation
                if not z.alive and not z.dying:
                    self.zombies.remove(z)
            
            # Draw weather
            weather.draw(self.screen)
            
            # Apply darkness
            day_night.apply_overlay(self.screen, 6)  # Dark atmosphere
            
            # Draw UI
            self.draw_ui()
            
            # Wave announcement
            if self.wave_announce_timer > 0:
                self.wave_announce_timer -= 1
                wave_text = self.font.render(f"WAVE {self.wave}!", True, (255, 100, 100))
                self.screen.blit(wave_text, (self.WIDTH//2 - wave_text.get_width()//2, self.HEIGHT//3))
            
            # Check game over
            if self.car.health <= 0:
                running = False
            
            # Handle events
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    import sys
                    pygame.quit()
                    sys.exit()
                elif e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_ESCAPE:
                        running = False
            
            pygame.display.flip()
        
        # Stop audio
        try:
            audio_manager.stop_engine_sound()
            audio_manager.stop_music()
        except Exception:
            pass
        
        # Show results
        await self.show_results()
    
    def draw_ui(self):
        """Draw survival mode UI"""
        from main import WHITE, draw_health_bar
        
        # Health bar
        draw_health_bar(self.car)
        
        # Survival time
        time_text = self.small_font.render(f"Time: {self.survival_time}s", True, WHITE)
        self.screen.blit(time_text, (self.WIDTH - 200, 20))
        
        # Kills
        kills_text = self.small_font.render(f"Kills: {self.kills}", True, WHITE)
        self.screen.blit(kills_text, (self.WIDTH - 200, 50))
        
        # Wave
        wave_text = self.small_font.render(f"Wave: {self.wave}", True, (255, 200, 100))
        self.screen.blit(wave_text, (self.WIDTH - 200, 80))
        
        # Zombies alive
        zombies_alive = len([z for z in self.zombies if z.alive])
        zombie_text = self.small_font.render(f"Zombies: {zombies_alive}", True, (255, 100, 100))
        self.screen.blit(zombie_text, (self.WIDTH - 200, 110))
        
        # Mode indicator
        mode_text = self.font.render("SURVIVAL MODE", True, (255, 255, 0))
        self.screen.blit(mode_text, (20, 80))
    
    async def show_results(self):
        """Show survival results screen"""
        from main import WHITE, BLACK
        
        waiting = True
        while waiting:
            self.screen.fill((20, 20, 30))
            
            # Title
            title = self.font.render("SURVIVAL ENDED", True, (255, 100, 100))
            self.screen.blit(title, (self.WIDTH//2 - title.get_width()//2, 150))
            
            # Stats
            y = 250
            stats = [
                f"Survived: {self.survival_time} seconds",
                f"Waves: {self.wave}",
                f"Zombies Killed: {self.kills}",
                f"Score: {self.kills * 10 + self.survival_time * 5}"
            ]
            
            for stat in stats:
                stat_text = self.small_font.render(stat, True, WHITE)
                self.screen.blit(stat_text, (self.WIDTH//2 - stat_text.get_width()//2, y))
                y += 40
            
            # Continue
            continue_text = self.small_font.render("Press any key to continue", True, (200, 200, 200))
            self.screen.blit(continue_text, (self.WIDTH//2 - continue_text.get_width()//2, 500))
            
            pygame.display.flip()
            
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    import sys
                    pygame.quit()
                    sys.exit()
                elif e.type == pygame.KEYDOWN or e.type == pygame.MOUSEBUTTONDOWN:
                    waiting = False
            
            await asyncio.sleep(0)
