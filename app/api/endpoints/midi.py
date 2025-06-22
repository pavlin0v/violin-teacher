from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from pathlib import Path
import mido, asyncio, pretty_midi

from app.api.deps import get_session
from app.models.models import MidiFile, SheetMusic, User
from app.models.enums import FileStatus
from app.api import deps

router = APIRouter()
UPLOAD_DIR = Path("./uploads/midi")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/upload", response_model=dict)
async def upload_midi_inline(
    sheet_id: str,
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(deps.get_current_user),
):
    sweet_music = await session.scalar(select(SheetMusic).where(SheetMusic.sheet_id == sheet_id))

    if sweet_music is None:
        raise HTTPException(
            status_code=404,
            detail="Sheet music not found"
        )

    user_dir = UPLOAD_DIR /f"{current_user.user_id}"
    user_dir.mkdir(parents=True, exist_ok=True)
    dst: Path = user_dir / f"{sheet_id}.mid"

    # 1) читаем и сохраняем без блокировок
    content = await file.read()
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, dst.write_bytes, content)  # non-blocking disk write

    await file.close()

    # 2) создаём запись
    midi = MidiFile(
        sheet_id=sheet_id,
        uploaded_by=current_user.user_id,
        filename=f"{sheet_id}.mid",
        status=FileStatus.PENDING
    )
    session.add(midi)
    await session.commit()

    # 3) парсим в том же executor
    mid = await loop.run_in_executor(None, pretty_midi.PrettyMIDI, str(dst))
    midi.parsed_json = {
        "notes": [
            {"start": n.start, "end": n.end,
             "note": pretty_midi.note_number_to_name(n.pitch)}
            for inst in mid.instruments for n in inst.notes
        ]
    }

    # 👉 формат “Начало Конец Нота”
    midi.status = FileStatus.READY
    await session.commit()
    return {"midi_file_id": str(dst), "status": midi.status}

@router.delete("/delete/{midi_file_id}")
async def delete_midi_file(
    midi_file_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(deps.get_current_user),
):
    # 1) находим запись
    midi_file = await session.scalar(select(MidiFile).where(MidiFile.sheet_id == midi_file_id))

    if midi_file is None:
        raise HTTPException(
            status_code=404,
            detail="Midi file not found"
        )

    if midi_file.uploaded_by != current_user.user_id:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to delete this file"
        )

    # 2) удаляем файл неблокирующе
    file_path = UPLOAD_DIR / str(current_user.user_id) / midi_file.filename
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(
        None, lambda: file_path.unlink(missing_ok=True)
    )

    # 3) удаляем запись из БД
    await session.delete(midi_file)
    await session.commit()
    return {"detail": "Midi file deleted successfully"}
