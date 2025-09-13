# 🔧 STL 3D Model Splitter

> **Professional 3D model splitting application for 3D printing**

Automatically cuts large STL models into smaller parts that fit within your 3D printer's build volume. Available as both **desktop application** and **web service**.

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://python.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![GUI](https://img.shields.io/badge/GUI-Tkinter-orange.svg)](https://docs.python.org/3/library/tkinter.html)
[![Web](https://img.shields.io/badge/Web-PHP%20%2B%20JS-777BB4.svg)](https://php.net)

## 📸 Demo

### Desktop Application
- **Interactive 3D Preview** with real-time split visualization
- **Animated Cutting Process** with part highlighting
- **Progress Tracking** with detailed status updates

### Web Application
- **Upload & Process** STL files directly in browser
- **Download ZIP** with all split parts
- **Responsive Design** works on any device

## ⚡ Quick Start

### 🌐 Web Version (Recommended)
```bash
git clone https://github.com/yourusername/3d-model-auto-cutter.git
cd 3d-model-auto-cutter
docker-compose up --build -d
# Open http://localhost:8080
```

### 🖥️ Desktop Version
```bash
git clone https://github.com/yourusername/3d-model-auto-cutter.git
cd 3d-model-auto-cutter
pip install trimesh numpy matplotlib
python cutter.py
```

## 🛠️ Technologies

### Desktop Application
- **Python 3.7+** - Core language
- **Tkinter** - GUI framework
- **Trimesh** - 3D mesh processing
- **NumPy** - Numerical computations
- **Matplotlib** - 3D visualization

### Web Application
- **PHP 8.1** - Backend API
- **JavaScript** - Frontend interface
- **Docker** - Containerization
- **Apache** - Web server
- **Python** - Processing engine

## 🚀 Features

### ✂️ Smart Model Splitting
- **Automatic Detection**: Analyzes model dimensions and printer build volume
- **Intelligent Cutting**: Uses Trimesh library for precise, watertight cuts
- **Fallback Support**: Handles non-watertight models with vertex filtering
- **Real-time Preview**: Live 3D visualization of split configuration

### 🖨️ 3D Printer Support
- **Quick Presets**: Ender 3, Prusa i3, Monoprice Mini
- **Custom Dimensions**: Set any build volume size
- **Model Orientation**: 180° flip option for better fitting

### 🎯 Advanced Visualization
- **3D Model Preview**: Interactive 3D view with rotation/zoom
- **Split Animation**: Real-time cutting progress with part highlighting
- **Grid Visualization**: Shows all split boundaries with 3D model overlay
- **Model + Grid View**: Semi-transparent model with colored split boundaries
- **Part Highlighting**: Bright green highlighting of current processing part
- **Multiple Views**: Isometric, Top, and Side view options

### ⚡ Performance & UX
- **Fast Processing**: Optimized algorithms for large models
- **Progress Tracking**: Real-time progress bar and status updates
- **Threaded Operations**: Non-blocking GUI during processing
- **Loading Feedback**: Progress bar shows during model loading
- **Fast Animation**: 0.01s per part for quick visual feedback
- **Auto-save**: Automatically saves parts to selected directory

## 📋 Requirements

- Python 3.7 or higher
- Required packages:
  ```bash
  pip install trimesh numpy matplotlib tkinter
  ```

## 🔧 Configuration

### Port Configuration (Web Version)
Edit `docker-compose.yml` to change the port:
```yaml
ports:
  - "3000:80"  # Change 8080 to your preferred port
```

**Popular ports:** `80`, `3000`, `5000`, `8000`

After changing port:
```bash
docker-compose down
docker-compose up --build -d
```

## 🎮 How to Use

### 1. Load Your Model
- Click **"📁"** next to STL field to browse for your STL file
- Model information will automatically display
- 3D preview will show your model

### 2. Configure Printer Settings
- **Quick Setup**: Use preset buttons (Ender3, Prusa, Mini)
- **Custom Setup**: Manually set X, Y, Z dimensions
- **Orientation**: Check "Flip 180° (X)" if needed

### 3. Preview Split Configuration
- Split preview updates automatically as you change settings
- Shows how many parts will be created
- Displays estimated dimensions for each part
- Click "📐 Show Split" to see 3D model with split grid overlay

### 4. Set Output Directory
- Click **"📁"** next to Output field
- Choose where to save the split parts

### 5. Start Splitting
- Click **"✂️ Split Model"** button
- Watch the real-time animation showing each part being processed
- See 3D model with colored split grid and highlighted current part
- Progress bar shows completion status
- Fast 0.01s animation per part for quick feedback

## 📊 Supported File Formats

- **Input**: STL files (both ASCII and Binary)
- **Output**: STL files (Binary format for smaller file sizes)

## 🔧 Technical Details

### Splitting Algorithm
1. **Primary Method**: Uses `trimesh.intersection()` for watertight models
   - Creates precise cuts with proper mesh topology
   - Maintains model integrity and surface quality

2. **Fallback Method**: Vertex filtering for non-watertight models
   - Filters triangles within specified bounds
   - Reindexes vertices for proper STL export
   - Ensures compatibility with all model types

### Performance Optimizations
- **Threaded Processing**: GUI remains responsive during operations
- **Debounced Updates**: Prevents excessive preview recalculations
- **Memory Efficient**: Processes models in chunks to handle large files
- **Fast Animation**: 0.01s per part for quick visual feedback
- **Model Subsampling**: Large models simplified for smooth visualization
- **Thread-Safe GUI**: All updates properly synchronized with main thread

## 🎨 User Interface

### Left Panel - Controls
- **📁 Files**: STL input and output directory selection
- **📊 Model**: Displays model dimensions, triangle count, and watertight status
- **🖨️ Printer**: Build volume settings and presets
- **✂️ Split**: Shows split configuration and part count
- **Progress**: Real-time progress bar and status updates

### Right Panel - 3D Visualization
- **🎯 3D Preview**: Interactive model visualization
- **Controls**: Refresh, Show Split, and view options (Isometric, Top, Side)
- **Animation**: Real-time cutting progress with part highlighting
- **Model + Grid**: Semi-transparent model with colored split boundaries
- **Part Labels**: P1, P2, P3... with highlighting for current part

## 🎬 Animation & Visualization

### Split Animation Sequence
1. **Initial Grid**: Shows complete split configuration with 3D model overlay
2. **Part Processing**: Each part highlighted in bright green with star (*)
3. **Real-time Progress**: Progress bar and status updates
4. **Fast Feedback**: 0.01s per part for quick visual response

### Visual Elements
- **Semi-transparent Model**: Light gray overlay (30% opacity)
- **Colored Grid**: Each part has unique color (red, blue, green, etc.)
- **Highlighted Part**: Bright lime green with thick border
- **Part Labels**: P1, P2, P3... with star (*) for current part
- **Bounding Box**: Black outline showing model boundaries

## 📈 Example Usage

### Large Model Splitting
```
Input: Large decorative vase (200×200×300 mm)
Printer: Ender 3 (220×220×250 mm)
Result: 8 parts automatically created
Animation: 0.08s total (8 parts × 0.01s)
```

### Complex Geometry
```
Input: Mechanical part with overhangs
Printer: Prusa i3 (250×210×210 mm)
Result: 12 parts with proper support considerations
Animation: 0.12s total (12 parts × 0.01s)
```

## 🐛 Troubleshooting

### Common Issues

**"Not all meshes are volumes!" Error**
- This is normal for non-watertight models
- The application automatically uses fallback method
- Parts will still be created successfully

**Model Not Loading**
- Ensure STL file is not corrupted
- Check file path doesn't contain special characters
- Try with a different STL file
- Progress bar should show "Loading model..." during load

**Animation Not Working**
- Ensure model is loaded before splitting
- Check that split preview shows parts
- Try clicking "📐 Show Split" to test visualization

**Slow Performance**
- Large models (>10k triangles) may take longer
- Close other applications to free up memory
- Consider reducing model complexity in your CAD software

### Performance Tips
- Use binary STL files for faster loading
- Ensure models are properly oriented before splitting
- Close unnecessary applications during processing
- Large models are automatically subsampled for smooth visualization
- Animation speed is optimized at 0.01s per part

## 🔄 Version History

### v2.0 (Current)
- ✅ Trimesh integration for precise cutting
- ✅ Real-time 3D visualization and animation
- ✅ Fallback support for non-watertight models
- ✅ Optimized UI with compact layout
- ✅ Fast animation system (0.01s per part)
- ✅ Progress tracking and status updates
- ✅ Model + Grid visualization with semi-transparent overlay
- ✅ Part highlighting with bright green current part
- ✅ Thread-safe GUI updates for loading feedback
- ✅ Model subsampling for smooth performance

### v1.0
- Basic STL splitting functionality
- Simple GUI interface
- Vertex filtering method only

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **[Trimesh](https://github.com/mikedh/trimesh)** - Robust 3D mesh processing
- **[Matplotlib](https://matplotlib.org/)** - 3D visualization
- **[Docker](https://docker.com/)** - Containerization platform

## 📞 Support

- 🐛 **Bug Reports**: [Create an issue](https://github.com/yourusername/3d-model-auto-cutter/issues)
- 💡 **Feature Requests**: [Start a discussion](https://github.com/yourusername/3d-model-auto-cutter/discussions)
- 📖 **Documentation**: Check the troubleshooting section above

---

<div align="center">

**Made with ❤️ for the 3D printing community**

[⭐ Star this repo](https://github.com/yourusername/3d-model-auto-cutter) • [🐛 Report Bug](https://github.com/yourusername/3d-model-auto-cutter/issues) • [💡 Request Feature](https://github.com/yourusername/3d-model-auto-cutter/discussions)

</div>
