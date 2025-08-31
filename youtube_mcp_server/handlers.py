import os
from typing import Dict, List, Any
from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable,
)
import re

# Load environment variables
load_dotenv()
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")


def validate_youtube_api_key() -> None:
    """Validate that YouTube API key is available."""
    if not YOUTUBE_API_KEY:
        raise ValueError("YOUTUBE_API_KEY environment variable is required")


def parse_duration(duration_str: str) -> int:
    """Parse ISO 8601 duration string to seconds."""
    if not duration_str:
        return 0

    # Parse PT format (e.g., PT4M13S, PT1H2M30S)
    pattern = r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?"
    match = re.match(pattern, duration_str)

    if not match:
        return 0

    hours = int(match.group(1)) if match.group(1) else 0
    minutes = int(match.group(2)) if match.group(2) else 0
    seconds = int(match.group(3)) if match.group(3) else 0

    return hours * 3600 + minutes * 60 + seconds


def build_youtube_service():
    """Build YouTube API service client."""
    validate_youtube_api_key()
    return build("youtube", "v3", developerKey=YOUTUBE_API_KEY)


async def search_videos(query: str, pageToken: str = None) -> Dict[str, Any]:
    """
    Search for videos on YouTube.

    Args:
        query: Search query string
        pageToken: Token for pagination (optional)

    Returns:
        Dictionary containing search results with basic video information
    """
    # Input validation
    if not query or not query.strip():
        raise ValueError("query parameter is required and cannot be empty")

    try:
        # Build YouTube service
        youtube = build_youtube_service()

        # Perform search
        search_params = {
            "q": query.strip(),
            "part": "snippet",
            "type": "video",
            "maxResults": 10,
            "order": "relevance",
        }

        if pageToken:
            search_params["pageToken"] = pageToken

        search_response = youtube.search().list(**search_params).execute()

        # Process results - convert search results to the expected format
        items = []
        for item in search_response["items"]:
            processed_item = {
                "id": {"kind": item["id"]["kind"], "videoId": item["id"]["videoId"]},
                "snippet": item["snippet"],
            }
            items.append(processed_item)

        # Build response
        result = {
            "items": items,
            "pageInfo": {
                "totalResults": search_response.get("pageInfo", {}).get(
                    "totalResults", 0
                ),
                "resultsPerPage": len(items),
            },
        }

        # Add pagination tokens if available
        if search_response.get("nextPageToken"):
            result["nextPageToken"] = search_response["nextPageToken"]
        if search_response.get("prevPageToken"):
            result["prevPageToken"] = search_response["prevPageToken"]

        return result

    except HttpError as e:
        error_details = e.error_details[0] if e.error_details else {}
        error_message = error_details.get("message", str(e))
        raise ValueError(f"YouTube API error: {error_message}")
    except Exception as e:
        raise ValueError(f"Unexpected error during video search: {str(e)}")


async def get_videos(ids: List[str], parts: List[str] = None) -> Dict[str, Any]:
    """
    Get detailed information about specific YouTube videos.

    Args:
        ids: List of video IDs to retrieve
        parts: List of parts to retrieve (default: ["snippet"])

    Returns:
        Dictionary containing detailed video information
    """
    # Input validation
    if not ids:
        raise ValueError("ids parameter is required and cannot be empty")

    if len(ids) > 50:
        raise ValueError("Maximum 50 video IDs allowed per request")

    # Validate all IDs are non-empty strings
    for video_id in ids:
        if not video_id or not isinstance(video_id, str) or not video_id.strip():
            raise ValueError("All video IDs must be non-empty strings")

    # Default parts if not provided
    if parts is None:
        parts = ["snippet"]

    # Validate parts
    valid_parts = {
        "snippet",
        "contentDetails",
        "statistics",
        "status",
        "player",
        "recordingDetails",
        "fileDetails",
        "processingDetails",
        "suggestions",
        "liveStreamingDetails",
        "localizations",
        "topicDetails",
    }
    invalid_parts = set(parts) - valid_parts
    if invalid_parts:
        raise ValueError(
            f"Invalid parts: {invalid_parts}. Valid parts are: {valid_parts}"
        )

    try:
        # Build YouTube service
        youtube = build_youtube_service()

        # Get detailed video information
        videos_response = (
            youtube.videos().list(part=",".join(parts), id=",".join(ids)).execute()
        )

        # Process results and add parsed duration for contentDetails
        items = []
        for video in videos_response["items"]:
            # Add parsed duration in seconds for convenience if contentDetails is requested
            if "contentDetails" in parts and "contentDetails" in video:
                if "duration" in video["contentDetails"]:
                    video["contentDetails"]["durationSeconds"] = parse_duration(
                        video["contentDetails"]["duration"]
                    )
            items.append(video)

        # Build response
        result = {
            "items": items,
            "pageInfo": {"totalResults": len(items), "resultsPerPage": len(items)},
        }

        return result

    except HttpError as e:
        error_details = e.error_details[0] if e.error_details else {}
        error_message = error_details.get("message", str(e))
        raise ValueError(f"YouTube API error: {error_message}")
    except Exception as e:
        raise ValueError(f"Unexpected error during video retrieval: {str(e)}")


