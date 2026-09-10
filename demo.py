from urielplus import urielplus

u = urielplus.URIELPlus()

# u.reset()

#Configuration
u.set_cache(True)

#Aggregation
# u.set_aggregation('A')

#Integrating databases
u.integrate_databases()

#Feature Coverage
# u.all_feature_coverage()

# # Imputation
u.softimpute_imputation()

#Feature Coverage
# u.all_feature_coverage()

# #Distance Calculation
# print(u.new_distance("script", "stan1290", "stan1293"))

# #Vector Retrieval
# english = "stan1293"  # Glottocode for Standard English

# vector = u.get_vector("syntactic", english)
# print(vector[english][:10])

# french = "stan1290"  # Glottocode for Standard French
# vectors = u.get_vector("syntactic", [english, french])
# print("English vector length:", len(vectors[english]))
# print("French vector length:", len(vectors[french]))

# typological_feats = u.get_typological_features_array()
# target_feature = "S_OBJECT_AFTER_VERB"
# feat_idx = list(typological_feats).index(target_feature)
# lang_idx = list(u.get_typological_languages_array()).index(english)
# raw_sources_for_feature = u.get_typological_data_array()[lang_idx][feat_idx]
# print(f"{target_feature} raw per-source values for English:", raw_sources_for_feature)
# print(f"{target_feature} via get_vector:", vector[english][feat_idx])