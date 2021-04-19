from __future__ import print_function
import os
import datetime
import numpy as np

from models.yolo import *
import torch
# import torch.nn as nn
# from models.common import Conv, DWConv
from utils.google_utils import attempt_download
import onnx


class Ensemble(nn.ModuleList):
    # Ensemble of models
    def __init__(self):
        super(Ensemble, self).__init__()

    def forward(self, x, augment=False):
        y = []
        for module in self:
            y.append(module(x, augment)[0])
        # y = torch.stack(y).max(0)[0]  # max ensemble
        # y = torch.cat(y, 1)  # nms ensemble
        y = torch.stack(y).mean(0)  # mean ensemble
        return y, None  # inference, train output

def attempt_load(weights, map_location=None):
    # Loads an ensemble of models weights=[a,b,c] or a single model weights=[a] or weights=a
    model = Ensemble()
    for w in weights if isinstance(weights, list) else [weights]:
        attempt_download(w)
        model.append(torch.load(w, map_location=map_location)['model'].float().fuse().eval())  # load FP32 model

    # Compatibility updates
    for m in model.modules():
        if type(m) in [nn.Hardswish, nn.LeakyReLU, nn.ReLU, nn.ReLU6]:
            m.inplace = True  # pytorch 1.7.0 compatibility
        elif type(m) is Conv:
            m._non_persistent_buffers_set = set()  # pytorch 1.6.0 compatibility

    if len(model) == 1:
        return model[-1]  # return model
    else:
        print('Ensemble created with %s\n' % weights)
        for k in ['names', 'stride']:
            setattr(model, k, getattr(model[-1], k))
        return model  # return ensemble


def convert_model(input_pth, output_onnx):
    print("NEW CONVERSION.py")
    print('cuda is available == {}'.format(torch.cuda.is_available()))
    device = select_device('')
    nc = 4
    # torch_model = attempt_load(input_pth, map_location=device).half()
    torch_model = attempt_load(input_pth, map_location=device)
    # torch_model = torch_model.to(device)
    # torch_model = torch_model.cpu()

    torch_model.model[-1].export = True

    torch_model.eval()

    half = True
    imgsz = 640
    batch_size = 2  # just a random number
    # x = torch.rand(batch_size, 3, 640, 640, device=device).half()
    x = torch.zeros((1, 3, imgsz, imgsz), device=device)  # init img
    # x = x.half()
    p = torch_model(x)

    torch.onnx.export(torch_model,  # model being run
                      x, #.to(device),  # model input (or a tuple for multiple inputs)
                      output_onnx,  # where to save the model (can be a file or file-like object)
                      verbose=False,
                      opset_version=12,  # the ONNX version to export the model to
                      input_names=['images'],  # the model's input names
                      output_names=['classes', 'boxes'] if p is None else ['output']  # the model's output names

                  )

    # onnx_model = onnx.load(f)  # load onnx model
    # onnx.checker.check_model(onnx_model)
    onnx_model = onnx.load(output_onnx)  # load onnx model
    onnx.checker.check_model(onnx_model)  # check onnx model
    # print(onnx.helper.printable_graph(onnx_model.graph))  # print a human readable model
    print('ONNX export success, saved as %s' % output_onnx)

    return