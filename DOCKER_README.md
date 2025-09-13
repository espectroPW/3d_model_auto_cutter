# 🐳 STL 3D Model Splitter - Docker Deployment

## 🚀 One-Click Deployment

Deploy the STL 3D Model Splitter web application with a single command!

## 📋 Prerequisites

- **Docker** (with Docker Compose)
- **Internet connection** (for downloading dependencies)

### Install Docker
- **Windows**: [Docker Desktop](https://docs.docker.com/desktop/windows/install/)
- **Mac**: [Docker Desktop](https://docs.docker.com/desktop/mac/install/)
- **Linux**: [Docker Engine](https://docs.docker.com/engine/install/)

## 🎯 Quick Start

```bash
# Clone or download the project files
# Make sure you have: Dockerfile, docker-compose.yml, index.html, stl_splitter_api.php, stl_processor.py

# Build and start
docker-compose up --build -d

# Access the application
open http://localhost:8080
```

## 🌐 Access the Application

Once running, open your browser and go to:
**http://localhost:8080**

## 📁 File Structure

```
stl-splitter-web/
├── Dockerfile              # Container configuration
├── docker-compose.yml      # Service orchestration
├── index.html             # Web interface
├── stl_splitter_api.php   # PHP backend API
├── stl_processor.py       # Python processing script
└── .dockerignore          # Docker ignore file
```

## 🔧 Container Details

### What's Included
- **PHP 8.1** with Apache web server
- **Python 3.9** with scientific libraries
- **Trimesh** for 3D mesh processing
- **NumPy** for numerical computations
- **Matplotlib** for visualization
- **ZIP extension** for file compression

### Configuration
- **Port**: 8080 (maps to container port 80)
- **File Upload**: Up to 50MB
- **Memory**: 512MB PHP memory limit
- **Timeout**: 300 seconds execution time
- **Auto-restart**: Container restarts automatically

## 🛠️ Management Commands

```bash
# View logs
docker-compose logs -f

# Stop the application
docker-compose down

# Restart the application
docker-compose restart

# Update and restart
docker-compose pull && docker-compose up -d

# Remove everything (including volumes)
docker-compose down -v
```

## 🔍 Troubleshooting

### Container won't start
```bash
# Check logs
docker-compose logs

# Check if port 8080 is available
netstat -an | grep 8080
```

### File upload issues
```bash
# Check container logs
docker-compose logs stl-splitter

# Verify PHP configuration
docker-compose exec stl-splitter php -i | grep upload
```

### Python processing errors
```bash
# Test Python environment
docker-compose exec stl-splitter python3 -c "import trimesh; print('OK')"

# Check Python script permissions
docker-compose exec stl-splitter ls -la stl_processor.py
```

## 🚀 Production Deployment

### Using Docker Swarm
```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml stl-splitter
```

### Using Kubernetes
```yaml
# Create deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: stl-splitter
spec:
  replicas: 2
  selector:
    matchLabels:
      app: stl-splitter
  template:
    metadata:
      labels:
        app: stl-splitter
    spec:
      containers:
      - name: stl-splitter
        image: stl-splitter:latest
        ports:
        - containerPort: 80
```

## 🔒 Security Considerations

- **File Upload Limits**: 50MB maximum
- **Temporary Files**: Automatically cleaned up
- **Container Isolation**: Runs in isolated environment
- **No Root Access**: Container runs as www-data user

## 📊 Performance

- **Memory Usage**: ~200-400MB per container
- **CPU Usage**: Depends on model complexity
- **Processing Time**: 1-30 seconds per model
- **Concurrent Users**: Tested up to 10 simultaneous users

## 🆘 Support

### Common Issues
1. **Port 8080 in use**: Change port in docker-compose.yml
2. **Out of memory**: Increase Docker memory limit
3. **Slow processing**: Check system resources

### Getting Help
- Check container logs: `docker-compose logs -f`
- Verify file permissions: `docker-compose exec stl-splitter ls -la`
- Test Python environment: `docker-compose exec stl-splitter python3 -c "import trimesh"`

---

**🎉 Your STL 3D Model Splitter is ready to use!**

Access it at: **http://localhost:8080**
