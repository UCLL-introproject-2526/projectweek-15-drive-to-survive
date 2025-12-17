import os
import json
import pygame

ALL_CAR_TYPES = {}
current_car_type = "default"

class CarType:
    def __init__(self, folder):
        self.folder = folder
        self.name = os.path.basename(folder)

        info_file = os.path.join(folder, "info.json")
        if os.path.exists(info_file):
            with open(info_file, "r") as f:
                data = json.load(f)
            self.display_name = data.get("name", self.name)
            is_def = data.get("is_default", False)
            if isinstance(is_def, bool):
                self.is_default = is_def
            else:
                self.is_default = str(is_def).lower() == "true"
            self.author = data.get("author", "")
            self.version = data.get("version", "1.0.0")
            self.base_image_path = data.get("base_image", "image.png")
        else:
            self.display_name = self.name.capitalize()
            self.is_default = False
            self.author = ""
            self.version = "1.0.0"
            self.base_image_path = "image.png"

        img_file = os.path.join(folder, self.base_image_path)
        if os.path.exists(img_file):
            try:
                self.image = pygame.image.load(img_file).convert_alpha()
                self.image_small = pygame.transform.scale(self.image, (120, 80))
            except Exception:
                # fallback
                self.image = pygame.Surface((200, 100), pygame.SRCALPHA)
                pygame.draw.rect(self.image, (100, 100, 200), (0, 40, 200, 60))
                self.image_small = pygame.transform.scale(self.image, (120, 80))
        else:
            self.image = pygame.Surface((200, 100), pygame.SRCALPHA)
            pygame.draw.rect(self.image, (100, 100, 200), (0, 40, 200, 60))
            self.image_small = pygame.transform.scale(self.image, (120, 80))

        # upgrades for this car will be loaded by upgrades module as needed

def load_car_types(cars_folder="assets/cars"):
    global ALL_CAR_TYPES, current_car_type
    ALL_CAR_TYPES.clear()
    car_types = []
    if not os.path.exists(cars_folder):
        print(f"Warning: Cars folder '{cars_folder}' not found!")
        return car_types

    for folder_name in os.listdir(cars_folder):
        folder_path = os.path.join(cars_folder, folder_name)
        if os.path.isdir(folder_path):
            try:
                ct = CarType(folder_path)
                car_types.append(ct)
                ALL_CAR_TYPES[ct.name.lower()] = ct
                print(f"  Loaded car type: {ct.name} (default: {ct.is_default})")
            except Exception as e:
                print(f"Error loading car type from {folder_path}: {e}")

    # pick default
    for name, ct in ALL_CAR_TYPES.items():
        if ct.is_default:
            current_car_type = name
            break

    # If no default was marked, fall back to the first available car type
    if current_car_type not in ALL_CAR_TYPES and car_types:
        current_car_type = car_types[0].name.lower()

    print(f"Total cars loaded: {len(car_types)}")
    return car_types

def get_current_car_type():
    return ALL_CAR_TYPES.get(current_car_type)

def get_car_type_list():
    return list(ALL_CAR_TYPES.values())

def set_current_car_type(name):
    global current_car_type
    current_car_type = name
