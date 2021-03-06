import random
import numpy as np
import cv2
import lmdb
import torch
import torch.utils.data as data
import data.util as util


class LQGTDataset(data.Dataset):
    '''
    Read LQ (Low Quality, here is LR) and GT image pairs.
    If only GT image is provided, generate LQ image on-the-fly.
    The pair is ensured by 'sorted' function, so please check the name convention.
    '''

    def __init__(self, opt):
        super(LQGTDataset, self).__init__()
        self.opt = opt
        self.data_type = self.opt['data_type']
        self.paths_LQ, self.paths_GT = None, None
        self.sizes_LQ, self.sizes_GT = None, None
        self.LQ_env, self.GT_env = None, None  # environment for lmdb

        self.paths_GT, self.sizes_GT = util.get_image_paths(self.data_type, opt['dataroot_GT'])
        self.paths_LQ, self.sizes_LQ = util.get_image_paths(self.data_type, opt['dataroot_LQ'])
        assert self.paths_GT, 'Error: GT path is empty.'
        if self.paths_LQ and self.paths_GT:
            assert len(self.paths_LQ) == len(
                self.paths_GT
            ), 'GT and LQ datasets have different number of images - {}, {}.'.format(
                len(self.paths_LQ), len(self.paths_GT))
        self.random_scale_list = [1]

    def _init_lmdb(self):
        # https://github.com/chainer/chainermn/issues/129
        self.GT_env = lmdb.open(self.opt['dataroot_GT'], readonly=True, lock=False, readahead=False,
                                meminit=False)
        self.LQ_env = lmdb.open(self.opt['dataroot_LQ'], readonly=True, lock=False, readahead=False,
                                meminit=False)

    def __getitem__(self, index):
        if self.data_type == 'lmdb':
            if (self.GT_env is None) or (self.LQ_env is None):
                self._init_lmdb()
        GT_path, LQ_path = None, None
        scale = self.opt['scale']
        GT_size = self.opt['GT_size']

        # get GT image
        GT_path = self.paths_GT[index]
        if self.data_type == 'lmdb':
            resolution = [int(s) for s in self.sizes_GT[index].split('_')]
        else:
            resolution = None
        img_GT1 = util.read_img(self.GT_env, GT_path, resolution)
        H2=np.size(img_GT1,0)
        W2=np.size(img_GT1,1)
        img_GT=img_GT1.reshape((1,H2,W2))
#        if img_GT1.ndim == 2:
#            img_GT1 = cv2.cvtColor(img_GT1, cv2.COLOR_GRAY2BGR)

#        img_GT[0,:,:]=img_GT1
#        img_GT[1,:,:]=img_GT1
#        img_GT[2,:,:]=img_GT1
        if img_GT.ndim == 2:
            img_GT = cv2.cvtColor(img_GT, cv2.COLOR_GRAY2BGR)
        


        # get LQ image
        if self.paths_LQ:
            LQ_path = self.paths_LQ[index]
            if self.data_type == 'lmdb':
                resolution = [int(s) for s in self.sizes_LQ[index].split('_')]
            else:
                resolution = None
            img_LQ1 = util.read_img(self.LQ_env, LQ_path, resolution)
#            if img_LQ1.ndim == 2:
#                img_LQ1 = cv2.cvtColor(img_LQ1, cv2.COLOR_GRAY2BGR)
            H=np.size(img_LQ1,0)
            W=np.size(img_LQ1,1)
            img_LQ=img_LQ1.reshape((1,H,W))

#            img_LQ[0,:,:]=img_LQ1
#            img_LQ[1,:,:]=img_LQ1
#            img_LQ[2,:,:]=img_LQ1

        else:  # down-sampling on-the-fly
            # randomly scale during training
            if self.opt['phase'] == 'train':

                # force to 3 channels
                if img_GT.ndim == 2:
                    img_GT = cv2.cvtColor(img_GT, cv2.COLOR_GRAY2BGR)


        img_GT = torch.from_numpy(np.ascontiguousarray(img_GT)).float()
        img_LQ = torch.from_numpy(np.ascontiguousarray(img_LQ)).float()
        img_GT = torch.from_numpy(np.ascontiguousarray(img_GT)).float()
        img_LQ = torch.from_numpy(np.ascontiguousarray(img_LQ)).float()
        if LQ_path is None:
            LQ_path = GT_path
        return {'LQ': img_LQ, 'GT': img_GT, 'LQ_path': LQ_path, 'GT_path': GT_path}

    def __len__(self):
        return len(self.paths_GT)
