import os

from dotenv import load_dotenv
from hubspot import HubSpot
from hubspot.crm.deals import ApiException
from openai import OpenAI

# Carrega as variáveis do arquivo .env
load_dotenv()

HUBSPOT_TOKEN = os.getenv("HUBSPOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Inicializa os clientes
hubspot_client = HubSpot(access_token=HUBSPOT_TOKEN)  # type: ignore
ai_client = OpenAI(api_key=OPENAI_API_KEY)


def verificar_novos_contratos():
    """Busca negócios fechados (Closed Won) no HubSpot para iniciar o processo."""
    print("Buscando novos contratos no HubSpot...")
    try:
        public_object_search_request = {
            "filterGroups": [
                {
                    "filters": [
                        {
                            "propertyName": "dealstage",
                            "operator": "EQ",
                            "value": "closedwon",
                        }
                    ]
                }
            ],
            "properties": ["dealname", "amount", "hs_object_id", "email"],
        }

        response = hubspot_client.crm.deals.search_api.do_search(
            public_object_search_request=public_object_search_request
        )

        assert response is not None
        for deal in response.results:  # type: ignore
            print(
                f"Contrato encontrado: {deal.properties.get('dealname')} - Valor: {deal.properties.get('amount')}"
            )

    except ApiException as e:
        print(f"Erro ao acessar HubSpot: {e}")


def gerar_mensagem_cobranca_ia(nome_cliente, valor, dias_atraso):
    """Usa IA para criar um e-mail de cobrança amigável, porém firme."""
    prompt = f"""
    Escreva um e-mail curto e profissional de cobrança para o cliente {nome_cliente}.
    O valor em aberto é R$ {valor} e está vencido há {dias_atraso} dias.
    O tom deve ser prestativo, lembrando-os da importância de manter o sistema ativo.
    """

    response = ai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )
    return response.choices[0].message.content


def checar_status_pagamentos_e_atualizar():
    """Verifica faturas pendentes, atualiza o HubSpot e usa IA se necessário."""
    print("Verificando status de pagamentos...")

    clientes_verificados = [
        {
            "nome": "Empresa XPTO",
            "email": "financeiro@xpto.com",
            "status_pagamento": "atrasado",
            "valor": "499.00",
            "dias_atraso": 5,
            "hubspot_deal_id": "123456",
        }
    ]

    for cliente in clientes_verificados:
        if cliente["status_pagamento"] == "atrasado":
            print(f"⚠️ Cliente {cliente['nome']} está com pagamento pendente!")

            email_cobranca = gerar_mensagem_cobranca_ia(
                cliente["nome"], cliente["valor"], cliente["dias_atraso"]
            )
            print(f"E-mail gerado pela IA:\n{email_cobranca}\n")

            try:
                hubspot_client.crm.deals.basic_api.update(
                    deal_id=cliente["hubspot_deal_id"],
                    simple_public_object_input={
                        "properties": {"dealstage": "payment_failed"}
                    },
                )
                print("Deal do HubSpot atualizado para inadimplente/atrasado.")
            except ApiException as e:
                print(f"Erro ao atualizar HubSpot: {e}")
        else:
            print(f"✅ Cliente {cliente['nome']} está com o pagamento em dia.")


if __name__ == "__main__":
    print("--- Iniciando Automação NexusPay Sync ---")
    verificar_novos_contratos()
    checar_status_pagamentos_e_atualizar()