import aiofiles
from aiobotocore.session import get_session
from botocore.exceptions import BotoCoreError, ClientError
from contextlib import asynccontextmanager
from io import BytesIO


# Create an async context manager for Polly client session
@asynccontextmanager
async def polly_client():
    session = get_session()
    async with session.create_client("polly", region_name="your-region", profile_name="PollyUser") as client:
        yield client





async def tts(text, gender, premium=False):
    """
    Synthesize speech from text using Amazon Polly, returning the resulting audio as an in-memory file-like object.

    This asynchronous function uses Amazon Polly to convert the provided text into speech, with options for different
    voices and engines. The resulting audio is returned as a `BytesIO` object, enabling in-memory handling of the audio
    data without the need for temporary file storage on disk.

    Parameters:
    -----------
    text : str
        The text to be converted into speech. Can be plain text or SSML (Speech Synthesis Markup Language).
        
    gender : str
        The desired gender of the voice. Accepted values are 'male' and 'female'.
        
    premium : bool, optional (default=False)
        If set to True, uses a premium voice with the 'long-form' engine. Otherwise, uses a standard voice.

    Returns:
    --------
    BytesIO
        A file-like object containing the synthesized speech in MP3 format. The object is in-memory and can be used
        directly without writing to disk.

    Raises:
    -------
    BotoCoreError, ClientError
        If the request to Amazon Polly fails, an exception is raised, and the function exits gracefully.

    IOError
        If there is an issue writing to the in-memory buffer, an IOError is raised, and the function exits gracefully.

    Example:
    --------
    async def main():
        audio_data = await tts("Hello World", "female", premium=False)

        # Save the audio to a file (optional)
        with open('output_speech.mp3', 'wb') as f:
            f.write(audio_data.read())

    asyncio.run(main())
    """
    # Count chars in text
    n = len(text)

    if premium:
        voice = 'Danielle' if gender.lower() == 'female' else 'Gregory'
        engine = 'long-form'
    else:
        voice = 'Joanna' if gender.lower() == 'female' else 'Matthew'
        engine = 'standard'

    if "<speak>" in text:
        # SSML
        text_type = "ssml"
    else:
        # Plain text
        text_type = "text"

    try:
        async with polly_client() as polly:
            # Request speech synthesis
            response = await polly.synthesize_speech(
                Text=text, 
                OutputFormat="mp3",
                VoiceId=voice, 
                Engine=engine, 
                TextType=text_type
            )
    except (BotoCoreError, ClientError) as error:
        # The service returned an error, exit gracefully
        print(error)
        sys.exit(-1)

    # Access the audio stream from the response
    if "AudioStream" in response:
        # Note: Closing the stream is important because the service throttles on the
        # number of parallel connections. Here we are using contextlib.closing to
        # ensure the close method of the stream object will be called automatically
        # at the end of the with statement's scope.
        audio_data = BytesIO()
        async with response["AudioStream"] as stream:
            try:
                # Write the output as a binary stream to the in-memory BytesIO object
                audio_data.write(await stream.read())
            except IOError as error:
                # Could not write to the in-memory buffer, exit gracefully
                print(error)
                sys.exit(-1)

        audio_data.seek(0)  # Rewind the BytesIO object to the beginning
    else:
        # The response didn't contain audio data, exit gracefully
        print("Could not stream audio")
        sys.exit(-1)

    # Log the number of characters
    if premium:
        await log_running_character_count(n)

    return audio_data  # Return the BytesIO object containing the audio data


# Example usage
# import asyncio
# 
# async def main():
#     audio_data = await tts("Hello World", "female", premium=False)
# 
#     # Save the audio to a file (if needed)
#     with open('output_speech.mp3', 'wb') as f:
#         f.write(audio_data.read())
# 
# asyncio.run(main())
