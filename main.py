import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import LabelEncoder
from imblearn.over_sampling import SMOTE
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
import pickle

df = pd.read_csv("D:\RealDownload\CustomerChurn\Customer-Churn-Prediction\WA_Fn-UseC_-Telco-Customer-Churn.csv")        #load the csv data to a pandas dataframe

#df.shape                                                                             #returns the dimensions of the dataset as a tuple (number of rows, number of columns)

#df.head()                                                                            #displays the first five rows of the dataset by default

pd.set_option("display.max_columns", None)                                            #ensures that all columns in the dataset are displayed 

#df.info()                                                                            #provides a concise summary of the dataset

df = df.drop(columns=["customerID"])                                                  #dropping customerID column as this is not required for modelling

#df.head()

#df.columns                                                                            #returns the list of column names in the dataset

numerical_features_list = ["tenure", "MonthlyCharges", "TotalCharges"]                 #printing the unique values in all the columns

for col in df.columns:
  if col not in numerical_features_list:
    print(col, df[col].unique())
    print("-"*50)

print(df.isnull().sum())                                                               #returns how many null values each column has

df["TotalCharges"] = df["TotalCharges"].replace({" ": "0.0"})                          #converting null spaces to 0.0

df["TotalCharges"] = df["TotalCharges"].astype(float)

#df.info()

print(df["Churn"].value_counts())                                                      #counts and displays the occurrences of each unique value in the "Churn" column

"""
Insights:
1. Customer ID removed as it is not required for modelling
2. No mmissing values in the dataset
3. Missing values in the TotalCharges column were replaced with 0
4. Class imbalance identified in the target
"""

#df.shape

#df.columns

#df.head(2)

#df.describe()

"""**Numerical Features - Analysis**

Understand the distribution of the numerical features
"""

def plot_histogram(df, column_name):

  plt.figure(figsize=(5, 3))
  sns.histplot(df[column_name], kde=True)
  plt.title(f"Distribution of {column_name}")
  # calculate the mean and median values for the columns
  col_mean = df[column_name].mean()
  col_median = df[column_name].median()
  # adding vertical lines for mean and median
  plt.axvline(col_mean, color="red", linestyle="--", label="Mean")
  plt.axvline(col_median, color="green", linestyle="-", label="Median")

  plt.legend()
  plt.show()

plot_histogram(df, "tenure")
plot_histogram(df, "MonthlyCharges")
plot_histogram(df, "TotalCharges")

"""Box plot for numerical features"""

def plot_boxplot(df, column_name):

  plt.figure(figsize=(5, 3))
  sns.boxplot(y=df[column_name])
  plt.title(f"Box Plot of {column_name}")
  plt.ylabel(column_name)
  plt.show

plot_boxplot(df, "tenure")
plot_boxplot(df, "MonthlyCharges")
plot_boxplot(df, "TotalCharges")

"""Correlation Heatmap for numerical columns"""

# correlation matrix - heatmap
plt.figure(figsize=(8, 4))
sns.heatmap(df[["tenure", "MonthlyCharges", "TotalCharges"]].corr(), annot=True, cmap="coolwarm", fmt=".2f")
plt.title("Correlation Heatmap")
plt.show()

"""Categorical features - Analysis

Countplot for categorical columns"""

object_cols = df.select_dtypes(include="object").columns.to_list()                          #all the non-numerical columns are grouped together and printed

object_cols = ["SeniorCitizen"] + object_cols

for col in object_cols:
  plt.figure(figsize=(5, 3))
  sns.countplot(x=df[col])
  plt.title(f"Count Plot of {col}")
  plt.show()

"""4. Data Preprocessing
Label encoding of target column"""

df["Churn"] = df["Churn"].replace({"Yes": 1, "No": 0})                                     # Churn column is changed from object type to integer

print(df["Churn"].value_counts())

"""Label encoding of categorical fetaures"""

object_columns = df.select_dtypes(include="object").columns                                # identifying columns with object data type
print(object_columns)

encoders = {}                                                                              # initialize a dictionary to save the encoders

