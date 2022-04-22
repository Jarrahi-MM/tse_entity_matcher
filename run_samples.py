from namad_matcher import *

comments = pd.read_csv("comments.csv")
for index, row in comments.iterrows():
    # print(index, end="")
    # run(row['body'])
    find(row['body'])
