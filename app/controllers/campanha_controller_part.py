
def atualizar_campanha(usuario_id, campanha_id, data):
    """
    Atualiza uma campanha existente (apenas administradores)
    
    Args:
        usuario_id: ID do usuário admin
        campanha_id: ID da campanha a atualizar
        data: Dicionário com dados a atualizar
    
    Returns:
        tuple: (response dict, status code)
    """
    usuario = Usuario.query.get(int(usuario_id))
    
    if not usuario or not usuario.is_admin:
        return {'erro': 'Acesso negado'}, 403
    
    campanha = Campanha.query.get(campanha_id)
    
    if not campanha:
        return {'erro': 'Campanha não encontrada'}, 404
        
    # Atualizar campos se fornecidos
    if 'titulo' in data: campanha.titulo = data['titulo']
    if 'descricao' in data: campanha.descricao = data['descricao']
    if 'slug' in data: campanha.slug = data['slug']
    if 'imagem_principal' in data: campanha.imagem_principal = data['imagem_principal']
    if 'codigo' in data: campanha.codigo = data['codigo']
    if 'tipo' in data: campanha.tipo = data['tipo']
    if 'premio' in data: campanha.premio = data['premio']
    if 'valor_titulo' in data: campanha.valor_titulo = data['valor_titulo']
    if 'total_titulos' in data: campanha.total_titulos = data['total_titulos']
    if 'regulamento' in data: campanha.regulamento = data['regulamento']
    if 'status' in data: campanha.status = data['status']
    
    # Datas
    if 'data_sorteio' in data:
        campanha.data_sorteio = datetime.fromisoformat(data['data_sorteio']) if data['data_sorteio'] else None
        
    if 'data_fim' in data:
        campanha.data_fim = datetime.fromisoformat(data['data_fim']) if data['data_fim'] else None
    
    db.session.commit()
    
    return {
        'mensagem': 'Campanha atualizada com sucesso',
        'campanha': campanha.to_dict()
    }, 200
