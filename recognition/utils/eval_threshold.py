best = None
with open("data/results.csv") as f:
    next(f)
    lines = f.readlines()
    for t in range(0,101):
        threshold = t / 100
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
            if(score>=threshold and is_enrolled == "False"):
                num_false_acceptances+=1
            if(score>=threshold and is_enrolled == "True" and pred == true_iden):
                num_true_acceptances+=1

        far = (num_false_acceptances/num_impostor_attemps)*100
        tar = (num_true_acceptances/num_legit_attempts)*100

        print(f"threshold={threshold:.2f} TAR={tar:.2f}%  FAR={far:.2f}%")

        if tar>= 95 and far <=1 and best is None:
            best = threshold

print(f"Best threshold: {best}")