import json
import boto3
import tempfile
import os
from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip, concatenate_audioclips
import moviepy.video.fx.all as vfx
import moviepy.audio.fx.all as afx

s3_client = boto3.client('s3')

def lambda_handler(event, context):
    """Lambda function handler for processing a presentation request."""
    try:
        # Update PATH to include the ffmpeg binary from the Lambda layer
        os.environ["PATH"] = f"/opt/bin:{os.environ['PATH']}"

        # Get the bucket name from environment variables
        bucket_name = os.environ['BUCKET_NAME']

        # Extract details from the event
        image_zip_s3_key = event['imageZipS3Key']
        audio_zip_s3_key = event['audioZipS3Key']

        # Path to the silent audio file bundled with the Lambda package
        silent_audio_path = os.path.join(os.getcwd(), 'assets/silent_audio_1s.wav')

        # Create a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Download and extract image ZIP from S3
            image_dir = download_and_extract_zip(bucket_name, image_zip_s3_key, temp_dir, "images")

            # Download and extract audio ZIP from S3
            audio_dir = download_and_extract_zip(bucket_name, audio_zip_s3_key, temp_dir, "audio")

            # Stitch video
            output_video_path = stitch_video(temp_dir, image_dir, audio_dir, silent_audio_path, filename='output_video.mp4')

            # Upload the final video to S3
            output_s3_key = f"{event['s3Subdirectory']}/final_video.mp4"
            upload_file_to_s3(output_video_path, bucket_name, output_s3_key)

        # Return the S3 path of the generated video
        return {
            "statusCode": 200,
            "body": json.dumps({
                "videoS3Key": f"s3://{bucket_name}/{output_s3_key}",
            }),
        }

    except Exception as e:
        print(f"Failed to process video: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({
                "message": f"Failed to process video: {str(e)}",
            }),
        }

def download_and_extract_zip(bucket_name, zip_s3_key, temp_dir, extract_to_subdir):
    """Downloads a ZIP file from S3 and extracts it to a specified subdirectory."""
    zip_path = f"{temp_dir}/{zip_s3_key.split('/')[-1]}"
    extract_path = f"{temp_dir}/{extract_to_subdir}"

    # Download the ZIP file from S3
    s3_client.download_file(bucket_name, zip_s3_key, zip_path)

    # Extract the ZIP file
    import zipfile
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_path)

    return extract_path

def upload_file_to_s3(file_path, bucket_name, s3_key):
    """Uploads a file to S3."""
    s3_client.upload_file(file_path, bucket_name, s3_key)

def stitch_video(sandbox, image_dir, audio_dir, silent_audio_path, filename='output_video.mp4'):
    """Stitch images and audio files into a video."""
    audio_files = sorted([f for f in os.listdir(audio_dir) if f.endswith('.mp3')])
    image_files = sorted([f for f in os.listdir(image_dir) if f.endswith('.jpg') or f.endswith('.png')])

    if len(audio_files) != len(image_files):
        raise ValueError(f"Number of audio ({len(audio_files)}) and image ({len(image_files)}) files do not match.")

    final_clips = []

    # Create a silent audio clip
    silent_audio = AudioFileClip(silent_audio_path)

    for i, (audio_file, image_file) in enumerate(zip(audio_files, image_files)):
        audio_path = os.path.join(audio_dir, audio_file)
        image_path = os.path.join(image_dir, image_file)

        # Create audio clip with fade effects
        audio_clip = AudioFileClip(audio_path).fx(afx.audio_fadeout, 0.5)

        # Add silent audio at the beginning and end of the narration clips
        audio_clip = concatenate_audioclips([silent_audio, audio_clip])
        audio_clip = concatenate_audioclips([audio_clip, silent_audio])

        image_clip = ImageClip(image_path).set_duration(audio_clip.duration)

        # If not the first clip, fade in
        if i > 0:
            image_clip = image_clip.fx(vfx.fadein, 0.5, initial_color=(255, 255, 255))
        # If not the last clip, fade out
        if i < len(audio_files) - 1:
            image_clip = image_clip.fx(vfx.fadeout, 0.5, final_color=(255, 255, 255))

        image_clip = image_clip.set_audio(audio_clip)

        final_clips.append(image_clip)

    # Combine the clips into a final video
    final_clip = concatenate_videoclips(final_clips, method="compose")

    # Specify the path for the temporary audio file in the writable /tmp directory
    temp_audio_path = os.path.join(sandbox, 'temp-audio.m4a')

    # Write the final video to a file in the /tmp directory
    output_path = os.path.join(sandbox, filename)
    final_clip.write_videofile(output_path,
                               codec='libx264',
                               audio_codec='aac',
                               temp_audiofile=temp_audio_path,  # Use temp_audio_path in /tmp
                               remove_temp=True,
                               fps=24)

    return output_path
