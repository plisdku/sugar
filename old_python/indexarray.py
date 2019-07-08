import numpy as np
import logging

class IndexArray3:
    """Store lists of integers (e.g. some object IDs) in a grid for quick spatial lookup.
    """
    
    def __init__(self, size_xyz, num_xyz, max_indices_per_cell=10):
        self.size_xyz = np.array(size_xyz)
        self.num_xyz = np.array(num_xyz)
        self.dxyz = self.size_xyz / self.num_xyz
        self.index_array = np.full((self.num_xyz[0], self.num_xyz[1], self.num_xyz[2], max_indices_per_cell), -1, dtype=int)
        
    def increment_max_particles(self):
        """Increase the size of self.index_array by one in each cell to accomodate more particles"""
        logging.info(f"Increasing size of index array to {self.index_array.shape[-1]+1}")
        shape = self.index_array.shape[:-1] + (self.index_array.shape[-1]+1,)
        new_index_array = np.full(shape, -1, dtype=int)
        new_index_array[...,:-1] = self.index_array
        self.index_array = new_index_array
        
    def xlines(self):
        return np.linspace(0.0, self.size_xyz[0], self.index_array.shape[0]+1)
    
    def ylines(self):
        return np.linspace(0.0, self.size_xyz[1], self.index_array.shape[1]+1)
    
    def zlines(self):
        return np.linspace(0.0, self.size_xyz[2], self.index_array.shape[2]+1)
    
    def get_cell(self, xyz):
        """Return cell index containing point xyz
        
        No bounds checking is performed.  This function can return cell indices that lie outside the grid.
        
        Args:
            xyz (np.ndarray): point to check
        
        Returns:
            np.ndarray: i and j indices of cell containing xy
        """
        return (np.asarray(xyz) // self.dxyz).astype(int)
        
    def add(self, idx, point):
        """Add index to cell corresponding to point
        """
        ii,jj,kk = self.get_cell(point)
        
        for nn in range(self.index_array.shape[3]):
            if self.index_array[ii,jj,kk,nn] == -1:
                self.index_array[ii,jj,kk,nn] = idx
                return
        
        self.increment_max_particles()
        self.add(idx, point)
#         raise Exception(f"Cannot add index {idx} to grid because cell {ii}, {jj}, {kk} is full.")
        
    def remove(self, idx, point):
        """Remove index from cell corresponding to point
        """
        ii,jj,kk = self.get_cell(point)
        
        for nn in range(self.index_array.shape[3]):
            if self.index_array[ii,jj,kk,nn] == idx:
                # Erase from here
                for mm in range(self.index_array.shape[3]-1, nn):
                    if self.index_array[ii,jj,kk,mm] != -1:
                        self.index_array[ii,jj,kk,nn] = self.index_array[ii,jj,kk,mm]
                        self.index_array[ii,jj,kk,mm] = -1
                        return
                self.index_array[ii,jj,kk,nn] = -1
                return
        
        raise Exception(f"Cannot remove index {idx} from grid because it is not present in cell {ii}, {jj}, {kk}")
        
    def move(self, idx, old_point, new_point):
        """Move index from one cell to another as necessary.
        """
        
        i0,j0,k0 = self.get_cell(old_point)
        i1,j1,k1 = self.get_cell(new_point)
        
        if i0 != i1 or j0 != j1 or k0 != k1:
            self.remove(idx, old_point)
            self.add(idx, new_point)
        
    def count(self):
        """Return number of indices in cell ii,jj,kk
        """
        grid_count = np.sum(self.index_array != -1, axis=3)
        return grid_count
    
    def at(self, ii, jj, kk):
        """Return list of indices in cell ii,jj,kk
        """
        indices = np.where(self.index_array[ii,jj,kk,:] != -1)[0]
        if len(indices) == 0:
            indices = np.zeros(0, dtype=int)
        return self.index_array[ii,jj,kk,indices]
    
    
    
    
   