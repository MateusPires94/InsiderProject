def postprocess(predictions):
    # Exemplo: converter para tipos nativos
    return [float(p) for p in predictions]