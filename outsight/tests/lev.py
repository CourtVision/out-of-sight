from Levenshtein import distance

def _load_list(path):
    with open(path, 'r') as f:
        whitelist = [plate.rstrip() for plate in f]
    return whitelist

whitelist = _load_list('io\photos_input\whitelist.txt')
distances = []
for i in whitelist:
    d = distance('KL5522473', i)
    distances.append(d)
    dist_dict = dict(zip(whitelist, distances))
    min_d_key = min(dist_dict, key=dist_dict.get) 
    min_d = dist_dict.get(min_d_key)

print(min_d)
print(min_d_key)
print(dist_dict)