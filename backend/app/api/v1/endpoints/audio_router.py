from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
import io
from app.services.llms.openai_client import openai_async_client

router = APIRouter()


@router.post("/transcribe", tags=["transcribe", "openai"])
async def transcribe_audio(file: UploadFile = File(...)) -> JSONResponse:
    print("Transcribing audio file")
    print(file.filename, file.content_type)
    try:

        response = await openai_async_client.audio.transcriptions.create(
            model="whisper-1",
            file=(file.filename, file.file, file.content_type),
            language="en",
            response_format="verbose_json",
            temperature=0.5,
            timestamp_granularities=["segment"],
            prompt="Transcribe the following audio file",
            timeout=600,
        )

        print(response, end=f"\n{'-'*50}\n")
        return JSONResponse(content=response.model_dump_json())
    except Exception as e:
        print("Failed with exception", e)
        raise HTTPException(status_code=500, detail=str(e))
