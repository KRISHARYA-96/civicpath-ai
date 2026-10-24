

import asyncio
from datetime import datetime, timezone
from uuid import uuid4

from uagents import Agent, Context, Protocol

from uagents_core.contrib.protocols.chat import (
    ChatAcknowledgement,
    ChatMessage,
    TextContent,
    chat_protocol_spec,
)


# Initialize an event loop for the current Python environment.
asyncio.set_event_loop(asyncio.new_event_loop())

# Create the CivicPath AI agent.
agent = Agent(name="civicpath_ai")

# Create the standard Fetch.ai chat protocol.
chat_protocol = Protocol(spec=chat_protocol_spec)


def create_chat_message(text: str) -> ChatMessage:
    """Create a uniquely identified chat message."""
    return ChatMessage(
        timestamp=datetime.now(timezone.utc),
        msg_id=uuid4(),
        content=[
            TextContent(type="text", text=text)
        ],
    )


@chat_protocol.on_message(ChatMessage)
async def handle_chat_message(
    ctx: Context,
    sender: str,
    message: ChatMessage,
):
    """Process a user's message and return a response."""

    # Acknowledge the incoming message.
    await ctx.send(
        sender,
        ChatAcknowledgement(
            timestamp=datetime.now(timezone.utc),
            acknowledged_msg_id=message.msg_id,
        ),
    )

    # Extract the text content.
    user_text = [
        item.text
        for item in message.content
        if isinstance(item, TextContent)
    ]

    text = " ".join(user_text).strip()

    if not text:
        reply = (
            "Welcome to CivicPath AI!\n\n"
            "Which government service do you need help finding?"
        )
    else:
        reply = (
            "Welcome to CivicPath AI!\n\n"
            f"Your request: {text}\n\n"
            "I can help organize government-service searches, "
            "eligibility questions, document checklists, and action plans.\n\n"
            "Prototype status: verified government-service discovery "
            "is not yet connected to this chat. Eligibility must be "
            "assessed using verified official rules and sufficient "
            "applicant information. No application has been submitted."
        )

    await ctx.send(sender, create_chat_message(reply))
    ctx.logger.info("CivicPath AI processed a chat message.")


@chat_protocol.on_message(ChatAcknowledgement)
async def handle_acknowledgement(
    ctx: Context,
    sender: str,
    message: ChatAcknowledgement,
):
    """Handle acknowledgements received from other agents."""
    ctx.logger.info(
        f"Received acknowledgement from {sender} "
        f"for message {message.acknowledged_msg_id}"
    )


# Register the chat protocol and publish its manifest.
agent.include(chat_protocol, publish_manifest=True)


if __name__ == "__main__":
    print("Starting CivicPath AI...")
    print("Agent address:", agent.address)
    agent.run()

