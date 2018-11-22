import time

import scipy
import scipy.optimize
import scipy.sparse
import scipy.sparse.linalg
from scipy.spatial import cKDTree

from morphic import core

class BoundElementPoint:
    
    def __init__(self, element_id, xi, data_label, data_index=None,
            fields=None, weight=1):
        self._class_ = 'elem'
        self.eid = element_id
        self.xi = xi
        self.fields = fields
        self.data = data_label
        self.data_index = data_index
        self.bind_weight = weight
        
        self.param_ids = None
        self.param_weights = None
        self.num_fields = 0
        self.num_elem_fields = 0
        self.data_ids = None
    
    def get_field_id(self, field_index):
        return self.fields[field_index]
        
    def get_bind_weight(self):
        return self.bind_weight
        
    def get_param_ids(self, field_index):
        return self.param_ids[self.fields[field_index]]
        
    def get_param_weights(self, field):
        return self.param_weights * self.bind_weight
        
    def update_from_mesh(self, mesh):
        element = mesh.elements[self.eid]
        self.param_ids = element._get_param_indicies()
        self.param_weights = element.weights(self.xi)[0]
        self.num_fields = len(self.param_ids)
        self.num_elem_fields = len(self.param_ids)
        
        if self.fields == None:
            self.fields = range(self.num_fields)
        else:
            self.num_fields = len(self.fields)
        
    def get_data(self, data, field, mesh):
        if self.data_index == None:
            return data[self.data].get_data(self.data_ids)[field]
        else:
            #~ print data[self.data].values.shape
            #~ print self.data_index, self.fields, field
            #~ print data[self.data].values[self.data_index, field]
            return data[self.data].values[self.data_index, field]
        
        

class BoundNodeValue:
    
    def __init__(self, node_id, field_id, comp_id, data_label, index=None, weight=1):
        self._class_ = 'node'
        self.nid = node_id
        self.field_id = field_id
        self.comp_id = comp_id
        self.data = data_label
        self.data_index = index
        self.bind_weight = weight
        
        self.param_ids = None
        self.param_weights = 1
        self.num_fields = 1
        self.data_ids = None
        
    def get_field_id(self, field):
        return self.field_id
        
    def get_bind_weight(self):
        return self.bind_weight
        
    def get_param_ids(self, field):
        return [self.param_ids]
        
    def get_param_weights(self, field):
        return [self.param_weights * self.bind_weight]
        
    def update_from_mesh(self, mesh):
        node = mesh.nodes[self.nid]
        self.param_ids = node._get_param_indicies()[self.field_id][self.comp_id]
    
    def get_data(self, data, field, mesh):
        if self.data_index == None:
            x = mesh.nodes[self.nid].values[0]
            xc = data[self.data].find_closest(x, 1)
            if isinstance(xc, scipy.ndarray):
                return xc[field]
            else:
                return xc
        else:
            return data[self.data].values[self.data_index, field]
        

class Data:
    
    def __init__(self, label, values):
        self.id = label
        self.values = values
        self.tree = None
        if isinstance(self.values, scipy.ndarray):
            if len(values.shape) == 2 and values.shape[0] > 1:
                self.tree = cKDTree(self.values)
            else:
                self.xc = values
        else:
            self.values = self.values * scipy.ones((10)) ### HACK ####
            self.xc = self.values * scipy.ones((10)) ### HACK ####
                
            
        self.row_ind = 0
        self.Phi = None
        self.ii = None
        self.err_sqr_sum = None
        self.num_err = None
    
    def init_phi(self, M, N):
        self.row_ind = 0
        self.Phi = scipy.sparse.lil_matrix((M, N))
    
    def add_point(self, point):
        if point._class_ == 'elem' and self.tree != None:
            point.data_ids = []
            for pids in point.param_ids:
                self.Phi[self.row_ind, pids] = point.param_weights
                point.data_ids.append(self.row_ind)
                self.row_ind += 1
                
    def update_point_data(self, params):
        if self.Phi != None and self.tree != None:
            xd = self.Phi.dot(params)
            rr, ii = self.tree.query(xd.reshape((xd.size/self.values.shape[1], self.values.shape[1])))
            self.xc = self.values[ii, :].reshape(xd.size)
            self.num_err = rr.shape[0]
            self.err_sqr_sum = (rr*rr).sum()
    
    def get_data(self, ind):
        if ind == None:
            return self.xc
        return self.xc[ind]
    
    def find_closest(self, x, num=1):
        if self.tree:
            r, ii = self.tree.query(list(x))
            return self.values[ii]
        else:
            return self.values
        

