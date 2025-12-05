import asyncio
import time
import os
from types import SimpleNamespace

import pytest

from agentom import logging_utils
from agentom.settings import settings


def test_plugin_logs_user_and_tool(tmp_path, monkeypatch):
    # Point logs to a temporary workspace for the test
    monkeypatch.setattr(settings, 'WORKSPACE_DIR', tmp_path)

    # Re-run setup to ensure the test logger writes into tmp_path/logs
    logger = logging_utils.setup_logging()

    # Find the file handler path
    log_file = None
    for h in logger.handlers:
        if hasattr(h, 'baseFilename'):
            log_file = h.baseFilename
            break

    assert log_file and os.path.exists(os.path.dirname(log_file))

    plugin = logging_utils.CustomLoggingPlugin()

    # Fake invocation context and user message
    invocation = SimpleNamespace(session_id='sess-123')
    user_message = SimpleNamespace(parts=[SimpleNamespace(text='Hello Agent')])

    asyncio.run(plugin.on_user_message_callback(invocation_context=invocation, user_message=user_message))

    # Simulate a tool call
    fake_tool = SimpleNamespace(name='list_files')
    args = {'path': '/tmp'}
    asyncio.run(plugin.before_tool_callback(tool=fake_tool, tool_args=args, tool_context=None))
    asyncio.run(plugin.after_tool_callback(tool=fake_tool, tool_args=args, tool_context=None, result={'ok': True}))

    # Simulate a model response
    model_response = SimpleNamespace(content=SimpleNamespace(parts=[SimpleNamespace(text='Here is the answer.')]))
    asyncio.run(plugin.after_model_callback(callback_context=None, llm_response=model_response))

    # Give logging a moment to flush
    time.sleep(0.01)

    # Read the log file and assert our messages are present
    with open(log_file, 'r', encoding='utf-8') as f:
        data = f.read()

    assert 'Hello Agent' in data
    assert 'Tool Call: list_files' in data or 'Tool args' in data
    assert 'Here is the answer.' in data
