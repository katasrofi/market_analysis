import pandas as pd

df: pd.DataFrame = pd.read_csv("Groceries_dataset.csv")

# Check and Clean the data
from func import check_data, DropDuplicates
check_data(df)

df_cleaned = DropDuplicates(df)
check_data(df_cleaned)

# Save Data Into csv
df_cleaned.to_csv("DataPreprocessing/DataCleaned.csv", index=True, index_label='id')

# Preprocessing the data
DfPreprocessing: pd.DataFrame = pd.read_csv("DataPreprocessing/DataCleaned.csv")

# Clean the data
DfPreprocessing["Member_number"] = DfPreprocessing["Member_number"].astype(str)
DfPreprocessing["itemDescription"] = DfPreprocessing["itemDescription"].str.strip()

# Create matrix for Apriori selection
matrix: pd.DataFrame = (
    DfPreprocessing.groupby(['Member_number', 'itemDescription'])['itemDescription']
    .count()
    .unstack()
    .fillna(0)
    .reset_index()
)
# Drop the member_number because it doesn't needed for Apriori Algorithm
matrix: pd.DataFrame = matrix.drop("Member_number", axis = 1)

# Change the value to Binary
matrix_set: pd.DataFrame = matrix.map(lambda x:1 if x >= 1 else 0)

# Ignore the warnings
import warnings
warnings.filterwarnings('ignore')

# Import apriori and association_rules library
from mlxtend.frequent_patterns import apriori, association_rules

# Calculate pattern transanction using apriori with frequent transanction 1%
frequent_items: pd.DataFrame = apriori(matrix_set, min_support=0.01, use_colnames=True)
# print(frequent_items.sort_values(by='support', ascending=False))

# Seach the market rule using association_rules
matrix_rules: pd.DataFrame = association_rules(frequent_items, metric='lift', min_threshold=1)

# Print the Result
print(matrix_rules.sort_values(by='lift', ascending=False))

# Edit the Frequent and Market Rules data for Visualization
def extract_item(frozenset_str: frozenset) -> str:
    item = list(frozenset_str)[0]
    return item

# Make a copy
df_rules = matrix_rules.copy()

# Apply the function
df_rules["antecedents"] = df_rules["antecedents"].apply(extract_item)
df_rules["consequents"] = df_rules["consequents"].apply(extract_item)

# capitalize the first letter for easy to read
df_rules["antecedents"] = df_rules["antecedents"].str.capitalize()
df_rules["consequents"] = df_rules["consequents"].str.capitalize()
# Save the data
df_rules.to_csv('DataPreprocessing/MarketRules.csv', index=False)
