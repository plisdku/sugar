import numpy as np
import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d as a3

from indexarray import IndexArray3
import cube

class ParticleGrid3:
    """Quick spatial lookup of polygons in 2d.
    """
    def __init__(self, size_xyz, initial_strain=1.0, particles=None, max_particle_radius=None):
        
        self.particles = []
        self.size_xyz = np.array(size_xyz)
        self.diagonal_size = np.sqrt(np.sum(self.size_xyz**2))
        self.strain = initial_strain
        
        self.index_array = None
        self.dxyz = None
        self.nxyz = None
        
        if particles is not None:
            self.particles = particles
            max_radius = np.max([poly.radius() for poly in self.particles])
            self._build_index_array(max_radius*2)
        elif max_particle_radius is not None:
            self._build_index_array(max_particle_radius*2)
        else:
            raise Exception("Either particles or max_particle_radius must be given")
        
        
    def _build_index_array(self, min_cell_size):
        """Set up IndexArray for polygon IDs
        
        The IndexArray resolution is chosen based on the particle sizes, so
        a particle can only overlap particles in neighboring index array cells
        and not further away.  The array needs to be rebuilt as the particle sizes
        grow (as the strain parameter increases).
        """
        self.nxyz = (np.array(self.size_xyz) // min_cell_size).astype(int)
        self.index_array = IndexArray3(self.size_xyz, self.nxyz)

        for idx,particle in enumerate(self.particles):
            self.index_array.add(idx, particle.centroid)
    
    def has_intersection(self, particle):
        """Return True if particle intersects another particle in the grid.
        """
        for _ in self.iterate_intersections(particle):
            return True
        return False
    
    def has_any_intersection(self):
        """Return True if any particle intersects another particle in the grid.
        """
        for particle in self.particles:
            for _ in self.iterate_intersections(particle):
                return True
        return False
    
    def iterate_intersections(self, particle):
        """Iterator over indices of particles that intersect the given particle.
        """
        
        ijk = self.index_array.get_cell(particle.centroid)
        self_displacement = np.zeros(3)
        
        for ii_itr in range(ijk[0]-1, ijk[0]+2):
            i_super, ii = divmod(ii_itr, self.nxyz[0])
            self_displacement[0] = -i_super*self.size_xyz[0]
            for jj_itr in range(ijk[1]-1, ijk[1]+2):
                j_super, jj = divmod(jj_itr, self.nxyz[1])
                self_displacement[1] = -j_super*self.size_xyz[1]
                for kk_itr in range(ijk[2]-1, ijk[2]+2):
                    k_super, kk = divmod(kk_itr, self.nxyz[2])
                    self_displacement[2] = -k_super*self.size_xyz[2]
                    
                    for idx in self.index_array.at(ii,jj,kk):
                        other_particle = self.particles[idx]
                        if particle != other_particle:
                            does_intersect = particle.is_intersecting(other_particle, self.strain, self_displacement)
                            if does_intersect:
                                yield idx
    
    def force(self, particle):
        """Calculate repulsive force due to nearest particles.
        
        Let r be the displacement vector from this particle to a neighboring particle.
        Let d be the diagonal size of the entire space (a scaling factor).
        Let R be the normalized distance r/d.
        The repulsive force vector is then -R/norm(R)**2: it points away from the
        other particle and its magnitude is d/r.
        
        The force is only summed for particles in adjacent cells, for simplicity.
        """
        
        ijk = self.index_array.get_cell(particle.centroid)
        self_displacement = np.zeros(3)
        
        force = np.zeros(3)
        
        for ii_itr in range(ijk[0]-1, ijk[0]+2):
            i_super = ii_itr // self.nxyz[0]
            ii = ii_itr % self.nxyz[0]
            self_displacement[0] = -i_super*self.size_xyz[0]
            for jj_itr in range(ijk[1]-1, ijk[1]+2):
                j_super = jj_itr // self.nxyz[1]
                jj = jj_itr % self.nxyz[1]
                self_displacement[1] = -j_super*self.size_xyz[1]
                for kk_itr in range(ijk[2]-1, ijk[2]+2):
                    k_super = kk_itr // self.nxyz[2]
                    kk = kk_itr % self.nxyz[2]
                    self_displacement[2] = -k_super*self.size_xyz[2]
                    
                    for idx in self.index_array.at(ii,jj,kk):
                        other_particle = self.particles[idx]
                        if particle != other_particle:
                            displacement = other_particle.centroid - particle.centroid - self_displacement
                            distance_squared = np.sum(displacement**2)
                            force -= self.diagonal_size*(displacement/distance_squared)
        return force

    def all_intersections(self):
        out = []
        for idx, particle in enumerate(self.particles):
            out.extend(list(self.iterate_intersections(particle)))
        return np.unique(out)
    
    def add_particle(self, particle):
        
        max_allowable_radius = self.index_array.dxyz.min()/2
        if particle.radius > max_allowable_radius:
            raise Exception(f"Particle radius {particle.radius} is bigger than max allowable radius {max_allowable_radius} from cell size {self.index_array.dxyz}.")
        
        if self.has_intersection(particle):
            raise Exception("Particle would cause intersection.")
        
        new_idx = len(self.particles)
        self.particles.append(particle)
        self.index_array.add(new_idx, particle.centroid)
    
    def try_add_particle(self, genfun):
        """Attempt to add a non-intersecting polygon to the grid.
        
        This operation will fail if the generated polygons are too large for the cell size of IndexArray,
        as well as if the generated polygons intersect existing polygons.
        """
        
        max_allowable_radius = self.index_array.dxyz.min()/2
        
        max_attempts = 100
        for m in range(max_attempts):
            trial_particle = genfun()
            
            if trial_particle.radius > max_allowable_radius:
                raise Exception(f"Trial particle radius {trial_particle.radius} is bigger than max allowable radius {max_allowable_radius}")
            
            failed = False
            for other_particle in self.iterate_intersections(trial_particle):
                failed = True
                break
            if failed:
                continue
            
            new_idx = len(self.particles)
            self.particles.append(trial_particle)
            self.index_array.add(new_idx, trial_particle.centroid)
            return
        
        raise Exception(f"Compliant polygon could not be found in {max_attempts} attempts")
    
    def plt_polygons(self, show_lines=True, show_ids=False, z_cmap=None):
        
        idx_intersecting = self.all_intersections()

        for idx,particle in enumerate(self.particles):
            
            if idx in idx_intersecting:
                color = 'r'
            elif z_cmap is not None:
                f = particle.centroid[2]/self.size_xyz[2]
                color = z_cmap(f)
            else:
                color = 'g'
            
            xyz = particle.points(self.strain)
            plt.fill(xyz[0,[0,4,6,2]], xyz[1,[0,4,6,2]], color=color)
            
            if show_ids:
                plt.annotate(str(idx), particle.centroid[:2])
        
        if show_lines:
            plt.hlines(self.index_array.ylines(), 0.0, self.size_xyz[0], linewidth=0.2)
            plt.vlines(self.index_array.xlines(), 0.0, self.size_xyz[1], linewidth=0.2)
            
    def plt_polygons_3d(self, show_lines=True, show_ids=False, z_cmap=None, idx_cmap=None, colors=None):
        
        idx_intersecting = self.all_intersections()

        for idx,particle in enumerate(self.particles):
            
            if idx in idx_intersecting:
                color = 'r'
            elif z_cmap is not None:
                f = particle.centroid[2]/self.size_xyz[2]
                color = z_cmap(f)
            elif idx_cmap is not None:
                f = idx/(len(self.particles)-1)
                color = idx_cmap(f)
            elif colors is not None:
                color = colors[idx]
            else:
                color = 'g'
            
            xyz = particle.points(self.strain)
            all_vertices_list = []
            for f in cube.Cube.faces:
                vertices = xyz[:,f]
                all_vertices_list.append(vertices.T)
            polygons = a3.art3d.Poly3DCollection(all_vertices_list, color=color)
            plt.gca().add_collection3d(polygons)
            
            if show_ids:
                plt.annotate(str(idx), particle.centroid[:2])
        