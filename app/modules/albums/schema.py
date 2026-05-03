from app.core.schema import CamelCaseSchema
from app.modules.images.schema import ImageResponseDto


class AlbumCreateDto(CamelCaseSchema):
    title: str
    search: str | None = None



class AlbumImagesPageResponseDto(CamelCaseSchema):
    items: list[ImageResponseDto]
    page: int
    limit: int
    total: int


class RemoveAlbumImagesDto(CamelCaseSchema):
    image_ids: list[int]


class RemoveAlbumImagesResponseDto(CamelCaseSchema):
    removed_count: int
