#!/usr/bin/env python3
"""
Face Scanner Program
A comprehensive face detection and scanning system using OpenCV
Author: AI Assistant
Version: 1.0
"""

import cv2
import numpy as np
import os
import json
import time
from datetime import datetime
import hashlib
import threading
from pathlib import Path
import argparse
import sys

class FaceScanner:
    def __init__(self, data_dir="face_data"):
        """Initialize the face scanner with data directory"""
        self.data_dir = Path(data_dir)
        self.scanned_faces_dir = self.data_dir / "scanned_faces"
        self.logs_dir = self.data_dir / "logs"
        
        # Create directories
        self.data_dir.mkdir(exist_ok=True)
        self.scanned_faces_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)
        
        # Initialize face detection
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        # Initialize camera
        self.cap = None
        self.is_scanning = False
        
        # Scan counter
        self.scan_count = 0
        
        # Load existing scan log
        self.scan_log_file = self.logs_dir / "scan_log.json"
        self.scan_log = self.load_scan_log()
        
    def load_scan_log(self):
        """Load existing scan log from JSON file"""
        if self.scan_log_file.exists():
            try:
                with open(self.scan_log_file, 'r') as f:
                    return json.load(f)
            except:
                return {"scans": []}
        return {"scans": []}
    
    def save_scan_log(self):
        """Save scan log to JSON file"""
        with open(self.scan_log_file, 'w') as f:
            json.dump(self.scan_log, f, indent=2)
    
    def generate_face_id(self, face_image):
        """Generate unique ID for face based on image hash"""
        # Convert image to bytes and generate hash
        _, encoded = cv2.imencode('.jpg', face_image)
        face_hash = hashlib.md5(encoded.tobytes()).hexdigest()
        return f"face_{face_hash[:8]}_{int(time.time())}"
    
    def detect_faces(self, frame):
        """Detect faces in the given frame"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30),
            flags=cv2.CASCADE_SCALE_IMAGE
        )
        return faces, gray
    
    def save_face_image(self, face_image, face_id):
        """Save detected face image to file"""
        filename = f"{face_id}.jpg"
        filepath = self.scanned_faces_dir / filename
        cv2.imwrite(str(filepath), face_image)
        return str(filepath)
    
    def log_scan(self, face_id, filepath, confidence=None):
        """Log scan information"""
        scan_info = {
            "face_id": face_id,
            "timestamp": datetime.now().isoformat(),
            "filepath": filepath,
            "confidence": confidence,
            "scan_number": self.scan_count
        }
        self.scan_log["scans"].append(scan_info)
        self.save_scan_log()
    
    def start_scanning(self, save_images=True, display=True):
        """Start face scanning process"""
        print("Starting face scanner...")
        print("Press 'q' to quit, 's' to save current face")
        
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("Error: Could not open camera")
            return
        
        self.is_scanning = True
        
        try:
            while self.is_scanning:
                ret, frame = self.cap.read()
                if not ret:
                    print("Error: Could not read frame")
                    break
                
                # Detect faces
                faces, gray = self.detect_faces(frame)
                
                # Draw rectangles around faces
                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                    
                    # Extract face region
                    face_roi = gray[y:y+h, x:x+w]
                    
                    # Resize face to standard size
                    face_resized = cv2.resize(face_roi, (200, 200))
                    
                    # Generate face ID
                    face_id = self.generate_face_id(face_resized)
                    
                    # Save face if enabled
                    if save_images:
                        filepath = self.save_face_image(face_resized, face_id)
                        self.scan_count += 1
                        self.log_scan(face_id, filepath)
                        
                        # Display info
                        cv2.putText(frame, f"Saved: {face_id}", (x, y-10), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                
                # Display frame
                if display:
                    cv2.imshow('Face Scanner', frame)
                
                # Check for key presses
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('s') and len(faces) > 0:
                    # Manual save
                    x, y, w, h = faces[0]
                    face_roi = gray[y:y+h, x:x+w]
                    face_resized = cv2.resize(face_roi, (200, 200))
                    face_id = self.generate_face_id(face_resized)
                    filepath = self.save_face_image(face_resized, face_id)
                    self.scan_count += 1
                    self.log_scan(face_id, filepath)
                    print(f"Manually saved face: {face_id}")
        
        except KeyboardInterrupt:
            print("\nScanning interrupted by user")
        
        finally:
            self.stop_scanning()
    
    def stop_scanning(self):
        """Stop face scanning and cleanup"""
        self.is_scanning = False
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        print("Face scanner stopped")
    
    def get_scan_stats(self):
        """Get scanning statistics"""
        total_scans = len(self.scan_log["scans"])
        unique_faces = len(set(scan["face_id"] for scan in self.scan_log["scans"]))
        
        return {
            "total_scans": total_scans,
            "unique_faces": unique_faces,
            "scanned_faces_dir": str(self.scanned_faces_dir),
            "log_file": str(self.scan_log_file)
        }
    
    def list_scanned_faces(self):
        """List all scanned faces"""
        faces = []
        for scan in self.scan_log["scans"]:
            faces.append({
                "face_id": scan["face_id"],
                "timestamp": scan["timestamp"],
                "filepath": scan["filepath"]
            })
        return faces
    
    def cleanup_old_faces(self, days=30):
        """Clean up face images older than specified days"""
        cutoff_time = time.time() - (days * 24 * 60 * 60)
        removed_count = 0
        
        for scan in self.scan_log["scans"][:]:
            filepath = Path(scan["filepath"])
            if filepath.exists() and filepath.stat().st_mtime < cutoff_time:
                filepath.unlink()
                self.scan_log["scans"].remove(scan)
                removed_count += 1
        
        if removed_count > 0:
            self.save_scan_log()
            print(f"Cleaned up {removed_count} old face images")
    
    def export_scan_log(self, filename=None):
        """Export scan log to CSV format"""
        if not filename:
            filename = f"scan_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        import csv
        with open(filename, 'w', newline='') as csvfile:
            fieldnames = ['face_id', 'timestamp', 'filepath', 'confidence']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for scan in self.scan_log["scans"]:
                writer.writerow({
                    'face_id': scan["face_id"],
                    'timestamp': scan["timestamp"],
                    'filepath': scan["filepath"],
                    'confidence': scan.get("confidence", "")
                })
        
        print(f"Scan log exported to {filename}")

def main():
    """Main function to run the face scanner"""
    parser = argparse.ArgumentParser(description="Face Scanner Program")
    parser.add_argument("--data-dir", default="face_data", help="Directory to store face data")
    parser.add_argument("--no-save", action="store_true", help="Don't save face images")
    parser.add_argument("--no-display", action="store_true", help="Don't display video feed")
    parser.add_argument("--stats", action="store_true", help="Show scanning statistics")
    parser.add_argument("--list-faces", action="store_true", help="List all scanned faces")
    parser.add_argument("--cleanup", type=int, help="Clean up faces older than N days")
    parser.add_argument("--export", help="Export scan log to CSV file")
    
    args = parser.parse_args()
    
    scanner = FaceScanner(args.data_dir)
    
    if args.stats:
        stats = scanner.get_scan_stats()
        print("Scanning Statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
    
    elif args.list_faces:
        faces = scanner.list_scanned_faces()
        print(f"Found {len(faces)} scanned faces:")
        for face in faces:
            print(f"  {face['face_id']} - {face['timestamp']}")
    
    elif args.cleanup:
        scanner.cleanup_old_faces(args.cleanup)
    
    elif args.export:
        scanner.export_scan_log(args.export)
    
    else:
        # Start scanning
        save_images = not args.no_save
        display = not args.no_display
        scanner.start_scanning(save_images=save_images, display=display)

if __name__ == "__main__":
    main()
