# Compare two feature lists

with open("language_features_1.txt", "r", encoding="utf-8") as f:
    features_1 = {line.strip() for line in f if line.strip()}

with open("language_features_2.txt", "r", encoding="utf-8") as f:
    features_2 = {line.strip() for line in f if line.strip()}

only_in_1 = features_1 - features_2

print("Features in language_features_1.txt but not language_features_2.txt:")
for feature in sorted(only_in_1):
    print(feature)

only_in_2 = features_2 - features_1

print("Features in language_features_2.txt but not language_features_1.txt:")
for feature in sorted(only_in_2):
    print(feature)