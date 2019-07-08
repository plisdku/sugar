from struct import pack

import numpy as np
import matplotlib.pyplot as plt

def minmax(x):
    return np.min(x), np.max(x)
    
    

    
class Cube:
    
    ii,jj,kk = np.meshgrid([-1.0,1.0], [-1.0, 1.0], [-1.0, 1.0], indexing='ij')
    ijk = np.row_stack((ii.ravel(), jj.ravel(), kk.ravel()))
    
    faces = np.array([[0,2,6,4],
                      [1,5,7,3],
                      [0,4,5,1],
                      [6,2,3,7],
                      [0,1,3,2],
                      [4,6,7,5]])
    
    tri_faces = np.array([[0,2,6], [0,6,4],
                          [1,5,7], [1,7,3],
                          [0,4,5], [0,5,1],
                          [6,2,3], [6,3,7],
                          [0,1,3], [0,3,2],
                          [4,6,7], [4,7,5]])
    
    def __init__(self, centroid, r1, r2=None, r3=None):
        self.centroid = np.array(centroid)
        if r2 is None:
            r2 = r1
        if r3 is None:
            r3 = r1
        self.radii = np.array([r1,r2,r3])
        self.axes = np.diag(self.radii)
        self.radius = np.sqrt(r1**2 + r2**2 + r3**2)
    
    def __str__(self):
        return f"Cube at {self.centroid} radii {self.radii}"
    def __repr__(self):
        return str(self)
    
    def points(self, strain=1.0):
        return self.centroid[:,None] + strain*self.axes@Cube.ijk
    
    def is_intersecting(self, other, strain=1.0, displacement=None):
        if displacement is None:
            displacement = np.zeros(3)
        
        d = self.centroid + displacement - other.centroid
        r = (self.radius + other.radius)*strain
        if d[0]**2 + d[1]**2 + d[2]**2 > r**2:
            return False
        
        # Use separating axis theorem.
        # Don't bother with the optimization for squares.  Who cares.
        
        xyz_other = other.points(strain)
        xyz_self = self.points(strain)
        
        for xyz in range(3):
            n = self.axes[:,xyz]
            min_self, max_self = minmax(n@xyz_self)
            min_other, max_other = minmax(n@xyz_other)
            
            if max_self <= min_other or min_self >= max_other:
                return False
            
        for xyz in range(3):
            n = other.axes[:,xyz]
            min_self, max_self = minmax(n@xyz_self)
            min_other, max_other = minmax(n@xyz_other)
            
            if max_self <= min_other or min_self >= max_other:
                return False
        
        return True
        
    def rotate_x(self, theta):
        """Rotate about x axis"""
        m = np.array([[1.0, 0.0, 0.0],
                      [0.0, np.cos(theta), np.sin(theta)],
                      [0.0, -np.sin(theta), np.cos(theta)]])
        self.axes = m @ self.axes
                      
    def rotate_y(self, theta):
        """Rotate about y axis"""
        m = np.array([[np.cos(theta), 0.0, -np.sin(theta)],
                      [0.0, 1.0, 0.0], 
                      [np.sin(theta), 0.0, np.cos(theta)]])
        self.axes = m @ self.axes
        
    def rotate_z(self, theta):
        """Rotate about z axis"""
        m = np.array([[np.cos(theta), np.sin(theta), 0.0],
                      [-np.sin(theta), np.cos(theta), 0.0],
                      [0.0, 0.0, 1.0]])
        
        self.axes = m @ self.axes
    
    def translate(self, dxyz):
        self.centroid += dxyz
    
    def copy(self):
        c2 = Cube(self.centroid.copy(), *self.radii)
        c2.axes = self.axes.copy()
        return c2
    
    
def _write_one_binary(this_cube, strain, fh, solid_idx):
    points = this_cube.points(strain ).T
    
    for face in Cube.tri_faces:
        face_points = points[face,:]

        normal = np.cross(face_points[1,:] - face_points[0,:], face_points[2,:] - face_points[0,:])
        normal = normal / np.linalg.norm(normal)
        
        fh.write(pack("fff", *normal))
        
        for point in face_points:
            fh.write(pack("fff", *point))
        
        fh.write(pack("h", solid_idx))
        
def write_binary(filename, particles, strain):
    
    with open(filename, "wb") as fh:
        fh.write(bytes(np.arange(80, dtype=np.byte)))
        fh.write(pack("I", 12 * len(particles)))
        for ii,particle in enumerate(particles):
            _write_one_binary(particle, strain, fh, ii)
            
# write_cubes_binary("cube_manyfaces.stl", jiggler.particle_grid.particles)