async def get_transcript(videoId: str, language: str = None) -> Dict[str, Any]:
    """
    Get transcript for a specific YouTube video.

    Uses the youtube-transcript-api library to fetch actual video transcripts
    from YouTube. Supports multiple languages and automatic/manual captions.
    Priority: 1) Requested language, 2) English, 3) Manual transcripts, 4) Any available.

    Args:
        videoId: YouTube video ID
        language: Preferred language code (e.g., 'en', 'es', 'fr'). Optional.

    Returns:
        Dictionary containing transcript information with text, timestamps, and metadata
    """
    # Input validation
    if not videoId or not videoId.strip():
        raise ValueError("videoId parameter is required and cannot be empty")

    video_id = videoId.strip()

    try:
        # Create API instance and get transcript list
        api = YouTubeTranscriptApi()
        transcript_list = api.list(video_id)

        # Try to find transcript in preferred order: requested language -> English -> manual -> any
        transcript = None
        language_code = None

        # 1. Try requested language first (if provided)
        if language and language.strip():
            try:
                transcript = transcript_list.find_transcript([language.strip()])
                language_code = language.strip()
            except NoTranscriptFound:
                pass

        # 2. If no requested language found, try English
        if transcript is None:
            try:
                transcript = transcript_list.find_transcript(["en"])
                language_code = "en"
            except NoTranscriptFound:
                pass

        # 3. If no English, try to get any manually created transcript
        if transcript is None:
            try:
                for t in transcript_list:
                    if not t.is_generated:  # Prefer manual transcripts
                        transcript = t
                        language_code = t.language_code
                        break
            except StopIteration:
                pass

        # 4. If no manual transcripts, use any available
        if transcript is None:
            try:
                transcript = next(iter(transcript_list))
                language_code = transcript.language_code
            except StopIteration:
                # No transcripts available at all
                pass

        if transcript is None:
            return {
                "videoId": video_id,
                "transcript": [],
                "available": False,
                "language": None,
            }

        # Fetch the actual transcript data
        transcript_data = transcript.fetch()

        # Format transcript data to match our schema
        formatted_transcript = []
        for entry in transcript_data:
            formatted_transcript.append(
                {
                    "text": entry.text,
                    "start": float(entry.start),
                    "duration": float(entry.duration),
                }
            )

        return {
            "videoId": video_id,
            "transcript": formatted_transcript,
            "available": True,
            "language": language_code,
        }

    except TranscriptsDisabled:
        return {
            "videoId": video_id,
            "transcript": [],
            "available": False,
            "language": None,
        }
    except NoTranscriptFound:
        return {
            "videoId": video_id,
            "transcript": [],
            "available": False,
            "language": None,
        }
    except VideoUnavailable:
        raise ValueError(f"Video {video_id} is unavailable or does not exist")
    except Exception as e:
        raise ValueError(f"Unexpected error during transcript retrieval: {str(e)}")


# Tool functions mapping
TOOL_FUNCTIONS = {
    "search_videos": search_videos,
    "get_videos": get_videos,
    "get_transcript": get_transcript,
}
