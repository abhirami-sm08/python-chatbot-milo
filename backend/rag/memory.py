from collections import defaultdict

MAX_HISTORY = 5

conversation_memory = defaultdict(list)


def add_message(customer_id, role, message):

    conversation_memory[customer_id].append(
        {
            "role": role,
            "message": message
        }
    )

    if len(conversation_memory[customer_id]) > MAX_HISTORY * 2:

        conversation_memory[customer_id] = (
            conversation_memory[customer_id][-MAX_HISTORY * 2:]
        )


def get_history(customer_id):

    history = conversation_memory.get(customer_id, [])

    if not history:
        return ""

    formatted = ""

    for chat in history:

        formatted += (
            f"{chat['role']}: "
            f"{chat['message']}\n"
        )

    return formatted


def clear_history(customer_id):

    if customer_id in conversation_memory:

        del conversation_memory[customer_id]