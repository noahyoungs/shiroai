import { PollyClient, SynthesizeSpeechCommand, Engine, VoiceId } from "@aws-sdk/client-polly";
import archiver from "archiver";
import streamBuffers from "stream-buffers";
import globalLogger from "./logger";
import { uploadBufferToS3 } from "./generate-utils";
import { sanitizeFileName } from "./sanitize-file-name";

// Initialize the Polly client
const pollyClient = new PollyClient({ region: 'us-east-1' });

// Helper function to delay execution
const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

// Helper function to implement exponential backoff with jitter
async function exponentialBackoffRetry(fn: () => Promise<any>, retries: number, baseDelay: number): Promise<any> {
    let attempt = 0;
    while (attempt < retries) {
        try {
            return await fn();
        } catch (error: any) {
            if (attempt === retries - 1 || error.name !== 'ThrottlingException') {
                throw error;
            }
            const jitter = Math.random() * 100; // Random jitter between 0-100ms
            const delayTime = baseDelay * Math.pow(2, attempt) + jitter; // Exponential backoff with jitter
            globalLogger.warn(`Retrying after ${delayTime}ms due to error: ${error.message}`);
            await delay(delayTime);
            attempt++;
        }
    }
}

/**
 * Function to generate audio files for each slide of a presentation using Amazon Polly.
 *
 * @param presentationID - The ID of the presentation.
 * @param s3Subdirectory - The subdirectory within the S3 bucket under the presentationId where audio.zip will be stored.
 * @param sortedSlidesArray - An array of sorted slides.
 * @param engine - The engine to use for Polly ('standard' or 'neural').
 * @param voiceId - The voice ID to use for Polly (e.g., 'Joanna', 'Matthew').
 * @returns A promise resolving to an object with the S3 key of the audio zip file, or an error.
 */
export async function generateAudio(
    presentationID: string,
    s3Subdirectory: string,
    sortedSlidesArray: any[],
    voice: 'Ruth' | 'Gregory' | 'Danielle' = 'Danielle'
): Promise<{ audioS3Key: string; manifest: { slide_id: string; audio_filename: string }[] } | Error> {
    globalLogger.info(`Starting audio generation for presentation ID: ${presentationID}`);

    // Ensure s3Subdirectory is in the format '/subdir/' or '/'
    if (s3Subdirectory === '' || !s3Subdirectory) {
        s3Subdirectory = '/';
    }

    if (s3Subdirectory[0] !== '/') {
        s3Subdirectory = '/' + s3Subdirectory;
    }

    if (s3Subdirectory[s3Subdirectory.length - 1] !== '/') {
        s3Subdirectory = s3Subdirectory + '/';
    }

    // Convert the voice to the appropriate Polly voiceId
    if (voice !== 'Ruth' && voice !== 'Gregory' && voice !== 'Danielle') {
        globalLogger.warn(`Invalid voice ${voice}, defaulting to 'Danielle'`);
        voice = 'Danielle';
    }

    const voiceId = voice === 'Ruth' ? VoiceId.Ruth : voice === 'Gregory' ? VoiceId.Gregory : VoiceId.Danielle;

    // Get all the scripts, one for each slide
    const scripts = sortedSlidesArray.map(slide => slide?.script);

    // Collect audio files in memory
    const audioBuffers: { buffer: Buffer; slide: any; fileName: string }[] = [];
    const manifest: { slide_id: string; audio_filename: string }[] = []; // Updated manifest to be an array of objects

    // Generate audio for all valid scripts concurrently
    const pollyPromises = scripts.map((script, index) => {
        const slide = sortedSlidesArray[index];

        // Check if the script is a valid, non-empty string
        if (typeof script === 'string' && script.trim().length > 0) {
            const command = new SynthesizeSpeechCommand({
                OutputFormat: "mp3",
                Text: script,
                TextType: "text",
                Engine: Engine.LONG_FORM,
                VoiceId: voiceId,
            });

            const sendPollyCommand = () => pollyClient.send(command).then(pollyResult => {
                if (pollyResult.AudioStream) {
                    return pollyResult.AudioStream.transformToByteArray()
                        .then(audioStream => {
                            const buffer = Buffer.from(audioStream);
                            const fileName = sanitizeFileName(`Slide_${index + 1}`) + '.mp3';

                            audioBuffers.push({ buffer, slide, fileName });
                            manifest.push({ slide_id: slide!.id, audio_filename: fileName }); // Updated manifest structure

                            globalLogger.info(`Audio generated successfully for slide: ${slide!.id}`);
                        });
                } else {
                    globalLogger.warn(`No audio stream returned for slide: ${slide!.id}`);
                }
            });

            return exponentialBackoffRetry(sendPollyCommand, 5, 500) // 5 retries with base delay of 500ms
                .catch(error => {
                    globalLogger.error(`Error generating audio for slide ${slide!.id}: ${error.message}`);
                    return null; // Resolve with null to continue processing other slides
                });
        } else {
            globalLogger.warn(`Invalid or empty script for slide ${slide.slide_id}, skipping audio generation.`);
            return Promise.resolve(null);
        }
    });

    // Wait for all Polly requests to complete
    await Promise.all(pollyPromises);

    try {
        globalLogger.info(`Creating zip archive for audio files of presentation ID: ${presentationID}`);
        const zipStream = new streamBuffers.WritableStreamBuffer({
            initialSize: 100 * 1024,
            incrementAmount: 10 * 1024,
        });

        const archive = archiver('zip', { zlib: { level: 9 } });

        archive.on('error', (err) => {
            throw err;
        });

        archive.pipe(zipStream);

        audioBuffers.forEach(({ buffer, fileName }) => {
            archive.append(buffer, { name: fileName });
        });

        await archive.finalize();

        const zipBuffer = zipStream.getContents() as Buffer;
        const zipFileName = `${presentationID}${s3Subdirectory}audio.zip`;

        globalLogger.info(`Uploading zip archive to S3: ${zipFileName}`);
        await uploadBufferToS3(zipBuffer, zipFileName, 'application/zip');

        globalLogger.info(`Audio zip uploaded to S3 successfully: ${zipFileName}`);
        return { audioS3Key: zipFileName, manifest };

    } catch (error: any) {
        globalLogger.error(`Failed to create or upload audio zip archive: ${error.message}\n${error.stack}`);
        return new Error(`Failed to create or upload audio zip archive: ${error.message}`);
    }
}

