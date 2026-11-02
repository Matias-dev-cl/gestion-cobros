def interface(request):
    """Choose public or staff navigation without changing view permissions."""
    match = request.resolver_match
    namespace = match.namespace if match else ''
    name = match.url_name if match else ''
    public = namespace == 'login' or (namespace == 'reportes' and name in {
        'revisar_consumo', 'simular_pago'})
    return {'fw_private': request.user.is_authenticated and not public}
