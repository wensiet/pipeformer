import urllib.parse


def extract_compute_name(path: str):
    paths = path.replace(".yaml", "").replace(".yml", "").split("/")
    if "compute" in paths:
        paths.remove("compute")
    res = ""
    for p in paths:
        res += p + "-"
    res = res.rstrip("-")
    return res


def get_id_by_uniq(timeweb, uniq: str):
    computes = timeweb.list_computes()
    for compute in computes:
        if compute.name == uniq:
            return compute.id
    raise ValueError(f"Compute with name {uniq} not found")


def url_encode(data: str):
    url_encoded = urllib.parse.quote(data)
    return url_encoded
