from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip, concatenate_audioclips
import moviepy.video.fx.all as vfx
import moviepy.audio.fx.all as afx
from io import BytesIO
import tempfile

silent_audio_path = "./assets/silent_audio_1s.wav"

def stitch_video(audio_files, image_files, filename='output_video.mp4'):
    """
    Stitches together a series of audio and image files to create a video, handling most inputs and outputs in memory.

    This function takes a list of audio files and a list of image files, and combines them to create a video
    where each image is displayed for the duration of its corresponding audio file. The audio for each image
    is prefixed and suffixed with a short silent clip to smooth transitions. The final video is returned as a
    file-like object in memory.

    Parameters:
    -----------
    audio_files : list of file-like objects (e.g., BytesIO)
        A list of file-like objects containing audio data in MP3 format. Each object corresponds to one clip.
        
    image_files : list of file-like objects (e.g., BytesIO)
        A list of file-like objects containing image data in PNG format. Each object corresponds to one image.

    filename : str, optional (default='output_video.mp4')
        The name of the output video file. Although this parameter is retained for compatibility, it has no effect on the in-memory operation of the function.

    Returns:
    --------
    video_buffer : BytesIO
        A file-like object containing the video data in MP4 format. This object can be used to save the video or pass it directly to other processes.

    Raises:
    -------
    ValueError:
        If the number of audio files does not match the number of image files.

    Example:
    --------
    audio_files = [BytesIO(open("audio1.mp3", "rb").read()), BytesIO(open("audio2.mp3", "rb").read())]
    image_files = [BytesIO(open("image1.png", "rb").read()), BytesIO(open("image2.png", "rb").read())]
    silent_audio_path = "path/to/silent_audio_1s.wav"

    video_data = stitch_video(audio_files, image_files, silent_audio_path)

    with open('output_video.mp4', 'wb') as f:
        f.write(video_data.read())
    """
    if len(audio_files) != len(image_files):
        raise ValueError(f"Number of audio ({len(audio_files)}) and image ({len(image_files)}) files do not match.")

    final_clips = []

    # Load the silent audio clip from the provided file path
    silent_audio = AudioFileClip(silent_audio_path)

    for i, (audio_file, image_file) in enumerate(zip(audio_files, image_files)):
        audio_clip = AudioFileClip(audio_file).fx(afx.audio_fadeout, 0.5)

        # Add silent audio at the beginning and end of the narration clips
        audio_clip = concatenate_audioclips([silent_audio, audio_clip, silent_audio])

        image_clip = ImageClip(image_file).set_duration(audio_clip.duration)

        # If not first clip, fade in
        if i > 0:
            image_clip = image_clip.fx(vfx.fadein, 0.5, initial_color=(255, 255, 255))
        # If not last clip, fade out
        if i < len(audio_files) - 1:
            image_clip = image_clip.fx(vfx.fadeout, 0.5, final_color=(255, 255, 255))

        image_clip = image_clip.set_audio(audio_clip)

        final_clips.append(image_clip)

    # Combine the clips
    final_clip = concatenate_videoclips(final_clips, method="compose")

    # Write video to a bytes buffer
    video_buffer = BytesIO()
    with tempfile.NamedTemporaryFile(delete=True) as temp_audio_file:
        final_clip.write_videofile(
            video_buffer.name,
            codec='libx264',
            audio_codec='aac',
            temp_audiofile=temp_audio_file.name,
            remove_temp=True,
            fps=24
        )

    video_buffer.seek(0)
    return video_buffer
