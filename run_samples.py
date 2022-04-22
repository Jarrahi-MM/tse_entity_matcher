from namad_matcher import *

comments = pd.read_csv("comments.csv")
for index, row in comments.iterrows():
    run(row['body'])