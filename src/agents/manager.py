from llms.OpenAI import ChatAssistant


class AgentManager:
    def __init__(self):
        self.next_key = 0
        self.agents = {}  # key, (task, full_message_history, model)
        self.chat = ChatAssistant()

    def create_agent(self, task, prompt, model):
        messages = [{"role": "user", "content": prompt}]

        agent_reply = self.chat.create_chat_completion(
            model=model,
            messages=messages,
        )

        messages.append({"role": "assistant", "content": agent_reply})

        key = self.next_key
        self.next_key += 1

        self.agents[key] = (task, messages, model)

        return key, agent_reply

    def message_agent(self, key, message):
        task, messages, model = self.agents[int(key)]

        messages.append({"role": "user", "content": message})

        agent_reply = self.chat.create_chat_completion(
            model=model,
            messages=messages,
        )

        messages.append({"role": "assistant", "content": agent_reply})

        return agent_reply

    def list_agents(self):
        return [(key, task) for key, (task, _, _) in self.agents.items()]

    def delete_agent(self, key):
        try:
            del self.agents[int(key)]
            return True
        except KeyError:
            return False