class Fit:
    
    def __init__(self, method='data_to_mesh_closest'):
        self.points = core.ObjectList()
        self.data = core.ObjectList()
        self.method = method
        
        self._objfns = {
            'd2mp': self.objfn_data_to_mesh_project,
            'd2mc': self.objfn_data_to_mesh_closest,
            'm2dc': self.objfn_mesh_to_data_closest,
            'data_to_mesh_project': self.objfn_data_to_mesh_project,
            'data_to_mesh_closest': self.objfn_data_to_mesh_closest,
            'mesh_to_data_closest': self.objfn_mesh_to_data_closest
            }
        
        if isinstance(method, str):
            self.objfn = self._objfns[method]
        
        self.on_start = None
        self.objective_function = None
        self.on_stop = None
        
        self.X = None
        self.Xi = None
        self.A = None
        self.invA = None
        
        self.svd_UT, self.svd_S, self.svd_VT = None, None, None
        self.svd_invA = None
        
        
        self.use_sparse = True
        self.param_ids = []
        self.num_dof = 0
        self.num_rows = 0
        
    def bind_element_point(self, element_id, xi, data,
            data_index=None, fields=None, weight=1):
        
        if not isinstance(data, str):
            label_not_in_data = True
            while label_not_in_data:
                data_label = '_' + str(element_id) + '_' + \
                        str(int(1000000 + 1000000 * scipy.rand()))
                if data_label not in self.data.keys():
                    label_not_in_data = False
                    
            self.set_data(data_label, data)
            data = data_label
        
        self.points.add(BoundElementPoint(element_id, xi, data,
                data_index=data_index, fields=fields, weight=weight))
    
    def bind_node_value(self, node_id, field_id, comp_id,
            data, index=None, weight=1):
        
        if not isinstance(data, str):
            data_label = '_' + str(node_id) + '_' + str(field_id) + \
                    '_' + str(comp_id) + '_' + \
                    str(int(1000000 * scipy.rand()))
            self.set_data(data_label, data)
            data = data_label
        if isinstance(node_id, list):
            for nid in node_id:
                self.points.add(BoundNodeValue(
                        nid, field_id, comp_id, data, index=index,
                        weight=weight))
        else:
            self.points.add(BoundNodeValue(
                    node_id, field_id, comp_id, data, index=index,
                    weight=weight))
    
    def set_data(self, label, values):
        self.data.add(Data(label, values))
    
    def get_data(self, mesh):
        Xd = scipy.zeros(self.num_rows)
        for ind, dm in enumerate(self.data_map):
            Xd[ind] = self.points[dm[0]].get_data(self.data, dm[1], mesh)
        return Xd
    
    def delete_all_data(self):
        self.data.reset_object_list()
    
    def get_column_index(self, param_ids):
        return [self.param_ids.index(pid) for pid in param_ids]
    
    def update_from_mesh(self, mesh):
        for point in self.points:
            point.update_from_mesh(mesh)
        self.generate_matrix()
    
    def generate_matrix(self):
        param_ids = []
        self.num_rows = 0
        for point in self.points:
            self.num_rows += point.num_fields
            if isinstance(point.param_ids, int):
                param_ids.extend([point.param_ids])
            elif isinstance(point.param_ids[0], list):
                param_ids.extend([item for sublist in point.param_ids
                        for item in sublist])
            else:
                param_ids.extend([item for item in point.param_ids])
        
        self.param_ids = [pid for pid in set(param_ids)]
        self.param_ids.sort()
        self.num_dof = len(self.param_ids)
        self.W = scipy.ones(self.num_rows)
        self.data_map = []
        
        if self.use_sparse:
            self.A = scipy.sparse.lil_matrix((self.num_rows, self.num_dof))
        
        else:
            self.A = scipy.zeros((self.num_rows, self.num_dof))
        
        row_ind = -1
        for pid, point in enumerate(self.points):
            bind_weight = point.get_bind_weight()
            for field_ind in range(point.num_fields):
                field = point.get_field_id(field_ind)
                weights = point.get_param_weights(field_ind)
                param_ids = point.get_param_ids(field_ind)
                cols = self.get_column_index(param_ids)
                row_ind += 1
                self.data_map.append([pid, field])
                for col, weight in zip(cols, weights):
                    self.A[row_ind, col] += weight
                    self.W[row_ind] = bind_weight
        
        if self.use_sparse:
            self.A = self.A.tocsc()
    
    def generate_fast_data(self):
        num_rows = {}
        for point in self.points:
            if point._class_ == 'elem':
                if point.data_index == None:
                    if point.data not in num_rows.keys():
                        num_rows[point.data] = 0
                    num_rows[point.data] += point.num_elem_fields
                    
        for key in num_rows.keys():
            self.data[key].init_phi(num_rows[key], self.num_dof)
        
        for point in self.points:
            if point._class_ == 'elem':
                if point.data_index == None:
                    self.data[point.data].add_point(point)
        
        
    def invert_matrix(self):
        from sparsesvd import sparsesvd
        self.svd_UT, self.svd_S, self.svd_VT = sparsesvd(self.A, self.A.shape[1])
        self.svd_invA = scipy.dot(\
            scipy.dot(self.svd_VT.T,scipy.linalg.inv(scipy.diag(self.svd_S))),self.svd_UT)
    
    
    def solve(self, mesh, max_iterations=1000, drms=1e-9, output=False):
        td, ts = 0, 0
        
        for data in self.data:
            data.update_point_data(mesh._core.P[self.param_ids])
        
        rms_err0 = self.compute_rms_err()
        
        drms_iter = 1e99
        
        niter = 0
        while drms_iter > drms and niter < max_iterations:
            niter += 1
            
            t0 = time.time()
            Xd = self.get_data(mesh) * self.W
            t1 = time.time()
            
            if self.svd_invA==None:
                self.lsqr_result = scipy.sparse.linalg.lsqr(self.A, Xd)
                solved_x = self.lsqr_result[0]
            else:
                solved_x = scipy.dot(self.svd_invA, Xd)
                
            mesh.update_parameters(self.param_ids, solved_x)
            t2 = time.time()
            
            for data in self.data:
                data.update_point_data(mesh._core.P[self.param_ids])
            
            rms_err1 = self.compute_rms_err()
            drms_iter = scipy.absolute(rms_err0 - rms_err1)
            rms_err0 = rms_err1
            t3 = time.time()
            
            td += (t1 - t0) + (t3 - t2)
            ts += t2 - t1
            
        if output:
            print 'Solve time: %4.2fs, (%4.2fs, %4.2fs)' % (ts+td, ts, td)
            if rms_err0 < 1e-2:
                print 'RMS err: %4.3e (iterations = %d)' % (rms_err0, niter)
            else:
                print 'RMS err: %4.3f (iterations = %d)' % (rms_err0, niter)
        
        return mesh, rms_err0
    
    def compute_rms_err(self):
        err_sqr_sum = 0
        num_err = 0
        for data in self.data:
            if data.err_sqr_sum != None and data.num_err != None:
                err_sqr_sum += data.err_sqr_sum
                num_err += data.num_err
        if num_err > 0:
            return scipy.sqrt(err_sqr_sum/num_err)
        else:
            return scipy.sqrt(err_sqr_sum)
            
            
    def optimize(self, mesh, Xd, ftol=1e-9, xtol=1e-9, maxiter=0, output=True):
        
        mesh.generate()
        
        Td = cKDTree(Xd)
        
        x0 = mesh.get_variables()
        t0 = time.time()
        x, success = scipy.optimize.leastsq(self.objfn, x0,
                args=[mesh, Xd, Td], ftol=ftol, xtol=xtol,
                maxfev=maxiter)
        if output: print 'Fit Time: ', time.time()-t0
        mesh.set_variables(x)
        return mesh
    
    def optimize2(self, mesh, data, ftol=1e-9, xtol=1e-9, maxiter=0, output=True):
        
        mesh.generate()
        
        if self.on_start != None:
            mesh, data = self.on_start(mesh, data)
        
        x0 = mesh.get_variables()
        t0 = time.time()
        x, success = scipy.optimize.leastsq(self.objective_function,
                x0, args=[mesh, data], ftol=ftol, xtol=xtol,
                maxfev=maxiter)
                
        if output: print 'Fit Time: ', time.time()-t0
        mesh.set_variables(x)
        mesh.update()
        
        if self.on_stop != None:
            mesh, data = self.on_stop(mesh, data)
        
        return mesh
    
    def objfn_mesh_to_data_closest(self, x0, args):
        mesh, Xd, Td = args[0], args[1], args[2]
        mesh.set_variables(x0)
        NXi = self.Xi.shape[0]
        ind = 0
        for element in mesh.elements:
            self.X[ind:ind+NXi,:] = element.evaluate(self.Xi)
            ind += NXi
        err = Td.query(list(self.X))[0]
        return err*err
    
    def objfn_data_to_mesh_closest(self, x0, args):
        mesh, Xd, Td = args[0], args[1], args[2]
        mesh.set_variables(x0)
        NXi = self.Xi.shape[0]
        ind = 0
        for element in mesh.elements:
            self.X[ind:ind+NXi,:] = element.evaluate(self.Xi)
            ind += NXi
        Tm = cKDTree(self.X)
        err = Tm.query(list(Xd))[0]
        self.err = err
        return err*err
    
    def objfn_data_to_mesh_project(self, x0, args):
        mesh, Xd, Td = args[0], args[1], args[2]
        mesh.set_variables(x0)
        err = scipy.zeros(Xd.shape[0])
        ind = 0
        for xd in Xd:
            xi1 = mesh.elements[1].project(xd)
            xi2 = mesh.elements[2].project(xd)
            if 0<=xi1<=1:
                xi = xi1
            elif 0<=xi2<=1:
                xi = xi2
            else:
                Xi = scipy.array([xi1, xi1-1, xi2, xi2-1])
                Xi2 = Xi*Xi
                ii = Xi2.argmin()
                xi = Xi[ii]
                if ii < 2:
                    elem = 1
                else:
                    elem = 2
            dx = mesh.elements[elem].evaluate(scipy.array([xi]))[0] - xd
            err[ind] = scipy.sum(dx * dx)
            ind += 1
        return err
