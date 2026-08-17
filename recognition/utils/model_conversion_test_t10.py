import torch
import numpy as np
import onnxruntime as onnx
from numpy.linalg import norm

def compare(v1,v2):
    return (np.dot(v1,v2)) / (np.linalg.norm(v1)*np.linalg.norm(v2))

variant='edgeface_xs_gamma_06'
pytorch_model = torch.hub.load('otroshi/edgeface', variant, source='github', pretrained=True)

pytorch_model.eval()

onnx_ses = onnx.InferenceSession("../models/edgeface_xs_gamme_06.onnx",providers=["CPUExecutionProvider"])


max_diff = 0.0

min_cos = 1.0

for i in range(100):
    tensor = torch.randn(1,3,112,112)

    with torch.no_grad():
        torch_out = pytorch_model(tensor).numpy().flatten()

    onnx_out = onnx_ses.run(None, {"input.1": tensor.numpy()})[0].flatten()

    diff = np.max(np.abs(torch_out - onnx_out))
    max_diff = max(max_diff, diff)

    cos_sim = compare(torch_out,onnx_out)
    min_cos = min(cos_sim,min_cos)

print(f"max abs diff: {max_diff}")
print(f"min cos sim: {min_cos}")