import sqlalchemy
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from fastapi.security import OAuth2PasswordRequestForm


from app.api import deps
from app.models.models import SheetMusic, User
from app.schemas.requests import SheetMusicRequest
from app.schemas.responses import SheetMusicResponse

router = APIRouter()


@router.post(
    "/create",
    response_model=SheetMusicResponse,
    status_code=status.HTTP_201_CREATED,
    description="Create new sheet music",
)
async def create_sheet_music(
    sheet_music_request: SheetMusicRequest,
    session: AsyncSession = Depends(deps.get_session),
    current_user: User = Depends(deps.get_current_user)
) -> SheetMusicResponse:
    sheet_music = await session.scalar(select(SheetMusic).where(SheetMusic.title == sheet_music_request.title))
    if sheet_music:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sheet music with this title already exists"
        )

    sheet_music = SheetMusic(
        title=sheet_music_request.title,
        composer=sheet_music_request.composer,
        description=sheet_music_request.description,
        owner_id=current_user.user_id,
    )

    session.add(sheet_music)
    await session.commit()
    await session.refresh(sheet_music)

    return SheetMusicResponse(
        sheet_id=sheet_music.sheet_id,
        title=sheet_music.title,
        author_name=sheet_music.composer,
        uploaded_by=sheet_music.owner_id,
        uploaded_at=sheet_music.created_at,
    )

@router.patch(
    "/update/{sheet_id}",
    response_model=SheetMusicResponse,
    status_code=status.HTTP_200_OK,
    description="Update sheet music",
)
async def update_sheet_music(
    sheet_id: str,
    sheet_music_request: SheetMusicRequest,
    session: AsyncSession = Depends(deps.get_session),
    current_user: User = Depends(deps.get_current_user)
) -> SheetMusicResponse:
    # 1. Получаем запись
    sheet_music = await session.scalar(select(SheetMusic).where(SheetMusic.sheet_id == sheet_id))

    if not sheet_music:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sheet music not found"
        )

    if sheet_music.owner_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update this sheet music"
        )

    # 2. Сбор данных только из запроса
    # Берём только реально переданные в JSON поля
    data = sheet_music_request.model_dump(exclude_unset=True)  # v2-метод :contentReference[oaicite:7]{index=7}

    # Обновляем экземпляр
    for key, val in data.items():
        setattr(sheet_music, key, val)

    await session.commit()
    await session.refresh(sheet_music)

    return SheetMusicResponse(
        sheet_id=sheet_music.sheet_id,
        title=sheet_music.title,
        author_name=sheet_music.composer,
        uploaded_by=sheet_music.owner_id,
        uploaded_at=sheet_music.created_at,
    )

@router.delete(
    "{sheet_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    description="Delete sheet music",
)
async def delete_sheet_music(
    sheet_id: str,
    session: AsyncSession = Depends(deps.get_session),
    current_user: User = Depends(deps.get_current_user)
) -> None:
    sheet_music = await session.scalar(select(SheetMusic).where(SheetMusic.sheet_id == sheet_id))

    if not sheet_music:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sheet music not found"
        )

    if sheet_music.owner_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this sheet music"
        )

    await session.execute(delete(SheetMusic).where(SheetMusic.sheet_id == sheet_id))
    await session.commit()


@router.get(
    "/mylist",
    response_model=list[SheetMusicResponse],
    status_code=status.HTTP_200_OK,
    description="Get all sheet music",
)
async def get_all_user_sheet_music(
    session: AsyncSession = Depends(deps.get_session),
    current_user: User = Depends(deps.get_current_user)
) -> list[SheetMusicResponse]:
    sheet_music_list = await session.scalars(
        select(SheetMusic).where(SheetMusic.owner_id == current_user.user_id)
    )
    return [SheetMusicResponse(
        sheet_id=sheet.sheet_id,
        title=sheet.title,
        author_name=sheet.composer,
        uploaded_by=sheet.owner_id,
        uploaded_at=sheet.created_at,
    ) for sheet in sheet_music_list]

@router.get(
    "/{sheet_id}",
    response_model=SheetMusicResponse,
    status_code=status.HTTP_200_OK,
    description="Get sheet music by ID",
)
async def get_sheet_music(
    sheet_id: str,
    session: AsyncSession = Depends(deps.get_session),
    current_user: User = Depends(deps.get_current_user)
) -> SheetMusicResponse:
    sheet_music = await session.scalar(select(SheetMusic).where(SheetMusic.sheet_id == sheet_id))

    if not sheet_music:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sheet music not found"
        )

    if sheet_music.owner_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this sheet music"
        )

    return SheetMusicResponse(
        sheet_id=sheet_music.sheet_id,
        title=sheet_music.title,
        author_name=sheet_music.composer,
        uploaded_by=sheet_music.owner_id,
        uploaded_at=sheet_music.created_at,
    )




