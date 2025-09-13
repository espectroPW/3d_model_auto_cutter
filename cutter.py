#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
STL 3D Model Splitter - Professional mesh splitting application
Uses Trimesh library for accurate 3D mesh cutting with watertight results
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import threading
from pathlib import Path
import numpy as np
import struct
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import math
import struct

try:
    import trimesh
    TRIMESH_AVAILABLE = True
except ImportError:
    TRIMESH_AVAILABLE = False
    print("ERROR: Missing trimesh library! Install: pip install trimesh")

class STL3DTrimeshSplitterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("STL 3D Model Splitter v2.0 (Trimesh)")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        if not TRIMESH_AVAILABLE:
            messagebox.showerror("Error", "Missing trimesh library!\n\nInstall with:\npip install trimesh")
            self.root.quit()
            return
        
        # Configuration variables
        self.input_file = tk.StringVar()
        self.output_dir = tk.StringVar()
        self.max_x = tk.DoubleVar(value=220.0)
        self.max_y = tk.DoubleVar(value=220.0)
        self.max_z = tk.DoubleVar(value=250.0)
        self.flip_model = tk.BooleanVar(value=False)
        
        # Model data
        self.mesh = None
        self.model_bounds = None
        self.split_preview = []
        self.update_timer = None
        
        # Bind file variable to auto-load
        self.input_file.trace_add('write', self.on_file_selected)
        
        # Bind dimension variables to preview updates
        self.max_x.trace_add('write', self.on_dimension_changed)
        self.max_y.trace_add('write', self.on_dimension_changed)
        self.max_z.trace_add('write', self.on_dimension_changed)
        
        self.create_widgets()
        
    def create_widgets(self):
        # Main horizontal split container
        main_container = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        left_panel = ttk.Frame(main_container, width=400)
        main_container.add(left_panel, weight=1)
        
        right_panel = ttk.Frame(main_container, width=600)
        main_container.add(right_panel, weight=2)
        
        self.create_left_panel(left_panel)
        self.create_right_panel(right_panel)
        
    def create_left_panel(self, parent):
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Application header
        title_label = ttk.Label(scrollable_frame, text="STL Splitter v2.0", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(5, 2))
        
        subtitle_label = ttk.Label(scrollable_frame, text="Trimesh", 
                                 font=("Arial", 9), foreground="gray")
        subtitle_label.pack(pady=(0, 10))
        
        # File selection section
        file_frame = ttk.LabelFrame(scrollable_frame, text="📁 Files", padding="8")
        file_frame.pack(fill=tk.X, padx=8, pady=3)
        
        ttk.Label(file_frame, text="STL:").pack(anchor=tk.W)
        
        file_select_frame = ttk.Frame(file_frame)
        file_select_frame.pack(fill=tk.X, pady=2)
        
        self.file_entry = ttk.Entry(file_select_frame, textvariable=self.input_file)
        self.file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Button(file_select_frame, text="Browse", 
                  command=self.browse_input_file).pack(side=tk.RIGHT, padx=(5, 0))
        
        ttk.Label(file_frame, text="Output:").pack(anchor=tk.W, pady=(8, 0))
        
        output_select_frame = ttk.Frame(file_frame)
        output_select_frame.pack(fill=tk.X, pady=2)
        
        self.output_entry = ttk.Entry(output_select_frame, textvariable=self.output_dir)
        self.output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Button(output_select_frame, text="Browse", 
                  command=self.browse_output_dir).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Model information display
        self.model_info_frame = ttk.LabelFrame(scrollable_frame, text="📊 Model", padding="6")
        self.model_info_frame.pack(fill=tk.X, padx=8, pady=3)
        
        self.model_info_label = ttk.Label(self.model_info_frame, 
                                         text="Load STL to see info",
                                         foreground="gray", font=("Arial", 9))
        self.model_info_label.pack(anchor=tk.W)
        
        # 3D printer configuration
        printer_frame = ttk.LabelFrame(scrollable_frame, text="🖨️ Printer", padding="6")
        printer_frame.pack(fill=tk.X, padx=8, pady=3)
        
        ttk.Label(printer_frame, text="Presets:", font=("Arial", 9)).pack(anchor=tk.W)
        preset_frame = ttk.Frame(printer_frame)
        preset_frame.pack(fill=tk.X, pady=2)
        
        ttk.Button(preset_frame, text="Ender 3", 
                  command=lambda: self.set_preset(220, 220, 250)).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(preset_frame, text="Prusa i3", 
                  command=lambda: self.set_preset(250, 210, 210)).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(preset_frame, text="Mini", 
                  command=lambda: self.set_preset(100, 100, 100)).pack(side=tk.LEFT)
        
        ttk.Label(printer_frame, text="Build Volume (mm):", font=("Arial", 9)).pack(anchor=tk.W, pady=(8, 2))
        
        dims_frame = ttk.Frame(printer_frame)
        dims_frame.pack(fill=tk.X)
        
        # X Y Z dimension inputs
        for axis, var, label in [("X", self.max_x, "X:"), 
                                ("Y", self.max_y, "Y:"), 
                                ("Z", self.max_z, "Z:")]:
            axis_frame = ttk.Frame(dims_frame)
            axis_frame.pack(fill=tk.X, pady=1)
            ttk.Label(axis_frame, text=label, width=8, font=("Arial", 9)).pack(side=tk.LEFT)
            spinbox = ttk.Spinbox(axis_frame, from_=10, to=1000, increment=10,
                               width=8, textvariable=var, format="%.0f",
                               command=self.schedule_preview_update)
            spinbox.pack(side=tk.LEFT, padx=3)
            ttk.Label(axis_frame, text="mm", font=("Arial", 8)).pack(side=tk.LEFT)
            
            # Additional bindings for immediate feedback
            spinbox.bind('<KeyRelease>', lambda e: self.schedule_preview_update())
            spinbox.bind('<ButtonRelease-1>', lambda e: self.schedule_preview_update())
        
        # Model orientation option
        flip_frame = ttk.Frame(dims_frame)
        flip_frame.pack(fill=tk.X, pady=(6, 2))
        self.flip_checkbox = ttk.Checkbutton(flip_frame, text="Flip 180° (X)", 
                                           variable=self.flip_model,
                                           command=self.on_flip_changed)
        self.flip_checkbox.pack(side=tk.LEFT)
        
        # Split configuration preview
        self.split_info_frame = ttk.LabelFrame(scrollable_frame, text="✂️ Split", padding="6")
        self.split_info_frame.pack(fill=tk.X, padx=8, pady=3)
        
        self.split_info_label = ttk.Label(self.split_info_frame,
                                         text="Load model to see split config",
                                         foreground="gray", font=("Arial", 9))
        self.split_info_label.pack(anchor=tk.W)
        
        # Action buttons
        button_frame = ttk.Frame(scrollable_frame)
        button_frame.pack(fill=tk.X, padx=8, pady=10)
        
        self.split_button = ttk.Button(button_frame, text="✂️ Split Model", 
                                      command=self.start_splitting, state='disabled')
        self.split_button.pack(fill=tk.X, pady=2)
        
        # Progress indicator
        self.progress = ttk.Progressbar(button_frame, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=(8, 2))
        
        self.status_label = ttk.Label(button_frame, text="Ready", foreground="green", font=("Arial", 9))
        self.status_label.pack()
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
    def create_right_panel(self, parent):
        view_frame = ttk.LabelFrame(parent, text="🎯 3D Preview", padding="3")
        view_frame.pack(fill=tk.BOTH, expand=True)
        
        self.fig = Figure(figsize=(8, 6), dpi=100)
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.ax.set_title("Load STL to view 3D preview")
        
        self.canvas = FigureCanvasTkAgg(self.fig, view_frame)
        self.canvas.draw()
        
        canvas_widget = self.canvas.get_tk_widget()
        canvas_widget.pack(fill=tk.BOTH, expand=True)
        
        # View control buttons
        controls_frame = ttk.Frame(view_frame)
        controls_frame.pack(fill=tk.X, pady=3)
        
        ttk.Button(controls_frame, text="🔄 Refresh", 
                  command=self.refresh_3d_view).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="📐 Show Split", 
                  command=self.show_split_preview).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(controls_frame, text="View:").pack(side=tk.LEFT, padx=(20, 5))
        ttk.Button(controls_frame, text="↗️ Isometric", 
                  command=self.set_isometric_view).pack(side=tk.LEFT, padx=2)
        ttk.Button(controls_frame, text="⬆️ Top", 
                  command=self.set_top_view).pack(side=tk.LEFT, padx=2)
        ttk.Button(controls_frame, text="➡️ Side", 
                  command=self.set_side_view).pack(side=tk.LEFT, padx=2)
    
    def set_preset(self, x, y, z):
        self.max_x.set(x)
        self.max_y.set(y)
        self.max_z.set(z)
        self.update_split_preview()
    
    def browse_input_file(self):
        filename = filedialog.askopenfilename(
            title="Select STL File",
            filetypes=[("STL files", "*.stl"), ("All files", "*.*")]
        )
        if filename:
            self.input_file.set(filename)
            if not self.output_dir.get():
                self.output_dir.set(os.path.dirname(filename))
    
    def browse_output_dir(self):
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.output_dir.set(directory)
    
    def on_file_selected(self, *args):
        """Auto-load model when file is selected"""
        if self.input_file.get() and os.path.exists(self.input_file.get()):
            self.root.after(100, self.load_and_analyze_model)
    
    def on_dimension_changed(self, *args):
        """Handle dimension changes"""
        self.schedule_preview_update()
    
    def on_flip_changed(self):
        """Handle model orientation change"""
        if self.mesh is not None:
            self.load_and_analyze_model()
    
    def schedule_preview_update(self):
        """Schedule preview update with debouncing"""
        if self.update_timer:
            self.root.after_cancel(self.update_timer)
        self.update_timer = self.root.after(300, self.update_split_preview)
    
    def update_split_preview_safe(self):
        """Thread-safe version of update_split_preview"""
        if self.mesh is not None:
            self.root.after(0, self.update_split_preview)
    
    def load_and_analyze_model(self):
        if not self.input_file.get():
            messagebox.showerror("Error", "Please select an STL file")
            return
        
        thread = threading.Thread(target=self._load_model_thread)
        thread.daemon = True
        thread.start()
    
    def _load_model_thread(self):
        try:
            # Update GUI in main thread
            self.root.after(0, lambda: self.status_label.configure(text="Loading model...", foreground="orange"))
            self.root.after(0, self.progress.start)
            
            input_path = self.input_file.get()
            
            print(f"Loading file: {input_path}")
            mesh = trimesh.load(input_path)
            
            if not isinstance(mesh, trimesh.Trimesh):
                raise ValueError("Failed to load STL file as valid 3D mesh")
            
            # Apply rotation if requested
            if self.flip_model.get():
                print("Applying 180° rotation around X-axis")
                rotation_matrix = trimesh.transformations.rotation_matrix(np.pi, [1, 0, 0])
                mesh.apply_transform(rotation_matrix)
            
            self.mesh = mesh
            
            # Calculate model bounds
            bounds = mesh.bounds
            self.model_bounds = (bounds[0][0], bounds[1][0], 
                               bounds[0][1], bounds[1][1],
                               bounds[0][2], bounds[1][2])
            
            width = bounds[1][0] - bounds[0][0]
            depth = bounds[1][1] - bounds[0][1]
            height = bounds[1][2] - bounds[0][2]
            
            # Update model information display (thread-safe)
            info_text = (f"📏 Dimensions: {width:.1f} × {depth:.1f} × {height:.1f} mm\n"
                        f"🔺 Triangles: {len(mesh.faces):,}\n"
                        f"🔘 Vertices: {len(mesh.vertices):,}\n"
                        f"📦 Volume: {mesh.volume:.1f} mm³\n"
                        f"✅ Watertight: {'Yes' if mesh.is_watertight else 'No'}")
            
            self.root.after(0, lambda: self.model_info_label.configure(text=info_text, foreground="black"))
            
            print(f"Model loaded: {width:.1f}×{depth:.1f}×{height:.1f} mm")
            print(f"Triangles: {len(mesh.faces)}, Vertices: {len(mesh.vertices)}")
            print(f"Watertight: {mesh.is_watertight}")
            
            # Update split preview and enable controls (thread-safe)
            self.root.after(0, self.update_split_preview)
            self.root.after(0, lambda: self.split_button.configure(state='normal'))
            self.root.after(0, self.refresh_3d_view)
            
        except Exception as e:
            error_msg = f"Error loading model: {str(e)}"
            print(error_msg)
            self.root.after(0, lambda: messagebox.showerror("Error", error_msg))
        finally:
            # Update GUI in main thread
            self.root.after(0, self.progress.stop)
            self.root.after(0, lambda: self.status_label.configure(text="Model loaded", foreground="green"))
