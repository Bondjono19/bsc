import onnxruntime
import onnx
path = "recognition/models/edgeface_xs_gamme_06.onnx"

m = onnx.load(path)
print([i.name for i in m.graph.input])