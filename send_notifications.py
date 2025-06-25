import json
import datetime
import time
import requests
from pywebpush import webpush, WebPushException
import os

# Arquivo de configuração com as chaves VAPID
VAPID_PRIVATE_KEY = "YOUR_VAPID_PRIVATE_KEY"  # Substitua por sua chave privada VAPID 
VAPID_PUBLIC_KEY = "BEl62iUYgUivxIkv69yViEuiBIa-Ib9-SkvMeAtA3LFgDzkrxZJjSgSnfckjBJuBkr3qBUYIHBQFLXYp5Nksh8U"  # Substitua por sua chave pública VAPID
VAPID_CLAIMS = {
    "sub": "mailto:iagochiapetta@gmail.com"  # Substitua por seu e-mail
}

SUBSCRIPTIONS_FILE = 'subscriptions.json'
TARGET_DATE = datetime.datetime(2025, 9, 5, 9, 30, 00)  # Ano, Mês, Dia, Hora, Minuto, Segundo

# Mensagens diárias para notificações
# Cada número representa o dia específico antes do casamento
# Para dias não listados, serão usadas mensagens aleatórias da lista MENSAGENS_DIARIAS
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

def load_subscriptions():
    """Carregar as inscrições de push do arquivo"""
    if os.path.exists(SUBSCRIPTIONS_FILE):
        with open(SUBSCRIPTIONS_FILE, 'r') as f:
            return json.load(f)
    return []

def send_push_notification(subscription, title, body):
    """Enviar notificação push para um dispositivo inscrito"""
    try:
        response = webpush(
            subscription_info=subscription,
            data=json.dumps({
                "title": title,
                "body": body,
                "url": "http://localhost:5001"
            }),
            vapid_private_key=VAPID_PRIVATE_KEY,
            vapid_claims=VAPID_CLAIMS
        )
        print(f"Notificação enviada, status: {response.status_code}")
        return True
    except WebPushException as e:
        print(f"Erro ao enviar notificação push: {e}")
        # Se a inscrição expirou ou não é mais válida (erro 410), retorne False
        if e.response and e.response.status_code == 410:
            return False
        return True
    except ValueError as e:
        # Erro de serialização da chave VAPID, ignorar para testes de demonstração
        print(f"Aviso de VAPID (ignore em testes): {e}")
        return True

def check_and_send_notifications():
    """Verificar e enviar notificações diárias baseadas na data atual"""
    subscriptions = load_subscriptions()
    if not subscriptions:
        print("Nenhum dispositivo inscrito para receber notificações.")
        return
    
    current_time = datetime.datetime.now()
    time_left = TARGET_DATE - current_time
    days_left = time_left.days
    
    # Se o casamento já passou, não enviar notificações
    if days_left < 0:
        print("O casamento já aconteceu. Nenhuma notificação para enviar.")
        return
    
    # Usar mensagem especial para dias específicos ou escolher uma mensagem diária aleatória
    if days_left in NOTIFICACOES_ESPECIAIS:
        mensagem = NOTIFICACOES_ESPECIAIS[days_left]
    else:
        import random
        mensagem_template = random.choice(MENSAGENS_DIARIAS)
        mensagem = mensagem_template.format(dias=days_left)
    
    print(f"Enviando notificação diária para {len(subscriptions)} dispositivos: {mensagem}")
    
    # Filtrar inscrições inválidas
    valid_subscriptions = []
    
    for subscription in subscriptions:
        is_valid = send_push_notification(
            subscription,
            f"Casamento Iago e Maria Eduarda - {days_left} dias",
            mensagem
        )
        if is_valid:
            valid_subscriptions.append(subscription)
    
    # Atualizar arquivo com apenas inscrições válidas
    if len(valid_subscriptions) < len(subscriptions):
        with open(SUBSCRIPTIONS_FILE, 'w') as f:
            json.dump(valid_subscriptions, f)
        print(f"Removidas {len(subscriptions) - len(valid_subscriptions)} inscrições inválidas.")
    
    print(f"Notificação diária enviada com sucesso para {len(valid_subscriptions)} dispositivos.")

if __name__ == "__main__":
    check_and_send_notifications()
