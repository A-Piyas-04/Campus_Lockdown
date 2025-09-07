# Campus Lockdown - Dark Campus Edition 🏫🔦

A thrilling 2D top-down exploration game built with Python and Pygame, where you navigate a dark campus environment using limited visibility and a flashlight to survive and explore.

## 🎮 Game Overview

Campus Lockdown is an atmospheric exploration game set in a mysterious campus during a lockdown scenario. Players must navigate through various campus buildings including libraries, cafeterias, dormitories, and parking areas while managing limited visibility in a dark environment.

## ✨ Features

### 🌟 Core Gameplay
- **Dark Atmosphere**: Navigate through a campus with limited visibility
- **Flashlight System**: Toggle flashlight to extend your vision radius
- **Smooth Movement**: Grid-based movement with smooth animations
- **Multiple Buildings**: Explore library, cafeteria, dormitory, and parking areas
- **Map Transitions**: Seamlessly move between outdoor campus and interior locations

### 🎒 Inventory & Items
- **Collectible Items**: Find health potions, magic scrolls, and golden keys
- **Inventory Management**: Track collected items with a visual inventory system
- **Item Descriptions**: Each item has unique properties and descriptions

### 🗺️ Map System
- **Large Campus Map**: Expansive 70x50 tile campus environment
- **Multiple Interior Maps**: Detailed interior layouts for each building
- **JSON-Based Maps**: Easy-to-edit map files for customization
- **Diverse Environments**: Grass, water features, pathways, and building interiors

### 🎨 Visual Features
- **Tile-Based Graphics**: Clean, colorful tile-based world
- **Custom Player Sprite**: SVG-based knight character with helmet and sword
- **Dynamic Lighting**: Darkness overlay with flashlight illumination
- **Rich Color Palette**: Distinct colors for different tile types and environments

## 🚀 Getting Started

### Prerequisites
- Python 3.7 or higher
- Pygame library

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd "Campus Lockdown"
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the game**:
   ```bash
   python main.py
   ```

## 🎮 Controls

- **Arrow Keys / WASD**: Move player character
- **F Key**: Toggle flashlight on/off
- **I Key**: Toggle inventory display
- **ESC**: Exit game

## 🏗️ Project Structure

```
Campus Lockdown/
├── main.py                 # Game entry point
├── requirements.txt        # Python dependencies
├── player_sprite.svg      # Custom player character sprite
├── classes/               # Game logic modules
│   ├── game.py           # Main game class and loop
│   ├── player.py         # Player character logic
│   ├── map.py            # Map loading and management
│   ├── tiles.py          # Tile system and definitions
│   ├── camera.py         # Camera and viewport system
│   └── items.py          # Item and inventory system
├── maps/                 # JSON map files
│   ├── campus_map.json   # Main outdoor campus
│   ├── library_map.json  # Library interior
│   ├── cafeteria_map.json # Cafeteria interior
│   ├── dormitory_map.json # Dormitory interior
│   └── parking_map.json  # Parking area
├── config/               # Configuration files
└── utils/                # Utility functions
```

## 🎯 Game Mechanics

### Visibility System
- **Base Visibility**: Limited radius around player in dark environment
- **Flashlight Mode**: Extended visibility when flashlight is active
- **Dynamic Darkness**: Overlay system creates atmospheric lighting

### Building Exploration
- **Door System**: Enter buildings through designated door tiles
- **Interior Navigation**: Each building has unique interior layouts
- **Return Mechanism**: Exit buildings to return to main campus

### Item Collection
- **Health Potions**: Restore player health (red items)
- **Magic Scrolls**: Contain ancient knowledge (blue items)
- **Golden Keys**: Open locked doors and chests (gold items)

## 🛠️ Technical Details

### Built With
- **Python 3.x**: Core programming language
- **Pygame 2.5.2**: Game development framework
- **JSON**: Map data storage format
- **SVG**: Vector graphics for sprites

### Key Classes
- `Game`: Main game loop and state management
- `Player`: Character movement and animation
- `Map`: Tile-based world loading and rendering
- `Camera`: Viewport and scrolling system
- `Inventory`: Item collection and management
- `Tile`: Individual map tile properties

### Performance Features
- **Efficient Rendering**: Only visible tiles are drawn
- **Smooth Animation**: Interpolated movement between grid positions
- **Memory Management**: Proper resource cleanup and optimization

## 🎨 Customization

### Adding New Maps
1. Create a new JSON file in the `maps/` directory
2. Follow the existing map format with tile character mappings
3. Define spawn points and map dimensions
4. Add appropriate door connections

### Tile Types
The game supports various tile types including:
- **Terrain**: Grass, water, pathways, trees
- **Buildings**: Walls, doors, interior furniture
- **Interactive**: Different door types for building transitions

## 🐛 Troubleshooting

### Common Issues
- **Map Loading Errors**: Ensure JSON map files are properly formatted
- **Performance Issues**: Reduce map size or optimize tile rendering
- **Movement Problems**: Check collision detection and walkable tile definitions

## 🤝 Contributing

Contributions are welcome! Please feel free to:
- Report bugs and issues
- Suggest new features
- Submit pull requests
- Create new maps or sprites

## 📝 License

This project is open source. Please check the license file for details.

## 🎮 Future Enhancements

- **Sound Effects**: Ambient audio and sound feedback
- **NPCs**: Interactive characters throughout the campus
- **Quests**: Objective-based gameplay missions
- **Multiplayer**: Network-based cooperative exploration
- **Save System**: Progress persistence between sessions
- **Mini-Map**: Overview navigation aid

---

**Enjoy exploring the mysterious Campus Lockdown! 🔦🏫**