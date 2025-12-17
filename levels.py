"""
Level System for Zombie Car Game
Manages level progression with increasing difficulty
"""

class LevelConfig:
    """Configuration for a single level"""
    def __init__(self, level_number, distance_required, zombie_count, zombie_health_multiplier, 
                 zombie_damage_multiplier, money_reward, description, terrain_difficulty):
        self.level_number = level_number
        self.distance_required = distance_required  # Distance needed to complete level
        self.zombie_count = zombie_count  # Base number of zombies
        self.zombie_health_multiplier = zombie_health_multiplier  # Health scaling
        self.zombie_damage_multiplier = zombie_damage_multiplier  # Damage scaling
        self.money_reward = money_reward  # Bonus money for completing level
        self.description = description  # Level description
        self.terrain_difficulty = terrain_difficulty  # 1-5: terrain roughness

class LevelManager:
    """Manages level progression and difficulty scaling"""
    
    def __init__(self):
        self.current_level = 1
        self.levels = self._initialize_levels()
    
    def _initialize_levels(self):
        """Initialize all level configurations"""
        levels = {
            1: LevelConfig(
                level_number=1,
                distance_required=5000,
                zombie_count=6,
                zombie_health_multiplier=1.0,
                zombie_damage_multiplier=1.0,
                money_reward=100,
                description="Tutorial Zone - Learn the basics",
                terrain_difficulty=1
            ),
            2: LevelConfig(
                level_number=2,
                distance_required=7000,
                zombie_count=8,
                zombie_health_multiplier=1.2,
                zombie_damage_multiplier=1.1,
                money_reward=200,
                description="The Suburbs - More zombies ahead",
                terrain_difficulty=2
            ),
            3: LevelConfig(
                level_number=3,
                distance_required=8000,
                zombie_count=10,
                zombie_health_multiplier=1.4,
                zombie_damage_multiplier=1.2,
                money_reward=300,
                description="City Outskirts - Increasing threat",
                terrain_difficulty=2
            ),
            4: LevelConfig(
                level_number=4,
                distance_required=9000,
                zombie_count=12,
                zombie_health_multiplier=1.6,
                zombie_damage_multiplier=1.3,
                money_reward=400,
                description="Downtown - Heavy resistance",
                terrain_difficulty=3
            ),
            5: LevelConfig(
                level_number=5,
                distance_required=10000,
                zombie_count=15,
                zombie_health_multiplier=1.8,
                zombie_damage_multiplier=1.4,
                money_reward=500,
                description="Industrial Zone - Tough zombies",
                terrain_difficulty=3
            ),
            6: LevelConfig(
                level_number=6,
                distance_required=11000,
                zombie_count=18,
                zombie_health_multiplier=2.0,
                zombie_damage_multiplier=1.5,
                money_reward=600,
                description="The Quarantine - No mercy",
                terrain_difficulty=4
            ),
            7: LevelConfig(
                level_number=7,
                distance_required=12000,
                zombie_count=20,
                zombie_health_multiplier=2.2,
                zombie_damage_multiplier=1.6,
                money_reward=750,
                description="Military Base - Elite zombies",
                terrain_difficulty=4
            ),
            8: LevelConfig(
                level_number=8,
                distance_required=13000,
                zombie_count=22,
                zombie_health_multiplier=2.5,
                zombie_damage_multiplier=1.7,
                money_reward=900,
                description="Ground Zero - Maximum threat",
                terrain_difficulty=5
            ),
            9: LevelConfig(
                level_number=9,
                distance_required=14000,
                zombie_count=25,
                zombie_health_multiplier=2.8,
                zombie_damage_multiplier=1.8,
                money_reward=1100,
                description="The Horde - Survive the swarm",
                terrain_difficulty=5
            ),
            10: LevelConfig(
                level_number=10,
                distance_required=15000,
                zombie_count=30,
                zombie_health_multiplier=3.0,
                zombie_damage_multiplier=2.0,
                money_reward=1500,
                description="Final Stand - Ultimate challenge",
                terrain_difficulty=5
            )
        }
        
        # For levels beyond 10, generate dynamically with increasing difficulty
        for level_num in range(11, 51):  # Support up to level 50
            levels[level_num] = LevelConfig(
                level_number=level_num,
                distance_required=15000 + (level_num - 10) * 500,
                zombie_count=30 + (level_num - 10) * 2,
                zombie_health_multiplier=3.0 + (level_num - 10) * 0.15,
                zombie_damage_multiplier=2.0 + (level_num - 10) * 0.05,
                money_reward=1500 + (level_num - 10) * 200,
                description=f"Endless Mode - Level {level_num}",
                terrain_difficulty=5
            )
        
        return levels
    
    def get_level_config(self, level_number):
        """Get configuration for a specific level"""
        if level_number in self.levels:
            return self.levels[level_number]
        else:
            # Return a dynamically generated level for very high levels
            return LevelConfig(
                level_number=level_number,
                distance_required=15000 + (level_number - 10) * 500,
                zombie_count=min(50, 30 + (level_number - 10) * 2),
                zombie_health_multiplier=3.0 + (level_number - 10) * 0.15,
                zombie_damage_multiplier=min(3.0, 2.0 + (level_number - 10) * 0.05),
                money_reward=1500 + (level_number - 10) * 200,
                description=f"Endless Mode - Level {level_number}",
                terrain_difficulty=5
            )
    
    def get_current_level_config(self):
        """Get configuration for the current level"""
        return self.get_level_config(self.current_level)
    
    def advance_level(self):
        """Advance to the next level"""
        self.current_level += 1
        return self.get_current_level_config()
    
    def reset_to_level(self, level_number):
        """Reset to a specific level"""
        self.current_level = level_number
        return self.get_current_level_config()
    
    def get_zombie_spawn_positions(self, level_number):
        """Generate zombie spawn positions for a level"""
        import random
        config = self.get_level_config(level_number)
        positions = []
        
        # Spread zombies across the level distance
        segment_size = config.distance_required // (config.zombie_count + 1)
        
        for i in range(config.zombie_count):
            # Add some randomness to spawn positions
            base_position = segment_size * (i + 1)
            random_offset = random.randint(-segment_size // 3, segment_size // 3)
            position = max(500, base_position + random_offset)  # Ensure not too close to start
            positions.append(position)
        
        return positions
    
    def get_zombie_health(self, level_number, base_health):
        """Calculate zombie health for a level"""
        config = self.get_level_config(level_number)
        return base_health * config.zombie_health_multiplier
    
    def get_zombie_damage(self, level_number, base_damage):
        """Calculate zombie damage for a level"""
        config = self.get_level_config(level_number)
        return base_damage * config.zombie_damage_multiplier
    
    def get_level_info_text(self, level_number):
        """Get formatted text for level information"""
        config = self.get_level_config(level_number)
        return [
            f"LEVEL {config.level_number}",
            config.description,
            f"Distance Required: {config.distance_required}m",
            f"Zombies: {config.zombie_count}",
            f"Reward: ${config.money_reward}"
        ]
    
    def is_level_complete(self, distance, level_number):
        """Check if the level is complete based on distance traveled"""
        config = self.get_level_config(level_number)
        return distance >= config.distance_required
    
    def get_completion_reward(self, level_number):
        """Get the reward for completing a level"""
        config = self.get_level_config(level_number)
        return config.money_reward

# Global level manager instance
_level_manager = None

def get_level_manager():
    """Get or create the global level manager"""
    global _level_manager
    if _level_manager is None:
        _level_manager = LevelManager()
    return _level_manager

def reset_level_manager():
    """Reset the level manager to start from level 1"""
    global _level_manager
    _level_manager = LevelManager()
    return _level_manager
