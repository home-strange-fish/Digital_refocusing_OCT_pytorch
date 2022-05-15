# -*- coding: utf-8 -*-
import torch
import torch.nn as nn
#vgg = models.vgg16(pretrained=False)
pre=torch.load(r'.\experiments\pretrained_models\MSRResNetx4.pth')
pre.conv_first.weight
vgg.load_state_dict(pre)
vgg.features[0]=nn.Conv2d(1, 64, kernel_size=3, padding=1)