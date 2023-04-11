import pytest
from src.manager import AgentManager

def test_agent_manager():
    agent_manager = AgentManager()

    # Test create_agent
    task = "Sample task"
    prompt = "Hello agent!"
    model = "gpt-4"  # Replace this with your actual model name
    key, agent_reply = agent_manager.create_agent(task, prompt, model)
    assert key == 0
    assert agent_reply is not None

    # Test message_agent
    message = "What is the meaning of life?"
    agent_response = agent_manager.message_agent(key, message)
    assert agent_response is not None

    # Test list_agents
    agent_list = agent_manager.list_agents()
    assert len(agent_list) == 1
    assert agent_list[0] == (key, task)

    # Test delete_agent
    assert agent_manager.delete_agent(key)
    assert not agent_manager.delete_agent(key)  # Agent should no longer exist
