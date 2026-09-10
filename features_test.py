# #Exploring the language vectors npz files within data folder for lang2vec (URIEL). 

import numpy as np 

#features.npz

# Load the NPZ file 
npz_file = np.load('urielplus/database/features.npz', allow_pickle=True) 

# List the names of the arrays stored in the file 
print("Arrays in the NPZ file:", npz_file.files) 
    
# Optionally, you can access individual arrays by their names 
features = npz_file['feats'] 
languages = npz_file['langs'] 
sources = npz_file['sources'] 
data = npz_file['data'] 

#List of features 
with open("language_features.txt", "w", encoding='utf-8') as f: 
    for item in features: f.write(f"{item}\n") 
    print("Array written to language_features.txt") 

#List of languages 
with open("language_names.txt", "w", encoding='utf-8') as f: 
    for item in languages: 
        f.write(f"{item}\n") 
    print("Array written to language_names.txt") 

#List of sources
with open("feature_sources.txt", "w", encoding='utf-8') as f: 
    for item in sources: f.write(f"{item}\n") 
    print("Array written to feature_sources.txt") 


#Individual language   
lang = 1488

with open("language_names.txt", "r", encoding='utf-8') as f:
    counter = 1
    for line in f:
        if counter == lang:
            file_name = line.strip() + ".txt"
        counter += 1

# Set print options to ensure no truncation 
np.set_printoptions(threshold=np.inf) 

# Write the array to a file 
with open(file_name, "w", encoding='utf-8') as f: 
    f.write(np.array2string(data[lang-1].astype(int), separator=', '))
    print("Array written to " + file_name)


# #family_features.npz

# # Load the NPZ file 
# npz_file = np.load('lang2vec/data/family_features.npz', allow_pickle=True) 

# # List the names of the arrays stored in the file 
# print("Arrays in the NPZ file:", npz_file.files) 
    
# # Optionally, you can access individual arrays by their names 
# features = npz_file['feats'] 
# languages = npz_file['langs'] 
# sources = npz_file['sources'] 
# data = npz_file['data'] 

# #List of features 
# with open("fam_language_features.txt", "w", encoding='utf-8') as f: 
#     for item in features: f.write(f"{item}\n") 
#     print("Array written to language_features.txt") 

# #List of languages 
# with open("fam_language_names.txt", "w", encoding='utf-8') as f: 
#     for item in languages: 
#         f.write(f"{item}\n") 
#     print("Array written to geo_language_names.txt") 

# #List of sources
# with open("fam_feature_sources.txt", "w", encoding='utf-8') as f: 
#     for item in sources: f.write(f"{item}\n") 
#     print("Array written to feature_sources.txt") 


# #Individual language   
# lang = 7871

# with open("fam_language_names.txt", "r", encoding='utf-8') as f:
#     counter = 1
#     for line in f:
#         if counter == lang:
#             file_name = line.strip() + ".txt"
#         counter += 1

# # Set print options to ensure no truncation 
# np.set_printoptions(threshold=np.inf) 

# # Write the array to a file 
# with open(file_name, "w", encoding='utf-8') as f: 
#     f.write(np.array2string(data[lang-1], separator=', ')) 
#     print("Array written to " + file_name)


# #geocoord_features.npz

# # Load the NPZ file 
# npz_file = np.load('lang2vec/data/geocoord_features.npz', allow_pickle=True) 

# # List the names of the arrays stored in the file 
# print("Arrays in the NPZ file:", npz_file.files) 
    
# # Optionally, you can access individual arrays by their names 
# features = npz_file['feats'] 
# languages = npz_file['langs'] 
# sources = npz_file['sources'] 
# data = npz_file['data'] 

# #List of features 
# with open("geo_language_features.txt", "w", encoding='utf-8') as f: 
#     for item in features: f.write(f"{item}\n") 
#     print("Array written to geo_language_features.txt") 

# #List of languages 
# with open("geo_language_names.txt", "w", encoding='utf-8') as f: 
#     for item in languages: 
#         f.write(f"{item}\n") 
#     print("Array written to geo_language_names.txt") 

# #List of sources
# with open("geo_feature_sources.txt", "w", encoding='utf-8') as f: 
#     for item in sources: f.write(f"{item}\n") 
#     print("Array written to geo_feature_sources.txt") 


# #Individual language   
# lang = 7979

# with open("geo_language_names.txt", "r", encoding='utf-8') as f:
#     counter = 1
#     for line in f:
#         if counter == lang:
#             file_name = line.strip() + ".txt"
#         counter += 1

# # Set print options to ensure no truncation 
# np.set_printoptions(threshold=np.inf) 

# # Write the array to a file 
# with open(file_name, "w", encoding='utf-8') as f: 
#     f.write(np.array2string(data[lang-1], separator=', ')) 
#     print("Array written to " + file_name)