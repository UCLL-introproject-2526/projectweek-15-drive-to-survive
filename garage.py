import pygame
import sys
import state
from car_types import get_car_type_list, get_current_car_type, set_current_car_type
from upgrades import load_upgrades, save_all_upgrades_status


class ArrowButton:
    def __init__(self, x, y, width, height, direction="left"):
        self.rect = pygame.Rect(x, y, width, height)
        self.direction = direction  # "left" or "right"
        self.hovered = False
        
    def update(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)
    
    def is_clicked(self, mouse_pos, mouse_pressed):
        return self.hovered and mouse_pressed
    
    def render(self, surface):
        # Import colors locally to avoid circular dependency
        ARROW_HOVER = (255, 255, 100)
        ARROW_COLOR = (200, 200, 200)
        WHITE = (255, 255, 255)
        BLACK = (0, 0, 0)
        
        color = ARROW_HOVER if self.hovered else ARROW_COLOR
        pygame.draw.rect(surface, color, self.rect, border_radius=5)
        pygame.draw.rect(surface, WHITE, self.rect, 2, border_radius=5)
        
        # Draw arrow triangle
        center_x = self.rect.centerx
        center_y = self.rect.centery
        size = min(self.rect.width, self.rect.height) // 3
        
        if self.direction == "left":
            points = [
                (center_x + size, center_y - size),
                (center_x - size, center_y),
                (center_x + size, center_y + size)
            ]
        else:  # right
            points = [
                (center_x - size, center_y - size),
                (center_x + size, center_y),
                (center_x - size, center_y + size)
            ]
        
        pygame.draw.polygon(surface, BLACK, points)


