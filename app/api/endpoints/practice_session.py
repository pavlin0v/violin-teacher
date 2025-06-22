from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api import deps
from app.models.models import PracticeSession, User, SheetMusic, MidiFile
from app.schemas.requests import PracticeSessionCreateRequest, PracticeSessionUpdateRequest
from app.schemas.responses import PracticeSessionResponse

router = APIRouter()


@router.post(
    "/create",
    response_model=PracticeSessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать сессию практики",
    description="Создать новую сессию практики для произведения",
)
async def create_practice_session(
    session_request: PracticeSessionCreateRequest,
    session: AsyncSession = Depends(deps.get_session),
    current_user: User = Depends(deps.get_current_user)
) -> PracticeSessionResponse:
    # Проверяем, что sheet_music существует и принадлежит пользователю
    sheet_music = await session.scalar(
        select(SheetMusic).where(
            SheetMusic.sheet_id == session_request.sheet_id,
            SheetMusic.owner_id == current_user.user_id
        )
    )
    if not sheet_music:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sheet music not found or you don't have access to it"
        )

    # Проверяем, что MIDI файл существует и связан с этой музыкой
    midi_file = await session.scalar(
        select(MidiFile).where(
            MidiFile.midi_file_id == session_request.midi_file_id,
            MidiFile.sheet_id == session_request.sheet_id
        )
    )
    if not midi_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="MIDI file not found or not associated with this sheet music"
        )

    practice_session = PracticeSession(
        user_id=current_user.user_id,
        sheet_id=session_request.sheet_id,
        midi_file_id=session_request.midi_file_id,
        metric_pref=session_request.metric_pref or {}
    )

    session.add(practice_session)
    await session.commit()
    await session.refresh(practice_session)

    return PracticeSessionResponse(
        session_id=practice_session.session_id,
        user_id=practice_session.user_id,
        sheet_id=practice_session.sheet_id,
        midi_file_id=practice_session.midi_file_id,
        status=practice_session.status,
        metric_pref=practice_session.metric_pref,
        audio_url=practice_session.audio_url,
        start_at=practice_session.start_at,
        end_at=practice_session.end_at,
        created_at=practice_session.created_at,
        updated_at=practice_session.updated_at,
    )


@router.patch(
    "/update/{session_id}",
    response_model=PracticeSessionResponse,
    status_code=status.HTTP_200_OK,
    summary="Обновить сессию практики",
    description="Обновить статус и данные сессии практики",
)
async def update_practice_session(
    session_id: str,
    session_request: PracticeSessionUpdateRequest,
    session: AsyncSession = Depends(deps.get_session),
    current_user: User = Depends(deps.get_current_user)
) -> PracticeSessionResponse:
    # Получаем сессию практики
    practice_session = await session.scalar(
        select(PracticeSession).where(PracticeSession.session_id == session_id)
    )

    if not practice_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Practice session not found"
        )

    if practice_session.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update this practice session"
        )

    # Обновляем только переданные поля
    data = session_request.model_dump(exclude_unset=True)

    for key, val in data.items():
        setattr(practice_session, key, val)

    await session.commit()
    await session.refresh(practice_session)

    return PracticeSessionResponse(
        session_id=practice_session.session_id,
        user_id=practice_session.user_id,
        sheet_id=practice_session.sheet_id,
        midi_file_id=practice_session.midi_file_id,
        status=practice_session.status,
        metric_pref=practice_session.metric_pref,
        audio_url=practice_session.audio_url,
        start_at=practice_session.start_at,
        end_at=practice_session.end_at,
        created_at=practice_session.created_at,
        updated_at=practice_session.updated_at,
    )


@router.delete(
    "/{session_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить сессию практики",
    description="Удалить сессию практики",
)
async def delete_practice_session(
    session_id: str,
    session: AsyncSession = Depends(deps.get_session),
    current_user: User = Depends(deps.get_current_user)
) -> None:
    practice_session = await session.scalar(
        select(PracticeSession).where(PracticeSession.session_id == session_id)
    )

    if not practice_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Practice session not found"
        )

    if practice_session.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this practice session"
        )

    await session.execute(delete(PracticeSession).where(PracticeSession.session_id == session_id))
    await session.commit()


@router.get(
    "/mylist",
    response_model=list[PracticeSessionResponse],
    status_code=status.HTTP_200_OK,
    summary="Получить мои сессии",
    description="Получить все сессии практики пользователя",
)
async def get_all_user_practice_sessions(
    session: AsyncSession = Depends(deps.get_session),
    current_user: User = Depends(deps.get_current_user)
) -> list[PracticeSessionResponse]:
    practice_sessions = await session.scalars(
        select(PracticeSession).where(PracticeSession.user_id == current_user.user_id)
    )
    return [PracticeSessionResponse(
        session_id=ps.session_id,
        user_id=ps.user_id,
        sheet_id=ps.sheet_id,
        midi_file_id=ps.midi_file_id,
        status=ps.status,
        metric_pref=ps.metric_pref,
        audio_url=ps.audio_url,
        start_at=ps.start_at,
        end_at=ps.end_at,
        created_at=ps.created_at,
        updated_at=ps.updated_at,
    ) for ps in practice_sessions]


@router.get(
    "/{session_id}",
    response_model=PracticeSessionResponse,
    status_code=status.HTTP_200_OK,
    summary="Получить сессию практики",
    description="Получить сессию практики по ID",
)
async def get_practice_session(
    session_id: str,
    session: AsyncSession = Depends(deps.get_session),
    current_user: User = Depends(deps.get_current_user)
) -> PracticeSessionResponse:
    practice_session = await session.scalar(
        select(PracticeSession).where(PracticeSession.session_id == session_id)
    )

    if not practice_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Practice session not found"
        )

    if practice_session.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view this practice session"
        )

    return PracticeSessionResponse(
        session_id=practice_session.session_id,
        user_id=practice_session.user_id,
        sheet_id=practice_session.sheet_id,
        midi_file_id=practice_session.midi_file_id,
        status=practice_session.status,
        metric_pref=practice_session.metric_pref,
        audio_url=practice_session.audio_url,
        start_at=practice_session.start_at,
        end_at=practice_session.end_at,
        created_at=practice_session.created_at,
        updated_at=practice_session.updated_at,
    )
