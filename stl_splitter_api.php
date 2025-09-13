<?php
/**
 * STL 3D Model Splitter - Web API
 * Backend PHP script for processing STL files and creating split parts
 */

header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, GET, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

// Handle preflight requests
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    exit(0);
}

// Check if required extensions are available
if (!extension_loaded('zip')) {
    http_response_code(500);
    echo json_encode(['error' => 'ZIP extension not available']);
    exit;
}

class STLSplitter {
    private $tempDir;
    private $maxFileSize = 50 * 1024 * 1024; // 50MB
    
    public function __construct() {
        $this->tempDir = sys_get_temp_dir() . '/stl_splitter_' . uniqid();
        if (!mkdir($this->tempDir, 0755, true)) {
            throw new Exception('Cannot create temporary directory');
        }
    }
    
    public function __destruct() {
        $this->cleanup();
    }
    
    private function cleanup() {
        if (is_dir($this->tempDir)) {
            $this->deleteDirectory($this->tempDir);
        }
    }
    
    private function deleteDirectory($dir) {
        if (!is_dir($dir)) return;
        
        $files = array_diff(scandir($dir), ['.', '..']);
        foreach ($files as $file) {
            $path = $dir . '/' . $file;
            is_dir($path) ? $this->deleteDirectory($path) : unlink($path);
        }
        rmdir($dir);
    }
    
    public function processSTL($stlData, $filename, $maxX, $maxY, $maxZ, $flipModel = false) {
        try {
            // Save uploaded STL file
            $stlPath = $this->tempDir . '/input.stl';
            if (!file_put_contents($stlPath, $stlData)) {
                throw new Exception('Cannot save STL file');
            }
            
            // Use Python script to process STL
            $pythonScript = __DIR__ . '/stl_processor.py';
            $command = sprintf(
                'python "%s" "%s" %f %f %f %s 2>&1',
                $pythonScript,
                $stlPath,
                $maxX,
                $maxY,
                $maxZ,
                $flipModel ? 'true' : 'false'
            );
            
            $output = shell_exec($command);
            if ($output === null) {
                throw new Exception('Python processing failed');
            }
            
            // Debug: Log Python output
            error_log("Python output: " . $output);
            
            // Check if parts were created
            $partsDir = $this->tempDir . '/parts';
            if (!is_dir($partsDir)) {
                throw new Exception('No parts directory created. Python output: ' . $output);
            }
            
            $parts = glob($partsDir . '/*.stl');
            if (empty($parts)) {
                throw new Exception('No parts were created');
            }
            
            // Create ZIP file
            $zipPath = $this->tempDir . '/split_parts.zip';
            $zip = new ZipArchive();
            if ($zip->open($zipPath, ZipArchive::CREATE) !== TRUE) {
                throw new Exception('Cannot create ZIP file');
            }
            
            $baseName = pathinfo($filename, PATHINFO_FILENAME);
            foreach ($parts as $part) {
                $partName = basename($part);
                $zip->addFile($part, $partName);
            }
            $zip->close();
            
            // Return ZIP file data
            $zipData = file_get_contents($zipPath);
            if ($zipData === false) {
                throw new Exception('Cannot read ZIP file');
            }
            
            return [
                'success' => true,
                'zipData' => base64_encode($zipData),
                'partsCount' => count($parts),
                'filename' => $baseName . '_split_parts.zip'
            ];
            
        } catch (Exception $e) {
            return [
                'success' => false,
                'error' => $e->getMessage()
            ];
        }
    }
}

// Main API logic
try {
    if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
        throw new Exception('Only POST method allowed');
    }
    
    // Check if file was uploaded
    if (!isset($_FILES['stl_file']) || $_FILES['stl_file']['error'] !== UPLOAD_ERR_OK) {
        throw new Exception('No STL file uploaded or upload error');
    }
    
    $file = $_FILES['stl_file'];
    
    // Validate file size
    if ($file['size'] > 50 * 1024 * 1024) { // 50MB
        throw new Exception('File too large. Maximum size is 50MB');
    }
    
    // Validate file type
    $finfo = finfo_open(FILEINFO_MIME_TYPE);
    $mimeType = finfo_file($finfo, $file['tmp_name']);
    finfo_close($finfo);
    
    if (!in_array($mimeType, ['application/octet-stream', 'application/sla'])) {
        throw new Exception('Invalid file type. Please upload an STL file');
    }
    
    // Get parameters
    $maxX = floatval($_POST['max_x'] ?? 220);
    $maxY = floatval($_POST['max_y'] ?? 220);
    $maxZ = floatval($_POST['max_z'] ?? 250);
    $flipModel = ($_POST['flip_model'] ?? 'false') === 'true';
    
    // Validate parameters
    if ($maxX <= 0 || $maxY <= 0 || $maxZ <= 0) {
        throw new Exception('Invalid build volume dimensions');
    }
    
    // Read STL file
    $stlData = file_get_contents($file['tmp_name']);
    if ($stlData === false) {
        throw new Exception('Cannot read uploaded file');
    }
    
    // Process STL
    $splitter = new STLSplitter();
    $result = $splitter->processSTL($stlData, $file['name'], $maxX, $maxY, $maxZ, $flipModel);
    
    echo json_encode($result);
    
} catch (Exception $e) {
    http_response_code(400);
    echo json_encode([
        'success' => false,
        'error' => $e->getMessage()
    ]);
}
?>
