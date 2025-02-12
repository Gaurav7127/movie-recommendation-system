import joblib
import pandas as pd

# Load original pickle files
movies_dict = pd.read_pickle('movies_dict.pkl')
similarity = pd.read_pickle('similarity.pkl')

# Save compressed versions
joblib.dump(movies_dict, 'movies_dict_compressed.pkl', compress=3)
joblib.dump(similarity, 'similarity_compressed.pkl', compress=3)
