#!/usr/bin/env python
# coding: utf-8

# # Machine Learning to Identify Fraud in Enron Corpus
# 
# ### Final Project for Python for Data Science Course
# 
# #### Group Member:
# - FATHIAH - 
# - MATHEW GEORGE Jithin
# - TIATSE SOUOP Varesse
# - SZEPEK Maria Sofie

#    <center><img src="enron.jpg" alt="Getting started" /></center>

# ### Context and Enron Corpus
# 
# In late 2001, Enron, an American energy company, filed for bankruptcy after one of the largest financial scandals in corporate history. After the company's collapse, over 600,000 emails generated by 158 Enron employees - now known as the Enron Corpus - were acquired by the Federal Energy Regulatory Commission during its investigation. The data was then uploaded online, and since then, a number of people and organizations have graciously prepared, cleaned and organized the dataset that is available to the public today (a few years later, financial data of top Enron executives were released following their trial).
# 
# ### Project Description and Goal
# 
# The aim of this project is to apply machine learning techniques to build a predictive model that identifies Enron employees that may have committed fraud based on their financial and email data.
# 
# The dataset has:
# - 14 financial features (salary, bonus, etc.),
# - 6 email features (to and from messages, etc.)
# - A Boolean label that denotes whether a person is a person-of-interest (POI) or not (established from credible news sources).
# 
# It is these features that will be explored, cleaned, and then put through various machine learning algorithms, before finally tuning them and checking its accuracy (precision and recall).
# 
# ##### The objective is to get a precision and recall score of at least 0.48
# 
# First, the dataset will be manually explored to find outliers and trends and generally understand the data. Certain useful financial or email-based features will be chosen (manually and automatically using sklearn functions) and ensemble features created from those available, and then put through
# appropriate feature scaling. Then, numerous algorithms with parameter tuning will be trained and tested on the data.
# 
# The detailed results of the final algorithm, will be described in detail. The validation and evaluation metrics will be also shown and the reasoning behind their choice and its importance will be carefully explained. Finally, other ideas involving feature selection, feature scaling, other algorithms and usage
# of email texts will be discussed.

# ## Initial Preparation/Importing Libraries

# In[1]:


get_ipython().system('pip install feature_format')


# In[2]:


import sys
import pickle
sys.path.append("../tools/")
from feature_format import featureFormat, targetFeatureSplit
from tester import dump_classifier_and_data
import pandas as pd
import sys
import pickle
import csv
import matplotlib.pyplot as plt

sys.path.append("../tools/")
from feature_format import featureFormat, targetFeatureSplit
#from poi_data import *
from sklearn.feature_selection import SelectKBest
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import StratifiedShuffleSplit

from numpy import mean

from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_validate

from sklearn.metrics import accuracy_score, precision_score, recall_score

from sklearn.model_selection import train_test_split
import seaborn as sns
sns.set(style="white")
sns.set(style="whitegrid", color_codes=True)
import pandas as pd
import numpy as np
from sklearn import preprocessing
import matplotlib.pyplot as plt 
plt.rc("font", size=14)


# ## TASK 1: Features 
# 
# ### Create features list and import necessary files

# In[3]:


### Selecting features
target_label = 'poi'

email_features_list = [
    'from_messages',
    'from_poi_to_this_person',
    'from_this_person_to_poi',
    'shared_receipt_with_poi',
    'to_messages',
    ]
    
financial_features_list = [
    'bonus',
    'deferral_payments',
    'deferred_income',
    'director_fees',
    'exercised_stock_options',
    'expenses',
    'loan_advances',
    'long_term_incentive',
    'other',
    'restricted_stock',
    'restricted_stock_deferred',
    'salary',
    'total_payments',
    'total_stock_value',
]

features_list = [target_label] + financial_features_list + email_features_list


# In[6]:


### Load the dictionary containing the dataset
with open("final_project_dataset.pkl", "rb") as data_file:
    data_dict = pickle.load(data_file)


# In[7]:


