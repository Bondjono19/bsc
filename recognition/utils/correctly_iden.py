with open("data/results.csv","r") as f:
    next(f)
    lines = f.readlines()

true_identities = 0
correctly_predicted = 0
for line in lines:
    score,pred,true,is_enrolled = line.strip().split(",")
    score = float(score)
    if(is_enrolled == "True"):
        true_identities+=1
        if(pred == true and score >= 0.52):
            correctly_predicted+=1

print(f"true idents in set: {true_identities}")
print(f"correctly predicted: {correctly_predicted}")
print(f"rate: {correctly_predicted/true_identities}")
