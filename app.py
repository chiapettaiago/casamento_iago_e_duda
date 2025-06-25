from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import datetime
import json
import os

app = Flask(__name__)
CORS(app)  # Habilitando CORS para toda a aplicação

# Diretório para armazenar as inscrições de push
SUBSCRIPTIONS_FILE = 'subscriptions.json'

# Função para carregar as inscrições salvas
def load_subscriptions():
    if os.path.exists(SUBSCRIPTIONS_FILE):
        with open(SUBSCRIPTIONS_FILE, 'r') as f:
            return json.load(f)
    return []

# Função para salvar as inscrições
def save_subscriptions(subscriptions):
    with open(SUBSCRIPTIONS_FILE, 'w') as f:
        json.dump(subscriptions, f)

# Garantir que o arquivo exista
if not os.path.exists(SUBSCRIPTIONS_FILE):
    save_subscriptions([])

# Data do casamento - Ajuste conforme necessário
TARGET_DATE = datetime.datetime(2025, 9, 5, 9, 30, 00)  # Year, Month, Day, Hour, Minute, Second

nomes = ['Iago', 'Maria Eduarda']

# Mensagens diárias para notificações
# Cada número representa o dia específico antes do casamento
# Para dias não listados, serão usadas mensagens aleatórias
NOTIFICACOES_ESPECIAIS = {
    180: "Faltam 6 meses para o casamento de Iago e Maria Eduarda! Marque em sua agenda: 05/09/2025!",
    90: "Faltam 3 meses para o casamento de Iago e Maria Eduarda! O grande dia está chegando!",
    60: "Apenas 2 meses para o casamento! Reserve a data: 05/09/2025 - Casamento Iago e Maria Eduarda!",
    30: "30 dias para o casamento de Iago e Maria Eduarda! Logo seremos todos testemunhas desse momento!",
    14: "Apenas 2 semanas! O casamento de Iago e Maria Eduarda será em 05/09/2025. Esteja presente!",
    7: "Falta apenas 1 semana para o casamento de Iago e Maria Eduarda! Estamos ansiosos para celebrar com você!",
    3: "Apenas 3 dias para o casamento! Dia 05/09/2025, Iago e Maria Eduarda esperam por você!",
    2: "Em 2 dias, Iago e Maria Eduarda celebrarão seu amor! Não perca esse momento especial!",
    1: "Amanhã é o grande dia! O casamento de Iago e Maria Eduarda acontece amanhã!",
    0: "É hoje! O casamento de Iago e Maria Eduarda acontece hoje! Estamos esperando por você!"
}

# Mensagens genéricas para os demais dias
MENSAGENS_DIARIAS = [
    "Não esqueça: Dia 05/09/2025 é o casamento de Iago e Maria Eduarda!",
    "Marque em seu calendário: Faltam {dias} dias para o casamento de Iago e Maria Eduarda!",
    "Contagem regressiva: {dias} dias para o casamento! Esteja presente nesse momento especial!",
    "Iago e Maria Eduarda contam com sua presença em seu casamento, faltam apenas {dias} dias!",
    "Lembrete especial: O casamento de Iago e Maria Eduarda acontece em {dias} dias!",
    "Atualize sua agenda: {dias} dias para o casamento de Iago e Maria Eduarda!",
    "Faltam {dias} dias para o casamento! Iago e Maria Eduarda esperam por você!",
    "O amor está no ar! {dias} dias para o casamento de Iago e Maria Eduarda!"
]

# Servir o service worker na raiz
@app.route('/sw.js')
def service_worker():
    return send_from_directory('static', 'sw.js')

# Servir arquivos estáticos
@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

@app.route('/')
def index():
    return render_template('index.html', nomes=nomes)

@app.route('/api/route')
def api_route():
    current_time = datetime.datetime.now()
    time_left = TARGET_DATE - current_time
    days_left = time_left.days
    hours_left, remainder = divmod(time_left.seconds, 3600)
    minutes_left, seconds_left = divmod(remainder, 60)
    
    # Calcular o total de segundos para verificar se a contagem acabou
    total_seconds = time_left.total_seconds()
    
    # Verificar se temos uma notificação para o período atual
    notificacao = None
    
    # Usar mensagem especial para dias específicos ou escolher uma mensagem diária aleatória
    if days_left in NOTIFICACOES_ESPECIAIS:
        mensagem = NOTIFICACOES_ESPECIAIS[days_left]
        notificacao = {
            "dias": days_left,
            "mensagem": mensagem,
            "mostrar": True
        }
    else:
        import random
        mensagem_template = random.choice(MENSAGENS_DIARIAS)
        mensagem = mensagem_template.format(dias=days_left)
        notificacao = {
            "dias": days_left,
            "mensagem": mensagem,
            "mostrar": True
        }

    response = {
        'days': days_left,
        'hours': hours_left,
        'minutes': minutes_left,
        'seconds': seconds_left,
        'total_seconds': total_seconds,
        'notificacao': notificacao
    }
    
    return jsonify(response)

# Rota para salvar inscrição de push
@app.route('/api/subscribe', methods=['POST'])
def subscribe():
    subscription_info = request.json
    
    # Carregar inscrições existentes
    subscriptions = load_subscriptions()
    
    # Verificar se a inscrição já existe
    subscription_exists = False
    for sub in subscriptions:
        if sub.get('endpoint') == subscription_info.get('endpoint'):
            subscription_exists = True
            break
            
    # Adicionar nova inscrição se não existir
    if not subscription_exists:
        subscriptions.append(subscription_info)
        save_subscriptions(subscriptions)
    
    return jsonify({'success': True})

# Rota para cancelar inscrição
@app.route('/api/unsubscribe', methods=['POST'])
def unsubscribe():
    subscription_info = request.json
    
    # Carregar inscrições existentes
    subscriptions = load_subscriptions()
    
    # Remover a inscrição
    subscriptions = [sub for sub in subscriptions 
                    if sub.get('endpoint') != subscription_info.get('endpoint')]
    
    # Salvar as inscrições atualizadas
    save_subscriptions(subscriptions)
    
    return jsonify({'success': True})

# Nova rota para a página de data
@app.route('/data')
def data_page():
    return render_template('data.html', data=TARGET_DATE)

# Nova rota para a página de local
@app.route('/local')
def local_page():
    return render_template('local.html')

# Nova rota para a página de presentes
@app.route('/presentes')
def presentes_page():
    return render_template('presentes.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)