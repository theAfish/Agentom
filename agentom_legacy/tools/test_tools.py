import google.genai.types as types
from google.adk.agents.callback_context import CallbackContext

async def save_uploaded_file(context: CallbackContext, filename: str, file_bytes: bytes):
    artifact = types.Part.from_bytes(data=file_bytes, mime_type="application/pdf")
    version = await context.save_artifact(filename=filename, artifact=artifact)
    return {"status": "success", "version": version}