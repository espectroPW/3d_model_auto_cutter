#!/usr/bin/env python3
"""
STL Processor - Command line tool for splitting STL files
Used by PHP backend to process STL files
"""

import sys
import os
import numpy as np
import struct
import argparse
from pathlib import Path

try:
    import trimesh
    TRIMESH_AVAILABLE = True
except ImportError:
    TRIMESH_AVAILABLE = False
    print("ERROR: Missing trimesh library! Install: pip install trimesh")
    sys.exit(1)

class STLProcessor:
    def __init__(self):
        self.mesh = None
        self.model_bounds = None
        self.force_fallback = False
        
    def load_stl(self, filepath, flip_model=False):
        """Load STL file and optionally flip it"""
        try:
            print(f"Loading file: {filepath}")
            self.mesh = trimesh.load(filepath)
            
            if not isinstance(self.mesh, trimesh.Trimesh):
                raise ValueError("Failed to load STL file as valid 3D mesh")
            
            # Apply rotation if requested
            if flip_model:
                print("Applying 180° rotation around X-axis")
                rotation_matrix = trimesh.transformations.rotation_matrix(np.pi, [1, 0, 0])
                self.mesh.apply_transform(rotation_matrix)
            
            # Calculate model bounds
            bounds = self.mesh.bounds
            self.model_bounds = (bounds[0][0], bounds[1][0], 
                               bounds[0][1], bounds[1][1],
                               bounds[0][2], bounds[1][2])
            
            width = bounds[1][0] - bounds[0][0]
            depth = bounds[1][1] - bounds[0][1]
            height = bounds[1][2] - bounds[0][2]
            
            print(f"Model loaded: {width:.1f}×{depth:.1f}×{height:.1f} mm")
            print(f"Triangles: {len(self.mesh.faces)}, Vertices: {len(self.mesh.vertices)}")
            print(f"Watertight: {self.mesh.is_watertight}")
            print(f"Volume: {self.mesh.volume:.2f} mm³")
            
            # Test trimesh capabilities
            try:
                test_box = trimesh.creation.box(extents=[10, 10, 10])
                test_intersection = self.mesh.intersection(test_box)
                print(f"Trimesh intersection test: SUCCESS - {len(test_intersection.faces)} faces")
                
                # Test with actual model bounds
                model_box = trimesh.creation.box(
                    extents=(width, depth, height),
                    transform=trimesh.transformations.translation_matrix([
                        (bounds[0][0] + bounds[1][0]) / 2,
                        (bounds[0][1] + bounds[1][1]) / 2,
                        (bounds[0][2] + bounds[1][2]) / 2
                    ])
                )
                model_intersection = self.mesh.intersection(model_box)
                print(f"Model intersection test: SUCCESS - {len(model_intersection.faces)} faces")
                
                # Test if intersection creates watertight results
                if hasattr(test_intersection, 'is_watertight'):
                    print(f"Test intersection watertight: {test_intersection.is_watertight}")
                if hasattr(model_intersection, 'is_watertight'):
                    print(f"Model intersection watertight: {model_intersection.is_watertight}")
                
            except Exception as e:
                print(f"Trimesh intersection test: FAILED - {e}")
                print(f"Error type: {type(e).__name__}")
                import traceback
                print(f"Traceback: {traceback.format_exc()}")
                
                # If intersection fails, force fallback method
                print("WARNING: Intersection method not available - will use fallback method only")
                self.force_fallback = True
            
            if not self.mesh.is_watertight:
                print("WARNING: Model is not watertight - will use fallback method for splitting")
            
            return True
            
        except Exception as e:
            print(f"Error loading model: {e}")
            return False
    
    def calculate_splits(self, model_size, max_size):
        """Calculate number of splits required for given dimension"""
        if max_size is None or max_size <= 0:
            return 1
        splits = np.ceil(model_size / max_size)
        return int(splits)
    
    def split_model(self, max_x, max_y, max_z, output_dir):
        """Split model into parts"""
        if not self.mesh or not self.model_bounds:
            return False
        
        try:
            min_x, max_x_bound, min_y, max_y_bound, min_z, max_z_bound = self.model_bounds
            
            width = max_x_bound - min_x
            depth = max_y_bound - min_y
            height = max_z_bound - min_z
            
            # Calculate required splits - only X and Y (like the working code)
            xsplit = self.calculate_splits(width, max_x)
            ysplit = self.calculate_splits(depth, max_y)
            # Z-axis is not split - keep full height
            zsplit = 1
            
            total_parts = xsplit * ysplit * zsplit
            
            print(f"Split configuration: {xsplit}×{ysplit} = {total_parts} parts")
            
            # Create output directory
            os.makedirs(output_dir, exist_ok=True)
            
            # Generate split configuration data
            x_extent = np.linspace(min_x, max_x_bound, xsplit + 1)
            y_extent = np.linspace(min_y, max_y_bound, ysplit + 1)
            # Z extent is just the full range
            z_min, z_max = min_z, max_z_bound
            
            parts_created = 0
            part_number = 1
            
            print(f"Starting split operation on {len(self.mesh.faces)} triangles")
            
            for i in range(xsplit):
                for j in range(ysplit):
                    x_min = x_extent[i]
                    x_max = x_extent[i + 1] 
                    y_min = y_extent[j]
                    y_max = y_extent[j + 1]
                    
                    print(f"Processing part {part_number}: bounds ({x_min:.1f}, {y_min:.1f}, {z_min:.1f}) to ({x_max:.1f}, {y_max:.1f}, {z_max:.1f})")
                    
                    try:
                        print(f"Part {part_number}: Processing bounds ({x_min:.1f}, {y_min:.1f}, {z_min:.1f}) to ({x_max:.1f}, {y_max:.1f}, {z_max:.1f})")
                        
                        # Try intersection method first (for watertight models) - unless forced to use fallback
                        if not self.force_fallback:
                            try:
                                print(f"Part {part_number}: Trying intersection method...")
                                
                                # Create bounding box for this part
                                bounds_box = trimesh.creation.box(
                                    extents=(x_max - x_min, y_max - y_min, z_max - z_min),
                                    transform=trimesh.transformations.translation_matrix(
                                        [(x_max + x_min) / 2, (y_max + y_min) / 2, (z_max + z_min) / 2]
                                    )
                                )
                                
                                print(f"Part {part_number}: Created bounding box, attempting intersection...")
                                
                                # Intersect the mesh with the bounding box
                                section = self.mesh.intersection(bounds_box)
                                
                                print(f"Part {part_number}: Intersection completed, checking if empty...")
                                
                                # Check if the section contains geometry
                                if section.is_empty:
                                    print(f"Part {part_number}: No geometry in bounds - skipped")
                                    continue
                                
                                print(f"Part {part_number}: Section has {len(section.faces)} faces, {len(section.vertices)} vertices")
                                
                                # Export the part
                                output_filename = f"part_{part_number:02d}.stl"
                                output_filepath = os.path.join(output_dir, output_filename)
                                
                                # Use trimesh export
                                section.export(output_filepath)
                                parts_created += 1
                                
                                print(f"Part {part_number}: SUCCESS (intersection) - {len(section.faces)} triangles, {len(section.vertices)} vertices → {output_filename}")
                                
                            except Exception as intersection_error:
                                # Fallback to vertex filtering method for non-watertight models
                                print(f"Part {part_number}: Intersection failed ({intersection_error}), trying fallback method...")
                                print(f"Part {part_number}: Error type: {type(intersection_error).__name__}")
                                
                                # Get original mesh data
                                original_vertices = self.mesh.vertices
                                original_faces = self.mesh.faces
                                
                                print(f"Part {part_number}: Original mesh has {len(original_faces)} faces, {len(original_vertices)} vertices")
                                
                                # Find faces that have at least one vertex in the bounds
                                valid_faces = []
                                
                                for face_idx, face in enumerate(original_faces):
                                    face_vertices = original_vertices[face]
                                    
                                    # Check if any vertex of this face is within bounds
                                    for vertex in face_vertices:
                                        vx, vy, vz = vertex
                                        if (x_min <= vx <= x_max and 
                                            y_min <= vy <= y_max and 
                                            z_min <= vz <= z_max):
                                            valid_faces.append(face_idx)
                                            break
                                
                                print(f"Part {part_number}: Found {len(valid_faces)} valid faces in bounds")
                                
                                if not valid_faces:
                                    print(f"Part {part_number}: No faces found in bounds - skipped")
                                    continue
                                
                                # Extract valid faces and their vertices
                                part_faces = original_faces[valid_faces]
                                
                                # Get all unique vertices used by these faces
                                unique_vertex_indices = np.unique(part_faces.flatten())
                                part_vertices = original_vertices[unique_vertex_indices]
                                
                                # Reindex faces to use new vertex indices
                                vertex_map = {old_idx: new_idx for new_idx, old_idx in enumerate(unique_vertex_indices)}
                                reindexed_faces = np.array([[vertex_map[vertex] for vertex in face] for face in part_faces])
                                
                                print(f"Part {part_number}: Extracted {len(reindexed_faces)} faces, {len(part_vertices)} vertices")
                                
                                # Export the part using simple STL writer
                                output_filename = f"part_{part_number:02d}.stl"
                                output_filepath = os.path.join(output_dir, output_filename)
                                
                                self.write_stl_simple(output_filepath, part_vertices, reindexed_faces)
                                parts_created += 1
                                
                                print(f"Part {part_number}: SUCCESS (fallback) - {len(reindexed_faces)} triangles, {len(part_vertices)} vertices → {output_filename}")
                        
                        else:
                            # Force fallback method (intersection not available)
                            print(f"Part {part_number}: Using fallback method (intersection not available)...")
                            
                            # Get original mesh data
                            original_vertices = self.mesh.vertices
                            original_faces = self.mesh.faces
                            
                            print(f"Part {part_number}: Original mesh has {len(original_faces)} faces, {len(original_vertices)} vertices")
                            
                            # Find faces that have at least one vertex in the bounds
                            valid_faces = []
                            
                            for face_idx, face in enumerate(original_faces):
                                face_vertices = original_vertices[face]
                                
                                # Check if any vertex of this face is within bounds
                                for vertex in face_vertices:
                                    vx, vy, vz = vertex
                                    if (x_min <= vx <= x_max and 
                                        y_min <= vy <= y_max and 
                                        z_min <= vz <= z_max):
                                        valid_faces.append(face_idx)
                                        break
                            
                            print(f"Part {part_number}: Found {len(valid_faces)} valid faces in bounds")
                            
                            if not valid_faces:
                                print(f"Part {part_number}: No faces found in bounds - skipped")
                                continue
                            
                            # Extract valid faces and their vertices
                            part_faces = original_faces[valid_faces]
                            
                            # Get all unique vertices used by these faces
                            unique_vertex_indices = np.unique(part_faces.flatten())
                            part_vertices = original_vertices[unique_vertex_indices]
                            
                            # Reindex faces to use new vertex indices
                            vertex_map = {old_idx: new_idx for new_idx, old_idx in enumerate(unique_vertex_indices)}
                            reindexed_faces = np.array([[vertex_map[vertex] for vertex in face] for face in part_faces])
                            
                            print(f"Part {part_number}: Extracted {len(reindexed_faces)} faces, {len(part_vertices)} vertices")
                            
                            # Export the part using simple STL writer
                            output_filename = f"part_{part_number:02d}.stl"
                            output_filepath = os.path.join(output_dir, output_filename)
                            
                            self.write_stl_simple(output_filepath, part_vertices, reindexed_faces)
                            parts_created += 1
                            
                            print(f"Part {part_number}: SUCCESS (forced fallback) - {len(reindexed_faces)} triangles, {len(part_vertices)} vertices → {output_filename}")
                        
                    except Exception as part_error:
                        print(f"Error processing part {part_number}: {part_error}")
                        import traceback
                        print(f"Part {part_number}: Traceback: {traceback.format_exc()}")
                        continue
                    
                    part_number += 1
            
            print(f"Split operation completed: {parts_created} parts created")
            return parts_created > 0
            
        except Exception as e:
            print(f"Error in split_model: {e}")
            return False
    
    def write_stl_simple(self, filename, vertices, faces):
        """Simple STL writer as fallback"""
        with open(filename, 'wb') as f:
            # Write header
            header = f'STL Part - {len(faces)} triangles'.encode('ascii')[:80]
            header = header.ljust(80, b'\0')
            f.write(header)
            
            # Write number of triangles
            f.write(struct.pack('<I', len(faces)))
            
            # Write each triangle
            for face in faces:
                v1, v2, v3 = vertices[face]
                
                # Calculate normal vector
                edge1 = v2 - v1
                edge2 = v3 - v1
                normal = np.cross(edge1, edge2)
                norm = np.linalg.norm(normal)
                if norm > 0:
                    normal = normal / norm
                else:
                    normal = np.array([0.0, 0.0, 1.0])
                
                # Write normal
                f.write(struct.pack('<fff', *normal))
                
                # Write vertices
                f.write(struct.pack('<fff', *v1))
                f.write(struct.pack('<fff', *v2))
                f.write(struct.pack('<fff', *v3))
                
                # Write attribute bytes
                f.write(struct.pack('<H', 0))

