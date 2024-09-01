import json
import boto3
import tempfile
import traceback
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
        bucket_name = os.environ.get('BUCKET_NAME')
        if not bucket_name:
            print("BUCKET_NAME environment variable is not set.")
            return {
                "statusCode": 500,
                "body": json.dumps({"message": "BUCKET_NAME environment variable is not set"})
            }

        # Check if keeping ZIPs after processing is enabled
        keep_zips = os.environ.get('KEEP_ZIPS_AFTER_PROCESSING', 'false').lower() == 'true'

        # Validate and extract details from the event
        required_params = ['presentationID', 'imageZipS3Key', 'audioZipS3Key', 'manifest']
        missing_params = [param for param in required_params if param not in event or not event[param]]
        
        if missing_params:
            print(f"Missing or invalid parameters: {', '.join(missing_params)}")
            return {
                "statusCode": 400,
                "body": json.dumps({"message": f"Missing or invalid parameters: {', '.join(missing_params)}"})
            }

        presentation_id = event['presentationID']
        image_zip_s3_key = event['imageZipS3Key']
        audio_zip_s3_key = event['audioZipS3Key']
        manifest = event['manifest']
        s3_subdirectory = event.get('s3Subdirectory')

        # Ensure s3Subdirectory is in the format '/subdir/' or '/'
        if not s3_subdirectory:
            s3_subdirectory = '/'
        if not s3_subdirectory.startswith('/'):
            s3_subdirectory = '/' + s3_subdirectory
        if not s3_subdirectory.endswith('/'):
            s3_subdirectory = s3_subdirectory + '/'

        # Path to the silent audio file bundled with the Lambda package
        silent_audio_path = os.path.join(os.getcwd(), 'assets/silent_audio_1s.wav')

        # Create a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            print(f"Temporary directory created at {temp_dir}")

            # Download and extract image ZIP from S3
            image_dir = download_and_extract_zip(bucket_name, image_zip_s3_key, temp_dir, "images")
            print(f"Images extracted to {image_dir}")

            # Download and extract audio ZIP from S3
            audio_dir = download_and_extract_zip(bucket_name, audio_zip_s3_key, temp_dir, "audio")
            print(f"Audio files extracted to {audio_dir}")

            # Stitch video
            output_video_path = stitch_video(temp_dir, image_dir, audio_dir, silent_audio_path, manifest, filename='output_video.mp4')
            print(f"Video stitched and saved at {output_video_path}")

            # Corrected: Include presentation_id in the S3 key
            output_s3_key = f"{presentation_id}{s3_subdirectory}/final_video.mp4"
            print(f"Uploading file {output_video_path} to S3 at {output_s3_key}")

            try:
                upload_file_to_s3(output_video_path, bucket_name, output_s3_key)
                print(f"Successfully uploaded file to S3: s3://{bucket_name}{output_s3_key}")
            except Exception as e:
                print(f"Failed to upload file to S3: {str(e)}")
                raise

            # Delete the ZIP files unless the flag is set to keep them
            if not keep_zips:
                delete_file(temp_dir, image_zip_s3_key.split('/')[-1])
                delete_file(temp_dir, audio_zip_s3_key.split('/')[-1])

        # Return the S3 path of the generated video
        return {
            "statusCode": 200,
            "body": json.dumps({
                "videoS3Key": f"s3://{bucket_name}/{output_s3_key}"
            })
        }

    except Exception as e:
        print(f"Failed to process video: {str(e)}")
        traceback.print_exc()
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

    print(f"Downloading ZIP file from S3: {zip_s3_key} to {zip_path}")
    s3_client.download_file(bucket_name, zip_s3_key, zip_path)
    print(f"ZIP file downloaded to {zip_path}")

    # Extract the ZIP file
    import zipfile
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_path)
    print(f"ZIP file extracted to {extract_path}")

    return extract_path

def upload_file_to_s3(file_path, bucket_name, s3_key):
    """Uploads a file to S3."""
    print(f"Uploading {file_path} to bucket {bucket_name} with key {s3_key}")
    s3_client.upload_file(file_path, bucket_name, s3_key)
    print(f"Upload complete for {file_path} to {s3_key}")

def delete_file(directory, filename):
    """Deletes a specified file from the given directory."""
    try:
        file_path = os.path.join(directory, filename)
        os.remove(file_path)
        print(f"Deleted file: {file_path}")
    except Exception as e:
        print(f"Error deleting file {file_path}: {str(e)}")

def stitch_video(sandbox, image_dir, audio_dir, silent_audio_path, manifest, filename='output_video.mp4'):
    """Stitch images and audio files into a video based on the provided manifest."""
    final_clips = []

    # Create a silent audio clip
    silent_audio = AudioFileClip(silent_audio_path)

    for i, slide in enumerate(manifest):
        audio_path = os.path.join(audio_dir, slide['audio_filename'])
        image_path = os.path.join(image_dir, slide['image_filename'])

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
        if i < len(manifest) - 1:
            image_clip = image_clip.fx(vfx.fadeout, 0.5, final_color=(255, 255, 255))

        image_clip = image_clip.set_audio(audio_clip)

        final_clips.append(image_clip)

    # Combine the clips into a final video
    final_clip = concatenate_videoclips(final_clips, method="compose")

    # Specify the path for the temporary audio file in the writable /tmp directory
    temp_audio_path = os.path.join(sandbox, 'temp-audio.m4a')

    # Write the final video to a file in the /tmp directory
    output_path = os.path.join(sandbox, filename)
    print(f"Writing final video to {output_path}")
    final_clip.write_videofile(output_path,
                               codec='libx264',
                               audio_codec='aac',
                               temp_audiofile=temp_audio_path,
                               remove_temp=True,
                               fps=24)

    print(f"Video file written to {output_path}")
    return output_path
