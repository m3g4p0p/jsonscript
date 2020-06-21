def get_params(json, params):
    return zip(json.get(
        '@params',
        range(len(params))
    ), params)
