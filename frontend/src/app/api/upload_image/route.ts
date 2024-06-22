import { NextRequest, NextResponse } from 'next/server';
import { uuidv7 } from 'uuidv7';  // Using uuidv7 as per your preference
import { S3Client, PutObjectCommand } from '@aws-sdk/client-s3';
import { RekognitionClient, DetectLabelsCommand } from '@aws-sdk/client-rekognition';
import sharp from 'sharp';
import busboy from 'busboy';
import { Readable } from 'stream';

const s3 = new S3Client({
  region: process.env.AWS_REGION,
  credentials: {
    accessKeyId: process.env.AWS_ACCESS_KEY_ID!,
    secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY!,
  },
});

const rekognition = new RekognitionClient({
  region: process.env.AWS_REGION,
  credentials: {
    accessKeyId: process.env.AWS_ACCESS_KEY_ID!,
    secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY!,
  },
});

export const config = {
  api: {
    bodyParser: false,
  },
};

export async function POST(req: NextRequest) {
  console.log("Starting POST request handling...");

  const headers: Record<string, string> = {};
  req.headers.forEach((value, key) => {
    headers[key] = value;
  });

  const bb = busboy({ headers });
  const fields: { [key: string]: string } = {};
  let fileBuffer: Buffer | null = null;
  let fileName: string | null = null;

  return new Promise((resolve, reject) => {
    bb.on('file', (fieldname, file, info) => {
      console.log(`File [${fieldname}]: filename: ${info.filename}, encoding: ${info.encoding}, mimeType: ${info.mimeType}`);
      const chunks: Buffer[] = [];
      file.on('data', (data) => {
        console.log(`File [${fieldname}] got ${data.length} bytes`);
        chunks.push(data);
      }).on('end', () => {
        console.log(`File [${fieldname}] Finished`);
        fileBuffer = Buffer.concat(chunks);
        fileName = info.filename;
      });
    });

    bb.on('field', (fieldname, val) => {
      console.log(`Field [${fieldname}]: value: ${val}`);
      fields[fieldname] = val;
    });

    bb.on('close', async () => {
      console.log('Busboy finished parsing form data.');
      
      const presentationID = fields.presentationID;
      const shape = fields.shape;

      if (!fileBuffer || !presentationID || !shape) {
        console.error("Missing required parameters");
        return resolve(NextResponse.json({ error: 'Missing required parameters' }, { status: 400 }));
      }

      const maxSize = shape === 'full' ? { width: 1920, height: 1080 } : { width: 1080, height: 1080 };

      try {
        console.log("Processing image with sharp...");
        const resizedBufferWebp = await sharp(fileBuffer)
          .resize(maxSize.width, maxSize.height, { fit: 'inside' })
          .webp()
          .toBuffer();

        const resizedBufferJpeg = await sharp(fileBuffer)
          .resize(maxSize.width, maxSize.height, { fit: 'inside' })
          .jpeg()
          .toBuffer();

        const metadata = await sharp(fileBuffer).metadata();
        const width = metadata.width;
        const height = metadata.height;

        const uploadParams = {
          Bucket: process.env.SOURCES_BUCKET_NAME!,
          Key: `${presentationID}/backgrounds/${uuidv7()}.webp`,
          Body: resizedBufferWebp,
          ContentType: 'image/webp',
        };

        console.log("Uploading image to S3 with params:", uploadParams);

        const command = new PutObjectCommand(uploadParams);
        const uploadResult = await s3.send(command);

        console.log("S3 upload result:", uploadResult);

        const detectLabelsParams = {
          Image: {
            Bytes: resizedBufferJpeg,
          },
          MaxLabels: 10,
          MinConfidence: 75,
        };

        console.log("Detecting labels with Rekognition...");
        const detectLabelsCommand = new DetectLabelsCommand(detectLabelsParams);
        const labelsResult = await rekognition.send(detectLabelsCommand);

        console.log("Rekognition labels result:", labelsResult);

        const labelNames = labelsResult.Labels?.map(label => label.Name).join(', ') || '';

        resolve(NextResponse.json({
          s3_key: uploadParams.Key,
          width: width,
          height: height,
          prompt: labelNames
        }, { status: 200 }));
      } catch (error) {
        console.error("Error processing, uploading image or detecting labels:", error);
        resolve(NextResponse.json({ error: error.message }, { status: 500 }));
      }
    });

    bb.on('error', (error) => {
      console.error("Busboy error:", error);
      reject(error);
    });

    if (req.body) {
      const stream = Readable.from(req.body);
      stream.pipe(bb);
    } else {
      reject(new Error("No body in request"));
    }
  });
}