### 1.1.0 Explore csv file 
def make_csv(data_dict):
    """ generates a csv file from a data set"""
    fieldnames = ['name'] + data_dict.itervalues().next().keys()
    with open('data.csv', 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for record in data_dict:
            person = data_dict[record]
            person['name'] = record
            assert set(person.keys()) == set(fieldnames)
            writer.writerow(person)


# ### Initial data exploration

# In[9]:


### 1.1.1 Dataset Exploration
print('# Exploratory Data Analysis #')
data_dict.keys()
print('Total number of data points: %d' % len(data_dict.keys()))
num_poi = 0
for name in data_dict.keys():
    if data_dict[name]['poi'] == True:
        num_poi += 1
print('Number of Persons of Interest: %d' % num_poi)
print('Number of people without Person of Interest label: %d' % (len(data_dict.keys()) - num_poi))


# In[10]:


### 1.1.2 Feature Exploration
all_features = data_dict['ALLEN PHILLIP K'].keys()
print('Each person has %d features available' %  len(all_features))
### Evaluate dataset for completeness
missing_values = {}
for feature in all_features:
    missing_values[feature] = 0
for person in data_dict.keys():
    records = 0
    for feature in all_features:
        if data_dict[person][feature] == 'NaN':
            missing_values[feature] += 1
        else:
            records += 1


# In[11]:


### Print results of completeness analysis
print('Number of Missing Values for Each Feature:')
for feature in all_features:
    print("%s: %d" % (feature, missing_values[feature]))


# In[ ]:





# ## TASK 2: Remove Outliers
# 
# We detect a few features with outliers and remove them to make the analysis more robust. 

# In[12]:


def PlotOutlier(data_dict, feature_x, feature_y):
    """ Plot with flag = True in Red """
    data = featureFormat(data_dict, [feature_x, feature_y, 'poi'])
    for point in data:
        x = point[0]
        y = point[1]
        poi = point[2]
        if poi:
            color = 'red'
        else:
            color = 'blue'
        plt.scatter(x, y, color=color)
    plt.xlabel(feature_x)
    plt.ylabel(feature_y)
    plt.show()

# 2.1 Visualise outliers
print(PlotOutlier(data_dict, 'total_payments', 'total_stock_value'))
print(PlotOutlier(data_dict, 'from_poi_to_this_person', 'from_this_person_to_poi'))
print(PlotOutlier(data_dict, 'salary', 'bonus'))
#Remove outlier TOTAL line in pickle file.
data_dict.pop( 'TOTAL', 0 )


# 2.2 Function to remove outliers
def remove_outlier(dict_object, keys):
    """ removes list of outliers keys from dict object """
    for key in keys:
        dict_object.pop(key, 0)

outliers = ['TOTAL', 'THE TRAVEL AGENCY IN THE PARK', 'LOCKHART EUGENE E','FREVERT MARK A','LAVARATO JOHN J',"SKILLING JEFFREY K","LAY KENNETH L"]
remove_outlier(data_dict, outliers)


# ### Plotting after outliers removal

# In[13]:


import matplotlib.pyplot
def showData(data_set, first_feature, second_feature):
    data = featureFormat(data_set, [first_feature, second_feature, 'poi'])
    for point in data:
        x = point[0]
        y = point[1]
        poi = point[2]
        if poi:
            color = 'red'
        else:
            color = 'blue'
        matplotlib.pyplot.scatter(x, y, color=color)

    matplotlib.pyplot.xlabel(first_feature)
    matplotlib.pyplot.ylabel(second_feature)
    matplotlib.pyplot.show()


# In[14]:


# Visualize data to identify outliers
# data_dict.T.to_dict
# data_dict.pop('LAY KENNETH L',0)
showData(data_dict, 'total_payments','total_stock_value')
showData(data_dict, 'from_poi_to_this_person', 'from_this_person_to_poi')
showData(data_dict, 'salary', 'bonus')
showData(data_dict, 'restricted_stock', 'exercised_stock_options')
showData(data_dict, 'long_term_incentive', 'deferred_income')


# In[15]:


print(PlotOutlier(data_dict, 'total_payments', 'total_stock_value'))


# In[16]:


### 1.1.0 Explore csv file 
def make_csv(data_dict):
    """ generates a csv file from a data set"""
    fieldnames = ['name'] + data_dict.itervalues().next().keys()
    with open('data.csv', 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for record in data_dict:
            person = data_dict[record]
            person['name'] = record
            assert set(person.keys()) == set(fieldnames)
            writer.writerow(person)

### 1.1.1 Dataset Exploration
print('# Exploratory Data Analysis #')
data_dict.keys()
print('Total number of data points: %d' % len(data_dict.keys()))
num_poi = 0
for name in data_dict.keys():
    if data_dict[name]['poi'] == True:
        num_poi += 1
print('Number of Persons of Interest: %d' % num_poi)
print('Number of people without Person of Interest label: %d' % (len(data_dict.keys()) - num_poi))


###1.1.2 Feature Exploration
all_features = data_dict['ALLEN PHILLIP K'].keys()
print('Each person has %d features available' %  len(all_features))
### Evaluate dataset for completeness
missing_values = {}
for feature in all_features:
    missing_values[feature] = 0
for person in data_dict.keys():
    records = 0
    for feature in all_features:
        if data_dict[person][feature] == 'NaN':
            missing_values[feature] += 1
        else:
            records += 1

### Print results of completeness analysis
print('Number of Missing Values for Each Feature:')
for feature in all_features:
    print("%s: %d" % (feature, missing_values[feature]))


# ### Data Frame

# In[17]:


df=pd.DataFrame.from_dict(data_dict, orient = 'index')
# data=df.T
df.replace('nan',np.nan)
df.replace(to_replace='NaN', value=np.nan, inplace=True)
df.head()


# In[18]:


df.dtypes


#  there are many null data in our dataset. In order to select the most appropriate features to explore, we will look for those that are present at least in 70% of the dataset. Considering there are 21 features (from which 70% is approximate to 15 features), we will first observe which instances have more than 15 not null values and choose the most complete features from this selection.

# In[83]:


notNullDataset = df.dropna(thresh=15)
notNullDataset.info()


# In[ ]:





# ###  Correlation Matrix of missing Value
# 
# We want to see the correlation between the missing values in order to see if the missing values are related to one another. The result shows the missing value as the white part. The missing data mechanism that we found is MAR and MCAR. 

# In[19]:


import seaborn as sns
dfp=df.drop(['poi'], axis=1)
## Calculating the correlation among features by Pearson method
correlationDataframe = df.corr()

# Drawing a heatmap with the numeric values in each cell
fig1, ax = plt.subplots(figsize=(14,10))
fig1.subplots_adjust(top=.945)
plt.suptitle('Features correlation from the Enron POI dataset', fontsize=14, fontweight='bold')

cbar_kws = {'orientation':"vertical", 'pad':0.025, 'aspect':70}
sns.heatmap(correlationDataframe, annot=True, fmt='.2f', linewidths=.3, ax=ax, cbar_kws=cbar_kws);


# In[20]:


df['poi'].head()


# In[22]:


get_ipython().system('pip install missingno')


# In[25]:


df[df['loan_advances']!='NaN']


# In[34]:


len(df)


# In[37]:


x=len(df[df['director_fees']!='NaN'])
y=len(df)
c=len(df[df['loan_advances']!='NaN'])
w=len(df[df['restricted_stock_deferred']!='NaN'])


# Observation: The length of the dataset without NaN on 'loan_advances' is 140, 'restricted_stock_deffered' is 140 and 'director fees' is 140, which are similar to the true length 140.

# In[38]:


print(f"we observe that the length of the dataset without NaN on 'loan advance' {c}, 'restricted stock deffered' {w} and 'director fees' {x} is quite similar to the true length {y}")


# In[23]:


import missingno as msno  # # pip install missingno

# Plot correlation heatmap of missingness
msno.matrix(df)


# According to the graph above, the data are missing at random (MAR) some columns are almost empty.
# 
# Whereas the plot below shows that there is no link between missing values.

# In[39]:


msno.heatmap(df)


# In[40]:


df.dtypes


# ### Removing the columns with missing values
# 
# Based on the above plots, we are removing the columns 'loan_advances', 'restricted_stock_deferred' and 'director_fees' as they have a lot of missing values.

# In[41]:


df_min = df[['from_messages',
      'from_poi_to_this_person',
      'from_this_person_to_poi',
    'shared_receipt_with_poi',
    'to_messages',
    'bonus',
    'deferral_payments',
    'deferred_income',
    'exercised_stock_options',
    'expenses',
    'long_term_incentive',
    'other',
    'restricted_stock',
    'salary',
    'total_payments',
    'total_stock_value',
           ]]


# Seeing the index because we will retransform the dataset into a dictionary.

# In[42]:


df.index


# We are using iterative imputer which fills the missing values using k-Nearest Neighbors. Two samples are close if the features that neither is missing are close.

# In[43]:


import numpy as np
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer
imp_mean = IterativeImputer(random_state=0)
# df_no_na = df.dropna()
imp_mean.fit(df_min)
x = imp_mean.transform(df_min)


# ### Dataset with filled missing values

# In[44]:


df_new = pd.DataFrame(x, index = df.index,
                      columns =['from_messages',
      'from_poi_to_this_person',
      'from_this_person_to_poi',
    'shared_receipt_with_poi',
    'to_messages',
    'bonus',
    'deferral_payments',
    'deferred_income',
    'exercised_stock_options',
    'expenses',
    'long_term_incentive',
    'other',
    'restricted_stock',
    'salary',
    'total_payments',
    'total_stock_value',
           ])
df_new.head()


# As there are some negative values in the new dataset, we plot the distribution of the new variables using histogram to see the distribution of each variable.

# In[45]:


df_new.hist()


# As we can see, the data are unbalanced and it can be a really big issue.

# In[49]:


sns.countplot(x='poi',data=df)
plt.show()


# We proceed with concatenation to add categorical variable poi to the filled dataset.

# In[50]:


print(len(pd.concat([df_new, df.poi],axis=1)))
df_good = pd.concat([df_new, df.poi],axis=1)
df_good.head(10)


# In[52]:


with open("final_project_dataset.pkl", "rb") as data_file:
    data_dict = pickle.load(data_file)

my_dataset = data_dict

## 3.2 add new features to dataset
def compute_fraction(poi_messages, all_messages):
    """ return fraction of messages from/to that person to/from POI"""    
    if poi_messages == 'NaN' or all_messages == 'NaN':
        return 0.
    fraction = poi_messages / all_messages
    return fraction

for name in my_dataset:
    data_point = my_dataset[name]
    from_poi_to_this_person = data_point["from_poi_to_this_person"]
    to_messages = data_point["to_messages"]
    fraction_from_poi = compute_fraction(from_poi_to_this_person, to_messages)
    data_point["fraction_from_poi"] = fraction_from_poi
    from_this_person_to_poi = data_point["from_this_person_to_poi"]
    from_messages = data_point["from_messages"]
    fraction_to_poi = compute_fraction(from_this_person_to_poi, from_messages)
    data_point["fraction_to_poi"] = fraction_to_poi


# 3.3 create new copies of feature list for grading
my_feature_list = features_list +['to_messages', 'from_poi_to_this_person', 'from_messages', 'from_this_person_to_poi','shared_receipt_with_poi', 'fraction_to_poi']


# 3.4 get K-best features
num_features = 10 

# 3.5 functio using SelectKBest
def get_k_best(data_dict, features_list, k):
    """ runs scikit-learn's SelectKBest feature selection
        returns dict where keys=features, values=scores
    """
    data = featureFormat(data_dict, features_list)
    labels, features = targetFeatureSplit(data)

    k_best = SelectKBest(k=k)
    k_best.fit(features, labels)
    scores = k_best.scores_
    print(scores)
    unsorted_pairs = zip(features_list[1:], scores)
    sorted_pairs = list(reversed(sorted(unsorted_pairs, key=lambda x: x[1])))
    k_best_features = dict(sorted_pairs[:k])
    print ("{0} best features: {1}\n".format(k, k_best_features.keys(), scores))
    return k_best_features


best_features = get_k_best(my_dataset, my_feature_list, num_features)

my_feature_list = [target_label] + list(set(best_features.keys()))

# 3.6 print features
print ("{0} selected features: {1}\n".format(len(my_feature_list) - 1, my_feature_list[1:]))

# 3.7 extract the features specified in features_list
data = featureFormat(my_dataset, my_feature_list,sort_keys = True)
# split into labels and features
labels, features = targetFeatureSplit(data)

# 3.8 scale features via min-max
from sklearn import preprocessing
scaler = preprocessing.MinMaxScaler()
features = scaler.fit_transform(features)


from sklearn.naive_bayes import GaussianNB
g_clf = GaussianNB()

###4.2  Logistic Regression Classifier
from sklearn.linear_model import LogisticRegression

l_clf = Pipeline(steps=[
        ('scaler', StandardScaler()),
        ('classifier', LogisticRegression(C=1e-08, class_weight=None, dual=False, fit_intercept=True, intercept_scaling=1, 
max_iter=100, multi_class='ovr', penalty='l2', random_state=42, solver='liblinear', tol=0.001, verbose=0))])

###4.3  K-means Clustering
from sklearn.cluster import KMeans
k_clf = KMeans(n_clusters=2, tol=0.001)


###4.4 Support Vector Machine Classifier
from sklearn.svm import SVC
s_clf = SVC(kernel='rbf', C=1000,gamma = 0.0001,random_state = 42, class_weight = 'balanced')

###4.5 Random Forest
from sklearn.ensemble import RandomForestClassifier
rf_clf = RandomForestClassifier(max_depth = 5,max_features = 'sqrt',n_estimators = 10, random_state = 42)


###4.6 Gradient Boosting Classifier
from sklearn.ensemble  import GradientBoostingClassifier
gb_clf = GradientBoostingClassifier(loss='deviance', learning_rate=0.1, n_estimators=100,random_state = 42)

###4.7 evaluate function
def evaluate_clf(clf, features, labels, num_iters=1000, test_size=0.3):
    print (clf)
    accuracy = []
    precision = []
    recall = []
    first = True
    for trial in range(num_iters):
        features_train, features_test, labels_train, labels_test =            train_test_split(features, labels, test_size=test_size)
        clf.fit(features_train, labels_train)
        predictions = clf.predict(features_test)
        accuracy.append(accuracy_score(labels_test, predictions))
        precision.append(precision_score(labels_test, predictions))
        recall.append(recall_score(labels_test, predictions))
        if trial % 10 == 0:
            if first:
                sys.stdout.write('\nProcessing')
            sys.stdout.write('.')
            sys.stdout.flush()
            first = False

    print ("done.\n")
    print ("precision: {}".format(mean(precision)))
    print ("recall:    {}".format(mean(recall)))
    return mean(precision), mean(recall)

evaluate_clf(g_clf, features, labels)
evaluate_clf(l_clf, features, labels)
evaluate_clf(k_clf, features, labels)
evaluate_clf(s_clf, features, labels)
evaluate_clf(rf_clf, features, labels)
evaluate_clf(gb_clf, features, labels)


# The results of precision and recall show less than 0.48, which means that dealing with the imbalanced data is not relevant. 

# precision: 0.32828769841269845
# recall:    0.2859575396825397

# ### Treating imbalanced data
# 
# The data are imbalanced, which means that the people with POI is smaller than the people without POI. Using SMOTE in imblearn, we use knn method to create new value of POI person. The result shoes the same number of non POI and POI, which means it becomes balanced.

# In[56]:


get_ipython().system('pip install imblearn')


# In[57]:


X = df_good.loc[:, df_good.columns != 'poi']
y = df_good.loc[:, df_good.columns == 'poi']
from imblearn.over_sampling import SMOTE
os = SMOTE(random_state=0)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=0)
columns = X_train.columns
os_data_X,os_data_y=os.fit_resample(X_train, y_train)
os_data_X = pd.DataFrame(data=os_data_X,columns=columns )
os_data_y= pd.DataFrame(data=os_data_y,columns=['poi'])
# we can Check the numbers of our data
print("length of the oversampled ",len(os_data_X))
print("Number non poi of the oversampled ",len(os_data_y[os_data_y['poi']==0]))
print("Number poi of the oversampled ",len(os_data_y[os_data_y['poi']==1]))
print("Proportion of non poi of the oversampled ",len(os_data_y[os_data_y['poi']==0])/len(os_data_X))
print("Proportion of poi of the oversampled ",len(os_data_y[os_data_y['poi']==1])/len(os_data_X))


# Using os data, we can see the statistical description of each variable. The plot shows that the distribution is now balanced.

# In[58]:


os_data_X.describe()


# In[59]:


sns.countplot(x='poi',data=os_data_y)
plt.show()


# We now have the new length of the variable.

# In[60]:


#  len(os_data_y)


# ### Turning data into dictionary
# We turn the data into dictionary to match picklefind dictionary from the function created. 

# In[61]:


data_dict_new = pd.concat([os_data_X, os_data_y],axis=1)
data_dict_new.head(10)


# In[62]:


features_list = ['poi','from_messages', 'from_poi_to_this_person', 'from_this_person_to_poi',
       'shared_receipt_with_poi', 'to_messages', 'bonus', 'deferral_payments',
       'deferred_income', 'exercised_stock_options',
       'expenses', 'long_term_incentive', 'other', 'restricted_stock',
       'salary', 'total_payments', 'total_stock_value']


# ### Features engineering

# Feature engineering refers to the process of using domain knowledge to select and transform the most relevant variables from raw data when creating a predictive model using machine learning or statistical modeling.

# In[63]:


os_data_X['all_messages'] = os_data_X['from_messages']+os_data_X['to_messages']

os_data_X['incentive'] = os_data_X["restricted_stock"]/os_data_X["long_term_incentive"]
os_data_X['bonus_salary'] = os_data_X["bonus"]/os_data_X["salary"]
os_data_X['expenses_salary'] = os_data_X["expenses"]/os_data_X["salary"]
os_data_X['shared_ratio'] = os_data_X["shared_receipt_with_poi"]/os_data_X["all_messages"]
os_data_X['all_poi_ratio'] = ((os_data_X["shared_receipt_with_poi"]+
                            os_data_X["from_poi_to_this_person"]+
                            os_data_X["from_this_person_to_poi"])/
                              os_data_X["all_messages"])
os_data_X['fraction_from_poi'] = os_data_X["from_poi_to_this_person"]/os_data_X["to_messages"]
os_data_X['fraction_to_poi'] = os_data_X["fraction_from_poi"]/os_data_X["from_messages"]


# The new dictionary we obtain:

# In[64]:


data_dict_new = pd.concat([os_data_X, os_data_y],axis=1)
data_dict_new.head(10)


# Selecting features using selectKbest:

# In[65]:


my_dataset = data_dict_new.to_dict('index')
# 3.3 create new copies of feature list for grading
my_feature_list = features_list + ['shared_ratio','all_poi_ratio',
                                   "incentive","bonus_salary","expenses_salary",
                                   'to_messages', 'from_poi_to_this_person',
                                   'from_messages', 'from_this_person_to_poi','shared_receipt_with_poi',
                                   'fraction_to_poi']
# my_feature_list = features_list +["shared_ratio",'to_messages', 'from_poi_to_this_person', 'from_messages', 'from_this_person_to_poi','shared_receipt_with_poi', 'fraction_to_poi']


# my_feature_list = 

# 3.4 get K-best features
num_features = 7

# 3.5 function using SelectKBest
def get_k_best(data_dict, features_list, k):
    """ runs scikit-learn's SelectKBest feature selection
        returns dict where keys=features, values=scores
    """
    data = featureFormat(data_dict, features_list)
    labels, features = targetFeatureSplit(data)

    k_best = SelectKBest(k=k)
    k_best.fit(features, labels)
    scores = k_best.scores_
    print(scores)
    unsorted_pairs = zip(features_list[1:], scores)
    sorted_pairs = list(reversed(sorted(unsorted_pairs, key=lambda x: x[1])))
    k_best_features = dict(sorted_pairs[:k])
    print ("{0} best features: {1}\n".format(k, k_best_features.keys(), scores))
    return k_best_features

best_features = get_k_best(my_dataset, my_feature_list, num_features)

# test=["fraction_to_poi",'shared_receipt_with_poi',"fraction_from_poi"]#,"salary",'exercised_stock_options','total_stock_value','bonus']

my_feature_list = [target_label] +list(set(best_features.keys()))#ltest#list(set(best_features.keys()))

# 3.6 print features
# print ("{0} selected features: {1}\n".format(len(my_feature_list) - 1, my_feature_list[1:]))
print ("{0} selected features: {1}\n".format(len(my_feature_list), best_features))

# 3.7 extract the features specified in features_list
data = featureFormat(my_dataset, my_feature_list,sort_keys = True)
# split into labels and features
labels, features = targetFeatureSplit(data)

# 3.8 scale features via min-max
from sklearn import preprocessing
scaler = preprocessing.MinMaxScaler()
features = scaler.fit_transform(features)


# ### Extracting features and labels from dataset for local testing

# In[66]:


data = featureFormat(my_dataset, my_feature_list,sort_keys = True)
# split into labels and features
labels, features = targetFeatureSplit(data)


# ### Scaling the features by MinMaxScaler from Sklearn preprocessing module

# In[67]:


# 3.8 scale features via min-max
from sklearn import preprocessing
scaler = preprocessing.MinMaxScaler()
features = scaler.fit_transform(features)


# 
# ## TASK 4: Try a variety of classifiers
# We will try different classifiers to see which of the classifiers' prediction is the best. Classifiers are named clf for easy export.

# #### 4.1 Gaussian Naive Bayes Classifier

# In[68]:


from sklearn.naive_bayes import GaussianNB
g_clf = GaussianNB()


# #### 4.2  Logistic Regression Classifier

# In[69]:


from sklearn.linear_model import LogisticRegression

l_clf = Pipeline(steps=[
        ('scaler', StandardScaler()),
        ('classifier', LogisticRegression(C=1e-08, class_weight=None, dual=False, fit_intercept=True, intercept_scaling=1, 
max_iter=100, multi_class='ovr', penalty='l2', random_state=42, solver='liblinear', tol=0.001, verbose=0))])

l_clf = Pipeline(steps=[
        ('scaler', StandardScaler()),
        ('classifier', LogisticRegression(C=100, class_weight="balanced", dual=False, fit_intercept=True, intercept_scaling=1, 
max_iter=100, multi_class='ovr', penalty='l1', random_state=42, solver='liblinear', tol=0.0001, verbose=0, warm_start=False))])


# #### 4.3  K-means Clustering

# In[70]:


from sklearn.cluster import KMeans
k_clf = KMeans(n_clusters=2, tol=0.001)


# #### 4.4 Support Vector Machine Classifier

# In[71]:


from sklearn.svm import SVC
s_clf = SVC(kernel='rbf', C=1000,gamma = 0.0001,random_state = 42, class_weight = 'balanced')


# #### 4.5 Random Forest

# In[72]:


from sklearn.ensemble import RandomForestClassifier
rf_clf = RandomForestClassifier(max_depth = 5,max_features = 'sqrt',n_estimators = 10, random_state = 42)


# #### 4.6 Gradient Boosting Classifier

# In[73]:


from sklearn.ensemble  import GradientBoostingClassifier
gb_clf = GradientBoostingClassifier(loss='deviance', learning_rate=0.1, n_estimators=100,random_state = 42)


# ### Evaluate Function

# In[74]:


def evaluate_clf(clf, features, labels, num_iters=1000, test_size=0.3):
    print (clf)
    accuracy = []
    precision = []
    recall = []
    first = True
    for trial in range(num_iters):
        features_train, features_test, labels_train, labels_test =            train_test_split(features, labels, test_size=test_size)
        clf.fit(features_train, labels_train)
        predictions = clf.predict(features_test)
        accuracy.append(accuracy_score(labels_test, predictions))
        precision.append(precision_score(labels_test, predictions))
        recall.append(recall_score(labels_test, predictions))
        if trial % 10 == 0:
            if first:
                sys.stdout.write('\nProcessing')
            sys.stdout.write('.')
            sys.stdout.flush()
            first = False

    print ("done.\n")
    print ("precision: {}".format(mean(precision)))
    print ("recall:    {}".format(mean(recall)))
    return mean(precision), mean(recall)


### 4.8 Evaluate all functions
evaluate_clf(g_clf, features, labels)


# In[75]:


evaluate_clf(g_clf, features, labels)
evaluate_clf(l_clf, features, labels)
evaluate_clf(k_clf, features, labels)
evaluate_clf(s_clf, features, labels)
evaluate_clf(rf_clf, features, labels)
evaluate_clf(gb_clf, features, labels)


# As we can see we got really better results

# we can still improve our model by selecting the best test set, in order to avoid overfit and data leakage

# <center><img src="stra.png" alt="Getting started" /></center>

# In[76]:


features_list = ['poi','from_messages', 'from_poi_to_this_person', 'from_this_person_to_poi',
       'shared_receipt_with_poi', 'to_messages', 'bonus', 'deferral_payments',
       'deferred_income', 'exercised_stock_options',
       'expenses', 'long_term_incentive', 'other', 'restricted_stock',
       'salary', 'total_payments', 'total_stock_value']


# A model rely on several parameters and in order to select the best, we will use a GridSearch

# <center><img src="grid.png" alt="Getting started" /></center>

# In[78]:


best_features = get_k_best(my_dataset, features_list, num_features)

my_feature_list = [target_label] + list(set(best_features.keys()))

# 3.6 print features
print ("{0} selected features: {1}\n".format(len(my_feature_list) - 1, my_feature_list[1:]))

# 3.7 extract the features specified in features_list
data = featureFormat(my_dataset, my_feature_list,sort_keys = True)
# split into labels and features
labels, features = targetFeatureSplit(data)

# 3.8 scale features via min-max
from sklearn import preprocessing
scaler = preprocessing.MinMaxScaler()
features = scaler.fit_transform(features)

from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import make_pipeline
from  sklearn.tree import DecisionTreeClassifier
from sklearn.decomposition import PCA
pl = make_pipeline(SelectKBest(), PCA(random_state = 42, svd_solver='randomized'), DecisionTreeClassifier(random_state = 42))
params = dict(
	selectkbest__k = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
	decisiontreeclassifier__criterion = ['gini', 'entropy'],
	decisiontreeclassifier__splitter = ['best', 'random']
)

pca = PCA(n_components='mle')

from time import time

grid = GridSearchCV(pl, param_grid = params, scoring = 'recall')


from sklearn.ensemble import AdaBoostClassifier
clf_AdaBoost = AdaBoostClassifier()


# ### TASK 5: Tune the classifier
# 
# We tune the classifier to achieve better precision and recall.
# 
# Because of the small size of the dataset, the script uses stratified shuffle split cross validation to test the classifiers. Therefore, the data is shuffled each time before being split into split into a specified number of folds (compared to StratifiedKFold, which shuffles only once at the beginning).
# 
# In practice, the PCA improves training rate, simplifies the required neural structure to represent the data, and results in systems that better characterize the "intermediate structure" of the data instead of having to account for multiple scales - it is more accurate.
# 
# Our guess is that there are analogous reasons that apply to random forests of gradient boosted trees or other similar creatures.

# In[79]:


from sklearn.model_selection import train_test_split
features_train, features_test, labels_train, labels_test =     train_test_split(features, labels, test_size=0.3, random_state=42)

pca.fit(features_train)
features_train_pca = pca.transform(features_train)
features_test_pca = pca.transform(features_test)

grid.fit(features_train, labels_train)
clf_DT = grid.best_estimator_

t0 = time()
clf_DT.fit(features_train,labels_train)
print ("Decision Tree - training time:", round(time()-t0, 3), "s")
t1 = time()
predictions_DT = clf_DT.predict(features_test)
print ("Decision Tree - prediction time:", round(time()-t1, 3), "s")

t0 = time()
clf_AdaBoost.fit(features_train_pca,labels_train)
print( "AdaBoost - training time:", round(time()-t0, 3), "s")
t1 = time()
predictions_AdaBoost = clf_AdaBoost.predict(features_test_pca)
print ("AdaBoost - prediction time:", round(time()-t1, 3), "s")

### Stochastic Gradient Descent
from sklearn import linear_model
clf_SGD = linear_model.SGDClassifier(class_weight = "balanced")

### Gaussian Naive Bayes
from sklearn.naive_bayes import GaussianNB
clf_NB = GaussianNB()

### Random Forests
from sklearn.ensemble import RandomForestClassifier
clf_RF = RandomForestClassifier()


clf_SGD.fit(features_train_pca,labels_train)
predictions_SGD = clf_SGD.predict(features_test_pca)

clf_NB.fit(features_train_pca,labels_train)
predictions_NB = clf_NB.predict(features_test_pca)

clf_RF.fit(features_train_pca,labels_train)
predictions_RF = clf_RF.predict(features_test_pca)


from sklearn.metrics import precision_score, recall_score
print ("precision score for the Gaussian Naive Bayes Classifier : ",precision_score(labels_test,predictions_NB))
print ("recall score for the Gaussian Naive Bayes Classifier : ",recall_score(labels_test,predictions_NB))

print ("precision score for the Decision tree Classifier : ",precision_score(labels_test,predictions_DT))
print ("recall score for the Decision tree Classifier : ",recall_score(labels_test,predictions_DT))

print ("precision score for the AdaBoost Classifier : ",precision_score(labels_test,predictions_AdaBoost))
print ("recall score for the AdaBoost Classifier : ",recall_score(labels_test,predictions_AdaBoost))

print ("precision score for the Random Forest Classifier : ",precision_score(labels_test,predictions_RF))
print ("recall score for the Random Forest Classifier : ",recall_score(labels_test,predictions_RF))

print ("precision score for the Stochastic Gradient Descent Classifier : ",precision_score(labels_test,predictions_SGD))
print ("recall score for the Stochastic Gradient Descent Classifier : ",recall_score(labels_test,predictions_SGD))


# In[81]:


clf_SVC = SVC(gamma=3, C=2)
clf_SVC.fit(features_train,labels_train)
pickle.dump(my_dataset, open("my_dataset.pkl", "wb"))
pickle.dump(my_feature_list, open("my_feature_list.pkl", "wb"))

all_classifiers_list = [g_clf, l_clf, k_clf, s_clf, s_clf, rf_clf, gb_clf]
import tester
for clf in all_classifiers_list:
    print("Results classifier:")
    pickle.dump(clf, open("my_classifier.pkl", "wb"))
    tester.dump_classifier_and_data(clf, my_dataset, my_feature_list)
    tester.main();


# In[84]:


evaluate_clf(clf_SGD, features, labels)
evaluate_clf(clf_NB, features, labels)
evaluate_clf(clf_RF, features, labels)
evaluate_clf(clf_SVC, features, labels)


# ### TASK 6: Dump classifier, dataset, and features_list

# In[85]:


pickle.dump(my_dataset, open("my_dataset.pkl", "wb"))
pickle.dump(my_feature_list, open("my_feature_list.pkl", "wb"))   


# #### Final evaluation using tester.py script

# In[86]:


import tester 

all_classifiers_list = [g_clf, l_clf, k_clf, s_clf, s_clf, rf_clf, gb_clf]

for clf in all_classifiers_list:
    print("Results classifier:")
    pickle.dump(clf, open("my_classifier.pkl", "wb"))
    tester.dump_classifier_and_data(clf, my_dataset, my_feature_list)
    tester.main();


#    <center><img src="vote.png" alt="Getting started" /></center>

# dump&nbsp;your&nbsp;classifier,&nbsp;dataset&nbsp;and&nbsp;features_list

# &nbsp;so anyone&nbsp;can&nbsp;run/check&nbsp;your&nbsp;results

# In[87]:


clf = gb_clf




pickle.dump(clf, open("my_classifier.pkl", "wb"))
pickle.dump(my_dataset, open("my_dataset.pkl", "wb"))
pickle.dump(my_feature_list, open("my_feature_list.pkl", "wb"))

dump_classifier_and_data(clf, my_dataset, features_list)


# End conclusion:
# 
# Both **Random Forest** and **Gradient Boosting** are superior to the other algorithms used in terms of accuracy, precision and recall. 
# 
# Because the *recall* represents the number of hits (correctly identified POI's) in relation to the sum of hit and miss (all POI's to be detected), the *recall* is in this context, where the detection of fraud has priority, the most important parameter, especially compared to the in this context secondary *precision*, which describes the ratio of the number of hits relative to all supposedly detected frauds.
# 
# Although the Random Forest is superior to Gradient Boosting with about 87% precision, **Gradient Boosting** is therefore suggested as the most suitable algorithm in this context: with about 90% recall it is superior to the Random Forest in this respect.

#    <center><img src="thk.jpg" alt="Getting started" /></center>
