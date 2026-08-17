import numpy as np
from numpy.linalg import norm
import psycopg2
from pgvector.psycopg2 import register_vector

def compare(v1,v2):
    return (np.dot(v1,v2)) / (np.linalg.norm(v1)*np.linalg.norm(v2))


conn_x86 = psycopg2.connect(
    host="localhost", port=5432,
    dbname="db", user="postgres", password="password"
)
register_vector(conn_x86)

conn_arm = psycopg2.connect(
    host="localhost", port=5433,
    dbname="db", user="postgres", password="password"
)
register_vector(conn_arm)

cur_x86 = conn_x86.cursor()
cur_arm = conn_arm.cursor()

cur_x86.execute("SELECT id, vector FROM embeddings ORDER BY id")
cur_arm.execute("SELECT id, vector FROM embeddings ORDER BY id")

rows_x86 = cur_x86.fetchall()
rows_arm = cur_arm.fetchall()

max_diff = 0.0

min_cos = 1.0

for (id_x86, embedding_x86), (id_arm, embedding_arm) in zip(rows_x86,rows_arm):
    assert id_x86 == id_arm, f"mismatch for IDs: {id_x86} and {id_arm}"

    x86 = np.array(embedding_x86)
    arm = np.array(embedding_arm)

    diff = np.max(np.abs(arm - x86))
    max_diff = max(max_diff, diff)

    cos_sim = compare(arm,x86)
    min_cos = min(cos_sim,min_cos)

print(f"max abs diff: {max_diff}")
print(f"min cos sim: {min_cos}")