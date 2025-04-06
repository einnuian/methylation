import pandas as pd

df = pd.read_csv("results.csv", skiprows=22, usecols=["Well", 
                                                    "Well Position", 
                                                    "Omit", "Sample", 
                                                    "Target", "Cq", 
                                                    "Cq Mean", "Cq SD", 
                                                    "Threshold"])

print(df.head(10))

# Calculate EqCq values
df["EqCq"] = df.groupby(["Target", "Sample", ""])