def garage(car, screen, clock, WIDTH, HEIGHT, font, small_font, garage_bg, 
           stop_engine_sound, play_menu_music, AUDIO_ENABLED, _menu_music_loaded,
           WHITE, BUTTON, BUTTON_HOVER, UPGRADE_BG, EQUIPPED_COLOR, PURCHASED_COLOR):
    """Display garage with car selection and upgrade menu"""
    # Stop engine sound when entering garage
    stop_engine_sound()
    
    # Start menu music when entering garage
    if AUDIO_ENABLED and _menu_music_loaded:
        play_menu_music()
    
    # Laad alle auto's
    car_types_list = get_car_type_list()
    if not car_types_list:
        print("ERROR: No car types found!")
        return

    # Vind de index van de huidige auto
    current_index = 0
    cur = get_current_car_type()
    cur_name = cur.name.lower() if cur else None
    for i, car_type in enumerate(car_types_list):
        if car_type.name.lower() == cur_name:
            current_index = i
            break
    
    # Load upgrades for selected car
    load_upgrades()
    
    # Now apply equipped upgrades to the car
    car.apply_equipped_upgrades()
    
    # Now show upgrades for selected car
    running = True
    upgrades = load_upgrades()
    scroll_y = 0
    scroll_speed = 20
    confirmation_active = False
    confirmation_upgrade = None
    confirmation_action = None  # 'purchase' or 'toggle_equip'
    
    # Maak pijl buttons
    arrow_width = 40
    arrow_height = 60
    car_display_x = WIDTH // 3
    car_display_y = HEIGHT - 120
    
    left_arrow = ArrowButton(car_display_x - 150, car_display_y + 30, arrow_width, arrow_height, "left")
    right_arrow = ArrowButton(car_display_x + 110, car_display_y + 30, arrow_width, arrow_height, "right")

    while running:
        clock.tick(60)
        screen.blit(garage_bg, (0,0))

        # Show current car type
        current_car = get_current_car_type()
        if current_car:
            car_title = font.render(f"{current_car.display_name} - Upgrades", True, WHITE)
        else:
            car_title = font.render("Garage - Upgrades", True, WHITE)
        screen.blit(car_title, (WIDTH//2 - car_title.get_width()//2, 20))

        # Show current money
        money_text = small_font.render(f"Money: ${state.money}", True, WHITE)
        screen.blit(money_text, (50, 70))

        # Upgrade menu on the right
        upgrade_area = pygame.Rect(WIDTH - 300, 100, 250, 400)
        pygame.draw.rect(screen, UPGRADE_BG, upgrade_area)
        pygame.draw.rect(screen, WHITE, upgrade_area, 2)

        if not upgrades:
            no_upgrades_text = small_font.render("No upgrades available", True, WHITE)
            screen.blit(no_upgrades_text, (upgrade_area.centerx - no_upgrades_text.get_width()//2, 
                                          upgrade_area.centery - no_upgrades_text.get_height()//2))
        else:
            y_offset = 0
            for upgrade in upgrades:
                item_rect = pygame.Rect(upgrade_area.x + 10, upgrade_area.y + 10 + y_offset + scroll_y, 230, 60)
                
                # Different colors based on status
                if upgrade.equipped:
                    pygame.draw.rect(screen, EQUIPPED_COLOR, item_rect)  # Green for equipped
                elif upgrade.purchased:
                    pygame.draw.rect(screen, PURCHASED_COLOR, item_rect)  # Blue for purchased but not equipped
                else:
                    pygame.draw.rect(screen, (80,80,80), item_rect)  # Gray for not purchased
                    
                if item_rect.collidepoint(pygame.mouse.get_pos()):
                    pygame.draw.rect(screen, (120,120,120), item_rect, 2)

                # Align bottom of image to bottom of the button
                img = upgrade.image_small
                img_x = item_rect.x + 5
                img_y = item_rect.bottom - img.get_height()-15
                screen.blit(img, (img_x, img_y))

                # Text based on status
                if upgrade.equipped:
                    text_color = (200, 255, 200)
                    status = ""
                elif upgrade.purchased:
                    text_color = (200, 200, 255)
                    status = ""
                elif state.money >= upgrade.price:
                    text_color = WHITE
                    status = ""
                else:
                    text_color = (150, 150, 150)
                    status = ""
                    
                text = small_font.render(f"{upgrade.name} - ${upgrade.price}{status}", True, text_color)
                screen.blit(text, (item_rect.x + 90, item_rect.y + 15))
                y_offset += 70

        # Car preview at bottom with arrows
        # Gebruik de huidige car image (met eventuele upgrades)
        car_display_image = pygame.transform.scale(car.image, (int(car.image.get_width()*2.8), int(car.image.get_height()*2.8)))
        car_display_rect = car_display_image.get_rect(midbottom=(car_display_x, car_display_y + 60))
        screen.blit(car_display_image, car_display_rect)
        
        # Update and draw arrows
        left_arrow.update(pygame.mouse.get_pos())
        right_arrow.update(pygame.mouse.get_pos())
        left_arrow.render(screen)
        right_arrow.render(screen)
        
        # Draw car name under the car
        if current_car:
            car_name_text = font.render(current_car.display_name, True, WHITE)
            screen.blit(car_name_text, (car_display_x - car_name_text.get_width()//2, car_display_y + 70))

        # Start level button
        btn_next = pygame.Rect(WIDTH - 200, HEIGHT - 80, 160, 50)
        color = BUTTON_HOVER if btn_next.collidepoint(pygame.mouse.get_pos()) else BUTTON
        pygame.draw.rect(screen, color, btn_next, border_radius=10)
        screen.blit(small_font.render("Start Level", True, WHITE), (btn_next.centerx - 50, btn_next.centery - 10))

        # Confirmation popup
        if confirmation_active and confirmation_upgrade:
            popup_rect = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 - 80, 300, 120)
            pygame.draw.rect(screen, (60,60,60), popup_rect)
            pygame.draw.rect(screen, WHITE, popup_rect, 2)
            
            if confirmation_action == 'purchase':
                msg = small_font.render(f"Purchase {confirmation_upgrade.name} for ${confirmation_upgrade.price}?", True, WHITE)
            elif confirmation_action == 'toggle_equip':
                if confirmation_upgrade.equipped:
                    msg = small_font.render(f"Unequip {confirmation_upgrade.name}?", True, WHITE)
                else:
                    msg = small_font.render(f"Equip {confirmation_upgrade.name}?", True, WHITE)
            
            screen.blit(msg, (popup_rect.centerx - msg.get_width()//2, popup_rect.y + 20))

            # Yes/No buttons
            btn_yes = pygame.Rect(popup_rect.x + 30, popup_rect.y + 60, 100, 40)
            color = BUTTON_HOVER if btn_yes.collidepoint(pygame.mouse.get_pos()) else BUTTON
            pygame.draw.rect(screen, color, btn_yes, border_radius=5)
            screen.blit(small_font.render("Yes", True, WHITE), (btn_yes.centerx - 20, btn_yes.centery - 10))

            btn_no = pygame.Rect(popup_rect.x + 170, popup_rect.y + 60, 100, 40)
            color = BUTTON_HOVER if btn_no.collidepoint(pygame.mouse.get_pos()) else BUTTON
            pygame.draw.rect(screen, color, btn_no, border_radius=5)
            screen.blit(small_font.render("No", True, WHITE), (btn_no.centerx - 15, btn_no.centery - 10))

        # Event handling
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                # SAVE ALL STATUS BEFORE EXITING
                save_all_upgrades_status()
                pygame.quit()
                sys.exit()
            elif e.type == pygame.MOUSEBUTTONDOWN:
                if confirmation_active:
                    if btn_yes.collidepoint(e.pos):
                        if confirmation_action == 'purchase':
                            if state.money >= confirmation_upgrade.price and not confirmation_upgrade.purchased:
                                state.money -= confirmation_upgrade.price
                                car.purchase_upgrade(confirmation_upgrade)
                        elif confirmation_action == 'toggle_equip':
                            # Toggle equip/unequip
                            if confirmation_upgrade.equipped:
                                car.apply_upgrade(confirmation_upgrade, equip=False)
                            else:
                                car.apply_upgrade(confirmation_upgrade, equip=True)
                        confirmation_active = False
                        confirmation_upgrade = None
                        confirmation_action = None
                    elif btn_no.collidepoint(e.pos):
                        confirmation_active = False
                        confirmation_upgrade = None
                        confirmation_action = None
                else:
                    if btn_next.collidepoint(e.pos):
                        # SAVE ALL STATUS BEFORE STARTING LEVEL
                        save_all_upgrades_status()
                        running = False
                    
                    # Check arrow clicks for car selection
                    if left_arrow.is_clicked(pygame.mouse.get_pos(), pygame.mouse.get_pressed()[0]):
                        # Go to previous car
                        current_index = (current_index - 1) % len(car_types_list)
                        set_current_car_type(car_types_list[current_index].name.lower())
                        print(f"Selected car: {car_types_list[current_index].name.lower()}")
                        # Reset car with new selection - gebruik de nieuwe auto
                        car.__init__(apply_upgrades_now=False)
                        # Load upgrades for new car
                        load_upgrades()
                        # Now apply equipped upgrades
                        car.apply_equipped_upgrades()
                        upgrades = load_upgrades()
                    
                    elif right_arrow.is_clicked(pygame.mouse.get_pos(), pygame.mouse.get_pressed()[0]):
                        # Go to next car
                        current_index = (current_index + 1) % len(car_types_list)
                        set_current_car_type(car_types_list[current_index].name.lower())
                        print(f"Selected car: {car_types_list[current_index].name.lower()}")
                        # Reset car with new selection - gebruik de nieuwe auto
                        car.__init__(apply_upgrades_now=False)
                        # Load upgrades for new car
                        load_upgrades()
                        # Now apply equipped upgrades
                        car.apply_equipped_upgrades()
                        upgrades = load_upgrades()
                    
                    # Check upgrade clicks
                    if upgrades:
                        y_offset_check = 0
                        for upgrade in upgrades:
                            item_rect_check = pygame.Rect(upgrade_area.x + 10, upgrade_area.y + 10 + y_offset_check + scroll_y, 230, 60)
                            if item_rect_check.collidepoint(e.pos):
                                if not upgrade.purchased:
                                    # Not purchased yet - show purchase confirmation
                                    if state.money >= upgrade.price:
                                        confirmation_active = True
                                        confirmation_upgrade = upgrade
                                        confirmation_action = 'purchase'
                                else:
                                    # Already purchased - toggle equip/unequip
                                    confirmation_active = True
                                    confirmation_upgrade = upgrade
                                    confirmation_action = 'toggle_equip'
                            y_offset_check += 70
            elif e.type == pygame.MOUSEWHEEL:
                if upgrades:
                    scroll_y += e.y * scroll_speed
                    scroll_y = max(min(scroll_y, 0), -max(0, len(upgrades)*70 - upgrade_area.height))

        pygame.display.flip()
