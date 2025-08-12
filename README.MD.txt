# Face Scanner Program

A comprehensive Python-based face detection and scanning system using OpenCV.

## Features

- Real-time face detection from webcam
- Automatic saving of detected faces
- Detailed logging with timestamps
- File management and cleanup
- Export capabilities
- Command-line interface

## Installation

1. Install Python 3.7 or higher
2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Basic Usage
```bash
python face_scanner.py
```

### Command Line Options

- `--data-dir`: Specify directory for storing face data (default: face_data)
- `--no-save`: Don't save face images
- `--no-display`: Don't display video feed
- `--stats`: Show scanning statistics
- `--list-faces`: List all scanned faces
- `--cleanup N`: Clean up faces older than N days
- `--export FILE`: Export scan log to CSV file

### Examples

```bash
# Start scanning with default settings
python face_scanner.py

# Scan without saving images
python face_scanner.py --no-save

# Show statistics
python face_scanner.py --stats

# List all scanned faces
python face_scanner.py --list-faces

# Clean up faces older than 7 days
python face_scanner.py --cleanup 7

# Export scan log to CSV
python face_scanner.py --export scan_results.csv
```

## Controls During Scanning

- **q**: Quit the program
- **s**: Manually save current detected face

## File Structure

```
face_data/
├── scanned_faces/     # Directory containing saved face images
├── logs/
│   └── scan_log.json  # JSON log of all scans
```

## Scan Log Format

Each scan entry contains:
- `face_id`: Unique identifier for the face
- `timestamp`: ISO format timestamp
- `filepath`: Path to saved image
- `confidence`: Detection confidence (if available)

## Troubleshooting

### Camera Not Found
- Ensure your webcam is connected and not being used by another application
- Try changing the camera index in the code (line 65: `cv2.VideoCapture(0)`)

### Missing Dependencies
- Install OpenCV: `pip install opencv-python`
- Install NumPy: `pip install numpy`

### Permission Errors
- Ensure you have write permissions in the current directory
- Run as administrator if needed

## Security Notes

- Face images are stored locally on your machine
- No data is transmitted to external servers
- All files are stored in plain format for easy access
- Consider implementing encryption for sensitive applications

## License

This program is provided as-is for educational and personal use.
