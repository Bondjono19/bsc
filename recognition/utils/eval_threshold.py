THRESHOLD = 0.5

with open("data/results.csv") as f:
    next(f)
    lines = f.readlines()
    num_impostor_attemps = 0
    num_legit_attempts = 0
    num_false_acceptances = 0
    num_true_acceptances = 0
    for line in lines:
        score, pred, true_iden, is_enrolled = line.strip().split(",")
        score = float(score)
        if(is_enrolled == "True"):
            num_legit_attempts+=1
        else:
            num_impostor_attemps+=1
        if(score>=THRESHOLD and is_enrolled == "False"):
            num_false_acceptances+=1
        if(score>=THRESHOLD and is_enrolled == "True" and pred == true_iden):
            num_true_acceptances+=1

    far = (num_false_acceptances/num_impostor_attemps)*100
    tar = (num_true_acceptances/num_legit_attempts)*100

    print(f"FAR: {far}")
    print(f"TAR: {tar}")