import pygame 
import math
from player import Player
from zombie import Zombie, spawn_zombies
from terrain import Terrain
from upgrades import Upgrade, load_upgrades
from credits import CreditsScreen

class Logo:
    def __init__(self, image_path, x, y, width=None, height=None):
        self.__image = pygame.image.load(image_path)
        if width and height:
            self.__image = pygame.transform.scale(self.__image, (width, height))
        self.__x = x
        self.__y = y
    
    def render(self, srf):
        srf.blit(self.__image, (self.__x, self.__y))

class Button:
    def __init__(self, x, y, width, height, text, color=(100, 100, 100), hover_color=(150, 150, 150), text_color=(255, 255, 255), icon_path=None):
        self.__rect = pygame.Rect(x, y, width, height)
        self.__text = text
        self.__color = color
        self.__hover_color = hover_color
        self.__text_color = text_color
        self.__is_hovered = False
        self.__font = pygame.font.Font(None, 36)
        self.__icon = None
        if icon_path:
            self.__icon = pygame.image.load(icon_path)
            # Beetje padding adden zodat het settings icoon past
            icon_size = min(width - 10, height - 10)
            self.__icon = pygame.transform.scale(self.__icon, (int(icon_size), int(icon_size)))
    
    def is_clicked(self, mouse_pos, mouse_pressed):
        if self.__rect.collidepoint(mouse_pos) and mouse_pressed[0]:
            return True
        return False
    
    def update(self, mouse_pos):
        self.__is_hovered = self.__rect.collidepoint(mouse_pos)
    
    def render(self, srf):
        color = self.__hover_color if self.__is_hovered else self.__color
        pygame.draw.rect(srf, color, self.__rect)
        pygame.draw.rect(srf, (255, 255, 255), self.__rect, 2)  # Border
        
        if self.__icon:
            # Icoon centreren in de button
            icon_rect = self.__icon.get_rect(center=self.__rect.center)
            srf.blit(self.__icon, icon_rect)
        
        if self.__text:
            text_surface = self.__font.render(self.__text, True, self.__text_color)
            text_rect = text_surface.get_rect(center=self.__rect.center)
            srf.blit(text_surface, text_rect)

class Background: 
    def __init__(self, image):
        self.__image = self.__create_image(image)

    def __create_image(self, image):
        return pygame.image.load(image)
    
    def render(self, srf):
        srf.blit(self.__image, (0, 0))
    
class StartScreen:
    def __init__(self):
        self.__background = Background('images/Background-image.png')
        self.__logo = Logo('images/UI/logo.png', 112, 100, 800, 500)
        
        # Buttons - horizontaal naast elkaar, lager op scherm
        self.__start_button = Button(162, 600, 200, 60, 'Start Game', (50, 150, 50), (70, 200, 70))
        self.__credits_button = Button(412, 600, 200, 60, 'Credits', (100, 100, 50), (150, 150, 70))
        self.__quit_button = Button(662, 600, 200, 60, 'Quit', (150, 50, 50), (200, 70, 70))
        self.__settings_button = Button(954, 10, 60, 60, '', (50, 50, 150), (70, 70, 200), icon_path='images/ui/settings-icon.png')
        
    def update(self, mouse_pos):
        self.__start_button.update(mouse_pos)
        self.__credits_button.update(mouse_pos)
        self.__settings_button.update(mouse_pos)
        self.__quit_button.update(mouse_pos)
    
    def handle_click(self, mouse_pos, mouse_pressed):
        if self.__start_button.is_clicked(mouse_pos, mouse_pressed):
            return 'start_game'
        elif self.__credits_button.is_clicked(mouse_pos, mouse_pressed):
            return 'credits'
        elif self.__settings_button.is_clicked(mouse_pos, mouse_pressed):
            return 'settings'
        elif self.__quit_button.is_clicked(mouse_pos, mouse_pressed):
            return 'quit'
        return None
    
    def render(self, srf):
        self.__background.render(srf)
        self.__logo.render(srf)
        self.__start_button.render(srf)
        self.__credits_button.render(srf)
        self.__quit_button.render(srf)
        self.__settings_button.render(srf)

