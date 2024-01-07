from unittest.mock import AsyncMock
import pytest
from commands.help_command import help_message


@pytest.mark.asyncio
async def test_start_message(setup_state):
    message = AsyncMock()
    await help_message(message=message, state=setup_state)
    
    message.answer.assert_called()