import pygame

class GestureCamera:
    """
    Easter egg display system triggered by F12 key.
    """
    
    def __init__(self, screen_width, screen_height, easter_egg_image_path):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.easter_egg_image_path = easter_egg_image_path
        self.easter_egg_surface = None
        self.show_easter_egg = False
        self.easter_egg_timer = 0
        self.easter_egg_duration = 3000  # Show for 3 seconds
        self.gesture_detected = False
        
        # Load easter egg image
        try:
            img = pygame.image.load(easter_egg_image_path).convert_alpha()
            self.easter_egg_surface = pygame.transform.scale(img, (screen_width, screen_height))
            print("Easter egg image loaded successfully")
        except Exception as e:
            print(f"Error loading easter egg image: {e}")
            # Create a fallback surface
            self.easter_egg_surface = pygame.Surface((screen_width, screen_height))
            self.easter_egg_surface.fill((255, 0, 255))  # Magenta fallback
            font = pygame.font.Font(None, 72)
            text = font.render("EASTER EGG!", True, (255, 255, 255))
            text_rect = text.get_rect(center=(screen_width//2, screen_height//2))
            self.easter_egg_surface.blit(text, text_rect)
    
    def initialize_camera(self):
        """Initialize - kept for compatibility"""
        print("Easter egg system ready - Press F12 to activate")
        return True
    
    def handle_event(self, event):
        """Handle keyboard events to trigger easter egg"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F12:
                self.gesture_detected = True
                return True
        return False
    
    def update(self, dt):
        """Update easter egg state"""
        # Check if F12 was pressed
        if self.gesture_detected and not self.show_easter_egg:
            self.show_easter_egg = True
            self.easter_egg_timer = pygame.time.get_ticks()
            print("Easter egg triggered!")
            self.gesture_detected = False  # Reset trigger
        
        # Update timer
        if self.show_easter_egg:
            current_time = pygame.time.get_ticks()
            if current_time - self.easter_egg_timer >= self.easter_egg_duration:
                self.show_easter_egg = False
    
    def draw(self, screen):
        """Draw easter egg overlay if active"""
        if self.show_easter_egg and self.easter_egg_surface:
            screen.blit(self.easter_egg_surface, (0, 0))
    
    def cleanup(self):
        """Clean up resources"""
        pass
    
    def toggle(self):
        """Toggle - not used"""
        return True
