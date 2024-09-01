import { Request, Response } from "express";
import logger from "./logger";
import { generateJPGs } from "./generate-jpgs";
import { generateAudio } from "./generate-audio";
import { LambdaClient, InvokeCommand } from "@aws-sdk/client-lambda";
import { Engine, VoiceId } from "@aws-sdk/client-polly";
import * as fs from "fs";
import * as path from "path";

// Configure AWS Lambda client
const lambdaClient = new LambdaClient({ region: process.env.AWS_REGION });

// Read Lambda function name from environment variable
const lambdaFunctionName = process.env.EXPORT_MP4_LAMBDA_NAME;
if (!lambdaFunctionName) {
  throw new Error("EXPORT_MP4_LAMBDA_NAME environment variable is not set.");
}

// Optional flag to save lambdaPayload for debugging
const savePayloadForDebugging = process.env.SAVE_PAYLOAD_FOR_DEBUGGING === 'true';

/**
 * Function to generate a video for a presentation.
 *
 * @param presentationId - The ID of the presentation.
 * @param s3Subdirectory - The subdirectory within the S3 bucket where input files (JPEGs and audio) are stored (defaults to '').
 * @param outputResolution - The desired resolution of the output video ('1920x1080', '1280x720', etc.).
 * @param theme - The theme for the slides ('light' or 'dark', defaults to 'dark').
 * @param footnotes - Boolean indicating whether footnotes are included.
 * @param engine - The engine to use for Polly ('standard' or 'neural').
 * @param voiceId - The voice ID to use for Polly (e.g., 'Joanna', 'Matthew').
 */
export async function generateVideo(
  presentationId: string,
  s3Subdirectory: string,
  outputResolution: string,
  theme: string = 'dark',
  footnotes: boolean,
  engine: string = 'standard',
  voiceId: string = 'Joanna'
): Promise<{ videoS3Key: string; manifest?: { slide_id: string; image_filename?: string; audio_filename?: string }[] } | Error> {
  logger.info(`Starting video generation for presentation ID: ${presentationId}`);

  try {
    // Convert engine and voiceId to the appropriate enums
    const pollyEngine = engine === 'neural' ? Engine.NEURAL : Engine.STANDARD;
    const pollyVoiceId = VoiceId[voiceId.toUpperCase() as keyof typeof VoiceId];

    // Run generateJPGs and generateAudio concurrently using Promise.all
    logger.info(`Generating JPEG images and audio files concurrently for presentation ID: ${presentationId}`);

    const [generateJpgsResult, generateAudioResult] = await Promise.all([
      generateJPGs(presentationId, theme, footnotes, outputResolution, s3Subdirectory),
      generateAudio(presentationId, s3Subdirectory),
    ]);

    // Handle errors if any of the operations failed
    if (generateJpgsResult instanceof Error) {
      throw generateJpgsResult;
    }

    if (generateAudioResult instanceof Error) {
      throw generateAudioResult;
    }

    logger.info(`JPEG images and audio files generated successfully. S3 Keys - Images ZIP: ${generateJpgsResult.s3Key}, Audio ZIP: ${generateAudioResult.audioS3Key}`);

    // Store the manifests in memory
    const imageManifest = generateJpgsResult.manifest;
    const audioManifest = generateAudioResult.manifest;

    logger.info(`Image manifest and audio manifest stored in memory`);

    // Combine manifests from images and audio by matching slide_id
    const combinedManifest = imageManifest
      .map(imageEntry => {
        const audioEntry = audioManifest.find(audio => audio.slide_id === imageEntry.slide_id);
        if (audioEntry && imageEntry.image_filename && audioEntry.audio_filename) {
          return {
            slide_id: imageEntry.slide_id,
            image_filename: imageEntry.image_filename,
            audio_filename: audioEntry.audio_filename,
          };
        }
        return null;
      })
      .filter(entry => entry !== null); // Omit any slides that are missing either an image_filename or an audio_filename

    logger.info(`Combined manifest after matching slide_id`);

    // Prepare payload for AWS Lambda function with the ZIP file S3 keys
    const lambdaPayload = {
      s3Subdirectory,
      imageZipS3Key: generateJpgsResult.s3Key,  // S3 key for the ZIP file containing all slide images
      audioZipS3Key: generateAudioResult.audioS3Key, // S3 key for the ZIP file containing all slide audio
      outputResolution,
      manifest: combinedManifest,  // Include the combined manifest in the payload
    };

    logger.info(`Prepared payload for Lambda function`);

    // Save lambdaPayload to a JSON file if debugging is enabled
    if (savePayloadForDebugging) {
      const payloadPath = path.join(__dirname, 'lambdaPayloadDebug.json');
      fs.writeFileSync(payloadPath, JSON.stringify(lambdaPayload, null, 2));
      logger.info(`Lambda payload saved for debugging at: ${payloadPath}`);
    }

    // Invoke AWS Lambda function for video stitching synchronously
    logger.info(`Initiating Lambda function: ${lambdaFunctionName}`);
    const invokeCommand = new InvokeCommand({
      FunctionName: lambdaFunctionName,
      Payload: Buffer.from(JSON.stringify(lambdaPayload)),
      InvocationType: "RequestResponse", // Synchronous invocation to wait for the response
    });

    const lambdaResponse = await lambdaClient.send(invokeCommand);

    // Parse Lambda response
    const responsePayload = JSON.parse(new TextDecoder().decode(lambdaResponse.Payload));
    if (lambdaResponse.StatusCode !== 200) {
      throw new Error(`Lambda function failed with status code ${lambdaResponse.StatusCode}`);
    }

    const videoS3Key = responsePayload.videoS3Key;
    if (!videoS3Key) {
      throw new Error('Lambda function did not return a valid S3 key for the video.');
    }

    logger.info(`Lambda function executed successfully, video stored at: ${videoS3Key}`);

    return { videoS3Key, manifest: combinedManifest }; // Return videoS3Key and combined manifest

  } catch (error: any) {
    logger.error(`Failed to generate video: ${error.message}\n${error.stack}`);
    return new Error(`Failed to generate video: ${error.message}`);
  }
}

/**
 * Express handler to generate video for a presentation via HTTP request.
 *
 * @param req - The Express request object.
 * @param res - The Express response object.
 */
export async function generateVideoHandler(req: Request, res: Response) {
  const { presentationId } = req.params;
  const { outputResolution, theme = 'dark', footnotes = false, engine = 'standard', voiceId = 'Joanna' } = req.body;

  // Use a fixed S3 subdirectory for storing videos
  const s3Subdirectory = '/export/mp4';

  try {
    const result = await generateVideo(presentationId, s3Subdirectory, outputResolution, theme, footnotes, engine, voiceId);

    if (result instanceof Error) {
      res.status(500).send(result.message);
    } else {
      // Send the videoS3Key in the response
      res.json({ videoS3Key: result.videoS3Key });
    }
  } catch (error: any) {
    logger.error(`Failed to process generateVideoHandler: ${error.message}\n${error.stack}`);
    res.status(500).send(`Internal Server Error: ${error.message}`);
  }
}
