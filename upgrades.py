import pygame
import os
import json

class Upgrade:
    def __init__(self, folder):
        info_file = os.path.join(folder, "info.json")
        with open(info_file, "r") as f:
            data = json.load(f)
        self.name = data.get("name")
        self.car_damage = data.get("car_damage", 0)
        self.damage_reduction = data.get("damage_reduction", 0)
        self.speed_increase = data.get("speed_increase", 0)
        self.price = data.get("price", 50)
        img_file = os.path.join(folder, "image.png")
        self.image = pygame.image.load(img_file).convert_alpha()
        self.image_small = pygame.transform.scale(self.image, (80, 40))
        self.purchased = False
        self.equipped = False

def load_upgrades():
    """Load all upgrades from the upgrades folder"""
    upgrades_list = []
    upgrades_folder = "upgrades"
    if not os.path.exists(upgrades_folder):
        return upgrades_list
    for folder_name in os.listdir(upgrades_folder):
        folder_path = os.path.join(upgrades_folder, folder_name)
        if os.path.isdir(folder_path):
            upgrades_list.append(Upgrade(folder_path))
    return upgrades_list