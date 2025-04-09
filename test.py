import pandas as pd
import statistics

#to print the whole dataframe
pd.set_option('display.max_rows', None)

df = pd.read_csv("results.csv", skiprows=22, usecols=["Well", "Omit", 
                                                      "Sample", "Target", 
                                                      "Cq", "Cq Mean", 
                                                      "Threshold"])
# Set "Undetermined" to 40 and cast Cq values to type float
df["Cq"] = df["Cq"].replace("Undetermined", 40)
df["Cq"] = pd.to_numeric(df["Cq"])
#print(df.dtypes)
#print(df.head(10))

# Calculate EqCq values
'''df["EqCq"] = df.groupby(["Target", "Sample", ""])'''

# Filter controls by targets
'''
icr1_df = df[df["Target"].isin(["ICR1_M", "ICR1_UM"])& 
            (df["Sample"].str.contains("control", case=False))]
print(icr1_df)
'''

'''
Find outliers
'''
'''tmp_df = icr1_df[df["Sample"] == "Control A"]
pivoted = tmp_df.pivot(index="Well", columns="Target", values="Cq")
pivoted["dEqCq"] = pivoted["ICR1_M"] - pivoted["ICR1_UM"] #Assuming the endogenous control is UM
#print(pivoted.head(10))

# Extract the dEqCq and brute force to determine the min stdev
val_1 = pivoted["dEqCq"].iloc[0]
val_2 = pivoted["dEqCq"].iloc[1]
val_3 = pivoted["dEqCq"].iloc[2]
val_4 = pivoted["dEqCq"].iloc[3]

std_1 = statistics.stdev([val_2, val_3, val_4]) #stdev does not contain well 1
std_2 = statistics.stdev([val_1, val_3, val_4]) #stdev does not contain well 2
std_3 = statistics.stdev([val_1, val_2, val_4]) #stdev does not contain well 3
std_4 = statistics.stdev([val_1, val_2, val_3]) #stdev does not contain well 4

# Calculate the min values
# Iterate through the dict to find the first qualifying values
std_dict = {1:std_1, 2:std_2, 3:std_3, 4:std_4}
min_val = min(std_dict.values())
to_omit = 0
for key, value in std_dict.items():
    if value == min_val: 
        to_omit = key
        break


# Omit the row from the original df
#df = df[~(df["Well"] == to_omit)]
#print(df.head(10))
'''

'''
Find outliers for each sample in the df
'''
icr1_df = df[df["Target"].isin(["ICR1_M", "ICR1_UM"])]
pivoted = icr1_df.pivot(index=["Sample", "Well"], columns="Target", values="Cq").reset_index() # Move Sample and Well back into the dataframe
pivoted["dEqCq"] = pivoted["ICR1_M"] - pivoted["ICR1_UM"] #Assuming the endogenous control is UM
pivoted = pivoted.sort_values("Well")
#print(icr1_df)
#print(pivoted)
#print(len(pivoted))

"""
Find the outlier given four values

Args:
    val_1 (float)
    val_2 (float)
    val_3 (float)
    val_4 (float)

Returns:
    to_omit (int): the index of the value to omit such that the stdev is minimized
"""
def find_outliers(val_1, val_2, val_3, val_4):
    std_1 = statistics.stdev([val_2, val_3, val_4]) #stdev does not contain well 1
    std_2 = statistics.stdev([val_1, val_3, val_4]) #stdev does not contain well 2
    std_3 = statistics.stdev([val_1, val_2, val_4]) #stdev does not contain well 3
    std_4 = statistics.stdev([val_1, val_2, val_3]) #stdev does not contain well 4
    std_dict = {0:std_1, 1:std_2, 2:std_3, 3:std_4}
    min_val = min(std_dict.values())
    to_omit = 0
    for key, value in std_dict.items():
        if value == min_val: 
            to_omit = key
            break
    return to_omit

#print(len(icr1_df))

omitted_wells = []

for i in range(0, len(pivoted), 4):
    val_1 = pivoted["dEqCq"].iloc[i]
    val_2 = pivoted["dEqCq"].iloc[i+1]
    val_3 = pivoted["dEqCq"].iloc[i+2]
    val_4 = pivoted["dEqCq"].iloc[i+3]
    to_omit = pivoted["Well"].iloc[find_outliers(val_1, val_2, val_3, val_4) + i]
    omitted_wells.append(to_omit)
    #Omit from the original table
    icr1_df = icr1_df[~(df["Well"] == to_omit)]

print(icr1_df)
print(omitted_wells)