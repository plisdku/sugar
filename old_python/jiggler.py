import numpy as np
from particlegrid3 import ParticleGrid3


class Jiggler:
    def __init__(self, size, initial_strain, max_particle_radius, accel=1.1, decel=0.9, strain_accel=1.1, strain_decel=0.9, use_force=False):
        self.particle_grid = ParticleGrid3(size, initial_strain, max_particle_radius=max_particle_radius)
        
        # The size of the force is 1 from a particle across the entire space.
        # The force from a touching particle should typically be about
        # d / (radius0 + radius1) >= 0.5*d / max_radius.
        #
        # If the std of the randomness is sigma, then I think I would like
        # to have sigma = force scale, or sigma = 0.5*d / max_radius.
        # 
        # This ended up being about 5x too big so I am shrinking it again.
        
        if use_force:
            d = np.linalg.norm(size)
            big_force = 0.5*d/max_particle_radius
            self.force_factor = 0.25 / big_force
        else:
            self.force_factor = 0.0
        
        self.dtheta_scale = 0.01
        self.dxy_scale = 0.005
        self.dstrain_scale = 0.0001
        
        self.accel = accel
        self.decel = decel
        
        self.strain_accel = strain_accel
        self.strain_decel = strain_decel
        
        self.theta_scales = []
        self.dxy_scales = []
        self.strain_scales = []
        
        self.num_theta_accepted = 0
        self.num_theta_rejected = 0
        self.num_xy_accepted = 0
        self.num_xy_rejected = 0
        self.num_strain_accepted = 0
        self.num_strain_rejected = 0
        
        self.strain_accepted = []
        self.rotate_x_accepted = []
        self.translate_accepted = []
        
    def try_rotation(self):
        idx_particle = np.random.randint(0, len(self.particle_grid.particles))
        dtheta = self.dtheta_scale*np.random.randn()
        
        particle = self.particle_grid.particles[idx_particle]
        
        perturbed_particle = particle.copy()
        perturbed_particle.rotate_x(self.dtheta_scale*np.random.randn())
        perturbed_particle.rotate_y(self.dtheta_scale*np.random.randn())
        perturbed_particle.rotate_z(self.dtheta_scale*np.random.randn())
        
        # Temporarily swap in the perturbed particle.  This works if the centroid is not moving.
        self.particle_grid.particles[idx_particle] = perturbed_particle
        
        if self.particle_grid.has_intersection(perturbed_particle):
            # Undo the swap.
            self.particle_grid.particles[idx_particle] = particle
            self.dtheta_scale *= self.decel
            self.num_theta_rejected += 1
        else:
            # Keep the swap.
            self.dtheta_scale = min(self.dtheta_scale*self.accel, 2*np.pi)
            self.num_theta_accepted += 1
            pass
        
    def try_move(self):
        idx_particle = np.random.randint(0, len(self.particle_grid.particles))
        
        particle = self.particle_grid.particles[idx_particle]
        
        if self.force_factor != 0.0:
            force = self.particle_grid.force(particle)
            dxy = self.dxy_scale * (np.random.randn(3) + force*self.force_factor)
        else:
            dxy = self.dxy_scale * np.random.randn(3)
        
        perturbed_particle = particle.copy()
        perturbed_particle.translate(dxy)
        perturbed_particle.centroid %= self.particle_grid.size_xyz
        
        # Temporarily swap in the perturbed particle and update the grid.
        self.particle_grid.particles[idx_particle] = perturbed_particle
        self.particle_grid.index_array.move(idx_particle, particle.centroid, perturbed_particle.centroid)
        
        if self.particle_grid.has_intersection(perturbed_particle):
            # Undo the swap and move the particle back
            self.particle_grid.particles[idx_particle] = particle
            self.particle_grid.index_array.move(idx_particle, perturbed_particle.centroid, particle.centroid)
            self.dxy_scale *= self.decel
            self.num_xy_rejected += 1
        else:
            # Keep the swap.
            self.dxy_scale = min(self.dxy_scale*self.accel, self.particle_grid.size_xyz[0])
            self.num_xy_accepted += 1
            pass
        
    
    def try_perturb_strain(self):
        
        max_allowable_radius = self.particle_grid.index_array.dxyz.min()/2
        max_particle_radius = self.particle_grid.strain * np.max([p.radius for p in self.particle_grid.particles])
        
        if max_particle_radius > max_allowable_radius:
            print("Rebuilding grid")
            self.particle_grid._build_index_array(2*max_particle_radius)
        
        old_strain = self.particle_grid.strain
        new_strain = old_strain * (1 + self.dstrain_scale * (-0.5 + np.random.rand()))
        
        if new_strain < old_strain:
            p_accept = 0.05 # np.exp( (new_strain - self.strain) / temperature )
            
            if np.random.rand() < p_accept:
                self.particle_grid.strain = new_strain
                self.num_strain_accepted += 1
            else:
                self.num_strain_rejected += 1
                pass
        else:
            self.particle_grid.strain = new_strain
            if self.particle_grid.has_any_intersection():
                self.particle_grid.strain = old_strain
                self.dstrain_scale *= self.strain_decel
                self.num_strain_rejected += 1
            else:
                self.dstrain_scale *= self.strain_accel
                self.num_strain_accepted += 1
                pass

        
    