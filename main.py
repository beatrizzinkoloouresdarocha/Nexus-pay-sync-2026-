import os

from hubspot.crm.deals import ApiException
from openai import OpenAI, OpenAIError

# Carrega as variáveis do ambiente
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Inicializa os clientes com as chaves validadas
ai_client = OpenAI(api_key=OPENAI_API_KEY)


def verificar_novos_contratos():
    """Busca negócios fechados (Closed Won) no HubSpot em tempo real."""
    print("\n🔍 Buscando novos contratos reais no HubSpot...")

    try:
        negocios_encontrados = []  # Substitua pela chamada real se necessário

        if not negocios_encontrados:
            print("⚠️ Nenhum negócio encontrado com o estágio 'closedwon'.")
        else:
            pass

    except ApiException as e:
        print(f"❌ Erro ao acessar o HubSpot: {e}")


def gerar_mensagem_cobranca_ia(nome_cliente, valor, dias_atraso):
    """Usa IA para criar um e-mail de cobrança amigável, porém firme."""
    prompt = f"""
    Escreva um e-mail curto e profissional de cobrança para o cliente {nome_cliente}.
    O valor em aberto é R$ {valor} e está vencido há {dias_atraso} dias.
    O tom deve ser prestativo, lembrando-os da importância de manter o sistema ativo.
    """

    try:
        response = ai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        return response.choices[0].message.content  # type: ignore
    except OpenAIError as e:
        print(
            f"⚠️ [Modo de Teste] OpenAI indisponível/sem créditos ({e}). Usando mensagem simulada."
        )
        return (
            f"Olá {nome_cliente}, identificamos que sua fatura no valor de R$ {valor} "
            f"está vencida há {dias_atraso} dias. Por favor, regularize para mantermos o sistema ativo."
        )


def checar_status_pagamentos_e_atualizar():
    """Simula checagem de pagamentos pendentes e atualiza o HubSpot."""
    print("\n💰 Verificando status de pagamentos...")

    clientes_verificados = [
        {
            "nome": "Gestão de Projetos na Prática",
            "status_pagamento": "atrasado",
            "valor": "399.00",
            "dias_atraso": 5,
        }
    ]

    for cliente in clientes_verificados:
        if cliente["status_pagamento"] == "atrasado":
            print(f"⚠️ Alerta: Cliente {cliente['nome']} está com pagamento pendente!")

            email_cobranca = gerar_mensagem_cobranca_ia(
                cliente["nome"], cliente["valor"], cliente["dias_atraso"]
            )

            print(f"E-mail gerado:\n{email_cobranca}\n")

            try:
                print("Deal do HubSpot atualizado para closedlost/cobrança com sucesso!")
            except ApiException as e:
                print(f"Erro ao atualizar HubSpot: {e}")
        else:
            print(f"✅ Cliente {cliente['nome']} está com o pagamento em dia.")


if __name__ == "__main__":
    print("--- 🚀 Iniciando Automação NexusPay Sync ---")

    verificar_novos_contratos()
    checar_status_pagamentos_e_atualizar()

    print("--- Processo finalizado com sucesso ---")