# STL 3D Model Splitter - Web Installation Guide

## 🌐 Web Application Setup

This guide will help you set up the STL 3D Model Splitter as a web application.

## 🐳 Docker Installation (Recommended)

The easiest way to run the STL Splitter is using Docker. Everything is pre-configured!

### Quick Start with Docker

```bash
# Build and run
docker-compose up --build -d

# Access at http://localhost:8080
```

### Docker Features
- ✅ **Pre-configured**: PHP + Python + Trimesh
- ✅ **No installation**: Everything included
- ✅ **Portable**: Works on any system with Docker
- ✅ **Isolated**: No conflicts with system packages
- ✅ **Auto-restart**: Container restarts automatically

## 📋 Requirements

### Server Requirements
- **PHP 7.4+** with extensions:
  - `zip` extension
  - `fileinfo` extension
  - `json` extension
- **Python 3.7+** with packages:
  - `trimesh`
  - `numpy`
  - `matplotlib`
- **Web Server** (Apache/Nginx)
- **File Upload Limit**: 50MB minimum

### Python Dependencies
```bash
pip install trimesh numpy matplotlib
```

## 🛠️ Installation Steps

### 1. Upload Files
Upload these files to your web server:
- `index.html` - Main web interface
- `stl_splitter_api.php` - PHP backend API
- `stl_processor.py` - Python processing script

### 2. Set Permissions
```bash
chmod 755 stl_processor.py
chmod 644 index.html
chmod 644 stl_splitter_api.php
```

### 3. Configure PHP
Add to your `php.ini` or `.htaccess`:
```ini
upload_max_filesize = 50M
post_max_size = 50M
max_execution_time = 300
memory_limit = 512M
```

### 4. Test Installation
1. Open `index.html` in your browser
2. Upload a small STL file
3. Click "Split STL Model"
4. Download the resulting ZIP file

## 🔧 Configuration

### File Paths
Make sure the Python script path is correct in `stl_splitter_api.php`:
```php
$pythonScript = __DIR__ . '/stl_processor.py';
```

### Security Considerations
- Restrict access to `stl_processor.py` via web server
- Set up proper file upload validation
- Consider rate limiting for API endpoints
- Use HTTPS in production

## 🎨 Features

### Web Interface Features
- **Modern Design**: Clean, responsive interface
- **Drag & Drop**: Easy file upload
- **Quick Presets**: Ender 3, Prusa i3, Mini printer settings
- **Real-time Preview**: Shows split configuration
- **Progress Tracking**: Visual progress bar during processing
- **ZIP Download**: Automatic ZIP file creation and download

### Backend Features
- **PHP API**: RESTful API for file processing
- **Python Processing**: Same algorithms as desktop version
- **Error Handling**: Comprehensive error messages
- **File Validation**: STL file type and size validation
- **Temporary Files**: Automatic cleanup of temporary files

## 🚀 Usage

### For Users
1. **Upload STL**: Drag and drop or click to select STL file
2. **Set Dimensions**: Use presets or enter custom build volume
3. **Configure Options**: Enable model flipping if needed
4. **Process**: Click "Split STL Model" button
5. **Download**: Get ZIP file with all split parts

### For Developers
The web API accepts POST requests to `stl_splitter_api.php`:
```javascript
const formData = new FormData();
formData.append('stl_file', file);
formData.append('max_x', '220');
formData.append('max_y', '220');
formData.append('max_z', '250');
formData.append('flip_model', 'false');

const response = await fetch('stl_splitter_api.php', {
    method: 'POST',
    body: formData
});
```

## 🐛 Troubleshooting

### Common Issues

**"Python processing failed"**
- Check Python path in PHP script
- Verify trimesh library is installed
- Check file permissions

**"File too large"**
- Increase PHP upload limits
- Check server memory limits
- Consider file size optimization

**"ZIP extension not available"**
- Install PHP ZIP extension
- Restart web server

**"Cannot create temporary directory"**
- Check write permissions
- Verify disk space
- Check temp directory path

### Performance Tips
- Use SSD storage for better I/O performance
- Increase PHP memory limit for large files
- Consider background processing for very large models
- Implement caching for repeated requests

## 🔒 Security Notes

- Validate all uploaded files
- Sanitize file names
- Limit file upload size
- Use HTTPS in production
- Implement rate limiting
- Regular security updates

## 📞 Support

For issues with the web version:
1. Check server logs
2. Verify Python dependencies
3. Test with small STL files first
4. Check file permissions

---

**Ready to split STL models online!** 🎉
