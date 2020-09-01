import pandas as pd


def top_documents(input_file="techminer.csv", top_n=10):

    df = pd.read_csv(input_file)
    df = df.sort_values("Global_Citations", ascending=False).head(top_n)
    df = df.reset_index(drop=True)
    for i in range(len(df)):
        print(
            df.Authors[i].replace(";", ", ")
            + ". "
            + str(df.Year[i])
            + ". "
            + df.Title[i]
            + "\t"
            + str(int(df.Global_Citations[i]))
        )