for column in object_columns:                                                              # apply label encoding and store the encoders
  label_encoder = LabelEncoder()
  df[column] = label_encoder.fit_transform(df[column])
  encoders[column] = label_encoder

with open("encoders.pkl", "wb") as f:                                                      # save the encoders to a pickle file
  pickle.dump(encoders, f)

encoders

#df.head()

"""Traianing and test data split"""

X = df.drop(columns=["Churn"])                                                             # splitting the features and target
y = df["Churn"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)               # split training and test data

#print(y_train.shape)
#print(y_train.value_counts())

"""Synthetic Minority Oversampling TEchnique (SMOTE)"""

smote = SMOTE(random_state=42)

X_train_smote, y_train_smote = smote.fit_resample(X_train, y_train)

print(y_train_smote.shape)

print(y_train_smote.value_counts())

"""
5. Model Training

Training with default hyperparameters
"""

# dictionary of models
models = {
    "Decision Tree": DecisionTreeClassifier(random_state=42),
    "Random Forest": RandomForestClassifier(random_state=42),
    "XGBoost": XGBClassifier(random_state=42)
}

# dictionary to store the cross validation results
cv_scores = {}

# perform 5-fold cross validation for each model
for model_name, model in models.items():
  print(f"Training {model_name} with default parameters")
  scores = cross_val_score(model, X_train_smote, y_train_smote, cv=5, scoring="accuracy")
  cv_scores[model_name] = scores
  print(f"{model_name} cross-validation accuracy: {np.mean(scores):.2f}")
  print("-"*70)

cv_scores

"""Random Forest gives the highest accuracy compared to other models with default parameters"""

rfc = RandomForestClassifier(random_state=42)

rfc.fit(X_train_smote, y_train_smote)

print(y_test.value_counts())

"""**6. Model Evaluation**"""

# evaluate on test data
y_test_pred = rfc.predict(X_test)

print("Accuracy Score:\n", accuracy_score(y_test, y_test_pred))
print("Confsuion Matrix:\n", confusion_matrix(y_test, y_test_pred))
print("Classification Report:\n", classification_report(y_test, y_test_pred))

# save the trained model as a pickle file
model_data = {"model": rfc, "features_names": X.columns.tolist()}

with open("customer_churn_model.pkl", "wb") as f:
  pickle.dump(model_data, f)

"""7. Load the saved  model and  build a Predictive System"""

# load teh saved model and the feature names

with open("customer_churn_model.pkl", "rb") as f:
  model_data = pickle.load(f)

loaded_model = model_data["model"]
feature_names = model_data["features_names"]

print(loaded_model)

print(feature_names)

input_data = {
    'gender': 'Female',
    'SeniorCitizen': 0,
    'Partner': 'Yes',
    'Dependents': 'No',
    'tenure': 1,
    'PhoneService': 'No',
    'MultipleLines': 'No phone service',
    'InternetService': 'DSL',
    'OnlineSecurity': 'No',
    'OnlineBackup': 'Yes',
    'DeviceProtection': 'No',
    'TechSupport': 'No',
    'StreamingTV': 'No',
    'StreamingMovies': 'No',
    'Contract': 'Month-to-month',
    'PaperlessBilling': 'Yes',
    'PaymentMethod': 'Electronic check',
    'MonthlyCharges': 29.85,
    'TotalCharges': 29.85
}


input_data_df = pd.DataFrame([input_data])

with open("encoders.pkl", "rb") as f:
  encoders = pickle.load(f)


# encode categorical featires using teh saved encoders
for column, encoder in encoders.items():
  input_data_df[column] = encoder.transform(input_data_df[column])

# make a prediction
prediction = loaded_model.predict(input_data_df)
pred_prob = loaded_model.predict_proba(input_data_df)

print(prediction)

# results
print(f"Prediction: {'Churn' if prediction[0] == 1 else 'No Churn'}")
print(f"Prediciton Probability: {pred_prob}")

encoders

"""**To do:**
1. Implement Hyperparameter Tuining
2. Try Model Selection
3. Try downsampling
4. Try to address teh overfitting
5. Try Startified k fold CV
"""

