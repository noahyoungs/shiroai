// headless-service/src/routes/generate-video-router.ts
import express from "express";
import { generateVideoHandler } from "../utils/generate-video";

const router = express.Router();

router.post("/:presentationId/mp4", generateVideoHandler);

export default router;