import random

def predict(file):
    healthy_score = random.uniform(60, 95)
    diseased_score = 100 - healthy_score

    return {
        "Healthy (%)": round(healthy_score, 2),
        "Diseased (%)": round(diseased_score, 2)
    }
