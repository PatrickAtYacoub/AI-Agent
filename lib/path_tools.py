from container_tools import as_list


def path_cat(*paths):
    result = []
    for path in paths:
        if isinstance(path, type):
            components = path.__qualname__.split('.')
        elif isinstance(path, str):
            components = path.split('.')
        else:
            components = as_list(path)
        result.extend(components)
    return result

def path_get(nested_mapping, path, default=None, track_list=None):
    if nested_mapping is None or path is None:
        return default
    
    path = path_cat(path)
    components = list(path)
    current = nested_mapping
    
    while len(components) > 0:
        key = components.pop(0)
        if track_list is not None:
            track_list.append(key)
        
        if isinstance(current, (list, tuple)):
            try:
                index = int(key)
                current = current[index]
            except (ValueError, IndexError):
                return default
        else:
            if key in current:
                current = current[key]
            else:
                return default
    
    return current