import pandas as pd
import statistics

df = pd.read_csv("results.csv", skiprows=22, usecols=["Well", 
                                                    "Well Position", 
                                                    "Omit", "Sample", 
                                                    "Target", "Cq", 
                                                    "Cq Mean", "Cq SD", 
                                                    "Threshold"])
#Set "Undetermined" to 40 and cast Cq values to type float
df["Cq"] = df["Cq"].replace("Undetermined", 40)
df["Cq"] = pd.to_numeric(df["Cq"])
print(df.dtypes)
#print(df.head(10))

# Calculate EqCq values
'''df["EqCq"] = df.groupby(["Target", "Sample", ""])'''

# Filter controls by targets
icr1_df = df[df["Target"].isin(["ICR1_M", "ICR1_UM"])& 
            (df["Sample"].str.contains("control", case=False))]
#print(icr1_df.head(10))

# Find outliers
tmp_df = icr1_df[df["Sample"] == "Control A"]
pivoted = tmp_df.pivot(index="Well", columns="Target", values="Cq")
pivoted["dEqCq"] = pivoted["ICR1_M"] - pivoted["ICR1_UM"] #Assuming the endogenous control is UM
print(pivoted.head(10))

val_1 = pivoted["dEqCq"].iloc[0]
val_2 = pivoted["dEqCq"].iloc[1]
val_3 = pivoted["dEqCq"].iloc[2]
val_4 = pivoted["dEqCq"].iloc[3]

std_1 = statistics.stdev([val_1, val_2, val_3])
std_2 = statistics.stdev([val_2, val_3, val_4])
std_3 = statistics.stdev([val_1, val_2, val_4])
std_4 = statistics.stdev([val_1, val_3, val_4])

