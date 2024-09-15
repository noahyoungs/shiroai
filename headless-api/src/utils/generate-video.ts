// headless-api/src/utils/generate-video.ts
import { Request, Response } from "express";
import globalLogger from "./logger";
import { generateJPGs } from "./generate-jpgs";
import { generateAudio } from "./generate-audio";
import { LambdaClient, InvokeCommand } from "@aws-sdk/client-lambda";
import { Engine, VoiceId } from "@aws-sdk/client-polly";
import { fetchAndSortSlides } from "./generate-utils";
import { sanitizeFileName } from "./sanitize-file-name";


import * as fs from "fs";
import * as path from "path";

// Configure AWS Lambda client
const lambdaClient = new LambdaClient();

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
 * @param presentationID - The ID of the presentation.
 * @param s3Subdirectory - The subdirectory within the S3 bucket where input files (JPEGs and audio) are stored (defaults to '').
 * @param outputResolution - The desired resolution of the output video ('1920x1080', '1280x720', etc.).
 * @param theme - The theme for the slides ('light' or 'dark', defaults to 'dark').
 * @param footnotes - Boolean indicating whether footnotes are included.
 * @param engine - The engine to use for Polly ('standard' or 'neural').
 * @param voiceId - The voice ID to use for Polly (e.g., 'Joanna', 'Matthew').
 */
export async function generateVideo(
  userId: string,
  presentationID: string,
  s3Subdirectory: string,
  outputResolution: string,
  theme: string = 'dark',
  footnotes: boolean,
  voice: "Ruth" | "Gregory" | "Danielle" = 'Danielle'
): Promise<{ videoS3Key: string; manifest?: { slide_id: string; image_filename?: string; audio_filename?: string }[] } | Error> {
  globalLogger.info(`Starting video generation for presentation ID: ${presentationID}`);

  try {
    // Fetch and sort slides for the presentation
    const {presentation, sortedSlidesArray}  = await fetchAndSortSlides(userId, presentationID);

    // Images zip file name
    const imagesZipFileName = sanitizeFileName(presentation.topic);

    // // Convert engine and voiceId to the appropriate enums
    // const pollyEngine = engine === 'neural' ? Engine.NEURAL : Engine.STANDARD;
    // const pollyVoiceId = VoiceId[voiceId.toUpperCase() as keyof typeof VoiceId];

    // Run generateJPGs and generateAudio concurrently using Promise.all
    globalLogger.info(`Generating JPEG images and audio files concurrently for presentation ID: ${presentationID}`);

    const [generateJpgsResult, generateAudioResult] = await Promise.all([
      generateJPGs(presentationID, theme, footnotes, outputResolution, sortedSlidesArray, imagesZipFileName, s3Subdirectory),
      generateAudio(presentationID, s3Subdirectory, sortedSlidesArray, voice),
    ]);

    // Handle errors if any of the operations failed
    if (generateJpgsResult instanceof Error) {
      throw generateJpgsResult;
    }

    if (generateAudioResult instanceof Error) {
      throw generateAudioResult;
    }

    globalLogger.info(`JPEG images and audio files generated successfully. S3 Keys - Images ZIP: ${generateJpgsResult.s3Key}, Audio ZIP: ${generateAudioResult.audioS3Key}`);

    // Store the manifests in memory
    const imageManifest = generateJpgsResult.manifest;
    const audioManifest = generateAudioResult.manifest;

    globalLogger.info(`Image manifest and audio manifest stored in memory`);

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

    globalLogger.info(`Combined manifest after matching slide_id`);

    // Prepare payload for AWS Lambda function with the ZIP file S3 keys
    const lambdaPayload = {
      presentationID,
      s3Subdirectory,
      imageZipS3Key: generateJpgsResult.s3Key,  // S3 key for the ZIP file containing all slide images
      audioZipS3Key: generateAudioResult.audioS3Key, // S3 key for the ZIP file containing all slide audio
      outputResolution,
      manifest: combinedManifest,  // Include the combined manifest in the payload
    };

    globalLogger.info(`Prepared payload for Lambda function`);

    // Save lambdaPayload to a JSON file if debugging is enabled
    if (savePayloadForDebugging) {
      const payloadPath = path.join(__dirname, 'lambdaPayloadDebug.json');
      fs.writeFileSync(payloadPath, JSON.stringify(lambdaPayload, null, 2));
      globalLogger.info(`Lambda payload saved for debugging at: ${payloadPath}`);
    }

    // // Invoke AWS Lambda function for video stitching synchronously
    // logger.info(`Initiating Lambda function: ${lambdaFunctionName}`);
    // const invokeCommand = new InvokeCommand({
    //   FunctionName: lambdaFunctionName,
    //   Payload: Buffer.from(JSON.stringify(lambdaPayload)),
    //   InvocationType: "RequestResponse", // Synchronous invocation to wait for the response
    // });

    // const lambdaResponse = await lambdaClient.send(invokeCommand);

    const lambdaResponse = {
      StatusCode: 500,
      Payload: undefined,
    };
    
    // Parse Lambda response
    const responsePayload = JSON.parse(new TextDecoder().decode(lambdaResponse.Payload));
    if (lambdaResponse.StatusCode !== 200) {
      throw new Error(`Lambda function failed with status code ${lambdaResponse.StatusCode}, message: ${responsePayload.message}`);
    }

    const videoS3Key = responsePayload.videoS3Key;
    if (!videoS3Key) {
      throw new Error('Lambda function did not return a valid S3 key for the video.');
    }

    globalLogger.info(`Lambda function executed successfully, video stored at: ${videoS3Key}`);

    return { videoS3Key, manifest: combinedManifest }; // Return videoS3Key and combined manifest

  } catch (error: any) {
    globalLogger.error(`Failed to generate video: ${error.message}\n${error.stack}`);
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
  const { resolution, theme = 'dark', footnotes = false, voice = 'Danielle' } = req.body;

  // error if resolution is not '1920x1080' or '1280x720'
  if (resolution !== '1920x1080' && resolution !== '1280x720') {
    res.status(400).send('Invalid resolution. Resolution must be "1920x1080" or "1280x720".');
    return;
  }

  // error if theme is not 'light' or 'dark'
  if (theme !== 'light' && theme !== 'dark') {
    res.status(400).send('Invalid theme. Theme must be "light" or "dark".');
    return;
  }

  // error if footnotes is not a boolean
  if (typeof footnotes !== 'boolean') {
    res.status(400).send('Invalid footnotes. Footnotes must be a boolean.');
    return;
  }

  // error if voice is not 'Ruth', 'Gregory', or 'Danielle'
  if (voice !== 'Ruth' && voice !== 'Gregory' && voice !== 'Danielle') {
    res.status(400).send('Invalid voice. Voice must be "Ruth", "Gregory", or "Danielle".');
    return;
  }

  // Use a fixed S3 subdirectory for storing videos
  const s3Subdirectory = `/export/mp4`;

  try {
    const result = await generateVideo((req as any).userId, presentationId, s3Subdirectory, resolution, theme, footnotes, voice);

    if (result instanceof Error) {
      res.status(500).send(result.message);
    } else {
      // Send the videoS3Key in the response
      res.json({ videoS3Key: result.videoS3Key });
    }
  } catch (error: any) {
    globalLogger.error(`Failed to process generateVideoHandler: ${error.message}\n${error.stack}`);
    res.status(500).send(`Internal Server Error: ${error.message}`);
  }
}