class GarageScreen:
    def __init__(self):
        try:
            garage_bg_raw = pygame.image.load('images/Background-image-garage.png')
            self.__background = pygame.transform.scale(garage_bg_raw, (1024, 768))
        except:
            self.__background = None
        
        self.__title_font = pygame.font.Font(None, 48)
        self.__font = pygame.font.Font(None, 32)
        self.__small_font = pygame.font.Font(None, 24)
        
        self.__start_button = Button(412, 650, 200, 60, 'Start Level', (200, 70, 70), (255, 100, 80))
        self.__back_button = Button(20, 20, 120, 50, 'Menu', (70, 70, 70), (100, 100, 100))
        
        self.scroll_y = 0
        self.scroll_speed = 20
        self.confirmation_active = False
        self.confirmation_upgrade = None
    
    def update(self, mouse_pos):
        self.__start_button.update(mouse_pos)
        self.__back_button.update(mouse_pos)
        self.__back_button.update(mouse_pos)
    
    def handle_scroll(self, direction, upgrades_count):
        self.scroll_y += direction * self.scroll_speed
        max_scroll = max(0, upgrades_count * 70 - 400)
        self.scroll_y = max(min(self.scroll_y, 0), -max_scroll)
    
    def handle_click(self, mouse_pos, mouse_pressed, player, state, upgrades):
        if self.confirmation_active and self.confirmation_upgrade:
            # Handle confirmation popup
            popup_rect = pygame.Rect(1024//2 - 150, 768//2 - 120, 300, 240)
            btn_yes = pygame.Rect(popup_rect.x + 30, popup_rect.y + 180, 100, 40)
            btn_no = pygame.Rect(popup_rect.x + 170, popup_rect.y + 180, 100, 40)
            
            if btn_yes.collidepoint(mouse_pos) and mouse_pressed[0]:
                if state.money >= self.confirmation_upgrade.price:
                    state.money -= self.confirmation_upgrade.price
                    self.confirmation_upgrade.purchased = True
                    player.apply_upgrade(self.confirmation_upgrade)
                self.confirmation_active = False
                self.confirmation_upgrade = None
                return None
            elif btn_no.collidepoint(mouse_pos) and mouse_pressed[0]:
                self.confirmation_active = False
                self.confirmation_upgrade = None
                return None
        else:
            if self.__start_button.is_clicked(mouse_pos, mouse_pressed):
                return 'start_level'
            elif self.__back_button.is_clicked(mouse_pos, mouse_pressed):
                return 'back_to_menu'
            
            # Check upgrade clicks
            upgrade_area = pygame.Rect(1024 - 300, 100, 250, 500)
            y_offset = 0
            for upgrade in upgrades:
                item_rect = pygame.Rect(upgrade_area.x + 10, upgrade_area.y + 10 + y_offset + self.scroll_y, 230, 60)
                if item_rect.collidepoint(mouse_pos):
                    # Left click: buy (if not purchased) or equip (if purchased but not equipped)
                    if mouse_pressed[0]:
                        if not upgrade.purchased:
                            # Kopen
                            if state.money >= upgrade.price:
                                self.confirmation_active = True
                                self.confirmation_upgrade = upgrade
                        elif not upgrade.equipped:
                            # Al gekocht maar niet equipped - direct equippen
                            player.apply_upgrade(upgrade)
                    # Right click: unequip upgrade (if equipped) OR reset all if default
                    elif mouse_pressed[2]:
                        if upgrade.equipped:
                            if "default" in upgrade.name.lower() or "defauld" in upgrade.name.lower():
                                player.reset_all_upgrades()
                            else:
                                player.remove_upgrade(upgrade)
                y_offset += 70
        return None
    
    def render(self, srf, player, state, upgrades):
        # Background
        if self.__background:
            srf.blit(self.__background, (0, 0))
        else:
            srf.fill((50, 50, 50))
        
        # Back button
        self.__back_button.render(srf)
        
        # Title
        title = self.__title_font.render('Garage - Upgrades', True, (255, 255, 255))
        srf.blit(title, (1024//2 - title.get_width()//2, 20))
        
        # Money display
        money_text = self.__font.render(f'Money: ${state.money}', True, (255, 255, 255))
        srf.blit(money_text, (50, 80))
        
        # Level display
        level_text = self.__font.render(f'Level: {state.level}', True, (255, 255, 255))
        srf.blit(level_text, (50, 120))
        
        # Car preview
        try:
            car_img = pygame.transform.scale(player._Player__base_image, (500, 500))
            car_rect = car_img.get_rect(center=(300, 400))
            srf.blit(car_img, car_rect)
        except:
            pass
        
        # Upgrades menu
        upgrade_area = pygame.Rect(1024 - 300, 100, 250, 500)
        pygame.draw.rect(srf, (50, 50, 50), upgrade_area)
        pygame.draw.rect(srf, (255, 255, 255), upgrade_area, 2)
        
        y_offset = 0
        for upgrade in upgrades:
            item_rect = pygame.Rect(upgrade_area.x + 10, upgrade_area.y + 10 + y_offset + self.scroll_y, 230, 60)
            
            # Only draw if visible
            if item_rect.bottom > upgrade_area.top and item_rect.top < upgrade_area.bottom:
                # Bepaal kleur gebaseerd op status
                if upgrade.equipped:
                    color = (50, 100, 50)  # Groen voor equipped upgrades
                elif upgrade.purchased:
                    color = (60, 60, 80)  # Blauw-grijs voor owned upgrades
                else:
                    color = (80, 80, 80)
                    if item_rect.collidepoint(pygame.mouse.get_pos()):
                        color = (120, 120, 120)
                pygame.draw.rect(srf, color, item_rect)
                
                # Upgrade icon
                try:
                    icon = upgrade.image_small.copy()
                    if upgrade.equipped:
                        # Normaal voor equipped upgrades
                        pass
                    elif upgrade.purchased:
                        # Maak icon iets donkerder voor owned maar niet equipped
                        icon.fill((150, 150, 150, 180), special_flags=pygame.BLEND_RGBA_MULT)
                    srf.blit(icon, (item_rect.x + 5, item_rect.y + 10))
                except:
                    pass
                
                # Upgrade text
                if upgrade.equipped:
                    # Equipped - show as active
                    text_color = (100, 255, 100)
                    text = self.__small_font.render(f'{upgrade.name}', True, text_color)
                    srf.blit(text, (item_rect.x + 90, item_rect.y + 10))
                    if "default" in upgrade.name.lower() or "defauld" in upgrade.name.lower():
                        owned_text = self.__small_font.render('RIGHT CLICK: RESET', True, (200, 100, 50))
                    else:
                        owned_text = self.__small_font.render('EQUIPPED (R-CLICK)', True, (50, 200, 50))
                    srf.blit(owned_text, (item_rect.x + 90, item_rect.y + 35))
                elif upgrade.purchased:
                    # Purchased but not equipped - show as owned
                    text_color = (150, 150, 150)
                    text = self.__small_font.render(f'{upgrade.name}', True, text_color)
                    srf.blit(text, (item_rect.x + 90, item_rect.y + 10))
                    owned_text = self.__small_font.render('OWNED (CLICK)', True, (100, 100, 200))
                    srf.blit(owned_text, (item_rect.x + 90, item_rect.y + 35))
                else:
                    text_color = (255, 255, 255) if state.money >= upgrade.price else (150, 150, 150)
                    text = self.__small_font.render(f'{upgrade.name}', True, text_color)
                    srf.blit(text, (item_rect.x + 90, item_rect.y + 10))
                    price_text = self.__small_font.render(f'${upgrade.price}', True, text_color)
                    srf.blit(price_text, (item_rect.x + 90, item_rect.y + 35))
            
            y_offset += 70
        
        # Start button
        self.__start_button.render(srf)
        
        # Confirmation popup
        if self.confirmation_active and self.confirmation_upgrade:
            popup_rect = pygame.Rect(1024//2 - 150, 768//2 - 120, 300, 240)
            pygame.draw.rect(srf, (60, 60, 60), popup_rect)
            pygame.draw.rect(srf, (255, 255, 255), popup_rect, 2)
            
            msg = self.__small_font.render(f'Purchase {self.confirmation_upgrade.name}', True, (255, 255, 255))
            srf.blit(msg, (popup_rect.centerx - msg.get_width()//2, popup_rect.y + 20))
            price_msg = self.__small_font.render(f'for ${self.confirmation_upgrade.price}?', True, (255, 255, 255))
            srf.blit(price_msg, (popup_rect.centerx - price_msg.get_width()//2, popup_rect.y + 50))
            
            # Yes/No buttons
            btn_yes = pygame.Rect(popup_rect.x + 30, popup_rect.y + 180, 100, 40)
            btn_no = pygame.Rect(popup_rect.x + 170, popup_rect.y + 180, 100, 40)
            
            yes_color = (255, 100, 80) if btn_yes.collidepoint(pygame.mouse.get_pos()) else (200, 70, 70)
            pygame.draw.rect(srf, yes_color, btn_yes, border_radius=5)
            yes_text = self.__small_font.render('Yes', True, (255, 255, 255))
            srf.blit(yes_text, (btn_yes.centerx - yes_text.get_width()//2, btn_yes.centery - yes_text.get_height()//2))
            
            no_color = (255, 100, 80) if btn_no.collidepoint(pygame.mouse.get_pos()) else (200, 70, 70)
            pygame.draw.rect(srf, no_color, btn_no, border_radius=5)
            no_text = self.__small_font.render('No', True, (255, 255, 255))
            srf.blit(no_text, (btn_no.centerx - no_text.get_width()//2, btn_no.centery - no_text.get_height()//2))

class State:
    def __init__(self, level=1):
        self.__background = Background('images/Background-image.png')
        self.terrain = Terrain()
        self.level = level
        self.zombies = spawn_zombies(level)
        self.money = 500

    def get_ground_height(self, x):
        return self.terrain.get_ground_height(x)

    def render(self, srf, cam_x):
        self.__background.render(srf)
        self.terrain.draw_ground(srf, cam_x)
        # Draw zombies
        for zombie in self.zombies:
            zombie.draw(srf, cam_x, self.terrain)

def create_main_surface():
    screen_size = (1024, 768)
    srf = pygame.display.set_mode(screen_size)
    return srf

def clear_surface(srf):
    srf.fill((0,0,0))

def render_frame(srf, state, player):
    clear_surface(srf)
    state.render(srf, player.world_x)
    player.render(srf, state)
    player.draw_health_bar(srf)
    player.draw_fuel_bar(srf)
    
    # Display distance, money, and fuel
    font = pygame.font.Font(None, 36)
    small_font = pygame.font.Font(None, 28)
    
    # Distance and money top right
    text = font.render(f'Distance: {int(player.world_x)}  Money: ${state.money}', True, (255, 255, 255))
    text_rect = text.get_rect(topright=(1024 - 10, 10))
    srf.blit(text, text_rect)
    
    # Fuel percentage top right below distance
    fuel_text = small_font.render(f'Fuel: {int(player.fuel)}%', True, (255, 255, 255))
    fuel_rect = fuel_text.get_rect(topright=(1024 - 10, 50))
    srf.blit(fuel_text, fuel_rect)
    
    pygame.display.flip()

def main():
    pygame.init()
    # Maakt scherm
    srf = create_main_surface()
    # Clock voor fps vast te zetten - anders gaat spel te snel
    clock = pygame.time.Clock()
    
    # Game states
    current_state = 'start_screen'  # 'start_screen', 'garage', 'credits', of 'playing'
    start_screen = StartScreen()
    garage_screen = GarageScreen()
    credits_screen = None  # Initialiseren wanneer nodig
    upgrades = load_upgrades()
    current_level = 1
    state = State(current_level)
    player = Player('images/truck/first-car-concept.png')
    player.initialize_position(state)  # Initiële positie 
    
    # Gameloop
    while True:
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.MOUSEWHEEL and current_state == 'garage':
                garage_screen.handle_scroll(event.y, len(upgrades))
            elif event.type == pygame.MOUSEWHEEL and current_state == 'credits':
                credits_screen.handle_scroll(event.y)
        
        if current_state == 'start_screen':
            start_screen.update(mouse_pos)
            action = start_screen.handle_click(mouse_pos, mouse_pressed)
            
            if action == 'start_game':
                current_state = 'garage'
            elif action == 'quit':
                pygame.quit()
                return
            elif action == 'credits':
                current_state = 'credits'
            elif action == 'settings':
                # Voeg settings functionaliteit toe
                pass
            
            clear_surface(srf)
            start_screen.render(srf)
            pygame.display.flip()
        
        elif current_state == 'garage':
            garage_screen.update(mouse_pos)
            action = garage_screen.handle_click(mouse_pos, mouse_pressed, player, state, upgrades)
            
            if action == 'start_level':
                current_state = 'playing'
            elif action == 'back_to_menu':
                current_state = 'start_screen'
            
            clear_surface(srf)
            garage_screen.render(srf, player, state, upgrades)
            pygame.display.flip()
        
        elif current_state == 'credits':
            if credits_screen is None:
                credits_screen = CreditsScreen()
            
            credits_screen.update(mouse_pos)
            action = credits_screen.handle_click(mouse_pos, mouse_pressed)
            
            if action == 'back_to_menu':
                current_state = 'start_screen'
            
            clear_surface(srf)
            credits_screen.render(srf)
            pygame.display.flip()
            
        elif current_state == 'playing':
            keys = pygame.key.get_pressed()
            player.update(state, keys)
            
            # Update zombies en check collisions
            for zombie in state.zombies:
                money_earned = zombie.update(player, state.terrain)
                state.money += money_earned
            
            render_frame(srf, state, player)
            
            # Check game over condities
            if player.world_x >= 10000:
                # Level complete - ga naar garage
                current_level += 1
                current_state = 'garage'
                old_money = state.money
                old_upgrades = player.purchased_upgrades.copy()  # Save upgrades
                state = State(current_level)
                state.money = old_money + (player.health * 5)  # Keep money + bonus
                player = Player('images/truck/first-car-concept.png')
                player.purchased_upgrades = old_upgrades  # Restore upgrades
                player.update_combined_image()  # Apply upgrades to image
                # Reapply upgrade stats
                for upgrade in old_upgrades:
                    player.damage_reduction += upgrade.damage_reduction
                    player.speed_multiplier += upgrade.speed_increase
                player.initialize_position(state)
            elif not player.is_alive() or player.fuel <= 0:
                # Game over - Terug naar startscherm
                current_state = 'start_screen'
                current_level = 1
                upgrades = load_upgrades()  # Reset upgrades
                state = State(current_level)
                player = Player('images/truck/first-car-concept.png')
                player.initialize_position(state)
        
        clock.tick(60)  # 60 FPS
        
main()
