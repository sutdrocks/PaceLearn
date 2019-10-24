import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

def cluster_now():
    # Path of original data
    path = r"original_data.csv"
    q_path = r"Grammar Questions.xlsx"
    data_path = r"Questions data.csv"
    
    # Original dataset 
    original_df = pd.read_csv(path)
    q_df = pd.read_excel(q_path)
    data_df = pd.read_csv(data_path)
    
    # temp dataset
    temp_df = original_df.copy()
    temp_df["average_score"] = (temp_df["WH_answer"] + temp_df["XQ_answer"])/2
    temp_df["average_timing"] = (temp_df["WH_time"] + temp_df["XQ_time"])/2
    
    # Set up X as average_score and average_timing
    X = temp_df[["average_score", "average_timing"]] 
    
    try:
        # Update with all the other options
        data_group = data_df.groupby("Questions").sum().reset_index()
        data_group["count"] = data_df.groupby("Questions").count().reset_index().iloc[:,[1]]
        
        for i in range(data_group.shape[0]):
            # Get the index
            dex = q_df[q_df["Questions"] == data_group.iloc[i,0]].index
            # Update marks
            X.iloc[dex, 0] = (X.iloc[dex, 0] + data_group.iloc[i,1])/ (1 + data_group.iloc[i,3])
            # Update time
            X.iloc[dex, 1] = (X.iloc[dex, 1] + data_group.iloc[i,2])/ (1 + data_group.iloc[i,3])
        
        # Kmeans 
        kmeans = KMeans(n_clusters=5, random_state=42).fit(X)
        
        # Entire dataset for X
        X_dataset = X.copy()
        #X_dataset = temp_df[["average_score", "average_timing"]] 
        X_dataset["cluster"] = kmeans.labels_ + 1
        
        true_false = []
        for i in range(X_dataset["cluster"].shape[0]):
            if X_dataset["cluster"].iloc[i] == q_df["Numeric_difficulty"].iloc[i]:
                true_false.append(" ")
            else:
                true_false.append("Updated")
        
        # Overide original grammar question data
        q_df["Numeric_difficulty"] = kmeans.labels_ + 1
        # Override Difficulty
        mapping_dict = {4:"C2", 2:"C1", 1:"B2", 5:"B1", 3:"A2"}
        q_df["Difficulty"] = q_df["Numeric_difficulty"].apply(lambda x: mapping_dict[x])
        # Update Updates
        q_df["Updates"] = true_false
        
        q_df.to_excel(q_path, index=False)
        print("Updated difficulty")
    
    except Exception as e:
        print("Error:", e)
# 

# Plot
#Visualisation
#plt.scatter(X_dataset[X_dataset["cluster"] == 0]["average_timing"], X_dataset[X_dataset["cluster"] == 0]["average_score"], s = 100, c = 'red', label = 'B2')
#plt.scatter(X_dataset[X_dataset["cluster"] == 1]["average_timing"], X_dataset[X_dataset["cluster"] == 1]["average_score"], s = 100, c = 'blue', label = 'C1')
#plt.scatter(X_dataset[X_dataset["cluster"] == 2]["average_timing"], X_dataset[X_dataset["cluster"] == 2]["average_score"], s = 100, c = 'green', label = 'A2')
#plt.scatter(X_dataset[X_dataset["cluster"] == 3]["average_timing"], X_dataset[X_dataset["cluster"] == 3]["average_score"], s = 100, c = 'cyan', label = 'C2')
#plt.scatter(X_dataset[X_dataset["cluster"] == 4]["average_timing"], X_dataset[X_dataset["cluster"] == 4]["average_score"], s = 100, c = 'magenta', label = 'B1')
#plt.scatter(kmeans.cluster_centers_[:, 0], kmeans.cluster_centers_[:, 1], s = 300, c = 'yellow', label = 'Centroids')
#plt.title('Clusters of questions')
#plt.xlabel('Average Time')
#plt.ylabel('Average Score')
#plt.legend()
#plt.show()
#plt.savefig("Post_Cluster.png")

# Against previous difficulty
#q_path = r"Grammar Questions.xlsx"
##
#q_df = pd.read_excel(q_path)
#Y_dataset = temp_df[["average_score", "average_timing"]]
#Y_dataset["cluster"] = q_df["Numeric_difficulty"]
#plt.scatter(Y_dataset[Y_dataset["cluster"] == 1]["average_timing"], Y_dataset[Y_dataset["cluster"] == 1]["average_score"], s = 100, c = 'red', label = 'A2')
#plt.scatter(Y_dataset[Y_dataset["cluster"] == 2]["average_timing"], Y_dataset[Y_dataset["cluster"] == 2]["average_score"], s = 100, c = 'blue', label = 'B1')
#plt.scatter(Y_dataset[Y_dataset["cluster"] == 3]["average_timing"], Y_dataset[Y_dataset["cluster"] == 3]["average_score"], s = 100, c = 'green', label = 'B2')
#plt.scatter(Y_dataset[Y_dataset["cluster"] == 4]["average_timing"], Y_dataset[Y_dataset["cluster"] == 4]["average_score"], s = 100, c = 'cyan', label = 'C1')
#plt.scatter(Y_dataset[Y_dataset["cluster"] == 5]["average_timing"], Y_dataset[Y_dataset["cluster"] == 5]["average_score"], s = 100, c = 'magenta', label = 'C2')
#plt.title('Clusters of questions')
#plt.xlabel('Average Time')
#plt.ylabel('Average Score')
#plt.legend()
##plt.show()
#plt.savefig("Pre_Cluster.png")