def get_model_info(stl_file, flip_model=False):
    """Get model information without splitting"""
    try:
        processor = STLProcessor()
        if not processor.load_stl(stl_file, flip_model):
            return None
        
        bounds = processor.model_bounds
        width = bounds[1] - bounds[0]
        depth = bounds[3] - bounds[2] 
        height = bounds[5] - bounds[4]
        
        info = {
            'triangles': len(processor.mesh.faces),
            'vertices': len(processor.mesh.vertices),
            'watertight': processor.mesh.is_watertight,
            'volume': processor.mesh.volume,
            'dimensions': f"{width:.1f}×{depth:.1f}×{height:.1f}",
            'width': width,
            'depth': depth,
            'height': height
        }
        
        return info
        
    except Exception as e:
        print(f"Error getting model info: {e}")
        return None

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Info: python stl_processor.py info <stl_file> [flip_model]")
        print("  Split: python stl_processor.py split <stl_file> <max_x> <max_y> <max_z> <flip_model> <output_dir>")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "info":
        if len(sys.argv) < 3:
            print("Usage: python stl_processor.py info <stl_file> [flip_model]")
            sys.exit(1)
        
        stl_file = sys.argv[2]
        flip_model = len(sys.argv) > 3 and sys.argv[3].lower() == 'true'
        
        info = get_model_info(stl_file, flip_model)
        if info:
            print(f"TRIANGLES:{info['triangles']}")
            print(f"VERTICES:{info['vertices']}")
            print(f"WATERTIGHT:{info['watertight']}")
            print(f"VOLUME:{info['volume']:.2f}")
            print(f"DIMENSIONS:{info['dimensions']}")
            print(f"WIDTH:{info['width']:.1f}")
            print(f"DEPTH:{info['depth']:.1f}")
            print(f"HEIGHT:{info['height']:.1f}")
        else:
            print("ERROR:Failed to load model")
            sys.exit(1)
    
    elif command == "split":
        if len(sys.argv) != 8:
            print("Usage: python stl_processor.py split <stl_file> <max_x> <max_y> <max_z> <flip_model> <output_dir>")
            sys.exit(1)
        
        stl_file = sys.argv[2]
        max_x = float(sys.argv[3])
        max_y = float(sys.argv[4])
        max_z = float(sys.argv[5])
        flip_model = sys.argv[6].lower() == 'true'
        output_dir = sys.argv[7]
        
        processor = STLProcessor()
        
        # Load the STL file
        if not processor.load_stl(stl_file, flip_model):
            print("Failed to load STL file")
            sys.exit(1)
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Split the model
        success = processor.split_model(max_x, max_y, max_z, output_dir)
        
        if success:
            print("STL processing completed successfully")
            sys.exit(0)
        else:
            print("STL processing failed")
            sys.exit(1)
    
    else:
        print("Unknown command. Use 'info' or 'split'")
        sys.exit(1)

if __name__ == "__main__":
    main()
