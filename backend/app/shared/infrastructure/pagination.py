from math import ceil
from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationLinks(BaseModel):
    """HAL-style pagination links"""

    self: str = Field(..., description="Current page URL")
    first: str = Field(..., description="First page URL")
    last: str = Field(..., description="Last page URL")
    next: Optional[str] = Field(None, description="Next page URL (if available)")
    prev: Optional[str] = Field(None, description="Previous page URL (if available)")


class PaginationMetadata(BaseModel):
    """Pagination metadata"""

    total_items: int = Field(..., description="Total number of items in the database")
    total_pages: int = Field(..., description="Total number of pages")
    current_page: int = Field(..., description="Current page number (1-indexed)")
    page_size: int = Field(..., description="Number of items per page")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_previous: bool = Field(..., description="Whether there is a previous page")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response with HAL-style links"""

    items: List[T] = Field(..., description="List of items for the current page")
    metadata: PaginationMetadata = Field(..., description="Pagination metadata")
    links: PaginationLinks = Field(
        ..., serialization_alias="_links", description="HAL-style navigation links"
    )

    model_config = {"populate_by_name": True}


def build_pagination_links(
    base_url: str,
    current_page: int,
    total_pages: int,
    page_size: int,
) -> PaginationLinks:
    """
    Build HAL-style pagination links

    Args:
        base_url: Base URL for the endpoint (without query parameters)
        current_page: Current page number (1-indexed)
        total_pages: Total number of pages
        page_size: Items per page

    Returns:
        PaginationLinks object with navigation URLs
    """
    # Validate and clamp inputs to safe values
    current_page = max(1, current_page)
    total_pages = max(1, total_pages)

    # Remove any existing query parameters from base_url
    if "?" in base_url:
        base_url = base_url.split("?")[0]

    # Build links
    self_link = f"{base_url}?page={current_page}&limit={page_size}"
    first_link = f"{base_url}?page=1&limit={page_size}"
    last_link = f"{base_url}?page={total_pages}&limit={page_size}"

    next_link = None
    if current_page < total_pages:
        next_link = f"{base_url}?page={current_page + 1}&limit={page_size}"

    prev_link = None
    if current_page > 1:
        prev_link = f"{base_url}?page={current_page - 1}&limit={page_size}"

    return PaginationLinks(
        self=self_link,
        first=first_link,
        last=last_link,
        next=next_link,
        prev=prev_link,
    )


def build_pagination_metadata(
    total_items: int,
    current_page: int,
    page_size: int,
) -> PaginationMetadata:
    """
    Build pagination metadata

    Args:
        total_items: Total number of items in database
        current_page: Current page number (1-indexed)
        page_size: Items per page

    Returns:
        PaginationMetadata object
    """
    # Validate and clamp inputs to safe values
    current_page = max(1, current_page)
    total_items = max(0, total_items)
    page_size = max(1, page_size)

    total_pages = max(1, ceil(total_items / page_size))

    return PaginationMetadata(
        total_items=total_items,
        total_pages=total_pages,
        current_page=current_page,
        page_size=page_size,
        has_next=current_page < total_pages,
        has_previous=current_page > 1,
    )


def create_paginated_response(
    items: List[T],
    total_items: int,
    page: int,
    limit: int,
    base_url: str,
) -> PaginatedResponse[T]:
    """
    Create a complete paginated response

    Args:
        items: List of items for the current page
        total_items: Total number of items in database
        page: Current page number (1-indexed)
        limit: Items per page
        base_url: Base URL for the endpoint

    Returns:
        PaginatedResponse with items, metadata, and links
    """
    metadata = build_pagination_metadata(total_items, page, limit)
    links = build_pagination_links(base_url, page, metadata.total_pages, limit)

    return PaginatedResponse(
        items=items,
        metadata=metadata,
        links=links,
    )