# CZĘŚĆ 2/2 - KONTYNUACJA KLASY STL3DTrimeshSplitterGUI

    def calculate_splits(self, model_size, max_size):
        """Calculate number of splits required for given dimension"""
        if max_size is None or max_size <= 0:
            return 1
        splits = np.ceil(model_size / max_size)
        return int(splits)
    
    def update_split_preview(self):
        if not self.model_bounds or not self.mesh:
            return
        
        try:
            min_x, max_x, min_y, max_y, min_z, max_z = self.model_bounds
            
            width = max_x - min_x
            depth = max_y - min_y
            height = max_z - min_z
            
            max_x_size = self.max_x.get()
            max_y_size = self.max_y.get()
            max_z_size = self.max_z.get()
            
            # Calculate required splits - only X and Y (like the working code)
            xsplit = self.calculate_splits(width, max_x_size)
            ysplit = self.calculate_splits(depth, max_y_size)
            # Z-axis is not split - keep full height
            zsplit = 1
            
            total_parts = xsplit * ysplit * zsplit
            
            # Calculate actual segment dimensions
            segment_size_x = width / xsplit
            segment_size_y = depth / ysplit
            segment_size_z = height  # Full height
            
            # Generate split configuration data
            self.split_preview = []
            x_extent = np.linspace(min_x, max_x, xsplit + 1)
            y_extent = np.linspace(min_y, max_y, ysplit + 1)
            # Z extent is just the full range
            z_min, z_max = min_z, max_z
            
            part_number = 1
            for i in range(xsplit):
                for j in range(ysplit):
                    x_min = x_extent[i]
                    x_max = x_extent[i + 1] 
                    y_min = y_extent[j]
                    y_max = y_extent[j + 1]
                    
                    self.split_preview.append({
                        'bounds': (x_min, x_max, y_min, y_max, z_min, z_max),
                        'index': (i, j),
                        'part_number': part_number
                    })
                    part_number += 1
            
            # Update UI with split information
            if total_parts == 1:
                split_text = "✅ Model fits in build volume - no splitting required"
                color = "green"
            else:
                split_text = (f"📦 Split into {total_parts} parts ({xsplit}×{ysplit})\n"
                             f"📏 Each part size: ~{segment_size_x:.1f}×{segment_size_y:.1f}×{segment_size_z:.1f} mm\n"
                             f"🔧 Model dimensions: {width:.1f}×{depth:.1f}×{height:.1f} mm\n"
                             f"🖨️ Max build volume: {max_x_size:.0f}×{max_y_size:.0f}×{max_z_size:.0f} mm")
                color = "blue"
            
            self.split_info_label.configure(text=split_text, foreground=color)
            
        except Exception as e:
            self.split_info_label.configure(text=f"Error calculating split: {str(e)}", 
                                          foreground="red")
            print(f"Error in update_split_preview: {e}")
    
    def refresh_3d_view(self):
        """Render 3D model visualization"""
        if not self.mesh:
            return
        
        self.ax.clear()
        
        # Get mesh geometry for visualization
        vertices = self.mesh.vertices
        faces = self.mesh.faces
        
        # Subsample faces for performance
        max_faces = 2000
        if len(faces) > max_faces:
            step = len(faces) // max_faces
            sampled_faces = faces[::step]
        else:
            sampled_faces = faces
        
        # Create 3D surface collection
        from mpl_toolkits.mplot3d.art3d import Poly3DCollection
        
        triangles = []
        colors = []
        
        for face in sampled_faces:
            triangle = vertices[face]
            triangles.append(triangle)
            
            # Height-based color gradient
            avg_z = np.mean(triangle[:, 2])
            if self.model_bounds:
                min_z, max_z = self.model_bounds[4], self.model_bounds[5]
                if max_z > min_z:
                    z_norm = (avg_z - min_z) / (max_z - min_z)
                    blue_intensity = 0.3 + 0.7 * (1 - z_norm)
                    colors.append((0.1, 0.4, blue_intensity, 0.8))
                else:
                    colors.append((0.2, 0.5, 0.9, 0.8))
            else:
                colors.append((0.2, 0.5, 0.9, 0.8))
        
        # Render mesh surfaces
        if triangles:
            poly_collection = Poly3DCollection(triangles,
                                             facecolors=colors,
                                             edgecolors='navy',
                                             linewidths=0.1,
                                             alpha=0.8)
            self.ax.add_collection3d(poly_collection)
        
        # Configure 3D plot appearance
        self.ax.set_xlabel('X (mm)')
        self.ax.set_ylabel('Y (mm)')
        self.ax.set_zlabel('Z (mm)')
        self.ax.set_title(f'STL Model ({len(self.mesh.faces):,} triangles)')
        
        # Set proportional axis scaling
        if self.model_bounds:
            min_x, max_x, min_y, max_y, min_z, max_z = self.model_bounds
            
            center_x = (min_x + max_x) / 2
            center_y = (min_y + max_y) / 2
            center_z = (min_z + max_z) / 2
            
            range_x = max_x - min_x
            range_y = max_y - min_y
            range_z = max_z - min_z
            
            max_range = max(range_x, range_y, range_z)
            padding = max_range * 0.15
            
            half_range = max_range / 2 + padding
            self.ax.set_xlim(center_x - half_range, center_x + half_range)
            self.ax.set_ylim(center_y - half_range, center_y + half_range)
            self.ax.set_zlim(center_z - half_range, center_z + half_range)
            
            try:
                self.ax.set_box_aspect([1,1,1])
            except:
                pass
        
        self.ax.view_init(elev=20, azim=45)
        self.ax.grid(True, alpha=0.3)
        self.canvas.draw()
    
    def show_split_preview(self):
        """Visualize split boundaries on 3D model"""
        if not self.split_preview or not self.model_bounds:
            messagebox.showwarning("Warning", "Load model and analyze split configuration first")
            return
        
        self.ax.clear()
        
        # Draw 3D model first (if available)
        if self.mesh:
            vertices = self.mesh.vertices
            faces = self.mesh.faces
            
            # Subsample faces for performance
            max_faces = 2000
            if len(faces) > max_faces:
                step = len(faces) // max_faces
                sampled_faces = faces[::step]
            else:
                sampled_faces = faces
            
            # Create 3D surface collection
            from mpl_toolkits.mplot3d.art3d import Poly3DCollection
            
            triangles = []
            colors = []
            
            for face in sampled_faces:
                triangle = vertices[face]
                triangles.append(triangle)
                
                # Semi-transparent model color
                colors.append((0.7, 0.7, 0.7, 0.3))  # Light gray, semi-transparent
            
            # Render mesh surfaces
            if triangles:
                poly_collection = Poly3DCollection(triangles,
                                                 facecolors=colors,
                                                 edgecolors='none',  # No edges for cleaner look
                                                 alpha=0.3)
                self.ax.add_collection3d(poly_collection)
        
        # Draw original model bounding box
        min_x, max_x, min_y, max_y, min_z, max_z = self.model_bounds
        
        vertices = [
            [min_x, min_y, min_z], [max_x, min_y, min_z],
            [max_x, max_y, min_z], [min_x, max_y, min_z],
            [min_x, min_y, max_z], [max_x, min_y, max_z],
            [max_x, max_y, max_z], [min_x, max_y, max_z]
        ]
        
        edges = [
            [0, 1], [1, 2], [2, 3], [3, 0],  # bottom
            [4, 5], [5, 6], [6, 7], [7, 4],  # top
            [0, 4], [1, 5], [2, 6], [3, 7]   # vertical
        ]
        
        # Draw model outline
        for edge in edges:
            points = [vertices[edge[0]], vertices[edge[1]]]
            xs, ys, zs = zip(*points)
            self.ax.plot(xs, ys, zs, 'k-', linewidth=2, alpha=0.7)
        
        # Draw split boundaries with different colors
        colors = ['red', 'blue', 'green', 'orange', 'purple', 'cyan', 'magenta', 'yellow']
        
        for i, part in enumerate(self.split_preview):
            x_min, x_max, y_min, y_max, z_min, z_max = part['bounds']
            color = colors[i % len(colors)]
            part_num = part['part_number']
            
            # Create split box vertices
            split_vertices = [
                [x_min, y_min, z_min], [x_max, y_min, z_min],
                [x_max, y_max, z_min], [x_min, y_max, z_min],
                [x_min, y_min, z_max], [x_max, y_min, z_max],
                [x_max, y_max, z_max], [x_min, y_max, z_max]
            ]
            
            # Draw split boundaries
            for edge in edges:
                points = [split_vertices[edge[0]], split_vertices[edge[1]]]
                xs, ys, zs = zip(*points)
                self.ax.plot(xs, ys, zs, color=color, linewidth=1.5, alpha=0.8)
            
            # Add part number labels
            center_x = (x_min + x_max) / 2
            center_y = (y_min + y_max) / 2
            center_z = (z_min + z_max) / 2
            self.ax.text(center_x, center_y, center_z, f'P{part_num}', 
                        fontsize=8, color=color, weight='bold')
        
        self.ax.set_xlabel('X (mm)')
        self.ax.set_ylabel('Y (mm)')
        self.ax.set_zlabel('Z (mm)')
        self.ax.set_title(f'Split Preview ({len(self.split_preview)} parts)')
        
        # Set axis limits with padding
        padding = 20
        self.ax.set_xlim(min_x - padding, max_x + padding)
        self.ax.set_ylim(min_y - padding, max_y + padding)
        self.ax.set_zlim(min_z - padding, max_z + padding)
        
        self.ax.view_init(elev=20, azim=45)
        self.ax.grid(True, alpha=0.3)
        self.canvas.draw()
    
    def set_isometric_view(self):
        """Set isometric camera angle"""
        if self.model_bounds:
            self.ax.view_init(elev=20, azim=45)
            self.canvas.draw()
    
    def set_top_view(self):
        """Set top-down camera angle"""
        if self.model_bounds:
            self.ax.view_init(elev=90, azim=0)
            self.canvas.draw()
    
    def set_side_view(self):
        """Set side camera angle"""
        if self.model_bounds:
            self.ax.view_init(elev=0, azim=0)
            self.canvas.draw()
    
    def highlight_part(self, part_bounds, part_number):
        """Highlight a specific part in the 3D view"""
        if not self.mesh or not self.model_bounds:
            return
        
        self.ax.clear()
        
        # Get mesh geometry for visualization
        vertices = self.mesh.vertices
        faces = self.mesh.faces
        
        # Subsample faces for performance
        max_faces = 2000
        if len(faces) > max_faces:
            step = len(faces) // max_faces
            sampled_faces = faces[::step]
        else:
            sampled_faces = faces
        
        # Create 3D surface collection
        from mpl_toolkits.mplot3d.art3d import Poly3DCollection
        
        triangles = []
        colors = []
        
        x_min, x_max, y_min, y_max, z_min, z_max = part_bounds
        
        for face in sampled_faces:
            triangle = vertices[face]
            triangles.append(triangle)
            
            # Check if this face is in the highlighted part
            face_center = np.mean(triangle, axis=0)
            in_part = (x_min <= face_center[0] <= x_max and 
                      y_min <= face_center[1] <= y_max and 
                      z_min <= face_center[2] <= z_max)
            
            if in_part:
                # Highlight this part in bright color
                colors.append((1.0, 0.2, 0.2, 0.9))  # Bright red
            else:
                # Dim other parts
                colors.append((0.3, 0.3, 0.3, 0.3))  # Gray, transparent
        
        # Render mesh surfaces
        if triangles:
            poly_collection = Poly3DCollection(triangles,
                                             facecolors=colors,
                                             edgecolors='navy',
                                             linewidths=0.1,
                                             alpha=0.8)
            self.ax.add_collection3d(poly_collection)
        
        # Configure 3D plot appearance
        self.ax.set_xlabel('X (mm)')
        self.ax.set_ylabel('Y (mm)')
        self.ax.set_zlabel('Z (mm)')
        self.ax.set_title(f'Part {part_number} Preview')
        
        # Set proportional axis scaling
        if self.model_bounds:
            min_x, max_x, min_y, max_y, min_z, max_z = self.model_bounds
            
            center_x = (min_x + max_x) / 2
            center_y = (min_y + max_y) / 2
            center_z = (min_z + max_z) / 2
            
            range_x = max_x - min_x
            range_y = max_y - min_y
            range_z = max_z - min_z
            
            max_range = max(range_x, range_y, range_z)
            padding = max_range * 0.15
            
            half_range = max_range / 2 + padding
            self.ax.set_xlim(center_x - half_range, center_x + half_range)
            self.ax.set_ylim(center_y - half_range, center_y + half_range)
            self.ax.set_zlim(center_z - half_range, center_z + half_range)
            
            try:
                self.ax.set_box_aspect([1,1,1])
            except:
                pass
        
        self.ax.view_init(elev=20, azim=45)
        self.ax.grid(True, alpha=0.3)
        self.canvas.draw()
    
    def show_split_preview_with_highlight(self, highlighted_part_bounds=None, highlighted_part_num=None):
        """Show split preview with optional part highlighting and 3D model"""
        if not self.split_preview or not self.model_bounds:
            messagebox.showwarning("Warning", "Load model and analyze split configuration first")
            return
        
        self.ax.clear()
        
        # Draw 3D model first (if available)
        if self.mesh:
            vertices = self.mesh.vertices
            faces = self.mesh.faces
            
            # Subsample faces for performance
            max_faces = 2000
            if len(faces) > max_faces:
                step = len(faces) // max_faces
                sampled_faces = faces[::step]
            else:
                sampled_faces = faces
            
            # Create 3D surface collection
            from mpl_toolkits.mplot3d.art3d import Poly3DCollection
            
            triangles = []
            colors = []
            
            for face in sampled_faces:
                triangle = vertices[face]
                triangles.append(triangle)
                
                # Semi-transparent model color
                colors.append((0.7, 0.7, 0.7, 0.3))  # Light gray, semi-transparent
            
            # Render mesh surfaces
            if triangles:
                poly_collection = Poly3DCollection(triangles,
                                                 facecolors=colors,
                                                 edgecolors='none',  # No edges for cleaner look
                                                 alpha=0.3)
                self.ax.add_collection3d(poly_collection)
        
        # Draw original model bounding box
        min_x, max_x, min_y, max_y, min_z, max_z = self.model_bounds
        
        vertices = [
            [min_x, min_y, min_z], [max_x, min_y, min_z],
            [max_x, max_y, min_z], [min_x, max_y, min_z],
            [min_x, min_y, max_z], [max_x, min_y, max_z],
            [max_x, max_y, max_z], [min_x, max_y, max_z]
        ]
        
        edges = [
            [0, 1], [1, 2], [2, 3], [3, 0],  # bottom
            [4, 5], [5, 6], [6, 7], [7, 4],  # top
            [0, 4], [1, 5], [2, 6], [3, 7]   # vertical
        ]
        
        # Draw model outline
        for edge in edges:
            points = [vertices[edge[0]], vertices[edge[1]]]
            xs, ys, zs = zip(*points)
            self.ax.plot(xs, ys, zs, 'k-', linewidth=2, alpha=0.7)
        
        # Draw split boundaries with different colors
        colors = ['red', 'blue', 'green', 'orange', 'purple', 'cyan', 'magenta', 'yellow']
        
        for i, part in enumerate(self.split_preview):
            x_min, x_max, y_min, y_max, z_min, z_max = part['bounds']
            part_num = part['part_number']
            
            # Check if this is the highlighted part
            is_highlighted = (highlighted_part_bounds and 
                            abs(x_min - highlighted_part_bounds[0]) < 0.1 and
                            abs(x_max - highlighted_part_bounds[1]) < 0.1 and
                            abs(y_min - highlighted_part_bounds[2]) < 0.1 and
                            abs(y_max - highlighted_part_bounds[3]) < 0.1 and
                            abs(z_min - highlighted_part_bounds[4]) < 0.1 and
                            abs(z_max - highlighted_part_bounds[5]) < 0.1)
            
            if is_highlighted:
                color = 'lime'  # Bright green for highlighted part
                linewidth = 3
                alpha = 1.0
            else:
                color = colors[i % len(colors)]
                linewidth = 1.5
                alpha = 0.8
            
            # Create split box vertices
            split_vertices = [
                [x_min, y_min, z_min], [x_max, y_min, z_min],
                [x_max, y_max, z_min], [x_min, y_max, z_min],
                [x_min, y_min, z_max], [x_max, y_min, z_max],
                [x_max, y_max, z_max], [x_min, y_max, z_max]
            ]
            
            # Draw split boundaries
            for edge in edges:
                points = [split_vertices[edge[0]], split_vertices[edge[1]]]
                xs, ys, zs = zip(*points)
                self.ax.plot(xs, ys, zs, color=color, linewidth=linewidth, alpha=alpha)
            
            # Add part number labels
            center_x = (x_min + x_max) / 2
            center_y = (y_min + y_max) / 2
            center_z = (z_min + z_max) / 2
            
            if is_highlighted:
                self.ax.text(center_x, center_y, center_z, f'P{part_num} *', 
                            fontsize=10, color=color, weight='bold')
            else:
                self.ax.text(center_x, center_y, center_z, f'P{part_num}', 
                            fontsize=8, color=color, weight='bold')
        
        # Set title
        if highlighted_part_num:
            self.ax.set_title(f'Split Preview - Processing Part {highlighted_part_num} *')
        else:
            self.ax.set_title(f'Split Preview ({len(self.split_preview)} parts)')
        
        self.ax.set_xlabel('X (mm)')
        self.ax.set_ylabel('Y (mm)')
        self.ax.set_zlabel('Z (mm)')
        
        # Set axis limits with padding
        padding = 20
        self.ax.set_xlim(min_x - padding, max_x + padding)
        self.ax.set_ylim(min_y - padding, max_y + padding)
        self.ax.set_zlim(min_z - padding, max_z + padding)
        
        self.ax.view_init(elev=20, azim=45)
        self.ax.grid(True, alpha=0.3)
        self.canvas.draw()
    
    def start_splitting(self):
        """Begin mesh splitting operation"""
        if not self.mesh:
            messagebox.showerror("Error", "Load model first")
            return
        
        if not self.output_dir.get():
            messagebox.showerror("Error", "Select output directory")
            return
        
        thread = threading.Thread(target=self._split_model_thread)
        thread.daemon = True
        thread.start()
    
    def _split_model_thread(self):
        """Execute mesh splitting using proper intersection method"""
        try:
            self.split_button.configure(state='disabled')
            self.progress.configure(mode='determinate', maximum=len(self.split_preview))
            self.progress['value'] = 0
            self.status_label.configure(text="Splitting model...", foreground="orange")
            
            base_name = Path(self.input_file.get()).stem
            output_path = self.output_dir.get()
            
            if len(self.split_preview) == 1:
                messagebox.showinfo("Info", "Model fits in build volume - no splitting required")
                return
            
            parts_created = 0
            
            print(f"Starting split operation on {len(self.mesh.faces)} triangles")
            
            # Show grid preview first
            self.root.after(0, self.show_split_preview)
            import time
            time.sleep(0.5)  # Show grid for 0.5 seconds
            
            # Process each split segment using proper intersection
            for i, part in enumerate(self.split_preview):
                x_min, x_max, y_min, y_max, z_min, z_max = part['bounds']
                part_num = part['part_number']
                
                # Update progress and status
                self.root.after(0, lambda p=i+1: self.progress.configure(value=p))
                self.root.after(0, lambda p=part_num: self.status_label.configure(
                    text=f"Processing part {p}...", foreground="orange"))
                
                # Show part preview animation with grid
                self.root.after(0, lambda bounds=part['bounds'], num=part_num: 
                              self.show_split_preview_with_highlight(bounds, num))
                
                # Force GUI update
                self.root.after(0, self.root.update)
                
                print(f"Processing part {part_num}: bounds ({x_min:.1f}, {y_min:.1f}, {z_min:.1f}) to ({x_max:.1f}, {y_max:.1f}, {z_max:.1f})")
                
                try:
                    # Try intersection method first (for watertight models)
                    try:
                        # Create bounding box for this part
                        bounds_box = trimesh.creation.box(
                            extents=(x_max - x_min, y_max - y_min, z_max - z_min),
                            transform=trimesh.transformations.translation_matrix(
                                [(x_max + x_min) / 2, (y_max + y_min) / 2, (z_max + z_min) / 2]
                            )
                        )
                        
                        # Intersect the mesh with the bounding box
                        section = self.mesh.intersection(bounds_box)
                        
                        # Check if the section contains geometry
                        if section.is_empty:
                            print(f"Part {part_num}: No geometry in bounds - skipped")
                            # Wait a bit to show the preview
                            import time
                            time.sleep(0.01)
                            continue
                        
                        # Export the part
                        output_filename = f"{base_name}_part_{part_num:02d}.stl"
                        output_filepath = os.path.join(output_path, output_filename)
                        
                        # Use trimesh export
                        section.export(output_filepath)
                        parts_created += 1
                        
                        print(f"Part {part_num}: SUCCESS - {len(section.faces)} triangles, {len(section.vertices)} vertices → {output_filename}")
                        
                        # Wait a bit to show the preview
                        import time
                        time.sleep(0.01)
                        
                    except Exception as intersection_error:
                        # Fallback to vertex filtering method for non-watertight models
                        print(f"Part {part_num}: Intersection failed ({intersection_error}), trying fallback method...")
                        
                        # Get original mesh data
                        original_vertices = self.mesh.vertices
                        original_faces = self.mesh.faces
                        
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
                        
                        if not valid_faces:
                            print(f"Part {part_num}: No faces found in bounds - skipped")
                            import time
                            time.sleep(0.01)
                            continue
                        
                        # Extract valid faces and their vertices
                        part_faces = original_faces[valid_faces]
                        
                        # Get all unique vertices used by these faces
                        unique_vertex_indices = np.unique(part_faces.flatten())
                        part_vertices = original_vertices[unique_vertex_indices]
                        
                        # Reindex faces to use new vertex indices
                        vertex_map = {old_idx: new_idx for new_idx, old_idx in enumerate(unique_vertex_indices)}
                        reindexed_faces = np.array([[vertex_map[vertex] for vertex in face] for face in part_faces])
                        
                        # Export the part using simple STL writer
                        output_filename = f"{base_name}_part_{part_num:02d}.stl"
                        output_filepath = os.path.join(output_path, output_filename)
                        
                        self.write_stl_simple(output_filepath, part_vertices, reindexed_faces)
                        parts_created += 1
                        
                        print(f"Part {part_num}: SUCCESS (fallback) - {len(reindexed_faces)} triangles, {len(part_vertices)} vertices → {output_filename}")
                        
                        # Wait a bit to show the preview
                        import time
                        time.sleep(0.01)
                    
                except Exception as part_error:
                    print(f"Error processing part {part_num}: {part_error}")
                    continue
            
            # Show final result and return to full model view
            self.root.after(0, self.refresh_3d_view)
            self.root.after(0, lambda: self.status_label.configure(
                text=f"Completed: {parts_created} parts created", foreground="green"))
            
            if parts_created > 0:
                messagebox.showinfo("Success", 
                                  f"Model split into {parts_created} parts.\n"
                                  f"Files saved to: {output_path}")
            else:
                messagebox.showerror("Error", "No valid parts were created.\n"
                                   "Please check the console for details.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Splitting failed: {str(e)}")
            print(f"Split operation error: {e}")
        finally:
            self.progress.configure(mode='indeterminate')
            self.progress.stop()
            self.split_button.configure(state='normal')
            self.status_label.configure(text="Ready", foreground="green")

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

def main():
    """Application entry point"""
    try:
        import matplotlib
        matplotlib.use('TkAgg')
    except ImportError:
        print("ERROR: Missing matplotlib library! Install: pip install matplotlib")
        return
    
    try:
        import numpy as np
    except ImportError:
        print("ERROR: Missing numpy library! Install: pip install numpy")
        return
    
    root = tk.Tk()
    app = STL3DTrimeshSplitterGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()