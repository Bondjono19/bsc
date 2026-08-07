import torch

variant='edgeface_xs_gamma_06'
model = torch.hub.load('otroshi/edgeface', variant, source='github', pretrained=True)
model.eval()

#define dummy input
tensor = torch.randn(1,3,112,112)

torch.onnx.export(
    model=model,
   args=tensor,
   f="edgeface_xs_gamma_06.onnx"
)